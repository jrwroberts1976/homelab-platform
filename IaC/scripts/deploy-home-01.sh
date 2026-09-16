#!/usr/bin/env bash

set -euo pipefail

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

HOME_HOSTNAME="home-01"
HOME_IPV4="192.168.2.60"
HOME_VM_ID="204"
HOME_MAC="02:00:00:00:02:04"
HAOS_VERSION="18.2"
HAOS_URL="https://github.com/home-assistant/operating-system/releases/download/${HAOS_VERSION}/haos_ova-${HAOS_VERSION}.qcow2.xz"
HAOS_SHA256="254e53f354df0739e3afc09be5431a07df53f0df6b703885404f665c454f254e"
HAOS_IMAGE_ID="local:import/haos_ova-${HAOS_VERSION}.qcow2"
HAOS_IMAGE_NAME="haos_ova-${HAOS_VERSION}.qcow2"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
CONFIG_DIR="$HOME/.config/homelab-iac"
PVE_ENV_FILE="$CONFIG_DIR/proxmox.env"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
TF_SOURCE_DIR="$REPO_ROOT/IaC/terraform/proxmox/home-01"
STATE_DIR="$HOME/.local/state/homelab-iac/home-01/terraform"
WORK_DIR="${RUNNER_TEMP:-/var/tmp}/home-01-${HOME_VM_ID}"
PLAN_FILE="$WORK_DIR/create.tfplan"

PVE_ENDPOINT="https://192.168.2.70:8006/"
PVE_NODE_NAME="PROXMOX"
PVE_SSH_HOST="192.168.2.70"

for cmd in terraform jq ssh ping curl grep awk python3; do
  require_cmd "$cmd"
done

[ "${HOME_ASSISTANT_ALLOW_DEPLOY:-false}" = "true" ] \
  || die "Refusing deployment. Re-run with HOME_ASSISTANT_ALLOW_DEPLOY=true after reviewing the Terraform plan workflow."

[ "$(hostname -s)" = "admin-01" ] || die "Run this workflow from admin-01"
[ -z "$(git -C "$REPO_ROOT" status --porcelain)" ] || die "Repository worktree is not clean"
[ "$(git -C "$REPO_ROOT" branch --show-current)" = "main" ] || die "Deployment must run from merged main"

[ -r "$PVE_ENV_FILE" ] || die "Missing Proxmox credential file: $PVE_ENV_FILE"
[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"

# shellcheck disable=SC1090
. "$PVE_ENV_FILE"
: "${TF_VAR_proxmox_api_token:?TF_VAR_proxmox_api_token missing from Proxmox credential file}"
export TF_VAR_proxmox_api_token

printf '===== HOME ASSISTANT OS DEPLOYMENT =====\n'
printf 'hostname=%s\n' "$HOME_HOSTNAME"
printf 'planned_ipv4=%s\n' "$HOME_IPV4"
printf 'vm_id=%s\n' "$HOME_VM_ID"
printf 'mac=%s\n' "$HOME_MAC"
printf 'haos=%s\n' "$HAOS_VERSION"
printf 'pve=%s\n' "$PVE_NODE_NAME"
printf 'state_dir=%s\n' "$STATE_DIR"

printf '\n===== CANONICAL / REPOSITORY GATE =====\n'
python3 "$REPO_ROOT/scripts/validate-estate.py"

jq -e \
  --arg host "$HOME_HOSTNAME" \
  --arg ip "$HOME_IPV4" \
  '.planned_assets | any(.name == $host and .address == $ip and .state == "planned" and .kind == "vm")' \
  "$REPO_ROOT/IaC/inventory/estate.json" >/dev/null \
  || die "Canonical planned home-01 reservation is missing"

printf 'canonical_reservation=PASS\n'
printf 'worktree_clean=PASS\n'

printf '\n===== LIVE COLLISION / CAPACITY GATE =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$PVE_SSH_HOST" true \
  || die "Root SSH to PROXMOX failed"

ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST" \
  "PVE_NODE_NAME='$PVE_NODE_NAME' HOME_VM_ID='$HOME_VM_ID' HOME_IPV4='$HOME_IPV4' HOME_MAC='$HOME_MAC' HOME_HOSTNAME='$HOME_HOSTNAME' HAOS_IMAGE_NAME='$HAOS_IMAGE_NAME' bash -s" <<'REMOTE_GATE'
set -euo pipefail

test "$(hostname -s)" = "$PVE_NODE_NAME"

if qm config "$HOME_VM_ID" >/dev/null 2>&1 || pct config "$HOME_VM_ID" >/dev/null 2>&1; then
  echo "VMID $HOME_VM_ID already exists"
  exit 25
fi

if grep -RHiE "$HOME_IPV4|$HOME_MAC|$HOME_HOSTNAME" /etc/pve/qemu-server /etc/pve/lxc 2>/dev/null; then
  echo 'identity collision found in /etc/pve'
  exit 26
fi

AVAILABLE_MB="$(free -m | awk '/^Mem:/ {print $7}')"
test "$AVAILABLE_MB" -ge 5000 || {
  echo "available_memory_mb=$AVAILABLE_MB"
  exit 27
}

echo "available_memory_mb=$AVAILABLE_MB"

pvesm status | awk '$1 == "vm-ssd" && $3 == "active" {found=1; if ($6 < 67108864) exit 2} END {if (!found) exit 3}'
echo 'vm_ssd_capacity=PASS'

LOCAL_CONFIG="$(pvesm config local)"
LOCAL_PATH="$(printf '%s\n' "$LOCAL_CONFIG" | awk '$1 == "path" {print $2; exit}')"
LOCAL_CONTENT="$(printf '%s\n' "$LOCAL_CONFIG" | awk '$1 == "content" {print $2; exit}')"
CONTENT_DIRS="$(printf '%s\n' "$LOCAL_CONFIG" | awk '$1 == "content-dirs" {print $2; exit}')"

test -n "$LOCAL_PATH" || {
  echo 'local storage path could not be determined'
  exit 28
}

case ",$LOCAL_CONTENT," in
  *,import,*) ;;
  *)
    echo "local_storage_content=$LOCAL_CONTENT"
    echo 'local storage does not permit import content'
    exit 29
    ;;
esac

IMPORT_REL='template/import'
if [ -n "$CONTENT_DIRS" ]; then
  OLDIFS="$IFS"
  IFS=','
  for entry in $CONTENT_DIRS; do
    case "$entry" in
      import=*) IMPORT_REL="${entry#import=}" ;;
    esac
  done
  IFS="$OLDIFS"
fi

IMPORT_DIR="${LOCAL_PATH%/}/${IMPORT_REL#/}"
IMPORT_PATH="$IMPORT_DIR/$HAOS_IMAGE_NAME"

printf 'local_storage_path=%s\n' "$LOCAL_PATH"
printf 'local_storage_content=%s\n' "$LOCAL_CONTENT"
printf 'haos_import_directory=%s\n' "$IMPORT_DIR"
printf 'haos_import_path=%s\n' "$IMPORT_PATH"
printf 'live_collision_capacity_gate=PASS\n'
REMOTE_GATE

if ping -c 2 -W 1 "$HOME_IPV4" >/dev/null 2>&1; then
  die "IP $HOME_IPV4 responds before home-01 creation"
fi

printf 'ipv4_silent=PASS\n'

[ ! -e "$STATE_DIR/terraform.tfstate" ] || die "home-01 Terraform state already exists"

printf '\n===== STAGE PINNED HAOS IMAGE =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST" \
  "HAOS_URL='$HAOS_URL' HAOS_SHA256='$HAOS_SHA256' HAOS_IMAGE_ID='$HAOS_IMAGE_ID' HAOS_IMAGE_NAME='$HAOS_IMAGE_NAME' bash -s" <<'REMOTE'
set -euo pipefail

for cmd in curl sha256sum xz qemu-img pvesm awk dirname readlink; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "missing command: $cmd"
    exit 31
  }
done

LOCAL_CONFIG="$(pvesm config local)"
LOCAL_PATH="$(printf '%s\n' "$LOCAL_CONFIG" | awk '$1 == "path" {print $2; exit}')"
LOCAL_CONTENT="$(printf '%s\n' "$LOCAL_CONFIG" | awk '$1 == "content" {print $2; exit}')"
CONTENT_DIRS="$(printf '%s\n' "$LOCAL_CONFIG" | awk '$1 == "content-dirs" {print $2; exit}')"

test -n "$LOCAL_PATH" || {
  echo 'local storage path could not be determined'
  exit 32
}

case ",$LOCAL_CONTENT," in
  *,import,*) ;;
  *)
    echo "local_storage_content=$LOCAL_CONTENT"
    echo 'local storage does not permit import content'
    exit 33
    ;;
esac

IMPORT_REL='template/import'
if [ -n "$CONTENT_DIRS" ]; then
  OLDIFS="$IFS"
  IFS=','
  for entry in $CONTENT_DIRS; do
    case "$entry" in
      import=*) IMPORT_REL="${entry#import=}" ;;
    esac
  done
  IFS="$OLDIFS"
fi

DEST_DIR="${LOCAL_PATH%/}/${IMPORT_REL#/}"
DEST="$DEST_DIR/$HAOS_IMAGE_NAME"
ARCHIVE="/var/tmp/${HAOS_IMAGE_NAME}.xz"
TMP_IMAGE="${DEST}.new"

mkdir -p "$DEST_DIR"

if [ -f "$DEST" ]; then
  qemu-img check "$DEST" >/dev/null
  RESOLVED="$(pvesm path "$HAOS_IMAGE_ID")"
  test "$(readlink -f "$RESOLVED")" = "$(readlink -f "$DEST")"
  echo 'haos_image=EXISTING_VALID'
  echo "haos_image_path=$DEST"
  echo "haos_volume_id=$HAOS_IMAGE_ID"
  exit 0
fi

rm -f "$ARCHIVE" "$TMP_IMAGE"

curl --fail --location --show-error --output "$ARCHIVE" "$HAOS_URL"
echo "$HAOS_SHA256  $ARCHIVE" | sha256sum --check -

xz --decompress --stdout "$ARCHIVE" > "$TMP_IMAGE"
qemu-img info "$TMP_IMAGE"
qemu-img check "$TMP_IMAGE"

mv "$TMP_IMAGE" "$DEST"
chmod 0644 "$DEST"
rm -f "$ARCHIVE"

qemu-img check "$DEST" >/dev/null
RESOLVED="$(pvesm path "$HAOS_IMAGE_ID")"
test "$(readlink -f "$RESOLVED")" = "$(readlink -f "$DEST")"

echo 'haos_image=STAGED_VERIFIED'
echo "haos_image_path=$DEST"
echo "haos_volume_id=$HAOS_IMAGE_ID"
REMOTE

printf '\n===== PREPARE DURABLE TERRAFORM STATE =====\n'
mkdir -p "$STATE_DIR" "$WORK_DIR"
find "$STATE_DIR" -maxdepth 1 -type f \( -name '*.tf' -o -name '.terraform.lock.hcl' \) -delete
cp "$TF_SOURCE_DIR"/*.tf "$STATE_DIR/"
cp "$TF_SOURCE_DIR/.terraform.lock.hcl" "$STATE_DIR/"

export TF_VAR_proxmox_endpoint="$PVE_ENDPOINT"
export TF_VAR_proxmox_node_name="$PVE_NODE_NAME"
export TF_VAR_vm_id="$HOME_VM_ID"
export TF_VAR_hostname="$HOME_HOSTNAME"
export TF_VAR_expected_ipv4="$HOME_IPV4"
export TF_VAR_mac_address="$HOME_MAC"
export TF_VAR_vm_datastore_id="vm-ssd"
export TF_VAR_haos_version="$HAOS_VERSION"
export TF_VAR_haos_image_id="$HAOS_IMAGE_ID"
export TF_VAR_protect_after_build=false

printf '\n===== TERRAFORM INIT / VALIDATE =====\n'
terraform -chdir="$STATE_DIR" init -input=false || die "Terraform init failed"
terraform -chdir="$STATE_DIR" validate || die "Terraform validation failed"

printf '\n===== TERRAFORM CREATE PLAN =====\n'
rm -f "$PLAN_FILE"
terraform -chdir="$STATE_DIR" plan -input=false -out="$PLAN_FILE" || die "Terraform plan failed"

terraform -chdir="$STATE_DIR" show -json "$PLAN_FILE" | jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
    and $changes[0].address == "proxmox_virtual_environment_vm.home"
    and $changes[0].change.actions == ["create"]
' >/dev/null || die "Plan contains an unapproved resource or action"

printf '\n===== APPROVED PLAN SUMMARY =====\n'
terraform -chdir="$STATE_DIR" show "$PLAN_FILE" | tail -120

printf '\n===== TERRAFORM APPLY =====\n'
terraform -chdir="$STATE_DIR" apply -input=false "$PLAN_FILE" \
  || die "Terraform apply failed"

printf '\n===== PROXMOX RUNTIME VALIDATION =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST" "
set -euo pipefail

qm status '$HOME_VM_ID' | grep -qx 'status: running'
qm config '$HOME_VM_ID' | grep -qx 'name: $HOME_HOSTNAME'
qm config '$HOME_VM_ID' | grep -qx 'bios: ovmf'
qm config '$HOME_VM_ID' | grep -qx 'machine: q35'
qm config '$HOME_VM_ID' | grep -qx 'memory: 4096'
qm config '$HOME_VM_ID' | grep -qx 'cores: 2'
qm config '$HOME_VM_ID' | grep -q 'agent: enabled=1'
qm config '$HOME_VM_ID' | grep -q 'onboot: 1'
qm config '$HOME_VM_ID' | grep -qi '$HOME_MAC'
qm config '$HOME_VM_ID' | grep -q '^scsi0: vm-ssd:'

echo 'vm_runtime_config=PASS'
" || die "Home Assistant VM runtime validation failed"

printf '\n===== DISCOVER FIRST-BOOT DHCP ADDRESS =====\n'
DHCP_IP=""
for attempt in $(seq 1 90); do
  GUEST_JSON="$(ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE_SSH_HOST" "qm guest cmd '$HOME_VM_ID' network-get-interfaces 2>/dev/null" || true)"

  DHCP_IP="$(printf '%s' "$GUEST_JSON" | jq -r '
    [
      .[]?
      | .["ip-addresses"][]?
      | select(.["ip-address-type"] == "ipv4")
      | .["ip-address"]
      | select(. != "127.0.0.1")
    ][0] // empty
  ' 2>/dev/null || true)"

  if [ -n "$DHCP_IP" ]; then
    break
  fi

  sleep 5
done

[ -n "$DHCP_IP" ] || die "HAOS booted but a guest-agent IPv4 address was not discovered"

printf 'first_boot_ipv4=%s\n' "$DHCP_IP"
printf 'planned_static_ipv4=%s\n' "$HOME_IPV4"

printf '\n===== HOME ASSISTANT WEB READINESS =====\n'
WEB_READY=0
for attempt in $(seq 1 90); do
  if curl --fail --silent --show-error --max-time 5 "http://$DHCP_IP:8123/" >/dev/null 2>&1; then
    WEB_READY=1
    break
  fi
  sleep 5
done

[ "$WEB_READY" -eq 1 ] || die "Home Assistant port 8123 did not become ready on first-boot address $DHCP_IP"

printf 'home_assistant_http=PASS\n'

printf '\n===== TERRAFORM DRIFT CHECK =====\n'
DRIFT_FILE="$WORK_DIR/post-create-plan.txt"
set +e
terraform -chdir="$STATE_DIR" plan -input=false -detailed-exitcode >"$DRIFT_FILE"
RC=$?
set -e
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

printf '\n===== RESULT: HAOS BASE BUILD PASS =====\n'
printf 'home-01 VM204 is running on PROXMOX.\n'
printf 'HAOS=%s\n' "$HAOS_VERSION"
printf 'first_boot_ipv4=%s\n' "$DHCP_IP"
printf 'planned_static_ipv4=%s\n' "$HOME_IPV4"
printf 'home_assistant_url=http://%s:8123\n' "$DHCP_IP"
printf 'proxmox_protection=DISABLED_PENDING_BACKUP_PROOF\n'
printf 'nightly_backup_schedule=NOT_YET_CHANGED\n'
printf 'usb_radio_passthrough=NOT_YET_CONFIGURED\n'
printf 'next_gate=COMPLETE_HA_ONBOARDING_AND_SET_STATIC_IPV4\n'

unset TF_VAR_proxmox_api_token
