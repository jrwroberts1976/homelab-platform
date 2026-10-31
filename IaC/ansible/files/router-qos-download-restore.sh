#!/bin/sh
# Roll back only the explicitly owned download QoS trial.
# Not suitable for arbitrary shared clsact configurations.
set -eu
DIR=/var/lib/router-qos-download-trial
IFB=ifb-wan0
test -f "$DIR/armed" || { echo "Download trial ownership marker missing" >&2; exit 1; }
# Do not touch the existing eth1 upload CAKE, PPPoE, DNS, DHCP or firewall.
if /usr/sbin/ip link show dev ppp0 >/dev/null 2>&1; then
  if /usr/sbin/tc qdisc show dev ppp0 | /bin/grep -q 'qdisc clsact'; then
    # Explicitly reject unfamiliar extra ingress filters instead of deleting them.
    /usr/sbin/tc filter show dev ppp0 ingress > "$DIR/filters-before-rollback.txt"
    if ! /bin/grep -q 'pref 49131' "$DIR/filters-before-rollback.txt"; then
      echo "Expected owned ingress filter missing; refuse qdisc removal" >&2
      exit 1
    fi
    /usr/sbin/tc filter del dev ppp0 ingress pref 49131
    # Trial preflight requires no existing clsact; still preserve qdisc if other filters exist.
    if [ -z "$(/usr/sbin/tc filter show dev ppp0 ingress)" ]; then
      /usr/sbin/tc qdisc del dev ppp0 clsact
    else
      echo "Other ingress filters remain; leave clsact in place" >&2
      exit 1
    fi
  fi
fi
if /usr/sbin/ip link show dev "$IFB" >/dev/null 2>&1; then
  /usr/sbin/ip link set dev "$IFB" down
  /usr/sbin/ip link del dev "$IFB" type ifb
fi
/usr/bin/touch "$DIR/rolled-back"
