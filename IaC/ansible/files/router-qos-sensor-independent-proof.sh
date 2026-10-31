#!/bin/bash
# TEST-ONLY: sensor-01; all tc/ip changes confined to a new named network namespace.
set -Eeuo pipefail
# Only the failing command and line are reported; no verbose shell tracing.
trap 'rc=$?; echo "QOS_PROOF_ERROR line=$LINENO rc=$rc command=$BASH_COMMAND" >&2' ERR
NS=qos-proof31
UNIT=qos-proof31-rollback
BASE=/run/qos-proof31
SELF=/run/qos-proof31-test.sh
verify_host() {
  [[ $(hostname) == sensor-01 ]]
  # Ansible execution context may have a different netns from PID 1.
  # Fail closed unless the host identity and expected production eth0 route agree.
  [[ $(ip -4 -o addr show dev eth0 scope global) == *"192.168.2.55/24"* ]]
  [[ $(ip -4 route show default) == *"default via 192.168.2.1 dev eth0"* ]]
}
exists_ns() { ip netns list | grep -Eq "^$NS( |$)"; }
inside() { ip netns exec "$NS" "$@"; }
verify_namespace_owner() {
  [[ -f "$BASE/ns-inode" && -f "$BASE/owner" ]] || return 1
  [[ $(cat "$BASE/owner") == qos-proof31 ]] || return 1
  exists_ns || return 1
  [[ $(stat -Lc %i "/run/netns/$NS") == "$(cat "$BASE/ns-inode")" ]] || return 1
  [[ $(stat -Lc %i "/run/netns/$NS") != "$(stat -Lc %i /proc/1/ns/net)" ]] || return 1
}
watchdog_locked() {
  verify_host
  [[ -d "$BASE" && -f "$BASE/owner" ]] || exit 1
  [[ $(cat "$BASE/owner") == qos-proof31 ]] || exit 1
  if exists_ns; then
    verify_namespace_owner || { echo "Namespace owner changed; refusing cleanup" >&2; exit 1; }
    inside tc filter del dev qd31 ingress pref 49131 2>/dev/null || :
    inside tc qdisc del dev qd31 clsact 2>/dev/null || :
    inside ip link del dev qi31 2>/dev/null || :
    ! inside ip link show dev qi31 >/dev/null 2>&1
    [[ -z $(inside tc filter show dev qd31 ingress) ]]
    ! inside tc qdisc show dev qd31 | grep -q 'qdisc clsact'
  fi
  touch "$BASE/rolled-back"
}
watchdog() {
  verify_host
  [[ -f "$BASE/ops.lock" ]] || { echo "Missing operations lock" >&2; return 1; }
  flock -x -w 20 "$BASE/ops.lock" /bin/bash "$SELF" watchdog-locked
}
cleanup() {
  # An early preflight failure may leave only the staged source script.
  if [[ ! -e "$BASE" && ! -e "$SELF" ]] && ! exists_ns; then
    if systemctl is-active --quiet "$UNIT.timer" || systemctl is-active --quiet "$UNIT.service"; then
      echo "Unexpected active watchdog with no ownership evidence; refusing cleanup" >&2
      return 1
    fi
    return 0
  fi
  # Cancel future execution, then wait for any running callback to finish.
  if systemctl is-active --quiet "$UNIT.timer"; then
    systemctl stop "$UNIT.timer" || { echo "Failed to stop watchdog timer; preserving executable" >&2; return 1; }
  fi
  [[ $(systemctl is-active "$UNIT.timer" 2>/dev/null || :) != active ]] || return 1
  for i in {1..20}; do
    case "$(systemctl is-active "$UNIT.service" 2>/dev/null || :)" in active|activating|deactivating) ;; *) break ;; esac
    sleep 1
  done
  case "$(systemctl is-active "$UNIT.service" 2>/dev/null || :)" in
    active|activating|deactivating) echo "Watchdog still running; preserving executable" >&2; return 1 ;;
  esac
  [[ -f "$BASE/owner" && $(cat "$BASE/owner") == qos-proof31 ]] || { echo "Missing ownership marker; preserving evidence" >&2; return 1; }
  if exists_ns; then
    verify_namespace_owner || { echo "Namespace owner mismatch; preserving resources" >&2; return 1; }
    watchdog
    inside ip link del dev qd31
    ip netns del "$NS"
  fi
  [[ ! -e "$BASE" || -f "$BASE/rolled-back" ]] || { echo "No rollback evidence" >&2; return 1; }
  # The executable is only removed once no scheduled/running callback needs it.
  rm -f "$SELF"
}
case "${1:-}" in
  watchdog) watchdog ;;
  watchdog-locked) watchdog_locked ;;
  cleanup) verify_host; cleanup ;;
  recover)
    verify_host
    [[ -d "$BASE" && -f "$BASE/owner" && -f "$BASE/ns-inode" && -f "$BASE/ops.lock" ]] || { echo "Missing ownership evidence; refuse recovery" >&2; exit 1; }
    [[ $(cat "$BASE/owner") == qos-proof31 ]] || exit 1
    if exists_ns; then verify_namespace_owner; fi
    cleanup
    ! exists_ns
    [[ ! -e "$SELF" ]]
    echo RECOVERY_PASS
    ;;
  run|run-partial|run-event-partial|run-python-partial)
    verify_host
    mode="$1"
    if [[ "$mode" == run-event-partial ]]; then
      [[ -f /run/qos-proof31-event-gate.py && -f /run/router-qos-download-ppp-event-replay.py ]] || exit 1
      [[ ! -L /run/qos-proof31-event-gate.py && ! -L /run/router-qos-download-ppp-event-replay.py ]] || exit 1
    fi
    [[ ! -e "$BASE" && ! -e "$SELF" ]] || { echo 'Reserved evidence exists'; exit 1; }
    ! exists_ns
    [[ -z $(systemctl list-units --all --plain --no-legend "$UNIT*" | grep -v '^$' || true) ]]
    [[ -z $(systemctl list-unit-files --no-legend "$UNIT*" | grep -v '^$' || true) ]]
    mkdir -m 0700 "$BASE"
    echo qos-proof31 > "$BASE/owner"
    touch "$BASE/ops.lock"
    cp "$0" "$SELF"
    chmod 0700 "$SELF"
    trap 'status=$?; trap - EXIT; if ! cleanup; then echo "Cleanup failed; recovery evidence preserved" >&2; exit 1; fi; exit "$status"' EXIT
    ip netns add "$NS"
    stat -Lc %i "/run/netns/$NS" > "$BASE/ns-inode"
    verify_namespace_owner
    [[ $(inside ip -o link show | wc -l) -eq 1 ]]
    inside ip link add qd31 type dummy
    inside ip link set qd31 up
    # Arm an independently scheduled systemd timer before tc/IFB changes.
    systemd-run --unit="$UNIT" --on-active=10s --collect -- /bin/bash "$SELF" watchdog
    systemctl is-active --quiet "$UNIT.timer"
    deadline=$(systemctl show "$UNIT.timer" -p NextElapseUSecMonotonic --value)
    [[ -n "$deadline" && "$deadline" != 0 && "$deadline" != n/a ]] || { echo "Timer deadline missing" >&2; exit 1; }
    if [[ "$mode" == run-python-partial ]]; then
      [[ -f /run/qos-proof31-python-installer.py && ! -L /run/qos-proof31-python-installer.py ]] || exit 1
      set +e
      flock -x -w 20 "$BASE/ops.lock" python3 -B /run/qos-proof31-python-installer.py --partial-kill
      result=$?
      set -e
      [[ "$result" == 137 ]]
      echo PYTHON_INSTALLER_KILLED
      for i in {1..35}; do [[ -f "$BASE/rolled-back" ]] && break; sleep 1; done
      [[ -f "$BASE/rolled-back" ]]
      ! inside ip link show dev qi31 >/dev/null 2>&1
      [[ -z $(inside tc filter show dev qd31 ingress) ]]
      echo PYTHON_WATCHDOG_ROLLBACK_PASS
      exit 0
    fi
    # The disposable installer process performs real tc operations, then dies.
    if [[ "$mode" == run-event-partial ]]; then
      decision=$(python3 /run/qos-proof31-event-gate.py --sensor-fixture)
      [[ "$decision" == PLAN_INSTALL ]] || exit 1
      echo PYTHON_PPP_PLAN_INSTALL_PASS
    fi
    # No host interfaces are ever named in these commands.
    set +e
    # Serialize installer and recovery callback to avoid teardown during tc changes.
    flock -x -w 20 "$BASE/ops.lock" ip netns exec "$NS" /bin/bash -euc '
      ip link add qi31 type ifb
      ip link set qi31 up
      tc qdisc add dev qi31 root cake bandwidth 43mbit besteffort flows
      if [[ "$1" == run-partial || "$1" == run-event-partial ]]; then
        tc qdisc show dev qi31 | grep -q cake
        kill -KILL "$BASHPID"
      fi
      tc qdisc add dev qd31 clsact
      tc filter add dev qd31 ingress pref 49131 matchall action mirred egress redirect dev qi31
      tc filter show dev qd31 ingress | grep -q 49131
      kill -KILL "$BASHPID"
    ' bash "$mode" 2>/dev/null
    result=$?
    set -e
    [[ $result == 137 ]]
    echo INSTALLER_KILLED
    if [[ "$mode" == run-partial || "$mode" == run-event-partial ]]; then echo PARTIAL_INSTALLER_KILLED; fi
    for i in {1..35}; do [[ -f "$BASE/rolled-back" ]] && break; sleep 1; done
    [[ -f "$BASE/rolled-back" ]]
    ! inside ip link show dev qi31 >/dev/null 2>&1
    [[ -z $(inside tc filter show dev qd31 ingress) ]]
    echo WATCHDOG_ROLLBACK_PASS
    if [[ "$mode" == run-partial || "$mode" == run-event-partial ]]; then echo PARTIAL_WATCHDOG_ROLLBACK_PASS; fi
    ;;
  *) echo 'Use run, run-partial, run-event-partial, run-python-partial, watchdog, cleanup' >&2; exit 2 ;;
esac
