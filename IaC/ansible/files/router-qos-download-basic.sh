#!/usr/bin/env bash
# Minimal, reversible download QoS on router-01; leave eth1 upload CAKE intact.
set -euo pipefail
[[ "$(hostname -s)" == "raspberrypi" ]] || { echo "REFUSE: wrong host"; exit 2; }
[[ $EUID -eq 0 ]] || { echo "REFUSE: root needed"; exit 2; }
WAN=ppp0
IFB=ifbqosdl0
PREF=49132
cmd="${1:-}"
case "$cmd" in
  preflight)
    ip link show dev "$WAN" >/dev/null
    test -z "$(tc filter show dev "$WAN" ingress)"
    ! tc qdisc show dev "$WAN" | grep -Eq 'clsact|ingress'
    ! ip link show dev "$IFB" >/dev/null 2>&1
    tc qdisc show dev eth1 | grep -q 'cake.*13Mbit'
    echo 'PASS: ready for minimal download QoS'
    ;;
  apply)
    "$0" preflight
    modprobe ifb
    ip link add "$IFB" type ifb
    trap 'tc qdisc del dev "$WAN" clsact 2>/dev/null || true; ip link del "$IFB" 2>/dev/null || true' ERR
    ip link set "$IFB" up
    tc qdisc add dev "$IFB" root cake bandwidth 43mbit besteffort flows
    tc qdisc add dev "$WAN" clsact
    tc filter add dev "$WAN" ingress pref "$PREF" matchall action mirred egress redirect dev "$IFB"
    tc qdisc show dev "$IFB" | grep -q 'cake.*43Mbit'
    tc filter show dev "$WAN" ingress | grep -q "$IFB"
    trap - ERR
    echo 'PASS: 43 Mbps download CAKE active'
    ;;
  remove)
    # Never delete a foreign qdisc or IFB. Only cleanup matching rule.
    if tc filter show dev "$WAN" ingress 2>/dev/null | grep -q "pref $PREF"; then
      if ! tc filter show dev "$WAN" ingress | grep -q "$IFB"; then
        echo 'REFUSE: filter not ours'; exit 2
      fi
      tc filter del dev "$WAN" ingress pref "$PREF"
      if test -z "$(tc filter show dev "$WAN" ingress)"; then
        tc qdisc del dev "$WAN" clsact
      fi
    fi
    if ip link show dev "$IFB" >/dev/null 2>&1; then
      tc qdisc show dev "$IFB" | grep -q 'cake.*43Mbit' || { echo 'REFUSE: IFB not ours'; exit 2; }
      ip link del "$IFB"
    fi
    echo 'PASS: basic download QoS removed'
    ;;
  status)
    tc qdisc show dev eth1
    tc qdisc show dev "$WAN"
    tc filter show dev "$WAN" ingress
    ip -br link show dev "$IFB" || true
    tc qdisc show dev "$IFB" || true
    ;;
  *) echo "usage: $0 preflight|apply|remove|status"; exit 2 ;;
esac
