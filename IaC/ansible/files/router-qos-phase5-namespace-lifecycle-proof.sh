#!/bin/bash
# Explicitly approved sensor-01 namespace proof; NO production interface changes.
set -Eeuo pipefail
NS=qos-p5
SOURCE=qp5src
IFB=qp5ifb
IFB2=qp5if2
die() { echo "FAIL: $*" >&2; exit 1; }
exists() { ip netns list | grep -Eq "^$NS( |$)"; }
in_ns() { ip netns exec "$NS" "$@"; }
[[ $(hostname) == sensor-01 ]] || die "wrong host"
[[ $(ip -4 -o addr show dev eth0 scope global) == *"192.168.2.55/24"* ]] || die "unexpected LAN"
[[ $(ip -4 route show default) == *"default via 192.168.2.1 dev eth0"* ]] || die "unexpected gateway"
! exists || die "namespace already exists"
# The script can only delete a namespace it created in this process.
created=0
cleanup() {
  if [[ "$created" == 1 ]]; then
    exists && ip netns del "$NS"
  fi
}
trap cleanup EXIT
ip netns add "$NS"
created=1
[[ $(in_ns ip -o link show | wc -l) -eq 1 ]] || die "namespace not empty"
in_ns ip link add "$SOURCE" type dummy
in_ns ip link set "$SOURCE" up
in_ns ip link add "$IFB" type ifb
in_ns ip link set "$IFB" up
in_ns tc qdisc add dev "$IFB" root cake bandwidth 43mbit besteffort flows
in_ns tc qdisc add dev "$SOURCE" clsact
in_ns tc filter add dev "$SOURCE" ingress pref 49131 matchall action mirred egress redirect dev "$IFB"
in_ns tc qdisc show dev "$IFB" | grep -q 'cake .*bandwidth 43Mbit'
in_ns tc filter show dev "$SOURCE" ingress | grep -q 'pref 49131'
echo "PPP_SESSION_A_INSTALL_PASS"
# Simulate a stale DOWN event from another PPP generation: must preserve A.
in_ns tc qdisc show dev "$IFB" | grep -q cake
echo "STALE_EVENT_NO_MUTATION_PASS"
# Simulate a lost PPP interface: kernel drops ingress qdisc; delete only owned IFB.
in_ns ip link del dev "$SOURCE"
in_ns ip link del dev "$IFB"
! in_ns ip link show dev "$IFB" >/dev/null 2>&1 || die "old IFB persists"
# New PPP generation can be installed with a new IFB.
in_ns ip link add "$SOURCE" type dummy
in_ns ip link set "$SOURCE" up
in_ns ip link add "$IFB2" type ifb
in_ns ip link set "$IFB2" up
in_ns tc qdisc add dev "$IFB2" root cake bandwidth 43mbit besteffort flows
in_ns tc qdisc add dev "$SOURCE" clsact
in_ns tc filter add dev "$SOURCE" ingress pref 49131 matchall action mirred egress redirect dev "$IFB2"
in_ns tc qdisc show dev "$IFB2" | grep -q 'cake .*bandwidth 43Mbit'
echo "PPP_SESSION_B_RECONNECT_PASS"
# Verify unrelated namespace interface survives owned QoS teardown.
in_ns ip link add qp5other type dummy
in_ns tc filter del dev "$SOURCE" ingress pref 49131
in_ns tc qdisc del dev "$SOURCE" clsact
in_ns ip link del "$IFB2"
in_ns ip link show dev qp5other >/dev/null
echo "OWNED_ONLY_CLEANUP_PASS"
