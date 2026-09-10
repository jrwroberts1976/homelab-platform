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
SOURCE_VM_ID="9001"
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

for cmd in terraform ansible-playbook jq ssh; do
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
printf 'clone_source_vm_id=%s\n' "$SOURCE_VM_ID"
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
[ "$HOST_AVAILABLE_KIB" -ge 3670016 ]   || die "PROXMOX has less than 3.5 GiB MemAvailable; refusing phase-1 sensor planning"

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
printf 'This Ansible phase may only reconcile the managed sensor cloud-init snippet.\n'
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
' "$PLAN_JSON" >/dev/null   || die "Plan differs from the approved sensor-01 clone specification"

printf '\n===== APPROVED CHANGE SET =====\n'
jq -r '
  .resource_changes[]
  | select(.change.actions != ["no-op"])
  | [.address, (.change.actions | join(","))]
  | @tsv
' "$PLAN_JSON"

printf '\n===== APPROVED SENSOR SPEC =====\n'
printf 'source_template=9001\n'
printf 'full_clone=true\n'
printf 'sensor_vm_id=201\n'
printf 'sensor_ipv4=192.168.2.55/24\n'
printf 'cpu_cores=4\n'
printf 'memory_mb=3072\n'
printf 'disk=vm-ssd:80GiB\n'
printf 'management_bridge=vmbr0\n'

printf '\n===== PLAN SUMMARY =====\n'
terraform -chdir="$DEPLOY_DIR" show "$PLAN_FILE" | tail -80

printf '\n===== RESULT =====\n'
printf 'SENSOR-01 TERRAFORM PLAN=PASS\n'
printf 'plan_file=%s\n' "$PLAN_FILE"
printf 'plan_json=%s\n' "$PLAN_JSON"
printf 'terraform_apply=NOT_RUN\n'
