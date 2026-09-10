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
TARGET_PVE="PROXMOX"
PVE_HOST="192.168.2.70"

PVE_ENV_FILE="$HOME/.config/homelab-iac/proxmox.env"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
SENSOR_SSH_KEY="$HOME/.ssh/proxmox-automation"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/sensor-01"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
STATE_ROOT="$HOME/.local/state/homelab-iac/sensor-01"
DEPLOY_DIR="$STATE_ROOT/terraform"
RUNNER_TMP="${RUNNER_TEMP:-/var/tmp}"
PLAN_FILE="$RUNNER_TMP/sensor-01-create.tfplan"
PLAN_JSON="$RUNNER_TMP/sensor-01-create.tfplan.json"
POST_PLAN="$RUNNER_TMP/sensor-01-post-create-plan.txt"

for cmd in terraform ansible-playbook jq ssh ssh-keygen; do
  require_cmd "$cmd"
done

[ -r "$PVE_ENV_FILE" ] || die "Missing Proxmox credential file: $PVE_ENV_FILE"
[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"
[ -r "$SENSOR_SSH_KEY" ] || die "Missing sensor SSH key: $SENSOR_SSH_KEY"
[ -r "$SENSOR_SSH_KEY.pub" ] || die "Missing sensor SSH public key: $SENSOR_SSH_KEY.pub"

# shellcheck disable=SC1090
. "$PVE_ENV_FILE"
: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from $PVE_ENV_FILE}"
export TF_VAR_proxmox_api_token

printf '===== SENSOR-01 GUARDED VM BUILD =====\n'
printf 'hostname=%s\n' "$SENSOR_HOSTNAME"
printf 'ipv4=%s\n' "$SENSOR_IPV4"
printf 'vm_id=%s\n' "$SENSOR_VM_ID"
printf 'clone_source_vm_id=%s\n' "$SOURCE_VM_ID"
printf 'pve=%s\n' "$TARGET_PVE"
printf 'terraform_state=%s\n' "$DEPLOY_DIR"

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
[ "$HOST_AVAILABLE_KIB" -ge 3670016 ]   || die "PROXMOX has less than 3.5 GiB MemAvailable; refusing phase-1 sensor build"

SOURCE_CONFIG="$(
  ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_HOST"     "qm config '$SOURCE_VM_ID'"
)" || die "Clone source VM $SOURCE_VM_ID is not readable"

printf '%s\n' "$SOURCE_CONFIG" | grep -Fxq 'template: 1'   || die "Clone source $SOURCE_VM_ID is not a Proxmox template"
printf '%s\n' "$SOURCE_CONFIG" | grep -Fxq 'name: debian-13-cloud-template-qga'   || die "Clone source $SOURCE_VM_ID has the wrong template identity"
printf '%s\n' "$SOURCE_CONFIG" | grep -Eq '^agent: .*enabled=1'   || die "Clone source $SOURCE_VM_ID does not have QEMU Guest Agent enabled"
printf '%s\n' "$SOURCE_CONFIG" | grep -Eq '^scsi0: vm-ssd:base-9001-disk-0,'   || die "Clone source $SOURCE_VM_ID system disk is not the expected vm-ssd base disk"
printf '%s\n' "$SOURCE_CONFIG" | grep -Eq '^ide2: vm-ssd:vm-9001-cloudinit,'   || die "Clone source $SOURCE_VM_ID cloud-init disk is not on vm-ssd"
printf '%s\n' "$SOURCE_CONFIG" | grep -Eq '^net0: .*bridge=vmbr0'   || die "Clone source $SOURCE_VM_ID management NIC is not on vmbr0"

printf 'vmid_%s=AVAILABLE\n' "$SENSOR_VM_ID"
printf 'ipv4_%s=NO_ACTIVE_HOST\n' "$SENSOR_IPV4"
printf 'vm_ssd=ACTIVE\n'
printf 'host_mem_available_kib=%s\n' "$HOST_AVAILABLE_KIB"
printf 'clone_source_%s=VALID\n' "$SOURCE_VM_ID"

printf '\n===== HYPERVISOR PREREQUISITES =====\n'
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

printf '\n===== REGENERATE APPROVED CREATE PLAN =====\n'
rm -f "$PLAN_FILE" "$PLAN_JSON"
terraform -chdir="$DEPLOY_DIR" plan -input=false -out="$PLAN_FILE"
terraform -chdir="$DEPLOY_DIR" show -json "$PLAN_FILE" >"$PLAN_JSON"

jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
  and $changes[0].address == "proxmox_virtual_environment_vm.sensor"
  and $changes[0].change.actions == ["create"]
  and $changes[0].change.after.name == "sensor-01"
  and $changes[0].change.after.node_name == "PROXMOX"
  and $changes[0].change.after.vm_id == 201
  and $changes[0].change.after.clone[0].vm_id == 9001
  and $changes[0].change.after.clone[0].full == true
  and $changes[0].change.after.clone[0].datastore_id == "vm-ssd"
  and $changes[0].change.after.cpu[0].cores == 4
  and $changes[0].change.after.memory[0].dedicated == 3072
  and $changes[0].change.after.disk[0].datastore_id == "vm-ssd"
  and $changes[0].change.after.disk[0].size == 80
  and $changes[0].change.after.initialization[0].ip_config[0].ipv4[0].address == "192.168.2.55/24"
  and $changes[0].change.after.initialization[0].ip_config[0].ipv4[0].gateway == "192.168.2.1"
  and $changes[0].change.after.network_device[0].bridge == "vmbr0"
' "$PLAN_JSON" >/dev/null   || die "Create plan differs from the approved sensor-01 specification"

printf 'approved_change=proxmox_virtual_environment_vm.sensor:create\n'

printf '\n===== TERRAFORM APPLY =====\n'
terraform -chdir="$DEPLOY_DIR" apply -input=false "$PLAN_FILE"

printf '\n===== WAIT FOR SENSOR SSH =====\n'
ssh-keygen -R "$SENSOR_IPV4" >/dev/null 2>&1 || true

READY=0
for attempt in $(seq 1 60); do
  if ssh -i "$SENSOR_SSH_KEY"     -o BatchMode=yes     -o StrictHostKeyChecking=accept-new     -o ConnectTimeout=3     "james@$SENSOR_IPV4" true >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 5
done
[ "$READY" -eq 1 ] || die "sensor-01 SSH did not become ready"

printf '\n===== GUEST IDENTITY / CLOUD-INIT VALIDATION =====\n'
ssh -i "$SENSOR_SSH_KEY" -o BatchMode=yes "james@$SENSOR_IPV4" \
  bash -s -- "$SENSOR_HOSTNAME" "$SENSOR_FQDN" "$SENSOR_IPV4" <<'REMOTE'
set -eu

EXPECTED_HOSTNAME="$1"
EXPECTED_FQDN="$2"
EXPECTED_IPV4="$3"

sudo cloud-init status --wait

echo "hostname=$(hostname -s)"
echo "fqdn=$(hostname -f)"

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

ROOT_SIZE="$(df -B1 --output=size / | tail -1 | tr -d ' ')"
echo "root_filesystem_bytes=$ROOT_SIZE"

FAILED_UNITS="$(sudo systemctl --failed --no-legend --plain)"
printf 'failed_units=%s\n' "$FAILED_UNITS"
test -z "$FAILED_UNITS"
REMOTE

printf '\n===== PROXMOX VM VALIDATION =====\n'
VM_CONFIG="$(
  ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_HOST"     "qm config '$SENSOR_VM_ID'"
)"

printf '%s\n' "$VM_CONFIG"
printf '%s\n' "$VM_CONFIG" | grep -Fxq 'name: sensor-01'
printf '%s\n' "$VM_CONFIG" | grep -Eq '^cores: 4$'
printf '%s\n' "$VM_CONFIG" | grep -Eq '^memory: 3072$'
printf '%s\n' "$VM_CONFIG" | grep -Eq '^net0: .*bridge=vmbr0'
printf '%s\n' "$VM_CONFIG" | grep -Eq '^scsi0: vm-ssd:.*size=80G'
printf '%s\n' "$VM_CONFIG" | grep -Eq '^ipconfig0: ip=192\.168\.2\.55/24,gw=192\.168\.2\.1$'
printf '%s\n' "$VM_CONFIG" | grep -Eq '^cicustom: user=local:snippets/sensor-01-user-data\.yaml$'

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
    die "Terraform post-create plan failed"
    ;;
esac

printf '\n===== RESULT: PASS =====\n'
printf 'sensor_vm_build=PASS\n'
printf 'sensor_vm_id=%s\n' "$SENSOR_VM_ID"
printf 'sensor_ipv4=%s\n' "$SENSOR_IPV4"
printf 'sensor_ssh=PASS\n'
printf 'sensor_qga=PASS\n'
printf 'terraform_drift=NONE\n'
printf 'sensor_toolchain=NOT_INSTALLED\n'
