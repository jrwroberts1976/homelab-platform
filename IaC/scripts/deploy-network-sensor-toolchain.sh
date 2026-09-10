#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

SENSOR_HOST="192.168.2.55"
SENSOR_USER="james"
SENSOR_KEY="$HOME/.ssh/proxmox-automation"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
INVENTORY="$ANSIBLE_DIR/inventory/hosts.yml"
PLAYBOOK="$ANSIBLE_DIR/playbooks/network-sensor.yml"
SECOND_RUN="${RUNNER_TEMP:-/var/tmp}/sensor-01-toolchain-idempotence.txt"

for cmd in ansible-playbook ssh curl; do
  require_cmd "$cmd"
done

[ -r "$SENSOR_KEY" ] || die "Missing sensor SSH key: $SENSOR_KEY"
[ -r "$INVENTORY" ] || die "Missing Ansible inventory: $INVENTORY"
[ -r "$PLAYBOOK" ] || die "Missing network sensor playbook: $PLAYBOOK"

printf '===== SENSOR-01 TOOLCHAIN DEPLOYMENT =====\n'
printf 'target=%s@%s\n' "$SENSOR_USER" "$SENSOR_HOST"
printf 'capture_policy=NO_CAPTURE_INTERFACE\n'
printf 'suricata_runtime=DISABLED\n'
printf 'zeek_runtime=STOPPED\n'

printf '\n===== LIVE PHASE-1 SAFETY PREFLIGHT =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes -o ConnectTimeout=5 "$SENSOR_USER@$SENSOR_HOST" bash -s <<'REMOTE'
set -eu

test "$(hostname -s)" = "sensor-01"
test "$(hostname -f)" = "sensor-01.jameshouse"
test "$(. /etc/os-release; printf '%s' "$VERSION_ID")" = "13"

GLOBAL_IFACES="$(ip -4 -o addr show scope global | awk '{print $2}' | sort -u)"
test "$GLOBAL_IFACES" = "eth0"

NON_LOOPBACK_IFACES="$(find /sys/class/net -mindepth 1 -maxdepth 1 -printf '%f\n' | grep -v '^lo$' | sort)"
test "$NON_LOOPBACK_IFACES" = "eth0"

! pgrep -x suricata >/dev/null 2>&1
! pgrep -x zeek >/dev/null 2>&1

getent ahostsv4 deb.debian.org >/dev/null
getent ahostsv4 download.opensuse.org >/dev/null

printf 'hostname=PASS\n'
printf 'debian_13=PASS\n'
printf 'management_interface=eth0\n'
printf 'capture_interface=ABSENT\n'
printf 'packet_engines_running=NO\n'
printf 'repository_dns=PASS\n'
REMOTE

printf '\n===== REPOSITORY REACHABILITY =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes "$SENSOR_USER@$SENSOR_HOST" \
  "curl -fsSI --max-time 15 https://deb.debian.org/debian/dists/trixie-backports/InRelease >/dev/null"
ssh -i "$SENSOR_KEY" -o BatchMode=yes "$SENSOR_USER@$SENSOR_HOST" \
  "curl -fsSI --max-time 15 https://download.opensuse.org/repositories/security:/zeek/Debian_13/Release.key >/dev/null"
printf 'repository_https=PASS\n'

printf '\n===== ANSIBLE SYNTAX CHECK =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" --syntax-check

printf '\n===== ANSIBLE TOOLCHAIN APPLY =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK"

printf '\n===== POST-DEPLOY VALIDATION =====\n'
ssh -i "$SENSOR_KEY" -o BatchMode=yes "$SENSOR_USER@$SENSOR_HOST" bash -s <<'REMOTE'
set -eu

echo "--- package versions ---"
dpkg-query -W -f='${Package}\t${Version}\n'   prometheus-node-exporter suricata suricata-update zeek-lts

SURICATA_VERSION="$(suricata --version)"
ZEEK_VERSION="$(/opt/zeek/bin/zeek --version)"
printf 'suricata=%s\n' "$SURICATA_VERSION"
printf 'zeek=%s\n' "$ZEEK_VERSION"

printf '%s\n' "$SURICATA_VERSION" | grep -q 'Suricata version 8\.0\.'
printf '%s\n' "$ZEEK_VERSION" | grep -q 'zeek version 8\.0\.'

test "$(systemctl is-enabled suricata 2>/dev/null || true)" = "disabled"
test "$(systemctl is-active suricata 2>/dev/null || true)" != "active"
! pgrep -x suricata >/dev/null 2>&1
! pgrep -x zeek >/dev/null 2>&1

systemctl is-enabled --quiet prometheus-node-exporter
systemctl is-active --quiet prometheus-node-exporter
curl -fsS --max-time 5 http://127.0.0.1:9100/metrics | grep -q '^node_uname_info'

GLOBAL_IFACES="$(ip -4 -o addr show scope global | awk '{print $2}' | sort -u)"
test "$GLOBAL_IFACES" = "eth0"
NON_LOOPBACK_IFACES="$(find /sys/class/net -mindepth 1 -maxdepth 1 -printf '%f\n' | grep -v '^lo$' | sort)"
test "$NON_LOOPBACK_IFACES" = "eth0"

FAILED_UNITS="$(sudo systemctl --failed --no-legend --plain)"
printf 'failed_units=%s\n' "$FAILED_UNITS"
test -z "$FAILED_UNITS"

printf 'suricata_installed=PASS\n'
printf 'suricata_runtime=DISABLED_STOPPED\n'
printf 'zeek_lts_installed=PASS\n'
printf 'zeek_runtime=STOPPED\n'
printf 'node_exporter=PASS\n'
printf 'capture_interface=ABSENT\n'
REMOTE

printf '\n===== TESTSERVER TO NODE EXPORTER =====\n'
curl -fsS --max-time 5 "http://$SENSOR_HOST:9100/metrics" | grep -q '^node_uname_info'
printf 'testserver_node_exporter_scrape=PASS\n'

printf '\n===== IDEMPOTENCE PASS =====\n'
rm -f "$SECOND_RUN"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" | tee "$SECOND_RUN"

grep -Eq 'sensor-01[[:space:]]*:.*changed=0[[:space:]]+unreachable=0[[:space:]]+failed=0' "$SECOND_RUN" \
  || die "Second Ansible pass was not cleanly idempotent"

printf '\n===== RESULT: PASS =====\n'
printf 'sensor_toolchain=PASS\n'
printf 'suricata_installed=PASS\n'
printf 'suricata_runtime=DISABLED_STOPPED\n'
printf 'zeek_lts_installed=PASS\n'
printf 'zeek_runtime=STOPPED\n'
printf 'node_exporter=PASS\n'
printf 'capture_interface=ABSENT\n'
printf 'ansible_idempotence=PASS\n'
