#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

MONITOR_HOST="192.168.2.52"
MONITOR_USER="james"
MONITOR_KEY="$HOME/.ssh/proxmox-automation"
LOKI_QUERY_URL="http://192.168.2.52:3100"
REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
INVENTORY="$ANSIBLE_DIR/inventory/hosts.yml"
PLAYBOOK="$ANSIBLE_DIR/playbooks/monitor-router-alloy.yml"
SECOND_RUN="${RUNNER_TEMP:-/var/tmp}/monitor-01-router-alloy-idempotence.txt"

for cmd in ansible-playbook curl jq ssh grep date; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$MONITOR_KEY" ] || die "Missing monitor SSH key: $MONITOR_KEY"
[ -r "$INVENTORY" ] || die "Missing Ansible inventory: $INVENTORY"
[ -r "$PLAYBOOK" ] || die "Missing monitor router Alloy playbook: $PLAYBOOK"

printf '===== MONITOR-01 ROUTER ALLOY DEPLOYMENT =====\n'
printf 'monitor=%s\n' "$MONITOR_HOST"
printf 'source=/var/log/homelab/router/rt-ac86u.log\n'
printf 'loki=127.0.0.1:3100\n'

printf '\n===== LIVE PREFLIGHT =====\n'
ssh -i "$MONITOR_KEY" -o BatchMode=yes -o ConnectTimeout=5 "$MONITOR_USER@$MONITOR_HOST" bash -s <<'REMOTE'
set -eu

test "$(hostname -s)" = "monitor-01"
test "$(hostname -f)" = "monitor-01.jameshouse"
test "$(systemctl is-active rsyslog 2>/dev/null || true)" = "active"
sudo ss -H -lunp | grep -F '192.168.2.52:5514' | grep -Fq rsyslogd
sudo test -s /var/log/homelab/router/rt-ac86u.log
sudo grep -m1 -F 'RT-AC86U-' /var/log/homelab/router/rt-ac86u.log >/dev/null
curl -fsS --max-time 3 http://127.0.0.1:3100/ready | grep -Fxq ready

printf 'identity=PASS\n'
printf 'router_syslog_receiver=ACTIVE\n'
printf 'router_log=ACTIVE\n'
printf 'loki_local=READY\n'
REMOTE

printf '\n===== ANSIBLE SYNTAX CHECK =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" --syntax-check

printf '\n===== ALLOY APPLY =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK"

printf '\n===== MONITOR RUNTIME VALIDATION =====\n'
ssh -i "$MONITOR_KEY" -o BatchMode=yes "$MONITOR_USER@$MONITOR_HOST" bash -s <<'REMOTE'
set -eu

systemctl is-enabled alloy | grep -Fxq enabled
systemctl is-active alloy | grep -Fxq active
sudo runuser -u alloy -- sh -c 'cd / && alloy validate /etc/alloy/config.alloy >/dev/null'
sudo runuser -u alloy -- test -r /var/log/homelab/router/rt-ac86u.log
id -nG alloy | tr ' ' '\n' | grep -Fxq adm
curl -fsS --max-time 3 http://127.0.0.1:3100/ready | grep -Fxq ready

printf 'alloy_version='
alloy --version | head -1
printf 'alloy_service=ACTIVE\n'
printf 'alloy_boot_persistence=PASS\n'
printf 'router_log_read_access=PASS\n'
printf 'loki_local=READY\n'
REMOTE

printf '\n===== ROUTER SYSLOG LOKI INGESTION VALIDATION =====\n'
START_NS="$(date -d '15 minutes ago' +%s%N)"
FOUND=0

for _ in $(seq 1 90); do
  END_NS="$(date +%s%N)"
  QUERY='{host="monitor-01",service="router-syslog",device="rt-ac86u"}'

  RESPONSE="$(
    curl -fsSG \
      "$LOKI_QUERY_URL/loki/api/v1/query_range" \
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

[ "$FOUND" -eq 1 ] || die "No Loki stream found for router syslog"
printf 'router_syslog_loki_ingestion=PASS\n'

printf '\n===== IDEMPOTENCE PASS =====\n'
rm -f "$SECOND_RUN"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" | tee "$SECOND_RUN"

grep -Eq 'monitor-01[[:space:]]*:.*changed=0[[:space:]]+unreachable=0[[:space:]]+failed=0' "$SECOND_RUN" \
  || die "Second Ansible pass was not cleanly idempotent"

printf '\n===== RESULT: PASS =====\n'
printf 'monitor_router_alloy=PASS\n'
printf 'alloy_service=ACTIVE\n'
printf 'alloy_boot_persistence=PASS\n'
printf 'router_syslog_to_loki=PASS\n'
printf 'loki_endpoint=127.0.0.1:3100\n'
printf 'historical_backfill=DISABLED\n'
printf 'ansible_idempotence=PASS\n'
