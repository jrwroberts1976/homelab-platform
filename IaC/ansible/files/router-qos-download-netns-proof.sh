#!/bin/sh
# Disposable network-namespace QoS compatibility proof only.
# MUST be invoked by unshare --net; never on the host network namespace.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
host_ns="$(readlink /proc/1/ns/net)"
test_ns="$(readlink /proc/self/ns/net)"
[ "$host_ns" != "$test_ns" ] || { echo "REFUSE: running in host network namespace" >&2; exit 2; }
[ -z "$(ip -o link show | grep -v ': lo:' || true)" ] || { echo "REFUSE: namespace not empty" >&2; exit 2; }
echo "Namespace isolation confirmed: $test_ns"
ip link add dev qos-proof0 type dummy
ip link set qos-proof0 up
ip link add dev qos-ifb0 type ifb
ip link set qos-ifb0 up
tc qdisc add dev qos-ifb0 root cake bandwidth 43mbit besteffort flows
tc qdisc add dev qos-proof0 clsact
tc filter add dev qos-proof0 ingress pref 49131 matchall action mirred egress redirect dev qos-ifb0
tc qdisc show dev qos-ifb0 | grep -q 'cake .*bandwidth 43Mbit'
tc filter show dev qos-proof0 ingress | grep -q '49131'
echo "PASS: real IFB/CAKE and ingress redirection installed inside isolated namespace"
tc filter del dev qos-proof0 ingress pref 49131
tc qdisc del dev qos-proof0 clsact
ip link del dev qos-ifb0
test -z "$(tc filter show dev qos-proof0 ingress)"
! ip link show dev qos-ifb0 >/dev/null 2>&1
echo "PASS: real tc/IFB cleanup complete"
# Deleting the dummy is bounded to the namespace. Namespace also disappears on exit.
ip link del dev qos-proof0
