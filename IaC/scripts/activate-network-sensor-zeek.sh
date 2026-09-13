#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

SENSOR_HOST="192.168.2.55"
SENSOR_USER="james"
SENSOR_KEY="$HOME/.ssh/proxmox-automation"
CAPTURE_IFACE="enx00249b63b38a"
REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
INVENTORY="$ANSIBLE_DIR/inventory/hosts.yml"
PLAYBOOK="$ANSIBLE_DIR/playbooks/network-sensor-config.yml"
SECOND_RUN="${RUNNER_TEMP:-/var/tmp}/sensor-01-zeek-idempotence.txt"

for cmd in ansible-playbook ssh grep; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$SENSOR_KEY" ] || die "Missing sensor SSH key: $SENSOR_KEY"
[ -r "$INVENTORY" ] || die "Missing Ansible inventory: $INVENTORY"
[ -r "$PLAYBOOK" ] || die "Missing sensor config playbook: $PLAYBOOK"

printf '===== SENSOR-01 ZEEK ACTIVATION =====\n'
printf 'capture_interface=%s\n' "$CAPTURE_IFACE"
printf 'suricata_expected=ACTIVE\n'
printf 'zeek_target=ACTIVE\n'

printf '\n===== LIVE SAFETY PREFLIGHT =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes -o ConnectTimeout=5 "$SENSOR_USER@$SENSOR_HOST" bash -s -- "$CAPTURE_IFACE" <<'REMOTE'
set -eu
IFACE="$1"

test "$(hostname -s)" = "sensor-01"
test "$(hostname -f)" = "sensor-01.jameshouse"
test -d "/sys/class/net/$IFACE"
! ip -4 -o addr show dev "$IFACE" | grep -q ' inet '
! ip -6 -o addr show dev "$IFACE" | grep -q ' inet6 '
ip link show dev "$IFACE" | grep -q 'PROMISC'
test "$(systemctl is-active suricata 2>/dev/null || true)" = "active"
sudo test -f /etc/homelab-network-sensor/capture-enabled
sudo /opt/zeek/bin/zeekctl check >/dev/null

echo 'identity=PASS'
echo 'capture_isolation=PASS'
echo 'suricata_runtime=ACTIVE'
echo 'zeek_config_check=PASS'
REMOTE

printf '\n===== ANSIBLE SYNTAX CHECK =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" --syntax-check

printf '\n===== ZEEK ACTIVATION APPLY =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK"

printf '\n===== ZEEK RUNTIME VALIDATION =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes "$SENSOR_USER@$SENSOR_HOST" bash -s -- "$CAPTURE_IFACE" <<'REMOTE'
set -eu
IFACE="$1"

sudo systemctl is-enabled homelab-zeek.service | grep -Fxq enabled
sudo systemctl is-active homelab-zeek.service | grep -Fxq active
sudo /opt/zeek/bin/zeekctl status | grep -Eq '^zeek[[:space:]]+standalone[[:space:]]+localhost[[:space:]]+running'
sudo pgrep -x zeek >/dev/null
grep -Fxq "interface=$IFACE" /opt/zeek/etc/node.cfg

READY=0
for _ in $(seq 1 30); do
  if sudo test -s /opt/zeek/logs/current/conn.log \
      && sudo grep -m1 -F '"community_id"' /opt/zeek/logs/current/conn.log >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done

test "$READY" -eq 1
FIRST_CHAR="$(sudo head -c 1 /opt/zeek/logs/current/conn.log)"
test "$FIRST_CHAR" = "{"

FAILED="$(sudo systemctl --failed --no-legend --plain)"
test -z "$FAILED"

echo 'homelab_zeek_service=PASS'
echo 'zeek_runtime=RUNNING'
echo 'zeek_conn_log=PASS'
echo 'zeek_json_logging=PASS'
echo 'zeek_community_id=PASS'
echo 'capture_interface=PASS'
REMOTE

printf '\n===== IDEMPOTENCE PASS =====\n'
rm -f "$SECOND_RUN"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" | tee "$SECOND_RUN"

grep -Eq 'sensor-01[[:space:]]*:.*changed=0[[:space:]]+unreachable=0[[:space:]]+failed=0' "$SECOND_RUN" \
  || die "Second Ansible pass was not cleanly idempotent"

printf '\n===== RESULT: PASS =====\n'
printf 'sensor_zeek_activation=PASS\n'
printf 'zeek_runtime=RUNNING\n'
printf 'zeek_boot_persistence=PASS\n'
printf 'zeek_json_logging=PASS\n'
printf 'zeek_community_id=PASS\n'
printf 'capture_interface=%s\n' "$CAPTURE_IFACE"
printf 'suricata_runtime=ACTIVE\n'
printf 'ansible_idempotence=PASS\n'
