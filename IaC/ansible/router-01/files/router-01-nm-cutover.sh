#!/usr/bin/env bash
# Pi4 in-place Debian13: local/off-SSH Ethernet cutover to router-01 LAN.
# Controlled by Ansible-staged units; NOT the obsolete networkd rollback.
set -Eeuo pipefail
umask 077

STATE=/var/lib/router-01-cutover
OVERRIDE=/etc/netplan/99-router-01-lan.yaml
STAGED=/var/lib/router-01-stage/forwarding/nftables.conf
LIVE_NFT=/etc/nftables.conf
SWITCH_MARKER="$STATE/applied"
CONFIRMED="$STATE/confirmed"
ROLLBACK_TIMER=router-lan-rollback.timer

mkdir -p "$STATE"
chmod 0700 "$STATE"
exec 9>"$STATE/lock"
flock -x 9

log(){ printf '%s %s\n' "$(date -Is)" "$*" | systemd-cat -t router-lan-cutover; }

ensure_baseline() {
  test "$(hostname -s)" = docker-01
  ip -4 -o addr show dev eth0 | grep -q '192.168.2.220/24'
  test "$(cat /sys/class/net/eth0/address)" = 'd8:3a:dd:5a:51:44'
  test "$(cat /sys/class/net/eth1/address)" = '00:24:9b:63:b3:8a'
  test -s /var/lib/router-01-stage/lan/99-router-01-lan.yaml
  test -s "$STAGED"
  test -e /etc/kea/kea-dhcp4.conf
  test -e /etc/unbound/unbound.conf.d/router-01.conf
  test "$(systemctl is-enabled kea-dhcp4-server.service)" = masked
  test "$(systemctl is-enabled unbound.service)" = masked
}

stop_docker() {
  # User approved BirdNET and Komodo outage. Preserve configurations/volumes.
  if systemctl -q is-active docker.service; then
    for file in /opt/birdnet-go/compose.yml /etc/komodo/compose.yml; do
      if test -f "$file"; then
        docker compose -f "$file" down --timeout 15 || log "Compose down nonzero: $file"
      fi
    done
  fi
  systemctl disable --now homelab-trivy-docker.timer 2>/dev/null || true
  systemctl stop homelab-trivy-docker.service 2>/dev/null || true
  systemctl disable --now docker.socket docker.service containerd.service 2>/dev/null || true
  if systemctl -q is-active docker.service; then
    log "ERROR Docker still active; refusing to flush its rules"
    return 1
  fi
}

apply() {
  test ! -f "$SWITCH_MARKER" || { log 'Already applied; use confirm/status'; exit 1; }
  ensure_baseline

  # eth0 must have been UNPLUGGED from the HP switch and MOVED to ASUS WAN.
  # Fail closed if the old ASUS LAN still responds to an eth0-sourced probe.
  test "$(cat /sys/class/net/eth0/carrier)" = 1 || { log 'eth0 has no cable carrier'; exit 1; }
  if ping -n -I eth0 -c 2 -W 1 192.168.2.1 >/dev/null 2>&1; then
    log 'ABORT old ASUS 192.168.2.1 still reachable on eth0; do not start DHCP'
    exit 1
  fi

  # Prepare automatic rollback BEFORE touching old LAN.
  systemctl enable --now "$ROLLBACK_TIMER"
  printf '%s\n' "$(sysctl -n net.ipv4.ip_forward)" > "$STATE/old-ip-forward"
  if test -f "$LIVE_NFT"; then cp -a "$LIVE_NFT" "$STATE/old-nftables.conf"; fi
  { echo 'flush ruleset'; nft list ruleset; } > "$STATE/old-running-rules.nft"
  test -s "$STATE/old-running-rules.nft"
  cp -a /etc/netplan/90-NM-75a1216a-9d1a-30cd-8aca-ace5526ec021.yaml "$STATE/old-netplan-eth0.yaml"
  log 'Backups made and rollback timer armed (10 min)'

  # No DHCP/NAT while Docker's old FORWARD DROP owns iptables-nft.
  stop_docker
  systemctl disable --now router-wan-guard.service 2>/dev/null || true

  # These files were syntax-validated separately before physical move.
  install -m 0644 /var/lib/router-01-stage/lan/99-router-01-lan.yaml "$OVERRIDE"
  netplan generate
  netplan apply
  ip -4 -o addr show dev eth0 | grep -q '192.168.3.1/24'

  install -m 0644 "$STAGED" "$LIVE_NFT"
  nft -c -f "$LIVE_NFT"
  nft -f "$LIVE_NFT"
  systemctl enable nftables.service

  install -m 0644 /var/lib/router-01-stage/forwarding/90-router-01-forwarding.conf /etc/sysctl.d/90-router-01-forwarding.conf
  sysctl -w net.ipv4.ip_forward=1 >/dev/null
  systemctl unmask kea-dhcp4-server.service unbound.service
  systemctl enable --now unbound.service kea-dhcp4-server.service
  # Attempt/retry ISP WAN even if ppp0 dropped during ONT move.
  systemctl enable router-pppoe.service
  systemctl restart router-pppoe.service

  touch "$SWITCH_MARKER"
  log 'LAN 192.168.3.1, Kea, Unbound, NAT staged and started; PPP reconnect requested. CONFIRM before timer expires.'
}

rollback() {
  if test -f "$CONFIRMED"; then
    log 'Rollback skipped: new router LAN confirmed'
    exit 0
  fi
  log 'Automatic/explicit rollback: returning to old Netplan DHCP'
  systemctl disable --now kea-dhcp4-server.service unbound.service 2>/dev/null || true
  systemctl mask kea-dhcp4-server.service unbound.service 2>/dev/null || true
  systemctl disable --now router-pppoe.service 2>/dev/null || true
  rm -f "$OVERRIDE"
  if test -f "$STATE/old-netplan-eth0.yaml"; then
    cp -a "$STATE/old-netplan-eth0.yaml" /etc/netplan/90-NM-75a1216a-9d1a-30cd-8aca-ace5526ec021.yaml
  fi
  netplan generate && netplan apply || log 'Netplan rollback failed: use local console'
  if test -f "$STATE/old-ip-forward"; then
    sysctl -w "net.ipv4.ip_forward=$(cat "$STATE/old-ip-forward")" >/dev/null || true
  fi
  rm -f /etc/sysctl.d/90-router-01-forwarding.conf
  systemctl disable --now nftables.service 2>/dev/null || true
  if test -f "$STATE/old-nftables.conf"; then
    cp -a "$STATE/old-nftables.conf" "$LIVE_NFT"
  fi
  if test -f "$STATE/old-running-rules.nft"; then
    nft -f "$STATE/old-running-rules.nft" || log 'Original nft rules not fully restorable; review locally'
  fi
  rm -f "$SWITCH_MARKER"
  log 'Old eth0 DHCP restored in config. Manually reconnect Pi eth0 to HP switch and ONT to ASUS WAN.'
}

confirm() {
  test -f "$SWITCH_MARKER"
  ip -4 -o addr show dev eth0 | grep -q '192.168.3.1/24'
  systemctl is-active --quiet kea-dhcp4-server.service
  systemctl is-active --quiet unbound.service
  ip -4 -o addr show dev ppp0 | grep -q 'inet '
  ip -4 route show default | grep -q 'dev ppp0'
  nft list table ip router_nat >/dev/null
  touch "$CONFIRMED"
  systemctl disable --now "$ROLLBACK_TIMER"
  log 'CONFIRMED new router LAN: automatic rollback disarmed'
}

status() {
  echo '--- LAN ---'
  ip -4 -o addr show dev eth0
  echo '--- PPP WAN ---'
  ip -4 -o addr show dev ppp0 2>/dev/null || true
  echo '--- Services ---'
  for s in router-pppoe kea-dhcp4-server unbound nftables docker; do
    printf '%s: ' "$s"
    systemctl is-active "$s.service" 2>/dev/null || true
  done
  echo "cutover_applied=$(test -f "$SWITCH_MARKER" && echo yes || echo no)"
  echo "cutover_confirmed=$(test -f "$CONFIRMED" && echo yes || echo no)"
  echo "rollback_timer=$(systemctl is-active "$ROLLBACK_TIMER" 2>/dev/null || true)"
}

case "${1:-}" in
  apply) apply ;;
  rollback) rollback ;;
  confirm) confirm ;;
  status) status ;;
  *) echo 'Usage: router-01-nm-cutover {apply|rollback|confirm|status}' >&2; exit 2 ;;
esac
