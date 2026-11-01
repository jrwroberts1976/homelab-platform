#!/usr/bin/env bash
# Create-only emergency download QoS recovery for an entirely missing IFB.
# NOT a cutover utility. Never deletes, adopts, or modifies an existing IFB.
# Requires independent approval and remains undeployed until isolation tests.
set -euo pipefail
[[ ${EUID} -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2
[[ "${1:-}" == restore-missing ]] || { echo "REFUSE: command" >&2; exit 2; }
APPROVAL=/run/router-qos-download-kernel-recovery.approved
[[ -f "$APPROVAL" && ! -L "$APPROVAL" ]] ||
  { echo "REFUSE: explicit kernel recovery approval absent" >&2; exit 2; }
exec 9>/run/lock/router-qos-download-basic.lock
flock -x 9
refuse() { echo "REFUSE: $*" >&2; exit 2; }
WAN=ppp0
IFB=ifbqosdl0
ip link show dev "$WAN" >/dev/null 2>&1 || refuse "PPP absent"
if ip link show dev "$IFB" >/dev/null 2>&1; then
  refuse "IFB already exists (never adopt or replace)"
fi
[[ ! -e /run/router-qos-download-basic.owner.json &&
   ! -L /run/router-qos-download-basic.owner.json ]] ||
  refuse "owner record exists"
tc qdisc show dev eth1 | grep -q 'cake.*13Mbit.*ptm overhead 30' ||
  refuse "upload baseline changed"
[[ -z "$(tc filter show dev "$WAN" ingress)" ]] ||
  refuse "PPP ingress not empty"
! tc qdisc show dev "$WAN" | grep -Eq 'clsact|ingress' ||
  refuse "PPP ingress qdisc already exists"
# Write a no-clobber, root-only progress journal before any kernel mutation.
# An interrupted run must never silently re-enter with uncertain state.
JOURNAL=/run/router-qos-download-kernel-recovery.progress
[[ ! -e "$JOURNAL" && ! -L "$JOURNAL" ]] ||
  refuse "existing recovery progress journal requires investigation"
umask 077
if ! ( set -C; printf '%s\n' "started boot=$(cat /proc/sys/kernel/random/boot_id)" > "$JOURNAL" ); then
  refuse "cannot create exclusive recovery progress journal"
fi
stage() { printf '%s\n' "$1" >> "$JOURNAL"; }
# Only create after all read-only guards. Failure is deliberately fail-stop:
# do NOT delete ambiguous partial state; the operator must inspect it.
stage "before modprobe"
modprobe ifb
stage "before IFB create"
ip link add "$IFB" type ifb
stage "IFB create returned success"
ip link set "$IFB" up
stage "IFB up returned success"
tc qdisc add dev "$IFB" root cake bandwidth 43mbit besteffort flows
stage "CAKE install returned success"
tc qdisc add dev "$WAN" clsact
stage "clsact install returned success"
tc filter add dev "$WAN" ingress pref 49132 matchall action mirred egress redirect dev "$IFB"
tc qdisc show dev "$IFB" | grep -q 'cake.*43Mbit' ||
  refuse "download qdisc verification failed"
tc filter show dev "$WAN" ingress | grep -q 'Redirect to device ifbqosdl0' ||
  refuse "redirect verification failed"
stage "redirect verification completed"
echo "PASS: create-only 43Mbit download recovery applied; no ownership claimed"
echo "WARNING: progress journal retained for explicit reconciliation; not proof of reconnect/reboot persistence"
