#!/usr/bin/env bash
# Execute on ARM64 Linux admin-01. Do not run on the target Pi.
set -Eeuo pipefail
umask 077
[[ $# -eq 4 ]] || { echo "usage: sudo $0 base.img.xz output.img secrets.txt ssh-public-key-file" >&2; exit 2; }
[[ $(id -u) -eq 0 && $(uname -m) = aarch64 ]] || { echo "Requires root on ARM64 Linux" >&2; exit 2; }
BASE=$(realpath "$1"); OUT=$(realpath -m "$2"); CREDS=$(realpath "$3"); PUBKEY=$(realpath "$4")
[[ -f "$BASE" && -f "$CREDS" && -f "$PUBKEY" && ! -e "$OUT" ]] || exit 2
WORK=$(mktemp -d /tmp/pi-router-build.XXXXXXXX)
LOOP=""
cleanup() { set +e; for p in dev/pts run sys proc dev boot/firmware; do if mountpoint -q "$WORK/root/$p"; then umount "$WORK/root/$p"; fi; done; if mountpoint -q "$WORK/root"; then umount "$WORK/root"; fi; if [[ -n "$LOOP" ]]; then losetup -d "$LOOP"; fi; rmdir "$WORK/root" "$WORK" 2>/dev/null || true; }
trap cleanup EXIT
echo "Decompressing official Raspberry Pi OS Lite ARM64 image..."
xz -dc "$BASE" > "$OUT"
LOOP=$(losetup --find --show --partscan "$OUT")
for n in $(seq 1 15); do [[ -b "$LOOP"p2 ]] && break; sleep 1; done
[[ -b "$LOOP"p1 && -b "$LOOP"p2 ]] || exit 1
mkdir -p "$WORK/root"
mount "$LOOP"p2 "$WORK/root"
ROOT="$WORK/root"
# Fail closed if the selected root partition is empty, corrupt, or not a Debian OS.
if [[ ! -r "$ROOT/etc/os-release" || ! -x "$ROOT/usr/bin/apt-get" || ! -x "$ROOT/usr/bin/dpkg" ]]; then
  echo "ERROR: Mounted partition 2 is not a usable Debian root filesystem." >&2
  echo "Inspect the untouched base image before retrying. No credentials were injected." >&2
  exit 1
fi
mkdir -p "$ROOT/boot/firmware"
mount "$LOOP"p1 "$ROOT/boot/firmware"
for p in dev proc sys run; do mount --bind "/$p" "$ROOT/$p"; done
mkdir -p "$ROOT/dev/pts"; mount --bind /dev/pts "$ROOT/dev/pts"
cp -L /etc/resolv.conf "$ROOT/etc/resolv.conf"
echo "Installing networking packages inside target filesystem..."
chroot "$ROOT" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get update
chroot "$ROOT" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends dnsmasq unbound nftables ppp openssh-server sudo ca-certificates
for svc in NetworkManager.service dhcpcd.service networking.service; do chroot "$ROOT" systemctl disable "$svc" 2>/dev/null || true; done
mkdir -p "$ROOT/etc/systemd/network" "$ROOT/etc/dnsmasq.d" "$ROOT/etc/unbound/unbound.conf.d" "$ROOT/etc/ppp/peers" "$ROOT/etc/systemd/system" "$ROOT/etc/sysctl.d"
cat > "$ROOT/etc/systemd/network/10-router-lan.network" <<EOF
[Match]
Name=eth0
MACAddress=d8:3a:dd:5a:51:44
[Network]
Address=192.168.3.1/24
ConfigureWithoutCarrier=yes
LinkLocalAddressing=no
IPv6AcceptRA=no
EOF
cat > "$ROOT/etc/systemd/network/20-router-wan.network" <<EOF
[Match]
MACAddress=00:24:9b:63:b3:8a
[Link]
ActivationPolicy=always-up
[Network]
DHCP=no
LinkLocalAddressing=no
EOF
cat > "$ROOT/etc/dnsmasq.d/router.conf" <<EOF
port=0
interface=eth0
bind-dynamic
dhcp-authoritative
dhcp-range=192.168.3.100,192.168.3.199,255.255.255.0,24h
dhcp-option=option:router,192.168.3.1
dhcp-option=option:dns-server,192.168.3.1
EOF
cat > "$ROOT/etc/unbound/unbound.conf.d/router.conf" <<EOF
server:
  interface: 127.0.0.1
  interface: 192.168.3.1
  access-control: 127.0.0.0/8 allow
  access-control: 192.168.3.0/24 allow
  do-ip6: no
EOF
cat > "$ROOT/etc/nftables.conf" <<EOF
#!/usr/sbin/nft -f
flush ruleset
table inet filter_router {
 chain input {
  type filter hook input priority 0; policy drop;
  iifname "lo" accept
  ct state established,related accept
  ct state invalid drop
  iifname "eth0" tcp dport {22,53} accept
  iifname "eth0" udp dport {53,67} accept
  iifname "eth0" ip protocol icmp accept
 }
 chain forward {
  type filter hook forward priority 0; policy drop;
  ct state established,related accept
  ct state invalid drop
  iifname "eth0" oifname "ppp0" ip saddr 192.168.3.0/24 accept
 }
 chain output { type filter hook output priority 0; policy accept; }
}
table ip nat_router {
 chain postrouting {
  type nat hook postrouting priority srcnat; policy accept;
  oifname "ppp0" ip saddr 192.168.3.0/24 masquerade
 }
}
EOF
echo "net.ipv4.ip_forward=1" > "$ROOT/etc/sysctl.d/90-router-forward.conf"
python3 - "$ROOT" "$CREDS" <<'PY'
import pathlib, sys
root, source = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
values = source.read_text().splitlines()
if len(values) != 2 or not all(values): raise SystemExit("secrets file needs username + password on separate lines")
user, password = values
def quote(v): return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
peer = root/"etc/ppp/peers/homelab-wan"
peer.write_text("plugin pppoe.so\nnic-eth1\nnoauth\ndefaultroute\nreplacedefaultroute\npersist\nholdoff 10\nmtu 1492\nmru 1492\nuser " + quote(user) + "\n")
peer.chmod(0o600)
for method in ("pap-secrets", "chap-secrets"):
    secret = root/"etc/ppp"/method
    secret.write_text(quote(user) + " * " + quote(password) + " *\n")
    secret.chmod(0o600)
PY
cat > "$ROOT/etc/systemd/system/router-pppoe.service" <<EOF
[Unit]
Description=PPPoE WAN
Wants=systemd-networkd.service
After=systemd-networkd.service
[Service]
Type=simple
ExecStartPre=/usr/sbin/ip link set dev eth1 up
ExecStart=/usr/sbin/pppd call homelab-wan nodetach
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF
chroot "$ROOT" useradd -m -s /bin/bash james 2>/dev/null || true
install -d -m 0700 "$ROOT/home/james/.ssh"
install -m 0600 "$PUBKEY" "$ROOT/home/james/.ssh/authorized_keys"
chroot "$ROOT" chown -R james:james /home/james/.ssh
install -d -m 0750 "$ROOT/etc/sudoers.d"
echo "james ALL=(ALL:ALL) NOPASSWD:ALL" > "$ROOT/etc/sudoers.d/90-james-router"
chmod 0440 "$ROOT/etc/sudoers.d/90-james-router"
chroot "$ROOT" systemctl disable kea-dhcp4-server.service 2>/dev/null || true
chroot "$ROOT" systemctl enable systemd-networkd.service dnsmasq.service unbound.service nftables.service router-pppoe.service ssh.service
chroot "$ROOT" dnsmasq --test
chroot "$ROOT" unbound-checkconf
chroot "$ROOT" nft -c -f /etc/nftables.conf
echo "nameserver 127.0.0.1" > "$ROOT/etc/resolv.conf"
sync
echo "Built $OUT (contains PPPoE credentials; keep file private)"
