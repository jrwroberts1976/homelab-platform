#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

HOSTNAME_INPUT="${DNS_HOSTNAME:-}"
IPV4_INPUT="${DNS_IPV4:-}"
TARGET_PVE="${DNS_PVE:-}"
CT_ID="${DNS_CT_ID:-}"

[ -n "$HOSTNAME_INPUT" ] || die "DNS_HOSTNAME is required"
[ -n "$IPV4_INPUT" ] || die "DNS_IPV4 is required"
[ -n "$TARGET_PVE" ] || die "DNS_PVE is required"
[ -n "$CT_ID" ] || die "DNS_CT_ID is required"

printf '%s' "$HOSTNAME_INPUT" | grep -Eq '^[a-z0-9][a-z0-9-]{0,62}$' || die "Invalid hostname"
printf '%s' "$IPV4_INPUT" | grep -Eq '^192\.168\.2\.[0-9]{1,3}$' || die "IPv4 must be in 192.168.2.0/24"
LAST_OCTET="${IPV4_INPUT##*.}"
[ "$LAST_OCTET" -ge 2 ] 2>/dev/null && [ "$LAST_OCTET" -le 254 ] || die "Invalid host address"
printf '%s' "$CT_ID" | grep -Eq '^[0-9]+$' || die "CT ID must be numeric"
[ "$CT_ID" -ge 100 ] || die "CT ID must be >= 100"

require_cmd terraform
require_cmd ansible-playbook
require_cmd jq
require_cmd ssh
require_cmd dig
require_cmd ping

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
RUNNER_TMP="${RUNNER_TEMP:-/tmp}"
CONFIG_DIR="$HOME/.config/homelab-iac"
CT_SSH_KEY="$HOME/.ssh/proxmox-automation"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/dns-resolver"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
STATE_ROOT="$HOME/.local/state/homelab-iac/dns-resolver"
DEPLOY_DIR="$STATE_ROOT/$HOSTNAME_INPUT"
WORK_DIR="$RUNNER_TMP/dns-resolver-$HOSTNAME_INPUT-$CT_ID"

case "$TARGET_PVE" in
  PROXMOX)
    PVE_ENDPOINT="https://192.168.2.70:8006/"
    PVE_SSH_HOST="192.168.2.70"
    PVE_ENV_FILE="$CONFIG_DIR/proxmox.env"
    DEFAULT_ROOTFS_DATASTORE="vm-ssd"
    ;;
  pve2)
    PVE_ENDPOINT="https://192.168.2.71:8006/"
    PVE_SSH_HOST="192.168.2.71"
    PVE_ENV_FILE="$CONFIG_DIR/proxmox-pve2.env"
    DEFAULT_ROOTFS_DATASTORE="local-lvm"
    ;;
  *)
    die "Unsupported PVE target: $TARGET_PVE"
    ;;
esac

PIHOLE_ENV_FILE="$CONFIG_DIR/pihole.env"
DEFAULT_TEMPLATE_FILE_ID="local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"

[ -r "$PVE_ENV_FILE" ] || die "Missing PVE credential file: $PVE_ENV_FILE"
[ -r "$PIHOLE_ENV_FILE" ] || die "Missing Pi-hole secret file: $PIHOLE_ENV_FILE"
[ -r "$CT_SSH_KEY" ] || die "Missing CT SSH key: $CT_SSH_KEY"
[ -r "$CT_SSH_KEY.pub" ] || die "Missing CT SSH public key: $CT_SSH_KEY.pub"
[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing PVE root SSH key: $PVE_ROOT_SSH_KEY"

# shellcheck disable=SC1090
. "$PVE_ENV_FILE"
# shellcheck disable=SC1090
. "$PIHOLE_ENV_FILE"

: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from PVE credential file}"
: "${PIHOLE_WEB_PASSWORD:?PIHOLE_WEB_PASSWORD missing from Pi-hole secret file}"
[ "${#PIHOLE_WEB_PASSWORD}" -ge 16 ] || die "Pi-hole web password must be at least 16 characters"

# Values loaded from the protected local env files must be exported for
# Terraform and Ansible child processes. Sourcing a plain VAR=value file only
# creates shell variables; child processes cannot see them until exported.
export TF_VAR_proxmox_api_token
export PIHOLE_WEB_PASSWORD

PVE_ROOTFS_DATASTORE="${PVE_ROOTFS_DATASTORE:-$DEFAULT_ROOTFS_DATASTORE}"
PVE_TEMPLATE_FILE_ID="${PVE_TEMPLATE_FILE_ID:-$DEFAULT_TEMPLATE_FILE_ID}"

printf '===== ONE-CLICK DNS RESOLVER BUILD =====\n'
printf 'hostname=%s\n' "$HOSTNAME_INPUT"
printf 'ipv4=%s\n' "$IPV4_INPUT"
printf 'pve=%s\n' "$TARGET_PVE"
printf 'ct_id=%s\n' "$CT_ID"
printf 'rootfs=%s\n' "$PVE_ROOTFS_DATASTORE"
printf 'template=%s\n' "$PVE_TEMPLATE_FILE_ID"

printf '\n===== SAFETY PREFLIGHT =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$PVE_SSH_HOST" true \
  || die "Root key-based SSH to $TARGET_PVE is not ready"

if ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST" "pct config '$CT_ID' >/dev/null 2>&1"; then
  die "CT ID $CT_ID already exists on $TARGET_PVE"
fi

if ping -c 1 -W 1 "$IPV4_INPUT" >/dev/null 2>&1; then
  die "IP $IPV4_INPUT already answers ICMP"
fi

ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST" \
  "pvesm status --storage '$PVE_ROOTFS_DATASTORE' >/dev/null && pvesm path '$PVE_TEMPLATE_FILE_ID' >/dev/null" \
  || die "Required storage/template is not ready on $TARGET_PVE"

[ ! -e "$DEPLOY_DIR/terraform.tfstate" ] || die "Terraform state already exists for $HOSTNAME_INPUT"
mkdir -p "$DEPLOY_DIR" "$WORK_DIR"
cp "$TF_SOURCE_DIR"/*.tf "$DEPLOY_DIR/"

CREATE_PLAN="$WORK_DIR/create.tfplan"
PROTECT_PLAN="$WORK_DIR/protect.tfplan"
INVENTORY_FILE="$WORK_DIR/inventory.yml"

export TF_VAR_proxmox_endpoint="$PVE_ENDPOINT"
export TF_VAR_proxmox_node_name="$TARGET_PVE"
export TF_VAR_vm_id="$CT_ID"
export TF_VAR_hostname="$HOSTNAME_INPUT"
export TF_VAR_ipv4_cidr="$IPV4_INPUT/24"
export TF_VAR_rootfs_datastore_id="$PVE_ROOTFS_DATASTORE"
export TF_VAR_template_file_id="$PVE_TEMPLATE_FILE_ID"
export TF_VAR_protect_after_build=false
export TF_VAR_ssh_public_keys
TF_VAR_ssh_public_keys="$(jq -n --arg key "$(cat "$CT_SSH_KEY.pub")" '[$key]')"

printf '\n===== TERRAFORM CREATE PLAN =====\n'
terraform -chdir="$DEPLOY_DIR" init -input=false
terraform -chdir="$DEPLOY_DIR" validate
terraform -chdir="$DEPLOY_DIR" plan -input=false -out="$CREATE_PLAN"

terraform -chdir="$DEPLOY_DIR" show -json "$CREATE_PLAN" | jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
    and $changes[0].address == "proxmox_virtual_environment_container.resolver"
    and $changes[0].change.actions == ["create"]
' >/dev/null || die "Create plan contains changes outside the single expected resolver creation"

printf '\n===== TERRAFORM CREATE APPLY =====\n'
terraform -chdir="$DEPLOY_DIR" apply -input=false "$CREATE_PLAN"

printf '\n===== REQUIRED LXC NESTING BOOTSTRAP =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST" \
  "pct set '$CT_ID' -features nesting=1 && (pct shutdown '$CT_ID' --timeout 30 || pct stop '$CT_ID') && pct start '$CT_ID'"

printf '\n===== WAIT FOR SSH =====\n'
ssh-keygen -R "$IPV4_INPUT" >/dev/null 2>&1 || true
READY=0
for attempt in $(seq 1 30); do
  if ssh -i "$CT_SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=3 "root@$IPV4_INPUT" true >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 4
done
[ "$READY" -eq 1 ] || die "Resolver SSH did not become ready"

cat > "$INVENTORY_FILE" <<EOF
---
all:
  children:
    dns_resolvers:
      hosts:
        $HOSTNAME_INPUT:
          ansible_host: $IPV4_INPUT
          ansible_user: root
          ansible_ssh_private_key_file: $CT_SSH_KEY
          dns_resolver_expected_ipv4: $IPV4_INPUT
          dns_resolver_hostname: $HOSTNAME_INPUT
EOF

printf '\n===== ANSIBLE CONFIGURATION =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" ansible-playbook -i "$INVENTORY_FILE" playbooks/dns-resolver.yml

printf '\n===== EXTERNAL VALIDATION =====\n'
dig "@$IPV4_INPUT" example.com A +short | grep -q .
dig "@$IPV4_INPUT" "$HOSTNAME_INPUT.jameshouse" A +short | grep -Fxq "$IPV4_INPUT"
dig "@$IPV4_INPUT" fail01.dnssec.works A +time=5 +tries=2 | grep -q 'status: SERVFAIL'

BLOCKED_DOMAIN="$(ssh -i "$CT_SSH_KEY" -o BatchMode=yes "root@$IPV4_INPUT" \
  "sqlite3 /etc/pihole/gravity.db 'SELECT domain FROM gravity LIMIT 1;'")"
[ -n "$BLOCKED_DOMAIN" ] || die "Could not select a gravity domain for blocking validation"
dig "@$IPV4_INPUT" "$BLOCKED_DOMAIN" A +short | grep -Fxq '0.0.0.0'

printf '\n===== ENABLE PROTECTION =====\n'
export TF_VAR_protect_after_build=true
terraform -chdir="$DEPLOY_DIR" plan -input=false -out="$PROTECT_PLAN"

terraform -chdir="$DEPLOY_DIR" show -json "$PROTECT_PLAN" | jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
    and $changes[0].address == "proxmox_virtual_environment_container.resolver"
    and $changes[0].change.actions == ["update"]
' >/dev/null || die "Protection plan contains changes outside the single expected resolver update"

terraform -chdir="$DEPLOY_DIR" apply -input=false "$PROTECT_PLAN"

printf '\n===== RESULT: PASS =====\n'
printf '%s (%s) is built, configured, validated and protected on %s as CT %s.\n' \
  "$HOSTNAME_INPUT" "$IPV4_INPUT" "$TARGET_PVE" "$CT_ID"
printf 'ASUS DHCP/DNS advertisement was not changed automatically.\n'
