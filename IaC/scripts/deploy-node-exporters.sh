#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
MONITOR_IPV4="192.168.2.52"

command -v ansible-playbook >/dev/null 2>&1 || die "ansible-playbook is required"
command -v curl >/dev/null 2>&1 || die "curl is required"
command -v jq >/dev/null 2>&1 || die "jq is required"

cd "$ANSIBLE_DIR"

printf '===== NODE EXPORTER SYNTAX =====\n'
ansible-playbook --syntax-check playbooks/node-exporters.yml || die "Node exporter syntax check failed"

printf '\n===== NODE EXPORTER FIRST APPLY =====\n'
ansible-playbook playbooks/node-exporters.yml || die "Node exporter first apply failed"

printf '\n===== NODE EXPORTER IDEMPOTENCE =====\n'
ansible-playbook playbooks/node-exporters.yml || die "Node exporter idempotence run failed"

printf '\n===== RECONCILE PROMETHEUS SCRAPE CONFIG =====\n'
cd "$REPO_ROOT"
bash IaC/scripts/deploy-monitoring-platform.sh || die "Monitoring configuration reconciliation failed"

printf '\n===== NODE EXPORTER PROMETHEUS VALIDATION =====\n'
TARGETS="$(curl -fsS "http://$MONITOR_IPV4:9090/api/v1/targets")" || die "Cannot read Prometheus targets"

printf '%s\n' "$TARGETS" | jq -r '
  .data.activeTargets[]
  | select(.labels.job == "node-exporter")
  | [
      (.labels.target_name // "-"),
      .labels.instance,
      .health,
      (.lastError // "")
    ]
  | @tsv
'

printf '%s\n' "$TARGETS" | jq -e '
  [.data.activeTargets[] | select(.labels.job == "node-exporter")] as $nodes
  | ($nodes | length) == 5
    and all($nodes[]; .health == "up")
' >/dev/null || die "Expected five healthy node-exporter targets"

printf '===== RESULT: PASS =====\n'
