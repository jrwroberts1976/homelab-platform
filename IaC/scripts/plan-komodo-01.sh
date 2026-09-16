#!/usr/bin/env bash

set -eu
umask 077

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 ||
    die "Required command not found: $1"
}

KOMODO_HOSTNAME="komodo-01"
KOMODO_IPV4="192.168.2.58"
KOMODO_CT_ID="104"
KOMODO_MAC="02:00:00:00:01:04"

TARGET_PVE="PROXMOX"
PVE_HOST="192.168.2.70"

LXC_TEMPLATE="local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"

PVE_ENV_FILE="$HOME/.config/homelab-iac/proxmox.env"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
AUTOMATION_PUBLIC_KEY="$HOME/.ssh/proxmox-automation.pub"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/komodo-01"

STATE_ROOT="$HOME/.local/state/homelab-iac/komodo-01"
DEPLOY_DIR="$STATE_ROOT/terraform"

RUNNER_TMP="${RUNNER_TEMP:-/var/tmp}"
PLAN_FILE="$RUNNER_TMP/komodo-01-create.tfplan"
PLAN_JSON="$RUNNER_TMP/komodo-01-create.tfplan.json"

for cmd in terraform jq ssh; do
  require_cmd "$cmd"
done

[ -r "$PVE_ENV_FILE" ] ||
  die "Missing Proxmox credential file: $PVE_ENV_FILE"

[ -r "$PVE_ROOT_SSH_KEY" ] ||
  die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"

[ -r "$AUTOMATION_PUBLIC_KEY" ] ||
  die "Missing automation public key: $AUTOMATION_PUBLIC_KEY"

# shellcheck disable=SC1090
. "$PVE_ENV_FILE"

: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from $PVE_ENV_FILE}"
export TF_VAR_proxmox_api_token

PUBLIC_KEY="$(tr -d '\r\n' < "$AUTOMATION_PUBLIC_KEY")"

printf '%s\n' "$PUBLIC_KEY" |
  grep -Eq '^ssh-(ed25519|rsa|ecdsa)' ||
  die "Automation public key is invalid"

TF_VAR_ssh_public_keys="$(
  jq -cn --arg key "$PUBLIC_KEY" '[$key]'
)"

export TF_VAR_ssh_public_keys

printf '===== KOMODO-01 LXC TERRAFORM PLAN-ONLY WORKFLOW =====\n'
printf 'hostname=%s\n' "$KOMODO_HOSTNAME"
printf 'ipv4=%s\n' "$KOMODO_IPV4"
printf 'ct_id=%s\n' "$KOMODO_CT_ID"
printf 'mac=%s\n' "$KOMODO_MAC"
printf 'pve=%s\n' "$TARGET_PVE"
printf 'template=%s\n' "$LXC_TEMPLATE"
printf 'terraform_state=%s\n' "$DEPLOY_DIR"
printf 'NOTE: Terraform apply is not performed by this workflow.\n'

printf '\n===== LIVE SAFETY PREFLIGHT =====\n'

ssh \
  -i "$PVE_ROOT_SSH_KEY" \
  -o BatchMode=yes \
  -o ConnectTimeout=5 \
  "root@$PVE_HOST" \
  'test "$(hostname)" = "PROXMOX" &&
   systemctl is-active --quiet pve-cluster &&
   mountpoint -q /etc/pve' ||
  die "PROXMOX identity/health gate failed"

if ssh \
  -i "$PVE_ROOT_SSH_KEY" \
  -o BatchMode=yes \
  "root@$PVE_HOST" \
  "find /etc/pve/nodes -type f \
     \( -path '*/qemu-server/$KOMODO_CT_ID.conf' \
        -o -path '*/lxc/$KOMODO_CT_ID.conf' \) \
     -print -quit | grep -q ."
then
  die "Cluster guest ID $KOMODO_CT_ID already exists"
fi

if ssh \
  -i "$PVE_ROOT_SSH_KEY" \
  -o BatchMode=yes \
  "root@$PVE_HOST" \
  "grep -RFiq '$KOMODO_MAC' /etc/pve/nodes"
then
  die "MAC $KOMODO_MAC already exists in the Proxmox cluster"
fi

if ssh \
  -i "$PVE_ROOT_SSH_KEY" \
  -o BatchMode=yes \
  "root@$PVE_HOST" \
  "nmap -sn -PR -n -e vmbr0 '$KOMODO_IPV4' 2>/dev/null |
   grep -q 'Host is up'"
then
  die "IP $KOMODO_IPV4 is active on the LAN"
fi

ssh \
  -i "$PVE_ROOT_SSH_KEY" \
  -o BatchMode=yes \
  "root@$PVE_HOST" \
  "pvesm status --storage vm-ssd | grep -q active" ||
  die "vm-ssd is not active"

ssh \
  -i "$PVE_ROOT_SSH_KEY" \
  -o BatchMode=yes \
  "root@$PVE_HOST" \
  "pveam list local |
   awk '{print \$1}' |
   grep -Fxq '$LXC_TEMPLATE'" ||
  die "Required Debian 13 LXC template is unavailable"

HOST_AVAILABLE_KIB="$(
  ssh \
    -i "$PVE_ROOT_SSH_KEY" \
    -o BatchMode=yes \
    "root@$PVE_HOST" \
    "awk '/MemAvailable:/ {print \$2}' /proc/meminfo"
)"

[ "$HOST_AVAILABLE_KIB" -ge 4194304 ] ||
  die "PROXMOX has less than 4 GiB MemAvailable"

printf 'ctid_%s=AVAILABLE\n' "$KOMODO_CT_ID"
printf 'ipv4_%s=NO_ACTIVE_HOST\n' "$KOMODO_IPV4"
printf 'mac_%s=AVAILABLE\n' "$KOMODO_MAC"
printf 'vm_ssd=ACTIVE\n'
printf 'lxc_template=AVAILABLE\n'
printf 'host_mem_available_kib=%s\n' "$HOST_AVAILABLE_KIB"

printf '\n===== PREPARE DURABLE TERRAFORM STATE =====\n'

mkdir -p "$DEPLOY_DIR"

find "$DEPLOY_DIR" \
  -maxdepth 1 \
  -type f \
  \( -name '*.tf' -o -name '.terraform.lock.hcl' \) \
  -delete

cp "$TF_SOURCE_DIR"/*.tf "$DEPLOY_DIR/"

if [ -f "$TF_SOURCE_DIR/.terraform.lock.hcl" ]; then
  cp "$TF_SOURCE_DIR/.terraform.lock.hcl" "$DEPLOY_DIR/"
fi

printf '\n===== TERRAFORM INIT / VALIDATE =====\n'

terraform -chdir="$DEPLOY_DIR" init -input=false
terraform -chdir="$DEPLOY_DIR" validate

printf '\n===== TERRAFORM CREATE PLAN =====\n'

rm -f "$PLAN_FILE" "$PLAN_JSON"

terraform \
  -chdir="$DEPLOY_DIR" \
  plan \
  -input=false \
  -out="$PLAN_FILE"

terraform \
  -chdir="$DEPLOY_DIR" \
  show \
  -json \
  "$PLAN_FILE" >"$PLAN_JSON"

chmod 0600 "$PLAN_FILE" "$PLAN_JSON"

jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
  and $changes[0].address == "proxmox_virtual_environment_container.komodo"
  and $changes[0].change.actions == ["create"]
  and $changes[0].change.after.node_name == "PROXMOX"
  and $changes[0].change.after.vm_id == 104
  and $changes[0].change.after.unprivileged == true
  and $changes[0].change.after.features[0].nesting == true
  and $changes[0].change.after.cpu[0].cores == 2
  and $changes[0].change.after.memory[0].dedicated == 2048
  and $changes[0].change.after.memory[0].swap == 512
  and $changes[0].change.after.disk[0].datastore_id == "vm-ssd"
  and $changes[0].change.after.disk[0].size == 32
  and $changes[0].change.after.initialization[0].hostname == "komodo-01"
  and $changes[0].change.after.initialization[0].ip_config[0].ipv4[0].address
      == "192.168.2.58/24"
  and $changes[0].change.after.initialization[0].ip_config[0].ipv4[0].gateway
      == "192.168.2.1"
  and $changes[0].change.after.network_interface[0].bridge == "vmbr0"
  and $changes[0].change.after.network_interface[0].mac_address
      == "02:00:00:00:01:04"
  and $changes[0].change.after.operating_system[0].template_file_id
      == "local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"
  and $changes[0].change.after.protection == false
' "$PLAN_JSON" >/dev/null ||
  die "Plan differs from the approved komodo-01 LXC specification"

printf '\n===== APPROVED CHANGE SET =====\n'

jq -r '
  .resource_changes[]
  | select(.change.actions != ["no-op"])
  | [.address, (.change.actions | join(","))]
  | @tsv
' "$PLAN_JSON"

printf '\n===== APPROVED KOMODO LXC SPEC =====\n'
printf 'ct_id=104\n'
printf 'unprivileged=true\n'
printf 'nesting=true\n'
printf 'keyctl=root-managed-post-create\n'
printf 'ipv4=192.168.2.58/24\n'
printf 'mac=02:00:00:00:01:04\n'
printf 'cpu_cores=2\n'
printf 'memory_mb=2048\n'
printf 'swap_mb=512\n'
printf 'disk=vm-ssd:32GiB\n'
printf 'protection=false\n'

printf '\n===== PLAN SUMMARY =====\n'

terraform \
  -chdir="$DEPLOY_DIR" \
  show "$PLAN_FILE" |
tail -120

printf '\n===== RESULT =====\n'
printf 'KOMODO-01 LXC TERRAFORM PLAN=PASS\n'
printf 'plan_file=%s\n' "$PLAN_FILE"
printf 'plan_json=%s\n' "$PLAN_JSON"
printf 'terraform_apply=NOT_RUN\n'
printf 'ct104=NOT_CREATED\n'
