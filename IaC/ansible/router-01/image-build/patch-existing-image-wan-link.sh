#!/usr/bin/env bash
# Offline, narrowly scoped patch for an existing Pi router disk image. Never run on a live Pi.
set -Eeuo pipefail
umask 077
[[ $(id -u) -eq 0 && $# -eq 1 ]] || { echo "Usage: sudo $0 absolute-existing-image" >&2; exit 2; }
IMAGE=$(realpath "$1")
[[ -f "$IMAGE" && "$IMAGE" = *.img ]] || { echo "Expected existing .img" >&2; exit 2; }
LOOP=""
MNT=$(mktemp -d /tmp/router-offline-patch.XXXXXXXX)
cleanup() {
  set +e
  if mountpoint -q "$MNT"; then umount "$MNT"; fi
  [[ -z "$LOOP" ]] || losetup -d "$LOOP"
  rmdir "$MNT" 2>/dev/null || true
}
trap cleanup EXIT
LOOP=$(losetup --find --show --partscan "$IMAGE")
[[ -b "${LOOP}p2" ]] || { echo "Missing root partition" >&2; exit 1; }
mount "${LOOP}p2" "$MNT"
[[ -f "$MNT/etc/os-release" && -x "$MNT/usr/sbin/pppd" && -f "$MNT/etc/systemd/system/router-pppoe.service" ]] || {
  echo "Refusing to modify image: expected Debian router files missing" >&2; exit 1;
}
install -d -m 0755 "$MNT/etc/systemd/network"
cat > "$MNT/etc/systemd/network/10-router-wan.link" <<'EOF'
[Match]
MACAddress=00:24:9b:63:b3:8a

[Link]
Name=eth1
EOF
chmod 0644 "$MNT/etc/systemd/network/10-router-wan.link"
grep -Fxq 'MACAddress=00:24:9b:63:b3:8a' "$MNT/etc/systemd/network/10-router-wan.link"
grep -Fxq 'Name=eth1' "$MNT/etc/systemd/network/10-router-wan.link"
sync
echo "PASS: offline WAN naming rule inserted into $IMAGE. Still requires controlled boot testing."
