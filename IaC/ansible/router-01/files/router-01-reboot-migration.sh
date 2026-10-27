#!/usr/bin/env bash
# One-shot, headless boot cutover. Installed by Ansible; never run before rewiring.
set -Eeuo pipefail
umask 077
ROOT=/var/lib/router-01-reboot-migration
STATE="$ROOT/state"
BOOT="$ROOT/boot"
BACKUP="$ROOT/backup"
OLD=/etc/netplan/90-NM-75a1216a-9d1a-30cd-8aca-ace5526ec021.yaml
WAN_NM=/etc/NetworkManager/conf.d/90-router-01-wan-unmanaged.conf
FW=/etc/nftables.conf
ROLLBACK=router-01-reboot-rollback.timer
mkdir -p "$STATE"
exec 9>"$STATE/lock"
flock -x 9
log() { echo "$(date -Is) $*" | systemd-cat -t router-reboot-migration; }
need() { if ! "$@"; then log "FAILED: $*"; exit 1; fi; }
check_identity() {
  test "$(hostname -s)" = docker-01
  test "$(cat /sys/class/net/eth0/address)" = d8:3a:dd:5a:51:44
  test "$(cat /sys/class/net/eth1/address)" = 00:24:9b:63:b3:8a
}
activate() {
  check_identity
  test ! -e "$STATE/confirmed" || exit 0
  test ! -e "$STATE/activated" || { log 'Previous activation exists; refusing repeat'; exit 1; }
  test -s "$BACKUP/old-eth0.yaml"
  for f in 99-router-01-lan.yaml 90-router-01-wan-unmanaged.conf nftables.conf 90-router-01-forwarding.conf; do
    test -s "$BOOT/$f"
  done
  test "$(cat /sys/class/net/eth0/carrier)" = 1 || { log 'ABORT eth0 no cable'; exit 1; }
  test "$(cat /sys/class/net/eth1/carrier)" = 1 || { log 'ABORT eth1 no ONT carrier'; exit 1; }
  if ping -n -I eth0 -c 2 -W 1 192.168.2.1 >/dev/null 2>&1; then
    log 'ABORT still attached to old ASUS LAN; DHCP prohibited'; exit 1
  fi
  need kea-dhcp4 -t /etc/kea/kea-dhcp4.conf
  need unbound-checkconf
  need nft -c -f "$BOOT/nftables.conf"
  # Recovery timer is armed before any live configuration is changed.
  need systemctl is-enabled --quiet "$ROLLBACK"
  need systemctl is-active --quiet "$ROLLBACK"
  log 'Independent rollback timer confirmed active before LAN activation'
  touch "$STATE/attempted"
  # Replace the original eth0 DHCP file, rather than overlaying another eth0 definition.
  install -m 0600 "$BOOT/99-router-01-lan.yaml" "$OLD"
  install -d -m 0755 /etc/NetworkManager/conf.d
  install -m 0644 "$BOOT/90-router-01-wan-unmanaged.conf" "$WAN_NM"
  need netplan generate
  need netplan apply
  need ip -4 -o addr show dev eth0
  ip -4 -o addr show dev eth0 | grep -q '192.168.3.1/24' || { log 'ERROR new LAN not present'; exit 1; }
  install -m 0600 "$BOOT/nftables.conf" "$FW"
  need nft -f "$FW"
  need systemctl enable nftables.service
  install -m 0644 "$BOOT/90-router-01-forwarding.conf" /etc/sysctl.d/90-router-01-forwarding.conf
  need sysctl -w net.ipv4.ip_forward=1
  # eth1 must be raw Ethernet, not a NetworkManager DHCP client.
  nmcli device set eth1 managed no || true
  ip link set eth1 up
  need systemctl unmask kea-dhcp4-server.service unbound.service
  need systemctl enable --now unbound.service kea-dhcp4-server.service
  need systemctl enable router-pppoe.service
  need systemctl restart router-pppoe.service
  touch "$STATE/activated"
  log 'Router activation attempted; PPPoE and ASUS DHCP lease must be checked before confirm'
}
rollback() {
  test ! -e "$STATE/confirmed" || { log 'Confirmed; no rollback'; exit 0; }
  # If activation never touched the network, preserve the original LAN intact.
  if test ! -e "$STATE/attempted"; then
    log 'No activation attempt; original LAN remains intact'
    systemctl disable --now router-01-reboot-activate.service 2>/dev/null || true
    systemctl disable --now router-01-reboot-rollback.timer 2>/dev/null || true
    exit 0
  fi
  log 'Restoring original LAN after unconfirmed reboot migration'
  systemctl disable --now kea-dhcp4-server.service unbound.service 2>/dev/null || true
  systemctl mask kea-dhcp4-server.service unbound.service 2>/dev/null || true
  systemctl disable --now router-pppoe.service 2>/dev/null || true
  if test -s "$BACKUP/old-eth0.yaml"; then
    install -m 0600 "$BACKUP/old-eth0.yaml" "$OLD"
  else
    log 'ERROR old Netplan backup missing'; exit 1
  fi
  rm -f /etc/netplan/99-router-01-lan.yaml "$WAN_NM"
  rm -f /etc/sysctl.d/90-router-01-forwarding.conf
  if test -s "$BACKUP/old-nftables.conf"; then
    install -m 0600 "$BACKUP/old-nftables.conf" "$FW"
  fi
  # Do not restore stale Docker-owned FORWARD DROP from the saved running snapshot.
  systemctl disable --now nftables.service 2>/dev/null || true
  nft flush ruleset || log 'WARN firewall flush failed'
  # Restore restrictive ICMP timestamp handling, while permitting old LAN recovery.
  nft add table ip router_recovery || true
  nft 'add chain ip router_recovery input { type filter hook input priority filter; policy accept; }' || true
  nft add rule ip router_recovery input ip protocol icmp icmp type timestamp-request drop || true
  if ! netplan generate || ! netplan apply; then
    log 'ERROR rollback Netplan apply failed; keeping migration markers for diagnosis'
    exit 1
  fi
  rm -f "$STATE/activated" "$STATE/attempted"
  systemctl disable --now router-01-reboot-activate.service 2>/dev/null || true
  systemctl disable --now router-01-reboot-rollback.timer 2>/dev/null || true
  log 'Old DHCP config restored. Reconnect Pi eth0 to HP switch and ONT to ASUS WAN.'
}
confirm() {
  test -e "$STATE/activated"
  ip -4 -o addr show dev eth0 | grep -q '192.168.3.1/24'
  systemctl is-active --quiet kea-dhcp4-server.service
  systemctl is-active --quiet unbound.service
  ip -4 -o addr show dev ppp0 | grep -q 'inet '
  ip -4 route show default | grep -q 'dev ppp0'
  nft list table ip router_nat >/dev/null
  test -s /var/lib/kea/kea-leases4.csv
  touch "$STATE/confirmed"
  systemctl disable --now "$ROLLBACK"
  systemctl disable router-01-reboot-activate.service 2>/dev/null || true
  log 'Confirmed and rollback timer stopped'
}
status() {
  ip -4 -brief addr show eth0
  ip -4 -brief addr show ppp0 2>/dev/null || true
  for s in kea-dhcp4-server unbound nftables router-pppoe router-01-reboot-rollback.timer; do
    echo "$s: $(systemctl is-active "$s" 2>/dev/null || true)"
  done
  for f in attempted activated confirmed; do
    echo "$f: $(test -e "$STATE/$f" && echo yes || echo no)"
  done
}
case "${1:-}" in
  activate) activate ;;
  rollback) rollback ;;
  confirm) confirm ;;
  status) status ;;
  *) echo 'usage: router-01-reboot-migration {activate|rollback|confirm|status}' >&2; exit 2;;
esac
