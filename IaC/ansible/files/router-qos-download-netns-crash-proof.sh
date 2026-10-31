#!/bin/sh
# TEST ONLY. Disposable namespace, independent parent cleanup after SIGKILL.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
[ "$(readlink /proc/self/ns/net)" != "$(readlink /proc/1/ns/net)" ] || { echo "REFUSE host namespace" >&2; exit 2; }
[ -z "$(ip -o link show | grep -v ': lo:' || true)" ] || { echo "REFUSE nonempty namespace" >&2; exit 2; }
ip link add dev qos-crash0 type dummy
ip link set qos-crash0 up
cleanup() {
  tc filter del dev qos-crash0 ingress pref 49131 2>/dev/null || :
  tc qdisc del dev qos-crash0 clsact 2>/dev/null || :
  ip link del dev qos-ifbc0 2>/dev/null || :
}
trap 'cleanup; ip link del dev qos-crash0 2>/dev/null || :' EXIT
for phase in ifb redirect; do
  echo "Injecting SIGKILL after $phase"
  set +e
  /bin/sh -c '
    set -eu
    ip link add dev qos-ifbc0 type ifb
    ip link set qos-ifbc0 up
    tc qdisc add dev qos-ifbc0 root cake bandwidth 43mbit besteffort flows
    if [ "$1" = redirect ]; then
      tc qdisc add dev qos-crash0 clsact
      tc filter add dev qos-crash0 ingress pref 49131 matchall action mirred egress redirect dev qos-ifbc0
    fi
    kill -KILL "$$"
  ' sh "$phase"
  status=$?
  set -e
  [ "$status" -eq 137 ] || { echo "Unexpected child exit $status" >&2; exit 1; }
  ip link show dev qos-ifbc0 >/dev/null
  if [ "$phase" = redirect ]; then
    tc filter show dev qos-crash0 ingress | grep -q '49131'
  fi
  # Parent is independent process, and removes resources after child was killed.
  cleanup
  ! ip link show dev qos-ifbc0 >/dev/null 2>&1
  [ -z "$(tc filter show dev qos-crash0 ingress)" ]
  ! tc qdisc show dev qos-crash0 | grep -q 'qdisc clsact'
  echo "PASS: independent cleanup after SIGKILL at $phase"
done
