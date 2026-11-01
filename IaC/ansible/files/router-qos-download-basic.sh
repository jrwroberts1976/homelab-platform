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
  # Manual removal must never infer ownership from IFB name or CAKE rate.
  # Reuse the complete active-path fingerprint and refuse partial/orphaned
  # state. A future recovery actuator must use authenticated ownership data.
  owned || { echo "REFUSE: complete live QoS ownership not verified"; return 2; }
  local listing
  listing="$(filters)"
  [[ "$(grep -c 'action order' <<< "$listing")" == 1 ]] ||
    { echo "REFUSE: multiple ingress filters"; return 2; }
  tc filter del dev "$WAN" ingress pref "$PREF"
  [[ -z "$(filters)" ]] || { echo "REFUSE: remaining filters"; return 2; }
  tc qdisc del dev "$WAN" clsact
  ip link del "$IFB"
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
    # After a PPP reconnect the old ppp0 disappears, but its IFB may remain.
    # Refuse orphan cleanup until authoritative ownership recovery is implemented.
    if has_ifb && clean_wan; then
      echo "REFUSE: orphan IFB ownership unverified; manual recovery required"
      exit 2
    fi
    if has_ifb || ! clean_wan; then
      echo "REFUSE: unexpected or partial download QoS state"; exit 2
    fi
    # Track only resources created by THIS attempt. Never invoke the general
    # remove operation from an installation-failure trap.
    made_ifb=0
    made_clsact=0
    made_filter=0
    install_rollback() {
      local original_rc=$?
      trap - ERR
      if (( made_filter )); then
        tc filter del dev "$WAN" ingress pref "$PREF" || true
      fi
      if (( made_clsact )); then
        # Refuse to remove a clsact that has acquired any unexpected filter.
        if [[ -z "$(filters)" ]]; then
          tc qdisc del dev "$WAN" clsact || true
        fi
      fi
      if (( made_ifb )); then
        # Keep the IFB if it has become associated with unexpected ingress.
        if clean_wan; then ip link del "$IFB" || true; fi
      fi
      return "$original_rc"
    }
    modprobe ifb
    trap 'install_rollback' ERR
    ip link add "$IFB" type ifb
    made_ifb=1
    ip link set "$IFB" up
    tc qdisc add dev "$IFB" root cake bandwidth 43mbit besteffort flows
    tc qdisc add dev "$WAN" clsact
    made_clsact=1
    tc filter add dev "$WAN" ingress pref "$PREF" matchall action mirred egress redirect dev "$IFB"
    made_filter=1
    owned || { echo "REFUSE: verification failed"; false; }
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
