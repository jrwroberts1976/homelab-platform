#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

MONITOR_HOST="192.168.2.52"
MONITOR_USER="james"
ROUTER_SOURCE="192.168.2.1"
SYSLOG_PORT="5514"
SSH_KEY="$HOME/.ssh/proxmox-automation"

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
INVENTORY="$ANSIBLE_DIR/inventory/hosts.yml"
PLAYBOOK="$ANSIBLE_DIR/playbooks/router-syslog.yml"
SECOND_RUN="${RUNNER_TEMP:-/var/tmp}/router-syslog-idempotence.txt"

for cmd in ansible-playbook ssh grep tee; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$SSH_KEY" ] || die "Missing SSH key: $SSH_KEY"
[ -r "$INVENTORY" ] || die "Missing Ansible inventory: $INVENTORY"
[ -r "$PLAYBOOK" ] || die "Missing router syslog playbook: $PLAYBOOK"

printf '===== ROUTER SYSLOG RECEIVER DEPLOYMENT =====\n'
printf 'receiver=%s:%s/udp\n' "$MONITOR_HOST" "$SYSLOG_PORT"
printf 'allowed_source=%s\n' "$ROUTER_SOURCE"
printf 'router_change=NONE\n'

printf '\n===== LIVE PREFLIGHT =====\n'
ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "$MONITOR_USER@$MONITOR_HOST" bash -s <<REMOTE
set -eu

test "\$(hostname -s)" = "monitor-01"
ip -4 -o addr show scope global | grep -Fq ' ${MONITOR_HOST}/24 '

LISTENER="\$(sudo ss -H -lunp | grep -F ':${SYSLOG_PORT} ' || true)"
if [ -n "\$LISTENER" ] && ! printf '%s\n' "\$LISTENER" | grep -Fq 'rsyslogd'; then
  printf 'Unexpected existing UDP/%s listener:\n%s\n' '${SYSLOG_PORT}' "\$LISTENER" >&2
  exit 1
fi

printf 'monitor_identity=PASS\n'
printf 'udp_%s_collision=NONE_OR_RSYSLOG\n' '${SYSLOG_PORT}'
REMOTE

printf '\n===== ANSIBLE SYNTAX CHECK =====\n'
cd "$ANSIBLE_DIR"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" --syntax-check

printf '\n===== ANSIBLE APPLY =====\n'
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK"

printf '\n===== RECEIVER VALIDATION =====\n'
ssh -i "$SSH_KEY" -o BatchMode=yes "$MONITOR_USER@$MONITOR_HOST" bash -s <<REMOTE
set -eu

sudo rsyslogd -N1

test "\$(systemctl is-enabled rsyslog)" = "enabled"
test "\$(systemctl is-active rsyslog)" = "active"

sudo ss -H -lunp \
  | grep -F '${MONITOR_HOST}:${SYSLOG_PORT}' \
  | grep -Fq 'rsyslogd'

sudo grep -Fq '${ROUTER_SOURCE}' /etc/rsyslog.d/30-asus-router-remote.conf
sudo grep -Fq '/var/log/homelab/router/rt-ac86u.log' /etc/rsyslog.d/30-asus-router-remote.conf
sudo test -d /var/log/homelab/router
sudo test -f /etc/logrotate.d/homelab-router-syslog

echo 'rsyslog_config=PASS'
echo 'rsyslog_service=PASS'
echo 'udp_5514_listener=PASS'
echo 'source_restriction=PASS'
echo 'log_rotation=PASS'
REMOTE

printf '\n===== IDEMPOTENCE PASS =====\n'
rm -f "$SECOND_RUN"
ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_ROLES_PATH="$ANSIBLE_DIR/roles" \
  ansible-playbook -i "$INVENTORY" "$PLAYBOOK" | tee "$SECOND_RUN"

grep -Eq 'monitor-01[[:space:]]*:.*changed=0[[:space:]]+unreachable=0[[:space:]]+failed=0' "$SECOND_RUN" \
  || die "Second Ansible pass was not cleanly idempotent"

printf '\n===== RESULT: PASS =====\n'
printf 'router_syslog_receiver=PASS\n'
printf 'receiver=%s:%s/udp\n' "$MONITOR_HOST" "$SYSLOG_PORT"
printf 'allowed_source=%s\n' "$ROUTER_SOURCE"
printf 'log_file=/var/log/homelab/router/rt-ac86u.log\n'
printf 'retention_days=30\n'
printf 'router_change=NOT_YET_CONFIGURED\n'
printf 'ansible_idempotence=PASS\n'
