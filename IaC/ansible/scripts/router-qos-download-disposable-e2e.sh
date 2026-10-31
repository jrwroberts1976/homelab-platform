#!/usr/bin/env bash
# Disposable namespace IFB/CAKE functional exercise; NEVER use on router-01.
# No SIGKILL; no host interface, route, nftables, PPP, or systemd changes.
set -Eeuo pipefail
[[ "$(hostname -s)" == "sensor-01" ]] || { echo "REFUSE: sensor-01 only" >&2; exit 2; }
[[ "${EUID}" -eq 0 ]] || { echo "REFUSE: root required" >&2; exit 2; }
for cmd in ip tc flock; do command -v "$cmd" >/dev/null || { echo "Missing $cmd" >&2; exit 2; }; done
ns="qos-p5-e2e"
src="qe2src"
ifb="qe2ifb"
lock="/run/lock/qos-p5-e2e.lock"
exec 9>"$lock"
flock -n 9 || { echo "REFUSE: another test owns lock" >&2; exit 2; }
if ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
  echo "REFUSE: test namespace already exists; will not touch foreign resources" >&2
  exit 2
fi
created=0
cleanup() {
  result=$?
  trap - EXIT ERR INT TERM
  if (( created )); then
    ip netns del "$ns" || { echo "WARNING: namespace cleanup failed: $ns" >&2; exit 3; }
  fi
  exit "$result"
}
trap cleanup EXIT
ip netns add "$ns"
created=1
ip -n "$ns" link add "$src" type dummy
ip -n "$ns" link set "$src" up
ip netns exec "$ns" ip link add "$ifb" type ifb
ip netns exec "$ns" ip link set "$ifb" up
ip netns exec "$ns" tc qdisc add dev "$ifb" root cake bandwidth 43mbit besteffort flows
ip netns exec "$ns" tc qdisc add dev "$src" clsact
ip netns exec "$ns" tc filter add dev "$src" ingress pref 49131 matchall action mirred egress redirect dev "$ifb"
echo "=== INSTALLED ==="
ip netns exec "$ns" tc -s qdisc show dev "$ifb"
ip netns exec "$ns" tc filter show dev "$src" ingress
ip netns exec "$ns" tc qdisc show dev "$src" | grep -q 'clsact'
ip netns exec "$ns" tc qdisc show dev "$ifb" | grep -q 'cake'
ip netns exec "$ns" tc filter show dev "$src" ingress | grep -q 'mirred'
ip netns exec "$ns" tc filter del dev "$src" ingress pref 49131
ip netns exec "$ns" tc qdisc del dev "$src" clsact
ip netns exec "$ns" ip link del dev "$ifb"
echo "=== REMOVED ==="
if ip netns exec "$ns" ip link show dev "$ifb" >/dev/null 2>&1; then
  echo "FAIL: IFB still present" >&2; exit 1
fi
if ip netns exec "$ns" tc qdisc show dev "$src" | grep -Eq 'clsact|ingress'; then
  echo "FAIL: ingress qdisc remains" >&2; exit 1
fi
if [[ -n "$(ip netns exec "$ns" tc filter show dev "$src" ingress)" ]]; then
  echo "FAIL: ingress filter remains" >&2; exit 1
fi
echo "PASS: disposable namespace IFB/CAKE install and teardown"
