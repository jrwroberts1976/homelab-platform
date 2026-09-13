#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

SENSOR_HOST="192.168.2.55"
SENSOR_USER="james"
SENSOR_KEY="$HOME/.ssh/proxmox-automation"
LOKI_URL="http://192.168.2.52:3100"
REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
INVENTORY="$ANSIBLE_DIR/inventory/hosts.yml"
PLAYBOOK="$ANSIBLE_DIR/playbooks/network-sensor-alloy.yml"
SECOND_RUN="${RUNNER_TEMP:-/var/tmp}/sensor-01-alloy-idempotence.txt"

for cmd in ansible-playbook curl jq ssh grep date; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$SENSOR_KEY" ] || die "Missing sensor SSH key: $SENSOR_KEY"
[ -r "$INVENTORY" ] || die "Missing Ansible inventory: $INVENTORY"
[ -r "$PLAYBOOK" ] || die "Missing sensor Alloy playbook: $PLAYBOOK"

printf '===== SENSOR-01 ALLOY DEPLOYMENT =====\n'
printf 'sensor=%s\n' "$SENSOR_HOST"
printf 'loki=%s\n' "$LOKI_URL"
printf 'sources=suricata,zeek\n'

printf '\n===== LIVE PREFLIGHT =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes -o ConnectTimeout=5 "$SENSOR_USER@$SENSOR_HOST" bash -s <<'REMOTE'
set -eu

test "$(hostname -s)" = "sensor-01"
test "$(hostname -f)" = "sensor-01.jameshouse"
test "$(systemctl is-active suricata 2>/dev/null || true)" = "active"
test "$(systemctl is-active homelab-zeek.service 2>/dev/null || true)" = "active"
sudo test -s /var/log/suricata/eve.json
sudo test -s /opt/zeek/spool/zeek/conn.log
curl -fsS --max-time 3 http://192.168.2.52:3100/ready | grep -Fxq ready

printf 'identity=PASS\n'
printf 'suricata_runtime=ACTIVE\n'
printf 'zeek_runtime=ACTIVE\n'
printf 'loki_connectivity=PASS\n'
REMOTE

printf '\n===== ANSIBLE SYNTAX CHECK =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" --syntax-check

printf '\n===== ALLOY APPLY =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK"

printf '\n===== SENSOR RUNTIME VALIDATION =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes "$SENSOR_USER@$SENSOR_HOST" bash -s <<'REMOTE'
set -eu

systemctl is-enabled alloy | grep -Fxq enabled
systemctl is-active alloy | grep -Fxq active
sudo -u alloy alloy validate /etc/alloy/config.alloy >/dev/null
sudo -u alloy test -r /var/log/suricata/eve.json
sudo -u alloy test -r /opt/zeek/spool/zeek/conn.log
id -nG alloy | tr ' ' '\n' | grep -Fxq zeek
curl -fsS --max-time 3 http://192.168.2.52:3100/ready | grep -Fxq ready

printf 'alloy_version='
alloy --version | head -1
printf 'alloy_service=ACTIVE\n'
printf 'alloy_boot_persistence=PASS\n'
printf 'suricata_read_access=PASS\n'
printf 'zeek_read_access=PASS\n'
printf 'loki_connectivity=PASS\n'
REMOTE

printf '\n===== LOKI INGESTION VALIDATION =====\n'
START_NS="$(date -d '15 minutes ago' +%s%N)"

for SERVICE in suricata zeek; do
  FOUND=0

  for _ in $(seq 1 60); do
    END_NS="$(date +%s%N)"
    QUERY="{host=\"sensor-01\",service=\"${SERVICE}\"}"

    RESPONSE="$(
      curl -fsSG \
        "$LOKI_URL/loki/api/v1/query_range" \
        --data-urlencode "query=$QUERY" \
        --data-urlencode "start=$START_NS" \
        --data-urlencode "end=$END_NS" \
        --data-urlencode 'limit=1'
    )"

    if printf '%s' "$RESPONSE" \
        | jq -e '.status == "success" and (.data.result | length > 0)' \
        >/dev/null; then
      FOUND=1
      break
    fi

    sleep 2
  done

  [ "$FOUND" -eq 1 ] || die "No Loki stream found for service=$SERVICE"
  printf '%s_loki_ingestion=PASS\n' "$SERVICE"
done

printf '\n===== IDEMPOTENCE PASS =====\n'
rm -f "$SECOND_RUN"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" | tee "$SECOND_RUN"

grep -Eq 'sensor-01[[:space:]]*:.*changed=0[[:space:]]+unreachable=0[[:space:]]+failed=0' "$SECOND_RUN" \
  || die "Second Ansible pass was not cleanly idempotent"

printf '\n===== RESULT: PASS =====\n'
printf 'sensor_alloy=PASS\n'
printf 'alloy_service=ACTIVE\n'
printf 'alloy_boot_persistence=PASS\n'
printf 'suricata_to_loki=PASS\n'
printf 'zeek_to_loki=PASS\n'
printf 'loki_endpoint=192.168.2.52:3100\n'
printf 'historical_backfill=DISABLED\n'
printf 'ansible_idempotence=PASS\n'
