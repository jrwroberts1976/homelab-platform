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
  # No standalone destructive teardown until the owner record and kernel
  # interface token are verified by an approved cutover transaction.
  # A matching CAKE rate and ingress redirect are not proof of ownership.
  echo "REFUSE: standalone removal disabled; use verified cutover transaction" >&2
  return 2
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
      # Reconnect: reuse only a recorded, kernel-verified IFB. Never delete it.
      # A failed attach removes only the clsact/filter created by this attempt.
      STAMP_HELPER=/usr/local/libexec/router-qos-download/stamp.py
      [[ -f "$STAMP_HELPER" && ! -L "$STAMP_HELPER" ]] ||
        { echo "REFUSE: ownership verifier missing"; exit 2; }
      python3 "$STAMP_HELPER" verify-reattach ||
        { echo "REFUSE: orphan IFB ownership unverified"; exit 2; }
      reconnect_filter=0
      reconnect_clsact=0
      reconnect_rollback() {
        local rc=$?
        trap - ERR
        if (( reconnect_filter )); then
          tc filter del dev "$WAN" ingress pref "$PREF" || true
        fi
        if (( reconnect_clsact )) && [[ -z "$(filters)" ]]; then
          tc qdisc del dev "$WAN" clsact || true
        fi
        return "$rc"
      }
      trap 'reconnect_rollback' ERR
      tc qdisc add dev "$WAN" clsact
      reconnect_clsact=1
      tc filter add dev "$WAN" ingress pref "$PREF" matchall action mirred egress redirect dev "$IFB"
      reconnect_filter=1
      owned || { echo "REFUSE: reconnect verification failed"; false; }
      trap - ERR
      echo "PASS: verified IFB reattached after PPP reconnect"
      exit 0
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
        if clean_wan; then
          if ip link del "$IFB"; then
            # Release only our stamp, and only after independently proving
            # that the IFB is gone. Never erase metadata for a live IFB.
            python3 "$STAMP_HELPER" release-after-delete ||
              echo "WARN: ownership record retained; manual review required" >&2
          fi
        fi
      fi
      return "$original_rc"
    }
    # Refuse to mutate network state if the approved stamp helper is absent.
    STAMP_HELPER=/usr/local/libexec/router-qos-download/stamp.py
    [[ -f "$STAMP_HELPER" && ! -L "$STAMP_HELPER" ]] ||
      { echo "REFUSE: ownership stamp helper missing"; exit 2; }
    [[ ! -e /run/router-qos-download-basic.owner.json &&
       ! -L /run/router-qos-download-basic.owner.json ]] ||
      { echo "REFUSE: existing ownership record requires reconciliation"; exit 2; }
    modprobe ifb
    trap 'install_rollback' ERR
    ip link add "$IFB" type ifb
    made_ifb=1
    python3 "$STAMP_HELPER" stamp
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
