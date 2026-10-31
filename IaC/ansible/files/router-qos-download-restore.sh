#!/bin/sh
# Roll back only the explicitly owned download QoS trial.
# Not suitable for arbitrary shared clsact configurations.
set -eu
DIR=/var/lib/router-qos-download-trial
IFB=ifb-wan0
test -f "$DIR/armed" || { echo "Download trial ownership marker missing" >&2; exit 1; }
# Do not touch the existing eth1 upload CAKE, PPPoE, DNS, DHCP or firewall.
# Never remove filters from a replacement PPP interface after a reconnect.
if [ -e /sys/class/net/ppp0/ifindex ]; then
  test -f "$DIR/ppp-ifindex" || { echo "Missing recorded PPP interface identity" >&2; exit 1; }
  current_id=$(/bin/cat /sys/class/net/ppp0/ifindex)
  original_id=$(/bin/cat "$DIR/ppp-ifindex")
  if [ "$current_id" != "$original_id" ]; then
    echo "ppp0 interface identity changed; leave replacement untouched" >&2
    if /usr/sbin/ip link show dev "$IFB" >/dev/null 2>&1; then
      /usr/sbin/ip link set dev "$IFB" down
      /usr/sbin/ip link del dev "$IFB" type ifb
    fi
    /usr/bin/touch "$DIR/rolled-back"
    exit 0
  fi
fi
if /usr/sbin/ip link show dev ppp0 >/dev/null 2>&1; then
  if /usr/sbin/tc qdisc show dev ppp0 | /bin/grep -q 'qdisc clsact'; then
    # Explicitly reject unfamiliar extra ingress filters instead of deleting them.
    /usr/sbin/tc filter show dev ppp0 ingress > "$DIR/filters-before-rollback.txt"
    # Also handle the partial-activation case: clsact added, redirect not yet attached.
    # Reject foreign filters BEFORE deleting any trial-owned filter.
    # A trial must never remove a shared clsact qdisc.
    if /bin/grep '^filter ' "$DIR/filters-before-rollback.txt" | /bin/grep -qv 'pref 49131'; then
      echo "Foreign ingress filter found; refuse cleanup" >&2
      exit 1
    fi
    if /bin/grep -q 'pref 49131' "$DIR/filters-before-rollback.txt"; then
      /usr/sbin/tc filter del dev ppp0 ingress pref 49131
    fi
    if [ -n "$(/usr/sbin/tc filter show dev ppp0 ingress)" ]; then
      echo "Ingress filters remain; preserve clsact" >&2
      exit 1
    fi
    /usr/sbin/tc qdisc del dev ppp0 clsact
  fi
fi
if /usr/sbin/ip link show dev "$IFB" >/dev/null 2>&1; then
  /usr/sbin/ip link set dev "$IFB" down
  /usr/sbin/ip link del dev "$IFB" type ifb
fi
/usr/bin/touch "$DIR/rolled-back"
