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
SENSOR_FQDN="sensor-01.jameshouse"
SENSOR_IPV4="192.168.2.55"
SENSOR_VM_ID="201"
SOURCE_VM_ID="9001"
PVE_HOST="192.168.2.70"

PVE_ENV_FILE="$HOME/.config/homelab-iac/proxmox.env"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
SENSOR_SSH_KEY="$HOME/.ssh/proxmox-automation"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/sensor-01"
DEPLOY_DIR="$HOME/.local/state/homelab-iac/sensor-01/terraform"
POST_PLAN="${RUNNER_TEMP:-/var/tmp}/sensor-01-validation-plan.txt"

for cmd in terraform ssh ssh-keygen; do
  require_cmd "$cmd"
done

[ -r "$PVE_ENV_FILE" ] || die "Missing Proxmox credential file: $PVE_ENV_FILE"
[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"
[ -r "$SENSOR_SSH_KEY" ] || die "Missing sensor SSH key: $SENSOR_SSH_KEY"
[ -d "$DEPLOY_DIR" ] || die "Missing durable Terraform directory: $DEPLOY_DIR"
[ -f "$DEPLOY_DIR/terraform.tfstate" ] || die "Missing sensor Terraform state"

# shellcheck disable=SC1090
. "$PVE_ENV_FILE"
: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from $PVE_ENV_FILE}"
export TF_VAR_proxmox_api_token

printf '===== SENSOR-01 POST-CREATE VALIDATION =====\n'

printf '\n===== TERRAFORM OWNERSHIP =====\n'
terraform -chdir="$DEPLOY_DIR" state list   | grep -Fxq 'proxmox_virtual_environment_vm.sensor'   || die "sensor-01 is not owned by the expected Terraform state"
printf 'terraform_state_ownership=PASS\n'

printf '\n===== PROXMOX VM EXISTENCE / CONFIG =====\n'
VM_CONFIG="$(
  ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$PVE_HOST"     "qm config '$SENSOR_VM_ID'"
)" || die "VM $SENSOR_VM_ID is not readable on PROXMOX"

printf '%s\n' "$VM_CONFIG"

printf '%s\n' "$VM_CONFIG" | grep -Fxq 'name: sensor-01'   || die "VM 201 name mismatch"
printf '%s\n' "$VM_CONFIG" | grep -Eq '^cores: 4$'   || die "VM 201 CPU mismatch"
printf '%s\n' "$VM_CONFIG" | grep -Eq '^memory: 3072$'   || die "VM 201 RAM mismatch"
printf '%s\n' "$VM_CONFIG" | grep -Eq '^net0: .*bridge=vmbr0'   || die "VM 201 management bridge mismatch"
printf '%s\n' "$VM_CONFIG" | grep -Eq '^scsi0: vm-ssd:.*size=80G'   || die "VM 201 disk mismatch"
IPCONFIG0="$(printf '%s\n' "$VM_CONFIG" | sed -n 's/^ipconfig0: //p')"
printf '%s\n' "$IPCONFIG0" | grep -Fq 'ip=192.168.2.55/24' \
  || die "VM 201 cloud-init IPv4 address mismatch"
printf '%s\n' "$IPCONFIG0" | grep -Fq 'gw=192.168.2.1' \
  || die "VM 201 cloud-init gateway mismatch"
printf '%s\n' "$VM_CONFIG" | grep -Eq '^cicustom: user=local:snippets/sensor-01-user-data\.yaml$'   || die "VM 201 cloud-init user-data mismatch"

if printf '%s\n' "$VM_CONFIG" | grep -Eq '^usb[0-9]+:'; then
  die "Unexpected USB passthrough is already attached during phase 1"
fi
printf 'proxmox_vm_config=PASS\n'
printf 'usb_capture_device=NOT_ATTACHED\n'

printf '\n===== QEMU GUEST AGENT FROM HYPERVISOR =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_HOST"   "qm agent '$SENSOR_VM_ID' ping" >/dev/null   || die "QEMU Guest Agent does not answer through Proxmox"
printf 'qga_hypervisor_ping=PASS\n'

printf '\n===== WAIT FOR SSH =====\n'
ssh-keygen -R "$SENSOR_IPV4" >/dev/null 2>&1 || true
READY=0
for attempt in $(seq 1 30); do
  if ssh -i "$SENSOR_SSH_KEY"     -o BatchMode=yes     -o StrictHostKeyChecking=accept-new     -o ConnectTimeout=3     "james@$SENSOR_IPV4" true >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 4
done
[ "$READY" -eq 1 ] || die "sensor-01 SSH is not reachable"
printf 'sensor_ssh=PASS\n'

printf '\n===== GUEST VALIDATION =====\n'
ssh -i "$SENSOR_SSH_KEY" -o BatchMode=yes "james@$SENSOR_IPV4"   bash -s -- "$SENSOR_HOSTNAME" "$SENSOR_FQDN" "$SENSOR_IPV4" <<'REMOTE'
set -eu

EXPECTED_HOSTNAME="$1"
EXPECTED_FQDN="$2"
EXPECTED_IPV4="$3"

sudo cloud-init status --wait

echo "hostname=$(hostname -s)"
echo "fqdn=$(hostname -f)"
echo "os=$(source /etc/os-release && printf '%s %s' "$PRETTY_NAME" "$VERSION_ID")"

test "$(hostname -s)" = "$EXPECTED_HOSTNAME"
test "$(hostname -f)" = "$EXPECTED_FQDN"
test -e /var/lib/cloud/sensor-01-bootstrap-complete

ip -4 -o addr show scope global
ip route

ip -4 -o addr show scope global | grep -q "$EXPECTED_IPV4/24"
ip route | grep -q '^default via 192\.168\.2\.1 '

sudo systemctl is-active --quiet qemu-guest-agent

MEM_KIB="$(awk '/MemTotal:/ {print $2}' /proc/meminfo)"
echo "guest_mem_total_kib=$MEM_KIB"
[ "$MEM_KIB" -ge 2800000 ]

echo "--- block devices ---"
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS

ROOT_SIZE="$(df -B1 --output=size / | tail -1 | tr -d ' ')"
echo "root_filesystem_bytes=$ROOT_SIZE"

FAILED_UNITS="$(sudo systemctl --failed --no-legend --plain)"
printf 'failed_units=%s\n' "$FAILED_UNITS"
test -z "$FAILED_UNITS"

test ! -e /var/log/suricata/eve.json
! command -v zeek >/dev/null 2>&1
REMOTE

printf 'guest_identity_network_qga=PASS\n'
printf 'sensor_toolchain=NOT_INSTALLED\n'

printf '\n===== SYNC CURRENT TERRAFORM SOURCE =====\n'
find "$DEPLOY_DIR" -maxdepth 1 -type f \( -name '*.tf' -o -name '.terraform.lock.hcl' \) -delete
cp "$TF_SOURCE_DIR"/*.tf "$DEPLOY_DIR/"
if [ -f "$TF_SOURCE_DIR/.terraform.lock.hcl" ]; then
  cp "$TF_SOURCE_DIR/.terraform.lock.hcl" "$DEPLOY_DIR/"
fi
terraform -chdir="$DEPLOY_DIR" init -input=false >/dev/null
terraform -chdir="$DEPLOY_DIR" validate

printf '\n===== TERRAFORM DRIFT CHECK =====\n'
set +e
terraform -chdir="$DEPLOY_DIR" plan -input=false -detailed-exitcode >"$POST_PLAN"
RC=$?
set -e

case "$RC" in
  0)
    printf 'terraform_drift=NONE\n'
    ;;
  2)
    cat "$POST_PLAN"
    die "Terraform reports post-create drift"
    ;;
  *)
    cat "$POST_PLAN"
    die "Terraform validation plan failed"
    ;;
esac

printf '\n===== RESULT: PASS =====\n'
printf 'sensor_vm_validation=PASS\n'
printf 'sensor_vm_id=%s\n' "$SENSOR_VM_ID"
printf 'sensor_ipv4=%s\n' "$SENSOR_IPV4"
printf 'sensor_ssh=PASS\n'
printf 'sensor_qga=PASS\n'
printf 'terraform_drift=NONE\n'
printf 'sensor_toolchain=NOT_INSTALLED\n'
