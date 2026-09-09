#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

MONITOR_HOSTNAME="monitor-01"
MONITOR_IPV4="192.168.2.52"
MONITOR_VM_ID="200"
TARGET_PVE="Proxmox-2"
PVE_HOST="192.168.2.71"
PVE_ENV_FILE="$HOME/.config/homelab-iac/proxmox-pve2.env"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
MONITOR_SSH_KEY="$HOME/.ssh/proxmox-automation"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/monitor-01"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
STATE_ROOT="$HOME/.local/state/homelab-iac/monitor-01"
DEPLOY_DIR="$STATE_ROOT/terraform"
RUNNER_TMP="${RUNNER_TEMP:-/var/tmp}"
PLAN_FILE="$RUNNER_TMP/monitor-01-create.tfplan"

require_cmd terraform
require_cmd ansible-playbook
require_cmd jq
require_cmd ssh
require_cmd ssh-keygen
require_cmd ping
require_cmd curl

[ -r "$PVE_ENV_FILE" ] || die "Missing Proxmox credential file: $PVE_ENV_FILE"
[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"
[ -r "$MONITOR_SSH_KEY" ] || die "Missing monitoring SSH key: $MONITOR_SSH_KEY"
[ -r "$MONITOR_SSH_KEY.pub" ] || die "Missing monitoring SSH public key: $MONITOR_SSH_KEY.pub"

# shellcheck disable=SC1090
. "$PVE_ENV_FILE"
: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from Proxmox credential file}"
export TF_VAR_proxmox_api_token

printf '===== MONITOR-01 DEPLOYMENT =====\n'
printf 'hostname=%s\n' "$MONITOR_HOSTNAME"
printf 'ipv4=%s\n' "$MONITOR_IPV4"
printf 'vm_id=%s\n' "$MONITOR_VM_ID"
printf 'pve=%s\n' "$TARGET_PVE"
printf 'state_dir=%s\n' "$DEPLOY_DIR"

printf '\n===== HYPERVISOR PREREQUISITES =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" ansible-playbook playbooks/proxmox-monitoring-prereqs.yml

printf '\n===== SAFETY PREFLIGHT =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$PVE_HOST" true \
  || die "Root SSH to $TARGET_PVE failed"

if [ ! -f "$DEPLOY_DIR/terraform.tfstate" ]; then
  if ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_HOST" \
    "qm config '$MONITOR_VM_ID' >/dev/null 2>&1 || pct config '$MONITOR_VM_ID' >/dev/null 2>&1"; then
    die "Guest ID $MONITOR_VM_ID already exists but no Terraform state is present"
  fi

  if ping -c 2 -W 1 "$MONITOR_IPV4" >/dev/null 2>&1; then
    die "IP $MONITOR_IPV4 responds but no Terraform state is present"
  fi
fi

printf '\n===== PREPARE DURABLE TERRAFORM STATE DIRECTORY =====\n'
mkdir -p "$DEPLOY_DIR"
find "$DEPLOY_DIR" -maxdepth 1 -type f \( -name '*.tf' -o -name '.terraform.lock.hcl' \) -delete
cp "$TF_SOURCE_DIR"/*.tf "$DEPLOY_DIR/"
cp "$TF_SOURCE_DIR/.terraform.lock.hcl" "$DEPLOY_DIR/"

printf '\n===== TERRAFORM INIT / VALIDATE =====\n'
terraform -chdir="$DEPLOY_DIR" init -input=false
terraform -chdir="$DEPLOY_DIR" validate

printf '\n===== TERRAFORM CREATE PLAN =====\n'
rm -f "$PLAN_FILE"
terraform -chdir="$DEPLOY_DIR" plan -input=false -out="$PLAN_FILE"

if [ ! -f "$DEPLOY_DIR/terraform.tfstate" ]; then
  terraform -chdir="$DEPLOY_DIR" show -json "$PLAN_FILE" | jq -e '
    [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
    | ($changes | length) == 3
      and ([ $changes[].address ] | sort) == ([
        "proxmox_download_file.debian_cloud_image",
        "proxmox_virtual_environment_file.cloud_init_user_data",
        "proxmox_virtual_environment_vm.monitor"
      ] | sort)
      and ([ $changes[].change.actions ] | all(. == ["create"]))
  ' >/dev/null || die "Initial create plan contains changes outside the three approved resources"
fi

printf '\n===== APPROVED PLAN SUMMARY =====\n'
terraform -chdir="$DEPLOY_DIR" show "$PLAN_FILE" | tail -40

printf '\n===== TERRAFORM APPLY =====\n'
if ! terraform -chdir="$DEPLOY_DIR" apply -input=false "$PLAN_FILE"; then
  die "Terraform apply failed; SSH wait was not started"
fi

printf '\n===== WAIT FOR SSH =====\n'
ssh-keygen -R "$MONITOR_IPV4" >/dev/null 2>&1 || true
READY=0
for attempt in $(seq 1 60); do
  if ssh -i "$MONITOR_SSH_KEY"     -o BatchMode=yes     -o StrictHostKeyChecking=accept-new     -o ConnectTimeout=3     "james@$MONITOR_IPV4" true >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 5
done
[ "$READY" -eq 1 ] || die "monitor-01 SSH did not become ready"

printf '\n===== CLOUD-INIT / IDENTITY VALIDATION =====\n'
ssh -i "$MONITOR_SSH_KEY" -o BatchMode=yes "james@$MONITOR_IPV4" '
hostname
hostname -f
test "$(hostname -s)" = "monitor-01"
test "$(hostname -f)" = "monitor-01.jameshouse"
test -e /var/lib/cloud/monitor-01-bootstrap-complete
ip -br addr
ip route
cat /etc/resolv.conf
sudo systemctl is-active qemu-guest-agent || exit 13
FAILED_UNITS="$(sudo systemctl --failed --no-legend --plain)"
printf "%s\n" "$FAILED_UNITS"
test -z "$FAILED_UNITS" || exit 14
'

printf '\n===== TERRAFORM DRIFT CHECK =====\n'
terraform -chdir="$DEPLOY_DIR" plan -input=false -detailed-exitcode >/tmp/monitor-01-post-create-plan.txt
RC=$?
case "$RC" in
  0)
    printf 'terraform_drift=NONE\n'
    ;;
  2)
    cat /tmp/monitor-01-post-create-plan.txt
    die "Terraform reports post-create drift"
    ;;
  *)
    cat /tmp/monitor-01-post-create-plan.txt
    die "Terraform post-create plan failed"
    ;;
esac

printf '\n===== RESULT: PASS =====\n'
printf '%s (%s) is provisioned from durable Terraform state at %s.\n' \
  "$MONITOR_HOSTNAME" "$MONITOR_IPV4" "$DEPLOY_DIR"
printf 'Monitoring applications have not yet been installed by this phase.\n'
