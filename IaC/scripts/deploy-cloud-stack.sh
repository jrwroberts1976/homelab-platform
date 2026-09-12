#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ENV_FILE="$HOME/.config/homelab-iac/cloud-01.env"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
SSH_KEY="$HOME/.ssh/proxmox-automation"
CLOUD_HOST="192.168.2.53"
CLOUD_DATA_ROOT="/srv/cloud-01-data"
CLOUD_DATA_DEVICE="/dev/disk/by-id/scsi-0QEMU_QEMU_HARDDISK_drive-scsi1"
CLOUD_DATA_BYTES="214748364800"

for cmd in ansible-playbook ssh python3 grep mktemp; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$ENV_FILE" ] || die "Missing protected cloud secret file: $ENV_FILE"
[ -r "$SSH_KEY" ] || die "Missing cloud SSH key: $SSH_KEY"

# shellcheck disable=SC1090
. "$ENV_FILE"

: "${NEXTCLOUD_ADMIN_USER:?NEXTCLOUD_ADMIN_USER missing}"
: "${NEXTCLOUD_ADMIN_PASSWORD:?NEXTCLOUD_ADMIN_PASSWORD missing}"
: "${CLOUD_POSTGRES_PASSWORD:?CLOUD_POSTGRES_PASSWORD missing}"
: "${CLOUD_REDIS_PASSWORD:?CLOUD_REDIS_PASSWORD missing}"

export NEXTCLOUD_ADMIN_USER NEXTCLOUD_ADMIN_PASSWORD
export CLOUD_POSTGRES_PASSWORD CLOUD_REDIS_PASSWORD

printf '===== CLOUD-01 PRODUCTION APPLICATION RECONCILIATION =====\n'
printf 'target=%s\n' "$CLOUD_HOST"
printf 'data_root=%s\n' "$CLOUD_DATA_ROOT"
printf 'approved_device=%s\n' "$CLOUD_DATA_DEVICE"

printf '\n===== PRODUCTION PREFLIGHT =====\n'
ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "james@$CLOUD_HOST" '
APPROVED_DEVICE="/dev/disk/by-id/scsi-0QEMU_QEMU_HARDDISK_drive-scsi1"
DATA_ROOT="/srv/cloud-01-data"
EXPECTED_BYTES="214748364800"

test "$(hostname -s)" = "cloud-01" || exit 21
systemctl is-active docker >/dev/null || exit 22
systemctl is-active chrony >/dev/null || exit 23
systemctl is-active prometheus-node-exporter >/dev/null || exit 24

REAL_DEVICE="$(readlink -f "$APPROVED_DEVICE")"
test -n "$REAL_DEVICE" || exit 31

TARGET="$(findmnt -rn -T "$DATA_ROOT" -o TARGET)"
SOURCE="$(findmnt -rn -T "$DATA_ROOT" -o SOURCE)"
FSTYPE="$(findmnt -rn -T "$DATA_ROOT" -o FSTYPE)"
OPTIONS="$(findmnt -rn -T "$DATA_ROOT" -o OPTIONS)"
LABEL="$(sudo blkid -s LABEL -o value "$REAL_DEVICE")"
SIZE="$(lsblk -bndo SIZE "$REAL_DEVICE")"

test "$TARGET" = "$DATA_ROOT" || exit 32
test "$SOURCE" = "$REAL_DEVICE" || exit 33
test "$FSTYPE" = "ext4" || exit 34
test "$LABEL" = "cloud-01-data" || exit 35
test "$SIZE" = "$EXPECTED_BYTES" || exit 36

case ",$OPTIONS," in
  *,rw,*) ;;
  *) exit 37 ;;
esac

FAILED_UNITS="$(sudo systemctl --failed --no-legend --plain)"
test -z "$FAILED_UNITS" || {
  printf "%s\n" "$FAILED_UNITS"
  exit 38
}

printf "hostname_gate=PASS\n"
printf "service_gate=PASS\n"
printf "storage_device=%s\n" "$REAL_DEVICE"
printf "storage_target=%s\n" "$TARGET"
printf "storage_fstype=%s\n" "$FSTYPE"
printf "storage_label=%s\n" "$LABEL"
printf "storage_options=%s\n" "$OPTIONS"
printf "storage_bytes=%s\n" "$SIZE"
printf "failed_units=NONE\n"
df -hT "$DATA_ROOT"
' || die "cloud-01 production preflight failed"

cd "$ANSIBLE_DIR" || die "Cannot enter Ansible directory"

printf '\n===== ANSIBLE SYNTAX =====\n'
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook --syntax-check playbooks/cloud-stack.yml \
  || die "cloud-01 application syntax check failed"

printf '\n===== ANSIBLE CHECK MODE =====\n'
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook --check playbooks/cloud-stack.yml \
  || die "cloud-01 application check mode failed"

printf '\n===== APPROVED PRODUCTION RECONCILIATION =====\n'
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook playbooks/cloud-stack.yml \
  -e cloud_stack_allow_deploy=true \
  || die "cloud-01 production application reconciliation failed"

printf '\n===== IDEMPOTENCE =====\n'
IDEMPOTENCE_OUT="$(mktemp)" || die "Cannot create idempotence output file"
ANSIBLE_NOCOLOR=1 ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook playbooks/cloud-stack.yml \
  -e cloud_stack_allow_deploy=true \
  >"$IDEMPOTENCE_OUT" 2>&1
IDEMPOTENCE_RC=$?
cat "$IDEMPOTENCE_OUT"

if [ "$IDEMPOTENCE_RC" -ne 0 ]; then
  rm -f "$IDEMPOTENCE_OUT"
  die "cloud-01 application idempotence run failed"
fi

if ! grep -Eq '^cloud-01[[:space:]]*:[[:space:]]+ok=[0-9]+[[:space:]]+changed=0[[:space:]]+unreachable=0[[:space:]]+failed=0' "$IDEMPOTENCE_OUT"; then
  rm -f "$IDEMPOTENCE_OUT"
  die "cloud-01 application second run was not idempotent"
fi
rm -f "$IDEMPOTENCE_OUT"
printf 'ansible_idempotence=PASS\n'

printf '\n===== APPLICATION HEALTH =====\n'
python3 - <<'PY'
import json
import urllib.request

url = "http://192.168.2.53:8080/status.php"
with urllib.request.urlopen(url, timeout=10) as response:
    payload = json.load(response)

assert payload.get("installed") is True, payload
assert payload.get("maintenance") is False, payload
assert payload.get("needsDbUpgrade") is False, payload
print("nextcloud_status=PASS")
print("nextcloud_version=" + str(payload.get("versionstring", "unknown")))
PY

ssh -i "$SSH_KEY" -o BatchMode=yes "james@$CLOUD_HOST" '
cd /opt/cloud-01 || exit 41

RUNNING="$(sudo docker compose ps --services --status running)"
for SERVICE in app cron db redis; do
  printf "%s\n" "$RUNNING" | grep -qx "$SERVICE" || exit 42
done

DB_ID="$(sudo docker compose ps -q db)"
REDIS_ID="$(sudo docker compose ps -q redis)"
test -n "$DB_ID" || exit 43
test -n "$REDIS_ID" || exit 44

test "$(sudo docker inspect -f "{{.State.Health.Status}}" "$DB_ID")" = "healthy" || exit 45
test "$(sudo docker inspect -f "{{.State.Health.Status}}" "$REDIS_ID")" = "healthy" || exit 46

DATA_ROOT="/srv/cloud-01-data"
TARGET="$(findmnt -rn -T "$DATA_ROOT" -o TARGET)"
FSTYPE="$(findmnt -rn -T "$DATA_ROOT" -o FSTYPE)"
OPTIONS="$(findmnt -rn -T "$DATA_ROOT" -o OPTIONS)"
test "$TARGET" = "$DATA_ROOT" || exit 47
test "$FSTYPE" = "ext4" || exit 48
case ",$OPTIONS," in
  *,rw,*) ;;
  *) exit 49 ;;
esac

FAILED_UNITS="$(sudo systemctl --failed --no-legend --plain)"
test -z "$FAILED_UNITS" || exit 50

printf "required_containers=RUNNING\n"
printf "postgres_health=healthy\n"
printf "redis_health=healthy\n"
printf "storage_postcheck=PASS\n"
printf "failed_units=NONE\n"
' || die "cloud-01 post-reconciliation health validation failed"

printf '\n===== RESULT: APPLICATION PRODUCTION PASS =====\n'
printf 'Nextcloud is healthy on the LAN at http://cloud-01.jameshouse:8080/\n'
printf 'User data is on the dedicated 200 GiB ext4 filesystem at /srv/cloud-01-data/data.\n'
printf 'Backups, restore testing and full observability integration remain separate delivery gates.\n'

unset NEXTCLOUD_ADMIN_PASSWORD CLOUD_POSTGRES_PASSWORD CLOUD_REDIS_PASSWORD
