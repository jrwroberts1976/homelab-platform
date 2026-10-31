#!/usr/bin/env bash
# Basic PPPoE download CAKE. Idempotent and fail-closed on foreign tc state.
# Only ppp0 ingress and ifbqosdl0; NEVER changes eth1 upload qdisc.
set -euo pipefail
[[ "$(hostname -s)" == "raspberrypi" && $EUID -eq 0 ]] || exit 2
WAN=ppp0
IFB=ifbqosdl0
PREF=49132
exec 9>/run/lock/router-qos-download-basic.lock
flock -x 9

has_ifb() { ip link show dev "$IFB" >/dev/null 2>&1; }
has_wan() { ip link show dev "$WAN" >/dev/null 2>&1; }
upload_ok() { tc qdisc show dev eth1 | grep -q 'cake.*13Mbit'; }
filters() { tc filter show dev "$WAN" ingress; }
owned() {
  has_ifb && has_wan &&
    tc qdisc show dev "$IFB" | grep -q 'cake.*43Mbit' &&
    tc qdisc show dev "$WAN" | grep -q 'clsact' &&
    filters | grep -q 'pref 49132' &&
    filters | grep -q 'Redirect to device ifbqosdl0'
}
clean_wan() {
  has_wan || return 1
  [[ -z "$(filters)" ]] && ! tc qdisc show dev "$WAN" | grep -Eq 'clsact|ingress'
}
remove_owned() {
  if has_wan && tc qdisc show dev "$WAN" | grep -q 'clsact'; then
    local listing
    listing="$(filters)"
    if [[ -n "$listing" ]]; then
      [[ "$listing" == *"pref 49132"* && "$listing" == *"Redirect to device ifbqosdl0"* ]] ||
        { echo "REFUSE: foreign ingress filter"; return 2; }
      # Require exactly one owned filter (displayed twice in tc summary).
      [[ "$(grep -c 'action order' <<< "$listing")" == 1 ]] ||
        { echo "REFUSE: multiple ingress filters"; return 2; }
      tc filter del dev "$WAN" ingress pref "$PREF"
      [[ -z "$(filters)" ]] || { echo "REFUSE: remaining filters"; return 2; }
    fi
    tc qdisc del dev "$WAN" clsact
  elif has_wan && [[ -n "$(filters)" ]]; then
    echo "REFUSE: unexpected ingress state"; return 2
  fi
  if has_ifb; then
    tc qdisc show dev "$IFB" | grep -q 'cake.*43Mbit' ||
      { echo "REFUSE: foreign IFB"; return 2; }
    ip link del "$IFB"
  fi
}
case "${1:-}" in
  preflight)
    has_wan && clean_wan && ! has_ifb && upload_ok ||
      { echo "REFUSE: preflight state"; exit 2; }
    echo "PASS: ready for download QoS"
    ;;
  ensure|apply)
    has_wan || { echo "SKIP: PPP interface absent"; exit 0; }
    upload_ok || { echo "REFUSE: upload CAKE changed"; exit 2; }
    if owned; then echo "PASS: already active"; exit 0; fi
    if has_ifb || ! clean_wan; then
      echo "REFUSE: unexpected or partial download QoS state"; exit 2
    fi
    modprobe ifb
    ip link add "$IFB" type ifb
    trap 'remove_owned || true' ERR
    ip link set "$IFB" up
    tc qdisc add dev "$IFB" root cake bandwidth 43mbit besteffort flows
    tc qdisc add dev "$WAN" clsact
    tc filter add dev "$WAN" ingress pref "$PREF" matchall action mirred egress redirect dev "$IFB"
    owned || { echo "REFUSE: verification failed"; exit 2; }
    trap - ERR
    echo "PASS: 43 Mbps download CAKE active"
    ;;
  remove)
    remove_owned
    echo "PASS: basic download QoS removed"
    ;;
  status)
    tc qdisc show dev eth1
    if has_wan; then tc qdisc show dev "$WAN"; filters; fi
    ip -br link show dev "$IFB" || true
    if has_ifb; then tc qdisc show dev "$IFB"; fi
    ;;
  *) echo "usage: $0 preflight|ensure|apply|remove|status"; exit 2 ;;
esac
