#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
SECRET_DIR="$HOME/.config/homelab-iac"
SECRET_FILE="$SECRET_DIR/monitoring.env"
MONITOR_IPV4="192.168.2.52"

command -v ansible-playbook >/dev/null 2>&1 || die "ansible-playbook is required"
command -v openssl >/dev/null 2>&1 || die "openssl is required"
command -v curl >/dev/null 2>&1 || die "curl is required"

mkdir -p "$SECRET_DIR"
chmod 700 "$SECRET_DIR"

if [ ! -s "$SECRET_FILE" ]; then
  umask 077
  printf 'GRAFANA_ADMIN_PASSWORD=%s\n' "$(openssl rand -hex 24)" >"$SECRET_FILE"
  printf 'created_secret_file=%s\n' "$SECRET_FILE"
fi

chmod 600 "$SECRET_FILE"

# shellcheck disable=SC1090
set -a
. "$SECRET_FILE"
set +a

: "${GRAFANA_ADMIN_PASSWORD:?GRAFANA_ADMIN_PASSWORD missing from $SECRET_FILE}"
export GRAFANA_ADMIN_PASSWORD

cd "$ANSIBLE_DIR"

printf '===== MONITORING PLAYBOOK SYNTAX =====\n'
ansible-playbook --syntax-check playbooks/monitoring.yml || die "Monitoring syntax check failed"

printf '\n===== MONITORING FIRST APPLY =====\n'
ansible-playbook playbooks/monitoring.yml || die "Monitoring first apply failed"

printf '\n===== MONITORING IDEMPOTENCE =====\n'
ansible-playbook playbooks/monitoring.yml || die "Monitoring idempotence run failed"

printf '\n===== CONTROLLER HEALTH CHECKS =====\n'
curl -fsS "http://$MONITOR_IPV4:9090/-/ready" >/dev/null || die "Prometheus controller check failed"
curl -fsS "http://$MONITOR_IPV4:3000/api/health" >/dev/null || die "Grafana controller check failed"
curl -fsS "http://$MONITOR_IPV4:9093/-/ready" >/dev/null || die "Alertmanager controller check failed"
curl -fsS "http://$MONITOR_IPV4:9115/" >/dev/null || die "Blackbox controller check failed"

printf 'prometheus=PASS\n'
printf 'grafana=PASS\n'
printf 'alertmanager=PASS\n'
printf 'blackbox=PASS\n'
printf 'grafana_secret=%s\n' "$SECRET_FILE"
printf '===== RESULT: PASS =====\n'
