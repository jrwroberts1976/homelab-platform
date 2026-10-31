#!/bin/sh
# Guarded recovery of only the download IFB trial objects. Safe if PPPoE has disconnected.
set -eu
IFB=ifb-wan0
TAG=49131
# The trial owns the whole clsact qdisc only after proving ingress was empty.
if /usr/sbin/ip link show dev ppp0 >/dev/null 2>&1; then
  if /usr/sbin/tc qdisc show dev ppp0 | /bin/grep -q 'qdisc clsact'; then
    /usr/sbin/tc qdisc del dev ppp0 clsact
  fi
fi
if /usr/sbin/ip link show dev "$IFB" >/dev/null 2>&1; then
  /usr/sbin/ip link set dev "$IFB" down
  /usr/sbin/ip link del dev "$IFB" type ifb
fi
/bin/mkdir -p /var/lib/router-qos-download-trial
/usr/bin/touch /var/lib/router-qos-download-trial/rolled-back
