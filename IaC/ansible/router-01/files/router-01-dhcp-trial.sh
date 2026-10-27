#!/usr/bin/env bash
# Temporary DHCP-ONLY trial for Debian13 Pi4 behind ASUS WAN.
# Never writes Netplan, persistent NM profiles, sysctl, nftables, or PPP units.
# Must be started by a deferred local systemd unit AFTER eth0 cable isolation.
set -Eeuo pipefail
umask 077

STATE=/run/router-01-dhcp-trial
PROFILE=router-01-dhcp-trial
ETH=eth0
OLD_TIMER=router-lan-switch.timer
UNDO_TIMER=router-dhcp-trial-rollback.timer
mkdir -p "$STATE"
exec 9>"$STATE/lock"
flock -x 9
log() { echo "$(date -Is) $*" | systemd-cat -t router-dhcp-trial; }

require_identity() {
  test "$(hostname -s)" = docker-01
  test "$(cat /sys/class/net/eth0/address)" = d8:3a:dd:5a:51:44
  test "$(cat /sys/class/net/eth1/address)" = 00:24:9b:63:b3:8a
}

start() {
  require_identity
  # A cutover from the previous experiment must not be pending.
  if systemctl -q is-active "$OLD_TIMER"; then
    log 'ABORT: old router-lan-switch timer still active'
    exit 1
  fi
  if test -e /etc/netplan/99-router-01-lan.yaml; then
    log 'ABORT: persistent router Netplan override present'
    exit 1
  fi
  if nmcli -t -f NAME connection show | grep -Fxq "$PROFILE"; then
    log 'ABORT: temporary DHCP profile already present'
    exit 1
  fi
  test "$(systemctl is-enabled kea-dhcp4-server.service)" = masked
  test "$(systemctl is-enabled unbound.service)" = masked
  test "$(cat /sys/class/net/eth0/carrier)" = 1 || {
    log 'ABORT: no physical cable carrier on eth0'; exit 1;
  }

  # No competing DHCP on the old ASUS LAN.
  # This is checked BEFORE eth0 has .3.1, while the old .2 link may exist.
  if ping -n -I eth0 -c 2 -W 1 192.168.2.1 >/dev/null 2>&1; then
    log 'ABORT: ASUS old LAN 192.168.2.1 reachable directly on eth0'
    exit 1
  fi

  # PPPoE WAN and internet were tested separately. Require them LIVE NOW.
  ip -4 -o address show dev ppp0 | grep -q 'inet ' || {
    log 'ABORT: PPPoE ppp0 has no IPv4'; exit 1;
  }
  ping -n -I ppp0 -c 2 -W 2 1.1.1.1 >/dev/null 2>&1 || {
    log 'ABORT: PPPoE cannot reach 1.1.1.1'; exit 1;
  }

  # Automatic service reversal is armed BEFORE touching eth0 or Kea.
  systemctl start "$UNDO_TIMER"
  log '15-minute DHCP-only rollback timer armed'

  # NM runtime profile is NOT saved to disk; reboot restores old Netplan.
  nmcli --wait 10 connection add save no type ethernet \
    ifname "$ETH" con-name "$PROFILE" \
    connection.autoconnect no \
    ipv4.method manual ipv4.addresses 192.168.3.1/24 \
    ipv4.never-default yes ipv6.method disabled
  nmcli --wait 20 connection up id "$PROFILE" ifname "$ETH"
  ip -4 -o address show dev "$ETH" | grep -q '192.168.3.1/24'

  # Start Kea only for this session: NEVER systemctl enable Kea here.
  /usr/sbin/kea-dhcp4 -t /etc/kea/kea-dhcp4.conf
  systemctl unmask kea-dhcp4-server.service
  systemctl disable kea-dhcp4-server.service
  systemctl start kea-dhcp4-server.service
  systemctl is-active --quiet kea-dhcp4-server.service
  test "$(systemctl is-enabled kea-dhcp4-server.service)" = disabled
  touch "$STATE/started"
  log 'DHCP TRIAL ACTIVE: eth0 .3.1, Kea running but DISABLED at boot; inspect ASUS WAN lease now'
}

rollback() {
  # Always stop Kea before eth0 may rejoin the old ASUS LAN.
  systemctl stop kea-dhcp4-server.service 2>/dev/null || true
  systemctl disable kea-dhcp4-server.service 2>/dev/null || true
  systemctl mask kea-dhcp4-server.service 2>/dev/null || true

  if nmcli -t -f NAME connection show | grep -Fxq "$PROFILE"; then
    nmcli --wait 5 connection down id "$PROFILE" || true
    nmcli connection delete id "$PROFILE" || true
  fi
  ip -4 address del 192.168.3.1/24 dev "$ETH" 2>/dev/null || true

  # Old DHCP profile is persistent; it can reactivate when original cable returns.
  nmcli --wait 5 connection up id netplan-eth0 ifname "$ETH" || true
  rm -f "$STATE/started"
  log 'DHCP TRIAL ENDED: Kea STOPPED, DISABLED, MASKED; ephemeral .3.1 removed'
  log 'Restore Pi eth0 to HP switch and ONT to ASUS WAN if reverting to original internet'
}

status() {
  echo '=== Pi IPv4 ==='
  ip -4 -brief address show eth0
  ip -4 -brief address show ppp0 2>/dev/null || true
  echo '=== Kea ==='
  systemctl is-active kea-dhcp4-server.service || true
  systemctl is-enabled kea-dhcp4-server.service || true
  echo '=== Trial rollback timer ==='
  systemctl is-active "$UNDO_TIMER" || true
  echo '=== Temporary profile ==='
  nmcli -t -f NAME connection show | grep -Fx "$PROFILE" || true
  echo '=== Recent Kea leases ==='
  if test -f /var/lib/kea/kea-leases4.csv; then tail -n 8 /var/lib/kea/kea-leases4.csv; fi
}

case "${1:-}" in
  start) start ;;
  rollback) rollback ;;
  status) status ;;
  *) echo 'usage: router-01-dhcp-trial {start|rollback|status}' >&2; exit 2 ;;
esac
