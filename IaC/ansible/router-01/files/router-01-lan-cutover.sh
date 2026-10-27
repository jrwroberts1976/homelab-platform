#!/usr/bin/env bash
# router-01 LAN readdressing: explicit final cutover with timed rollback.
# NOT for existing production docker-01. Install only after approved rebuild.
set -euo pipefail
umask 077

ACTION="${1:-}"
STAGE=/var/lib/router-01-stage
CURRENT=/etc/systemd/network/10-router-lan.network
NEW="${STAGE}/10-router-lan.network"
BACKUP="${STAGE}/lan-rollback/10-router-lan.network"
STATE="${STAGE}/lan-rollback/status"
LOCK="${STAGE}/lan-rollback/lock"
TIMER=router-01-lan-rollback.timer
OLD=192.168.2.220
TARGET=192.168.3.1
LAN=eth0
EXPECTED_MAC=d8:3a:dd:5a:51:44

die() { echo "router-01 cutover REFUSED: $*" >&2; exit 1; }
[ "$(id -u)" -eq 0 ] || die "must run as root"
case "$ACTION" in switch|confirm|rollback|status) ;; *) die "usage: $0 switch|confirm|rollback|status";; esac

# Never touch legacy docker-01 or any unsupported machine.
[ "$(hostname -s)" = "router-01" ] || die "hostname is not router-01"
[ -f /etc/router-01-reimage-complete ] || die "post-reimage marker absent"
[ -d "$STAGE" ] || die "missing root-private stage"
[ ! -L "$CURRENT" ] || die "active network configuration is symlinked"
[ -f "$CURRENT" ] || die "expected networkd bootstrap config absent"
[ "$(cat /sys/class/net/"$LAN"/address)" = "$EXPECTED_MAC" ] || die "unexpected LAN hardware"
systemctl -q is-active systemd-networkd.service || die "systemd-networkd not active"

ip_has() { ip -4 -o addr show dev "$LAN" | grep -qE "inet ${1}/"; }
# lock against concurrent manual/timer invocation; lock directory always preserved.
install -d -m 0700 "$STAGE/lan-rollback"
exec 9>"$LOCK"
flock -x 9

case "$ACTION" in
  status)
    echo "status=$(cat "$STATE" 2>/dev/null || echo not-started)"
    ip -4 -br addr show dev "$LAN"
    exit 0
    ;;
  switch)
    [ "${2:-}" = "--approved-handover" ] || die "explicit --approved-handover required"
    ip_has "$OLD" || die "original management address not present"
    [ ! -f "$STATE" ] || die "cutover already attempted; inspect recovery state first"
    [ -f "$NEW" ] && [ ! -L "$NEW" ] || die "new LAN candidate missing"
    grep -qF "Address=${TARGET}/24" "$NEW" || die "staged LAN config does not set target address"
    grep -qF "MACAddress=${EXPECTED_MAC}" "$NEW" || die "staged config targets unexpected hardware"
    grep -qF "$OLD" "$CURRENT" || die "active bootstrap config not using old address"
    # Ensure systemd-networkd actually owns *this* config file.
    networkctl status "$LAN" --no-pager | grep -qF "$CURRENT" ||
      die "unexpected active networkd file; console review required"
    [ -f /etc/systemd/system/router-01-lan-rollback.service ] || die "rollback unit missing"
    [ -f /etc/systemd/system/router-01-lan-rollback.timer ] || die "rollback timer missing"
    # Backup before arming. Timer is enabled for restart/reboot recovery.
    install -m 0600 "$CURRENT" "$BACKUP"
    printf 'pending\n' > "$STATE"
    systemctl daemon-reload
    if ! systemctl enable --now "$TIMER"; then
      printf 'failed-to-arm\n' > "$STATE"
      die "rollback timer could not be armed; LAN NOT changed"
    fi
    systemctl -q is-active "$TIMER" || die "timer not active; do not switch"
    # Activate changed LAN networkd file only after rollback is armed.
    install -m 0644 "$NEW" "$CURRENT"
    if ! networkctl reload || ! networkctl reconfigure "$LAN"; then
      # Let timer recover independently if the current SSH connection drops.
      echo "LAN reconfigure failed; timer remains armed for automatic rollback" >&2
      exit 2
    fi
    echo "LAN switch requested. SSH will move to ${TARGET}; confirm before timer expires."
    ;;
  confirm)
    [ -f "$STATE" ] && [ "$(cat "$STATE")" = pending ] || die "no pending cutover"
    ip_has "$TARGET" || die "target LAN address not active; cannot confirm"
    # Mark confirmation first, so an in-flight timer cannot undo a verified change.
    printf 'confirmed\n' > "$STATE"
    systemctl disable --now "$TIMER"
    echo "LAN address confirmed. Automatic rollback cancelled."
    ;;
  rollback)
    [ -f "$STATE" ] || exit 0
    [ "$(cat "$STATE")" = pending ] || exit 0
    [ -f "$BACKUP" ] || die "backup missing; manual console recovery required"
    install -m 0644 "$BACKUP" "$CURRENT"
    # Networkd re-addressing can disconnect the current session; called by timer too.
    networkctl reload
    networkctl reconfigure "$LAN"
    printf 'rolled-back\n' > "$STATE"
    systemctl disable --now "$TIMER" || true
    echo "Restored previous LAN networkd config. Verify ${OLD} from console."
    ;;
esac
