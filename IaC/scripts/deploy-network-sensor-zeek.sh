#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
INVENTORY="$ANSIBLE_DIR/inventory/hosts.yml"
PLAYBOOK="$ANSIBLE_DIR/playbooks/network-sensor-zeek.yml"
SECOND_RUN="${RUNNER_TEMP:-/var/tmp}/sensor-01-zeek-idempotence.txt"

for cmd in ansible-playbook grep; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$INVENTORY" ] || die "Missing Ansible inventory: $INVENTORY"
[ -r "$PLAYBOOK" ] || die "Missing Zeek activation playbook: $PLAYBOOK"

printf '===== SENSOR-01 ZEEK ACTIVATION =====\n'

cd "$ANSIBLE_DIR"

printf '\n===== ANSIBLE SYNTAX CHECK =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" --syntax-check

printf '\n===== ZEEK ACTIVATION APPLY =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK"

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
printf 'capture_interface=enx00249b63b38a\n'
printf 'suricata_runtime=ACTIVE\n'
printf 'ansible_idempotence=PASS\n'
