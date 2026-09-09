#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

CLOUD_HOSTNAME="${CLOUD_HOSTNAME:-cloud-01}"
CLOUD_IPV4="${CLOUD_IPV4:-192.168.2.53}"
CLOUD_VM_ID="${CLOUD_VM_ID:-200}"
SOURCE_TEMPLATE_VM_ID="${SOURCE_TEMPLATE_VM_ID:-9001}"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
CONFIG_DIR="$HOME/.config/homelab-iac"
PVE_ENV_FILE="$CONFIG_DIR/proxmox.env"
VM_SSH_KEY="$HOME/.ssh/proxmox-automation"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/cloud-01"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
STATE_DIR="$HOME/.local/state/homelab-iac/cloud-01/terraform"
WORK_DIR="${RUNNER_TEMP:-/var/tmp}/cloud-01-${CLOUD_VM_ID}"
PLAN_FILE="$WORK_DIR/create.tfplan"

PVE_ENDPOINT="https://192.168.2.70:8006/"
PVE_NODE_NAME="PROXMOX"
PVE_SSH_HOST="192.168.2.70"

for cmd in terraform ansible-playbook jq ssh ssh-keygen ping dig grep awk; do
  require_cmd "$cmd"
done

[ -r "$PVE_ENV_FILE" ] || die "Missing Proxmox credential file: $PVE_ENV_FILE"
[ -r "$VM_SSH_KEY" ] || die "Missing cloud VM SSH key: $VM_SSH_KEY"
[ -r "$VM_SSH_KEY.pub" ] || die "Missing cloud VM SSH public key: $VM_SSH_KEY.pub"
[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"

# shellcheck disable=SC1090
. "$PVE_ENV_FILE"
: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from Proxmox credential file}"
export TF_VAR_proxmox_api_token

printf '===== CLOUD-01 VM DEPLOYMENT =====\n'
printf 'hostname=%s\n' "$CLOUD_HOSTNAME"
printf 'ipv4=%s\n' "$CLOUD_IPV4"
printf 'vm_id=%s\n' "$CLOUD_VM_ID"
printf 'source_template=%s\n' "$SOURCE_TEMPLATE_VM_ID"
printf 'pve=%s\n' "$PVE_NODE_NAME"
printf 'state_dir=%s\n' "$STATE_DIR"

printf '\n===== SAFETY PREFLIGHT =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$PVE_SSH_HOST" true \
  || die "Root SSH to PROXMOX failed"

ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST" "
set -u
test \"\$(hostname -s)\" = '$PVE_NODE_NAME' || exit 21
qm config '$SOURCE_TEMPLATE_VM_ID' | grep -qx 'template: 1' || exit 22
qm config '$SOURCE_TEMPLATE_VM_ID' | grep -q '^agent: enabled=1' || exit 23
qm config '$SOURCE_TEMPLATE_VM_ID' | grep -q '^scsi0: vm-ssd:base-9001-disk-0' || exit 24
if qm config '$CLOUD_VM_ID' >/dev/null 2>&1 || pct config '$CLOUD_VM_ID' >/dev/null 2>&1; then
  echo 'VMID $CLOUD_VM_ID already exists'
  exit 25
fi
echo 'template_gate=PASS'
echo 'vmid_gate=PASS'
echo '4tb_test_status:'
ps -eo pid,etime,cmd | grep '[b]adblocks.*WD40EZRX' || echo 'badblocks not currently running; data disk remains out of scope'
" || die "PROXMOX/template safety gate failed"

if ping -c 2 -W 1 "$CLOUD_IPV4" >/dev/null 2>&1; then
  die "IP $CLOUD_IPV4 responds before cloud-01 creation"
fi

[ ! -e "$STATE_DIR/terraform.tfstate" ] || die "cloud-01 Terraform state already exists"

printf '\n===== PREPARE DURABLE TERRAFORM STATE =====\n'
mkdir -p "$STATE_DIR" "$WORK_DIR"
find "$STATE_DIR" -maxdepth 1 -type f \( -name '*.tf' -o -name '.terraform.lock.hcl' \) -delete
cp "$TF_SOURCE_DIR"/*.tf "$STATE_DIR/"
cp "$TF_SOURCE_DIR/.terraform.lock.hcl" "$STATE_DIR/"

export TF_VAR_proxmox_endpoint="$PVE_ENDPOINT"
export TF_VAR_proxmox_node_name="$PVE_NODE_NAME"
export TF_VAR_template_vm_id="$SOURCE_TEMPLATE_VM_ID"
export TF_VAR_vm_id="$CLOUD_VM_ID"
export TF_VAR_hostname="$CLOUD_HOSTNAME"
export TF_VAR_ipv4_cidr="$CLOUD_IPV4/24"
export TF_VAR_vm_datastore_id="vm-ssd"
export TF_VAR_protect_after_build=false
export TF_VAR_ssh_public_key
TF_VAR_ssh_public_key="$(tr -d '\r\n' < "$VM_SSH_KEY.pub")"

printf '\n===== TERRAFORM INIT / VALIDATE =====\n'
terraform -chdir="$STATE_DIR" init -input=false || die "Terraform init failed"
terraform -chdir="$STATE_DIR" validate || die "Terraform validation failed"

printf '\n===== TERRAFORM CREATE PLAN =====\n'
rm -f "$PLAN_FILE"
terraform -chdir="$STATE_DIR" plan -input=false -out="$PLAN_FILE" || die "Terraform plan failed"

terraform -chdir="$STATE_DIR" show -json "$PLAN_FILE" | jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
    and $changes[0].address == "proxmox_virtual_environment_vm.cloud"
    and $changes[0].change.actions == ["create"]
' >/dev/null || die "Plan contains an unapproved resource or action"

printf '\n===== APPROVED PLAN SUMMARY =====\n'
terraform -chdir="$STATE_DIR" show "$PLAN_FILE" | tail -80

printf '\n===== TERRAFORM APPLY =====\n'
terraform -chdir="$STATE_DIR" apply -input=false "$PLAN_FILE" \
  || die "Terraform apply failed"

printf '\n===== WAIT FOR CLOUD-01 SSH =====\n'
ssh-keygen -R "$CLOUD_IPV4" >/dev/null 2>&1 || true

READY=0
for attempt in $(seq 1 60); do
  if ssh -i "$VM_SSH_KEY" \
      -o BatchMode=yes \
      -o StrictHostKeyChecking=accept-new \
      -o ConnectTimeout=3 \
      "james@$CLOUD_IPV4" true >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 5
done
[ "$READY" -eq 1 ] || die "cloud-01 SSH did not become ready"

printf '\n===== CLOUD-INIT / IDENTITY VALIDATION =====\n'
ssh -i "$VM_SSH_KEY" -o BatchMode=yes "james@$CLOUD_IPV4" "
cloud-init status --wait
test \"\$(hostname -s)\" = '$CLOUD_HOSTNAME'
ip -4 -br addr
ip route
getent hosts deb.debian.org >/dev/null
sudo systemctl is-active qemu-guest-agent
FAILED_UNITS=\"\$(sudo systemctl --failed --no-legend --plain)\"
printf '%s\n' \"\$FAILED_UNITS\"
test -z \"\$FAILED_UNITS\"
" || die "cloud-init/identity validation failed"

printf '\n===== ANSIBLE CLOUD BASELINE =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook playbooks/cloud-01.yml \
  || die "cloud-01 Ansible baseline failed"

printf '\n===== PUBLISH CLOUD-01 LOCAL DNS =====\n'
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook playbooks/dns-local-records.yml \
  || die "cloud-01 DNS publication failed"

printf '\n===== VERIFY DUAL DNS =====\n'
for resolver in 192.168.2.51 192.168.2.50; do
  answer="$(dig @"$resolver" "$CLOUD_HOSTNAME.jameshouse" A +short | tail -1)"
  printf 'resolver=%s answer=%s\n' "$resolver" "$answer"
  [ "$answer" = "$CLOUD_IPV4" ] || die "$resolver did not return $CLOUD_IPV4"
done

printf '\n===== TERRAFORM DRIFT CHECK =====\n'
DRIFT_FILE="$WORK_DIR/post-create-plan.txt"
terraform -chdir="$STATE_DIR" plan -input=false -detailed-exitcode >"$DRIFT_FILE"
RC=$?
case "$RC" in
  0)
    printf 'terraform_drift=NONE\n'
    ;;
  2)
    cat "$DRIFT_FILE"
    die "Terraform reports post-create drift"
    ;;
  *)
    cat "$DRIFT_FILE"
    die "Terraform post-create plan failed"
    ;;
esac

printf '\n===== RESULT: BASE BUILD PASS =====\n'
printf '%s (%s), VM %s on %s, is provisioned and configured.\n' \
  "$CLOUD_HOSTNAME" "$CLOUD_IPV4" "$CLOUD_VM_ID" "$PVE_NODE_NAME"
printf 'NTP client: 192.168.2.70 preferred, 192.168.2.71 secondary.\n'
printf 'The 4 TB USB data disk was not attached, formatted, mounted or modified by this deployment.\n'
printf 'Nextcloud/PostgreSQL/Redis and final VM protection remain later gates.\n'

unset TF_VAR_proxmox_api_token TF_VAR_ssh_public_key
