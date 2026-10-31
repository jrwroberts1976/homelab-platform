#!/bin/sh
# Phase 2 candidate: staged only. NOT approved for live deployment.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
STATE=/run/router-qos-download-managed
IFB=ifb-wan0
PPP=ppp0
PREF=49131
case "${1:-}" in
  check)
    test -e /sys/class/net/$PPP/ifindex
    test "$(systemctl is-active router-qos-upload.service)" = active
    tc qdisc show dev eth1 | grep -q 'cake .*bandwidth 13Mbit .*ptm overhead 30'
    ip -4 route show default | grep -q '^default dev ppp0'
    ;;
  start)
    test -e /sys/class/net/$PPP/ifindex || { echo "PPP interface absent" >&2; exit 1; }
    # Never adopt trial leftovers or another subsystem's resources.
    test ! -e /var/lib/router-qos-download-trial/armed || {
      test -e /var/lib/router-qos-download-trial/rolled-back || exit 1
    }
    test ! -e "$STATE" || { echo "Existing managed state; refuse start" >&2; exit 1; }
    test -z "$(ip -br link show type ifb)"
    test -z "$(tc filter show dev "$PPP" ingress)"
    test -z "$(tc qdisc show dev "$PPP" | grep -E 'qdisc (clsact|ingress)' || true)"
    "$0" check
    mkdir -m 0700 "$STATE"
    cat /sys/class/net/$PPP/ifindex > "$STATE/ifindex"
    chmod 0600 "$STATE/ifindex"
    # Ownership flags are written immediately after each change for partial-failure recovery.
    ip link add dev "$IFB" type ifb
    touch "$STATE/ifb-owned"
    ip link set dev "$IFB" up
    tc qdisc replace dev "$IFB" root cake bandwidth 43mbit besteffort flows
    tc qdisc add dev "$PPP" clsact
    touch "$STATE/clsact-owned"
    tc filter add dev "$PPP" ingress pref "$PREF" matchall action mirred egress redirect dev "$IFB"
    touch "$STATE/filter-owned"
    ;;
  stop)
    test -d "$STATE" || exit 0
    # A reconnect creates a new PPP identity. Never delete its foreign qdisc.
    if test -f "$STATE/ifindex" && test -e /sys/class/net/$PPP/ifindex &&
       test "$(cat /sys/class/net/$PPP/ifindex)" = "$(cat "$STATE/ifindex")"; then
      if test -f "$STATE/clsact-owned"; then
        # Refuse to remove a shared ingress qdisc if unexpected filters exist.
        filters="$(tc filter show dev "$PPP" ingress)"
        foreign="$(printf '%s\n' "$filters" | grep '^filter ' | grep -v "pref $PREF" || true)"
        test -z "$foreign" || { echo "Foreign ingress filter; refusing teardown" >&2; exit 1; }
        if test -f "$STATE/filter-owned"; then
          printf '%s\n' "$filters" | grep -q "pref $PREF" &&
            tc filter del dev "$PPP" ingress pref "$PREF" || true
        fi
        test -z "$(tc filter show dev "$PPP" ingress)" || exit 1
        tc qdisc del dev "$PPP" clsact
      fi
    fi
    if test -f "$STATE/ifb-owned" && ip link show dev "$IFB" >/dev/null 2>&1; then
      ip link set dev "$IFB" down
      ip link del dev "$IFB" type ifb
    fi
    rm -f "$STATE/ifindex" "$STATE/ifb-owned" "$STATE/clsact-owned" "$STATE/filter-owned"
    rmdir "$STATE"
    ;;
  *)
    echo "Usage: $0 {check|start|stop}" >&2
    exit 2
    ;;
esac
