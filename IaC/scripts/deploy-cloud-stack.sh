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

printf '===== CLOUD-01 APPLICATION DEPLOYMENT =====\n'

ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 james@192.168.2.53 '
test "$(hostname -s)" = "cloud-01"
systemctl is-active docker
systemctl is-active chrony
systemctl is-active prometheus-node-exporter
' || die "cloud-01 baseline preflight failed"

printf '\n===== CONFIRM 4 TB DISK REMAINS OUTSIDE CLOUD-01 =====\n'
if ssh -i "$SSH_KEY" -o BatchMode=yes james@192.168.2.53   'lsblk -ndo NAME,SIZE,MODEL | grep -qE "3\.[0-9]T|WD40EZRX"'; then
  die "A 4 TB-class disk appears inside cloud-01; refusing staging deployment"
fi
printf 'cloud_data_disk_attached=NO\n'

cd "$ANSIBLE_DIR"
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles"   ansible-playbook playbooks/cloud-stack.yml   || die "cloud-01 application deployment failed"

printf '\n===== IDEMPOTENCE =====\n'
ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles"   ansible-playbook playbooks/cloud-stack.yml   || die "cloud-01 application idempotence run failed"

printf '\n===== EXTERNAL LAN VALIDATION FROM CONTROLLER =====\n'
python3 - <<'PY'
import json
import urllib.request

url = "http://192.168.2.53:8080/status.php"
with urllib.request.urlopen(url, timeout=10) as r:
    payload = json.load(r)
assert payload.get("installed") is True, payload
assert payload.get("maintenance") is False, payload
print("nextcloud_status=PASS")
print("nextcloud_version=" + str(payload.get("versionstring", "unknown")))
PY

printf '\n===== RESULT: APPLICATION STAGING PASS =====\n'
printf 'Nextcloud is available on the LAN at http://cloud-01.jameshouse:8080/\n'
printf 'Current user-data location is temporary staging storage on the 32 GiB system disk.\n'
printf 'Do not load irreplaceable production data until the 4 TB storage decision and backup/restore gates are complete.\n'

unset NEXTCLOUD_ADMIN_PASSWORD CLOUD_POSTGRES_PASSWORD CLOUD_REDIS_PASSWORD
