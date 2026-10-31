#!/bin/sh
# Phase 3 candidate only: not deployed. PPP ip-up.d/ip-down.d adapter.
# pppd runs hooks with interface name as $1 and passes phase via separate symlink/wrapper.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
[ "${1:-}" = "ppp0" ] || exit 0
case "${ROUTER_QOS_PPP_EVENT:-}" in
  up|down) ;;
  *) echo "Missing supported PPP event" >&2; exit 2 ;;
esac
# Deliberately no tc, systemctl start or interface manipulation in the hook.
# Phase 3 still requires an independent serialized, failure-safe reconciler.
logger -t router-qos-download "Uninstalled candidate received PPP ${ROUTER_QOS_PPP_EVENT} event for $1"
