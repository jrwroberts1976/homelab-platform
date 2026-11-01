#!/usr/bin/env bash
# Prepare a separate download IFB; does not redirect traffic or touch legacy IFB.
# Deliberately NOT an enabled service, hook, or live cutover program.
set -euo pipefail
[[ "${1:-}" == preflight ]] || { echo "REFUSE: only read-only preflight is available" >&2; exit 2; }
[[ $EUID -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2
exec 9>/run/lock/router-qos-download-basic.lock
flock -x 9
if ip link show dev ifbqosdl1 >/dev/null 2>&1; then
  echo "REFUSE: candidate IFB already exists" >&2; exit 2
fi
if ! ip link show dev ifbqosdl0 >/dev/null 2>&1; then
  echo "REFUSE: legacy IFB missing" >&2; exit 2
fi
if ! tc qdisc show dev ifbqosdl0 | grep -q 'cake.*43Mbit'; then
  echo "REFUSE: legacy download CAKE changed" >&2; exit 2
fi
if ! tc filter show dev ppp0 ingress | grep -q 'Redirect to device ifbqosdl0'; then
  echo "REFUSE: legacy redirect changed" >&2; exit 2
fi
if ! tc qdisc show dev eth1 | grep -q 'cake.*13Mbit.*ptm overhead 30'; then
  echo "REFUSE: upload CAKE changed" >&2; exit 2
fi
echo "PASS: candidate slot absent and legacy QoS present; no changes made"
echo "HOLD: creation, stamping, redirect switch and kernel rollback are not authorised"
