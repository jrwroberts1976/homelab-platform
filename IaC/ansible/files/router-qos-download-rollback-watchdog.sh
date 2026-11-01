#!/usr/bin/env bash
# Router download QoS cutover rollback watchdog. Restores entrypoint files ONLY.
# Deliberately never invokes ip/tc, stops PPP, removes IFB or changes firewall.
set -euo pipefail
[[ $EUID -eq 0 && "$(hostname -s)" == raspberrypi ]] || exit 2
ROOT=/var/lib/router-qos-download-cutover
ACTIVE_CTRL=/usr/local/sbin/router-qos-download-basic
ACTIVE_HOOK=/etc/ppp/ip-up.d/router-qos-download
OLD_CTRL=16f7db14bf5962360e7c684e374c7d676240f78ea1351effc66472031f0486a7
OLD_HOOK=25b96d3504f226a789cc959772a995e51e2867ecc797c3e218c3b6d89b75df8b
LOCK=/run/lock/router-qos-download-basic.lock
command -v sha256sum >/dev/null
check() {
  [[ -f "$ROOT/legacy-controller" && ! -L "$ROOT/legacy-controller" &&
     -f "$ROOT/legacy-ip-up-hook" && ! -L "$ROOT/legacy-ip-up-hook" ]] || return 2
  [[ "$(sha256sum "$ROOT/legacy-controller" | cut -d' ' -f1)" == "$OLD_CTRL" &&
     "$(sha256sum "$ROOT/legacy-ip-up-hook" | cut -d' ' -f1)" == "$OLD_HOOK" ]] || return 2
}
restore() {
  check || { echo "REFUSE: backup integrity mismatch"; exit 2; }
  exec 9>"$LOCK"
  flock -x 9
  # Atomic replacement of the two files; not an atomic transaction across them.
  # EXIT traps run after restore() returns: local variables would be unset.
  # Allocate global cleanup paths for the lifetime of this short-lived script.
  ctmp=""
  htmp=""
  trap 'rm -f -- "${ctmp:-}" "${htmp:-}"' EXIT
  ctmp="$(mktemp /usr/local/sbin/.router-qos-rollback.XXXXXX)"
  htmp="$(mktemp /etc/ppp/ip-up.d/.router-qos-rollback.XXXXXX)"
  cp "$ROOT/legacy-controller" "$ctmp"
  cp "$ROOT/legacy-ip-up-hook" "$htmp"
  chown root:root "$ctmp" "$htmp"
  chmod 0750 "$ctmp"
  chmod 0755 "$htmp"
  [[ "$(sha256sum "$ctmp" | cut -d' ' -f1)" == "$OLD_CTRL" &&
     "$(sha256sum "$htmp" | cut -d' ' -f1)" == "$OLD_HOOK" ]] || exit 2
  mv -f "$ctmp" "$ACTIVE_CTRL"
  mv -f "$htmp" "$ACTIVE_HOOK"
  check
  [[ "$(sha256sum "$ACTIVE_CTRL" | cut -d' ' -f1)" == "$OLD_CTRL" &&
     "$(sha256sum "$ACTIVE_HOOK" | cut -d' ' -f1)" == "$OLD_HOOK" ]] || exit 2
  echo "PASS: legacy QoS controller and hook files restored; kernel QoS NOT modified"
}
case "${1:-}" in
  verify) check && echo "PASS: rollback copies verified";;
  restore) restore;;
  *) echo "usage: $0 verify|restore"; exit 2;;
esac
