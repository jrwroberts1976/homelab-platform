#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

SENSOR_HOST="192.168.2.55"
SENSOR_USER="james"
SENSOR_KEY="$HOME/.ssh/proxmox-automation"
REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
INVENTORY="$ANSIBLE_DIR/inventory/hosts.yml"
PLAYBOOK="$ANSIBLE_DIR/playbooks/network-sensor-config.yml"
SECOND_RUN="${RUNNER_TEMP:-/var/tmp}/sensor-01-phase1-config-idempotence.txt"

for cmd in ansible-playbook ssh grep; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$SENSOR_KEY" ] || die "Missing sensor SSH key: $SENSOR_KEY"
[ -r "$INVENTORY" ] || die "Missing Ansible inventory: $INVENTORY"
[ -r "$PLAYBOOK" ] || die "Missing sensor config playbook: $PLAYBOOK"

printf '===== SENSOR-01 PHASE-1 CONFIGURATION =====\n'
printf 'capture_interface=ABSENT\n'
printf 'capture_gate=LOCKED\n'
printf 'suricata_runtime=DISABLED_STOPPED\n'
printf 'zeek_runtime=STOPPED\n'

printf '\n===== LIVE SAFETY PREFLIGHT =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes -o ConnectTimeout=5 "$SENSOR_USER@$SENSOR_HOST" bash -s <<'REMOTE'
set -eu

test "$(hostname -s)" = "sensor-01"
test "$(hostname -f)" = "sensor-01.jameshouse"

GLOBAL_IFACES="$(ip -4 -o addr show scope global | awk '{print $2}' | sort -u)"
test "$GLOBAL_IFACES" = "eth0"
NON_LOOPBACK_IFACES="$(find /sys/class/net -mindepth 1 -maxdepth 1 -printf '%f\n' | grep -v '^lo$' | sort)"
test "$NON_LOOPBACK_IFACES" = "eth0"

! pgrep -x suricata >/dev/null 2>&1
! pgrep -x zeek >/dev/null 2>&1

test "$(systemctl is-active suricata 2>/dev/null || true)" != "active"

printf 'identity=PASS\n'
printf 'management_interface=eth0\n'
printf 'capture_interface=ABSENT\n'
printf 'packet_engines_running=NO\n'
REMOTE

printf '\n===== ANSIBLE SYNTAX CHECK =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" --syntax-check

printf '\n===== PHASE-1 CONFIG APPLY =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK"

printf '\n===== POST-CONFIG VALIDATION =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes "$SENSOR_USER@$SENSOR_HOST" bash -s <<'REMOTE'
set -eu

sudo grep -F 'HOME_NET: "[192.168.2.0/24]"' /etc/suricata/suricata.yaml
sudo grep -F 'community-id: true' /etc/suricata/suricata.yaml
sudo grep -F 'community-id-seed: 0' /etc/suricata/suricata.yaml
sudo grep -F -- '- interface: sensor-capture-disabled' /etc/suricata/suricata.yaml

test -s /var/lib/suricata/rules/suricata.rules
sudo suricata -T -c /etc/suricata/suricata.yaml >/dev/null

test -f /etc/systemd/system/suricata.service.d/10-homelab-capture-gate.conf
test ! -e /etc/homelab-network-sensor/capture-enabled

grep -Fxq 'interface=sensor-capture-disabled' /opt/zeek/etc/node.cfg
grep -Fq '192.168.2.0/24' /opt/zeek/etc/networks.cfg
grep -Fq '@load policy/tuning/json-logs' /opt/zeek/share/zeek/site/homelab.zeek
grep -Fq '@load policy/protocols/conn/community-id-logging' /opt/zeek/share/zeek/site/homelab.zeek
grep -Fq 'redef CommunityID::seed = 0;' /opt/zeek/share/zeek/site/homelab.zeek
sudo /opt/zeek/bin/zeekctl check >/dev/null

! pgrep -x suricata >/dev/null 2>&1
! pgrep -x zeek >/dev/null 2>&1

test "$(systemctl is-enabled suricata 2>/dev/null || true)" = "disabled"
test "$(systemctl is-active suricata 2>/dev/null || true)" != "active"

printf 'suricata_config=PASS\n'
printf 'suricata_rules=PASS\n'
printf 'suricata_capture_gate=LOCKED\n'
printf 'zeek_json_logging=PASS\n'
printf 'community_id_shared_seed=PASS\n'
printf 'zeek_capture_sentinel=PASS\n'
printf 'packet_engines_running=NO\n'
REMOTE

printf '\n===== IDEMPOTENCE PASS =====\n'
rm -f "$SECOND_RUN"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" | tee "$SECOND_RUN"

grep -Eq 'sensor-01[[:space:]]*:.*changed=0[[:space:]]+unreachable=0[[:space:]]+failed=0' "$SECOND_RUN" \
  || die "Second Ansible pass was not cleanly idempotent"

printf '\n===== RESULT: PASS =====\n'
printf 'sensor_phase1_config=PASS\n'
printf 'suricata_config=PASS\n'
printf 'suricata_rules=PASS\n'
printf 'suricata_runtime=DISABLED_STOPPED\n'
printf 'zeek_config=PASS\n'
printf 'zeek_json_logging=PASS\n'
printf 'zeek_runtime=STOPPED\n'
printf 'community_id_shared_seed=0\n'
printf 'capture_interface=ABSENT\n'
printf 'capture_gate=LOCKED\n'
printf 'ansible_idempotence=PASS\n'
