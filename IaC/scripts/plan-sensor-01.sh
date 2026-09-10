#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

SENSOR_HOSTNAME="sensor-01"
SENSOR_IPV4="192.168.2.55"
SENSOR_VM_ID="201"
TARGET_PVE="PROXMOX"
PVE_HOST="192.168.2.70"
PVE_ENV_FILE="$HOME/.config/homelab-iac/proxmox.env"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/sensor-01"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
STATE_ROOT="$HOME/.local/state/homelab-iac/sensor-01"
DEPLOY_DIR="$STATE_ROOT/terraform"
RUNNER_TMP="${RUNNER_TEMP:-/var/tmp}"
PLAN_FILE="$RUNNER_TMP/sensor-01-create.tfplan"
PLAN_JSON="$RUNNER_TMP/sensor-01-create.tfplan.json"

for cmd in terraform ansible-playbook jq ssh ping; do
  require_cmd "$cmd"
done

[ -r "$PVE_ENV_FILE" ] || die "Missing Proxmox credential file: $PVE_ENV_FILE"
[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"

# shellcheck disable=SC1090
. "$PVE_ENV_FILE"
: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from $PVE_ENV_FILE}"
export TF_VAR_proxmox_api_token

printf '===== SENSOR-01 PLAN-ONLY WORKFLOW =====\n'
printf 'hostname=%s\n' "$SENSOR_HOSTNAME"
printf 'ipv4=%s\n' "$SENSOR_IPV4"
printf 'vm_id=%s\n' "$SENSOR_VM_ID"
printf 'pve=%s\n' "$TARGET_PVE"
printf 'terraform_state=%s\n' "$DEPLOY_DIR"
printf 'NOTE: this workflow does not apply the Terraform VM plan.\n'

printf '\n===== LIVE SAFETY PREFLIGHT =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$PVE_HOST"   'test "$(hostname)" = "PROXMOX" && systemctl is-active --quiet pve-cluster && mountpoint -q /etc/pve'   || die "PROXMOX identity/health gate failed"

if ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_HOST"   "qm config '$SENSOR_VM_ID' >/dev/null 2>&1 || pct config '$SENSOR_VM_ID' >/dev/null 2>&1"; then
  die "Guest ID $SENSOR_VM_ID already exists on $TARGET_PVE"
fi

if ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_HOST"   "nmap -sn -PR -n -e vmbr0 '$SENSOR_IPV4' 2>/dev/null | grep -q 'Host is up'"; then
  die "IP $SENSOR_IPV4 is active on the LAN"
fi

ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_HOST"   "pvesm status --storage vm-ssd | grep -q active"   || die "vm-ssd is not active on $TARGET_PVE"

HOST_AVAILABLE_KIB="$(
  ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_HOST"     "awk '/MemAvailable:/ {print \$2}' /proc/meminfo"
)"
[ "$HOST_AVAILABLE_KIB" -ge 3670016 ]   || die "PROXMOX has less than 3.5 GiB MemAvailable; refusing even phase-1 sensor planning"

printf 'vmid_%s=AVAILABLE\n' "$SENSOR_VM_ID"
printf 'ipv4_%s=NO_ACTIVE_HOST\n' "$SENSOR_IPV4"
printf 'vm_ssd=ACTIVE\n'
printf 'host_mem_available_kib=%s\n' "$HOST_AVAILABLE_KIB"

printf '\n===== HYPERVISOR PREREQUISITES =====\n'
printf 'This Ansible phase may only reconcile local import capability and the managed sensor cloud-init snippet.\n'
cd "$ANSIBLE_DIR"
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles"   ansible-playbook playbooks/proxmox-sensor-prereqs.yml

printf '\n===== PREPARE DURABLE TERRAFORM WORKING STATE =====\n'
mkdir -p "$DEPLOY_DIR"
find "$DEPLOY_DIR" -maxdepth 1 -type f \( -name '*.tf' -o -name '.terraform.lock.hcl' \) -delete
cp "$TF_SOURCE_DIR"/*.tf "$DEPLOY_DIR/"
if [ -f "$TF_SOURCE_DIR/.terraform.lock.hcl" ]; then
  cp "$TF_SOURCE_DIR/.terraform.lock.hcl" "$DEPLOY_DIR/"
fi

printf '\n===== TERRAFORM INIT / VALIDATE =====\n'
terraform -chdir="$DEPLOY_DIR" init -input=false
terraform -chdir="$DEPLOY_DIR" validate

printf '\n===== TERRAFORM CREATE PLAN =====\n'
rm -f "$PLAN_FILE" "$PLAN_JSON"
terraform -chdir="$DEPLOY_DIR" plan -input=false -out="$PLAN_FILE"
terraform -chdir="$DEPLOY_DIR" show -json "$PLAN_FILE" >"$PLAN_JSON"

jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) >= 1
  and ($changes | length) <= 2
  and any(
        $changes[];
        .address == "proxmox_virtual_environment_vm.sensor"
        and .change.actions == ["create"]
      )
  and all(
        $changes[];
        (
          .address == "proxmox_virtual_environment_vm.sensor"
          or .address == "proxmox_download_file.debian_cloud_image"
        )
        and .change.actions == ["create"]
      )
' "$PLAN_JSON" >/dev/null   || die "Plan contains an action outside the approved sensor VM/image creates"

printf '\n===== APPROVED CHANGE SET =====\n'
jq -r '
  .resource_changes[]
  | select(.change.actions != ["no-op"])
  | [.address, (.change.actions | join(","))]
  | @tsv
' "$PLAN_JSON"

printf '\n===== PLAN SUMMARY =====\n'
terraform -chdir="$DEPLOY_DIR" show "$PLAN_FILE" | tail -60

printf '\n===== RESULT =====\n'
printf 'SENSOR-01 TERRAFORM PLAN=PASS\n'
printf 'plan_file=%s\n' "$PLAN_FILE"
printf 'plan_json=%s\n' "$PLAN_JSON"
printf 'terraform_apply=NOT_RUN\n'
