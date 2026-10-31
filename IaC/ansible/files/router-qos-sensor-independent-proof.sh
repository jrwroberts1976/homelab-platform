#!/bin/bash
# TEST-ONLY: sensor-01; all tc/ip changes confined to a new named network namespace.
set -euo pipefail
NS=qos-proof31
UNIT=qos-proof31-rollback
BASE=/run/qos-proof31
SELF=/run/qos-proof31-test.sh
verify_host() {
  [[ $(hostname) == sensor-01 ]]
  [[ $(readlink /proc/self/ns/net) == $(readlink /proc/1/ns/net) ]]
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
  # Cancel future execution, then wait for any running callback to finish.
  systemctl stop "$UNIT.timer" 2>/dev/null || :
  for i in {1..20}; do
    [[ $(systemctl is-active "$UNIT.service" 2>/dev/null || :) != active ]] && break
    sleep 1
  done
  [[ $(systemctl is-active "$UNIT.service" 2>/dev/null || :) != active ]] || { echo "Watchdog still running" >&2; return 1; }
  if exists_ns; then
    verify_namespace_owner || { echo "Namespace owner mismatch; preserving resources" >&2; return 1; }
    watchdog
    inside ip link del dev qd31
    ip netns del "$NS"
  fi
  [[ ! -e "$BASE" || -f "$BASE/rolled-back" ]] || { echo "No rollback evidence" >&2; return 1; }
}
case "${1:-}" in
  watchdog) watchdog ;;
  watchdog-locked) watchdog_locked ;;
  cleanup) verify_host; cleanup ;;
  run)
    verify_host
    [[ ! -e "$BASE" && ! -e "$SELF" ]] || { echo 'Reserved evidence exists'; exit 1; }
    ! exists_ns
    [[ -z $(systemctl list-units --all --plain --no-legend "$UNIT*" | grep -v '^$' || true) ]]
    [[ -z $(systemctl list-unit-files --no-legend "$UNIT*" | grep -v '^$' || true) ]]
    mkdir -m 0700 "$BASE"
    echo qos-proof31 > "$BASE/owner"
    touch "$BASE/ops.lock"
    cp "$0" "$SELF"
    chmod 0700 "$SELF"
    trap 'cleanup && rm -f "$SELF"' EXIT
    ip netns add "$NS"
    stat -Lc %i "/run/netns/$NS" > "$BASE/ns-inode"
    verify_namespace_owner
    [[ $(inside ip -o link show | wc -l) -eq 1 ]]
    inside ip link add qd31 type dummy
    inside ip link set qd31 up
    # Arm an independently scheduled systemd timer before tc/IFB changes.
    systemd-run --unit="$UNIT" --on-active=10s --collect -- /bin/bash "$SELF" watchdog
    systemctl is-active --quiet "$UNIT.timer"
    [[ $(systemctl show "$UNIT.timer" -p NextElapseUSecMonotonic --value) != 0 ]] || { echo "Timer deadline missing" >&2; exit 1; }
    # The disposable installer process performs real tc operations, then dies.
    # No host interfaces are ever named in these commands.
    set +e
    # Serialize installer and recovery callback to avoid teardown during tc changes.
    flock -x -w 20 "$BASE/ops.lock" ip netns exec "$NS" /bin/bash -euc '
      ip link add qi31 type ifb
      ip link set qi31 up
      tc qdisc add dev qi31 root cake bandwidth 43mbit besteffort flows
      tc qdisc add dev qd31 clsact
      tc filter add dev qd31 ingress pref 49131 matchall action mirred egress redirect dev qi31
      tc filter show dev qd31 ingress | grep -q 49131
      kill -KILL "$BASHPID"
    ' 2>/dev/null
    result=$?
    set -e
    [[ $result == 137 ]]
    echo INSTALLER_KILLED
    for i in {1..35}; do [[ -f "$BASE/rolled-back" ]] && break; sleep 1; done
    [[ -f "$BASE/rolled-back" ]]
    ! inside ip link show dev qi31 >/dev/null 2>&1
    [[ -z $(inside tc filter show dev qd31 ingress) ]]
    echo WATCHDOG_ROLLBACK_PASS
    ;;
  *) echo 'Use run, watchdog, cleanup' >&2; exit 2 ;;
esac
