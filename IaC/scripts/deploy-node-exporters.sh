#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

REPO_ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
ANSIBLE_DIR="$REPO_ROOT/IaC/ansible"
MONITOR_IPV4="192.168.2.52"
MONITORING_DEFAULTS="$ANSIBLE_DIR/roles/monitoring_stack/defaults/main.yml"

for cmd in ansible-playbook curl jq awk mktemp; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$MONITORING_DEFAULTS" ] || die "Missing monitoring defaults: $MONITORING_DEFAULTS"

EXPECTED_NODE_TARGETS="$(awk '
  /^monitoring_node_exporter_targets:/ {
    in_targets = 1
    next
  }
  in_targets && /^[^[:space:]]/ {
    in_targets = 0
  }
  in_targets && /^[[:space:]]+- address:/ {
    count++
  }
  END {
    print count + 0
  }
' "$MONITORING_DEFAULTS")"

case "$EXPECTED_NODE_TARGETS" in
  ''|0|*[!0-9]*)
    die "Could not derive a valid Node Exporter target count from monitoring defaults"
    ;;
esac

printf 'expected_node_exporter_targets=%s\n' "$EXPECTED_NODE_TARGETS"

cd "$ANSIBLE_DIR" || die "Cannot enter Ansible directory"

printf '===== NODE EXPORTER SYNTAX =====\n'
ansible-playbook --syntax-check playbooks/node-exporters.yml || die "Node Exporter syntax check failed"

printf '\n===== NODE EXPORTER FIRST APPLY =====\n'
ansible-playbook playbooks/node-exporters.yml || die "Node Exporter first apply failed"

printf '\n===== NODE EXPORTER IDEMPOTENCE =====\n'
IDEMPOTENCE_OUT="$(mktemp)" || die "Cannot create idempotence output file"
ANSIBLE_NOCOLOR=1 ansible-playbook playbooks/node-exporters.yml >"$IDEMPOTENCE_OUT" 2>&1
IDEMPOTENCE_RC=$?
cat "$IDEMPOTENCE_OUT"

if [ "$IDEMPOTENCE_RC" -ne 0 ]; then
  rm -f "$IDEMPOTENCE_OUT"
  die "Node Exporter idempotence run failed"
fi

if grep -Eq 'changed=[1-9][0-9]*' "$IDEMPOTENCE_OUT"; then
  rm -f "$IDEMPOTENCE_OUT"
  die "Node Exporter second run reported changes"
fi
rm -f "$IDEMPOTENCE_OUT"
printf 'ansible_idempotence=PASS\n'

printf '\n===== RECONCILE PROMETHEUS SCRAPE CONFIG =====\n'
cd "$REPO_ROOT" || die "Cannot enter repository root"
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

printf '%s\n' "$TARGETS" | jq -e --argjson expected "$EXPECTED_NODE_TARGETS" '
  [.data.activeTargets[] | select(.labels.job == "node-exporter")] as $nodes
  | ($nodes | length) == $expected
    and all($nodes[]; .health == "up")
' >/dev/null || die "Prometheus Node Exporter target count/health does not match monitoring desired state"

printf 'node_exporter_target_count=%s\n' "$EXPECTED_NODE_TARGETS"
printf 'node_exporter_health=PASS\n'
printf '===== RESULT: PASS =====\n'
