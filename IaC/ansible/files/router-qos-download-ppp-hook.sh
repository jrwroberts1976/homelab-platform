#!/bin/sh
# Phase 3 staged PPP event adapter. NOT installed or deployed.
# Invoked from a future ip-up.d or ip-down.d wrapper with PPP interface in $1.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
[ "${1:-}" = "ppp0" ] || exit 0
case "${ROUTER_QOS_PPP_EVENT:-}" in
  up|down) ;;
  *) echo "Missing supported PPP event" >&2; exit 2 ;;
esac
# Event hook intentionally never mutates the network directly.
# Safe test override restricted to an explicit harmless fixture.
if [ "${ROUTER_QOS_TEST_MODE:-}" = 1 ]; then
  case "${ROUTER_QOS_TEST_LOG:-}" in
    /tmp/router-qos-ppp-hook-proof.*)
      printf '%s %s\n' "$ROUTER_QOS_PPP_EVENT" "$1" >> "$ROUTER_QOS_TEST_LOG"
      exit 0
      ;;
    *) echo "Unsafe test log destination" >&2; exit 2 ;;
  esac
fi
# No reconciler is wired in yet. It would be unsafe to pretend this deploys CAKE.
logger -t router-qos-download "Uninstalled candidate observed PPP ${ROUTER_QOS_PPP_EVENT} for $1"
