#!/usr/bin/env bash
# Recovery prototype for an ABSENT legacy download IFB; not an activation script.
# Does not remove or replace any kernel resource. Never touches WAN PPP, eth1,
# DHCP, routing or firewall. Requires a clean ppp0 ingress and missing IFB.
# Must not run until separately integrated into an approved cutover transaction.
set -euo pipefail
[[ ${EUID} -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2
WAN=ppp0
IFB=ifbqosdl0
LOCK=/run/lock/router-qos-download-basic.lock
exec 9>"$LOCK"
flock -x 9
refuse() { echo "REFUSE: $*" >&2; exit 2; }
[[ "${1:-}" == verify ]] || refuse "verification only; no live recovery mode"
ip link show dev "$WAN" >/dev/null || refuse "ppp0 absent"
ip link show dev "$IFB" >/dev/null 2>&1 && refuse "IFB exists: never adopt"
tc qdisc show dev eth1 | grep -q 'cake.*13Mbit.*ptm overhead 30' ||
  refuse "upload baseline changed"
[[ -z "$(tc filter show dev "$WAN" ingress)" ]] ||
  refuse "WAN ingress filters not empty"
! tc qdisc show dev "$WAN" | grep -Eq 'clsact|ingress' ||
  refuse "WAN ingress qdisc exists"
[[ ! -e /run/router-qos-download-basic.owner.json &&
   ! -L /run/router-qos-download-basic.owner.json ]] ||
  refuse "existing ownership record"
echo "PASS: prerequisites for a create-only recovery candidate are met"
echo "NOTE: this verify-only script does not restore kernel QoS"
