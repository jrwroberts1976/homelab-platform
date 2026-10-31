#!/bin/sh
# Disposable sensor-01 namespace test. NEVER target production interfaces.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
NS=qos-wd-proof
DUMMY=qos-wd0
IFB=qos-wdifb0
UNIT=homelab-qos-wd-real-proof
MARKER=/run/homelab-qos-wd-real-proof.complete
[ "$(hostname)" = sensor-01 ] || exit 2
[ "$(readlink /proc/self/ns/net)" = "$(readlink /proc/1/ns/net)" ] || exit 2
rollback() {
  if ip netns list | grep -Eq "^$NS( |$)"; then
    ip netns exec "$NS" sh -eu -c '
      tc filter del dev qos-wd0 ingress pref 49131 2>/dev/null || :
      tc qdisc del dev qos-wd0 clsact 2>/dev/null || :
      ip link del dev qos-wdifb0 2>/dev/null || :
      ! ip link show dev qos-wdifb0 >/dev/null 2>&1
      test -z "$(tc filter show dev qos-wd0 ingress)"
      ! tc qdisc show dev qos-wd0 | grep -q "qdisc clsact"
    '
  fi
  touch "$MARKER"
}
case "${1:-}" in
  rollback) rollback ;;
  test)
    test ! -e "$MARKER"
    ! ip netns list | grep -Eq "^$NS( |$)"
    test -z "$(systemctl list-units --all --plain --no-legend "$UNIT*" | grep -v '^$' || true)"
    test -z "$(systemctl list-unit-files --no-legend "$UNIT*" | grep -v '^$' || true)"
    ip netns add "$NS"
    # Namespace created disconnected; never touch physical eth0.
    ip netns exec "$NS" sh -eu -c '
      test "$(ip -o link show | wc -l)" -eq 1
      ip link add dev qos-wd0 type dummy
      ip link set dev qos-wd0 up
    '
    # Arm independent transient systemd timer BEFORE any shaping.
    systemd-run --unit="$UNIT" --on-active=8s --collect -- /bin/sh /run/router-qos-sensor-watchdog-real-proof.sh rollback
    ip netns exec "$NS" sh -eu -c '
      ip link add dev qos-wdifb0 type ifb
      ip link set dev qos-wdifb0 up
      tc qdisc add dev qos-wdifb0 root cake bandwidth 43mbit besteffort flows
      tc qdisc add dev qos-wd0 clsact
      tc filter add dev qos-wd0 ingress pref 49131 matchall action mirred egress redirect dev qos-wdifb0
      tc filter show dev qos-wd0 ingress | grep -q 49131
    '
    # Explicitly kill only the disposable installer child, not the Ansible process.
    set +e
    /bin/sh -c 'kill -KILL "$$"'
    code=$?
    set -e
    [ "$code" -eq 137 ] || exit 1
    echo INSTALLER_SIGKILL_CONFIRMED
    limit=30
    while [ ! -e "$MARKER" ] && [ "$limit" -gt 0 ]; do sleep 1; limit=$((limit-1)); done
    test -e "$MARKER"
    ip netns exec "$NS" sh -eu -c '
      ! ip link show dev qos-wdifb0 >/dev/null 2>&1
      test -z "$(tc filter show dev qos-wd0 ingress)"
      ! tc qdisc show dev qos-wd0 | grep -q "qdisc clsact"
    '
    echo INDEPENDENT_WATCHDOG_ROLLBACK_PASS
    ;;
  cleanup)
    # Ownership limited to the exact reserved namespace and timer name.
    if ip netns list | grep -Eq "^$NS( |$)"; then
      rollback || :
      ip netns exec "$NS" ip link del dev "$DUMMY" 2>/dev/null || :
      ip netns delete "$NS"
    fi
    systemctl stop "$UNIT.timer" 2>/dev/null || :
    rm -f "$MARKER"
    ;;
  *) exit 2 ;;
esac
