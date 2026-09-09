#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

TARGET_PVE_HOST="192.168.2.71"
TARGET_PVE_NAME="Proxmox-2"
MONITOR_HOSTNAME="monitor-01"
MONITOR_IPV4="192.168.2.52"
MONITOR_VM_ID="${MONITOR_VM_ID:-200}"
PVE_ROOT_SSH_KEY="${PVE_ROOT_SSH_KEY:-$HOME/.ssh/proxmox-root}"

require_cmd ssh
require_cmd ping
require_cmd awk
require_cmd grep

[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing Proxmox root SSH key: $PVE_ROOT_SSH_KEY"

printf '===== MONITOR-01 IAC PREFLIGHT =====\n'
printf 'target_pve=%s\n' "$TARGET_PVE_NAME"
printf 'target_pve_ipv4=%s\n' "$TARGET_PVE_HOST"
printf 'monitor_hostname=%s\n' "$MONITOR_HOSTNAME"
printf 'monitor_ipv4=%s\n' "$MONITOR_IPV4"
printf 'candidate_vm_id=%s\n' "$MONITOR_VM_ID"

printf '\n===== IP ADDRESS GATE =====\n'
if ping -c 2 -W 1 "$MONITOR_IPV4" >/dev/null 2>&1; then
  printf 'monitor_ipv4_status=IN_USE_OR_RESPONDING\n'
  exit 1
else
  printf 'monitor_ipv4_status=NO_ICMP_RESPONSE\n'
fi

printf '\n===== PROXMOX ROOT SSH =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$TARGET_PVE_HOST" true \
  || die "Root key-based SSH to $TARGET_PVE_NAME is not ready"
printf 'root_ssh=PASS\n'

printf '\n===== TARGET IDENTITY =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$TARGET_PVE_HOST" '
hostname
hostname -f
pveversion
'

printf '\n===== GUEST ID GATE =====\n'
if ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$TARGET_PVE_HOST" \
  "qm config '$MONITOR_VM_ID' >/dev/null 2>&1 || pct config '$MONITOR_VM_ID' >/dev/null 2>&1"; then
  printf 'candidate_vm_id_status=IN_USE\n'
  exit 1
else
  printf 'candidate_vm_id_status=FREE\n'
fi

printf '\n===== CURRENT GUESTS =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$TARGET_PVE_HOST" '
echo "--- VMs ---"
qm list
echo
echo "--- LXCs ---"
pct list
'

printf '\n===== STORAGE =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$TARGET_PVE_HOST" '
pvesm status
echo
echo "--- storage.cfg ---"
cat /etc/pve/storage.cfg
echo
echo "--- LVM ---"
pvs
vgs
lvs -a -o lv_name,vg_name,lv_size,data_percent,metadata_percent
'

printf '\n===== LOCAL IMAGE CONTENT =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$TARGET_PVE_HOST" '
find /var/lib/vz/template -maxdepth 2 -type f -printf "%p\n" 2>/dev/null | sort || true
find /var/lib/vz -maxdepth 2 -type f \( -name "*.qcow2" -o -name "*.img" -o -name "*.iso" \) -printf "%p\n" 2>/dev/null | sort || true
'

printf '\n===== NETWORK =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$TARGET_PVE_HOST" '
ip -br addr
echo
ip route
echo
cat /etc/resolv.conf
'

printf '\n===== DNS DEPENDENCY =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$TARGET_PVE_HOST" '
getent ahostsv4 deb.debian.org | head -3 || true
'

printf '\n===== HOST HEALTH =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$TARGET_PVE_HOST" '
uptime
systemctl --failed --no-legend --plain
'

printf '\n===== RESULT =====\n'
printf 'preflight=COLLECTED\n'
printf 'No VM, storage, network or service configuration was changed.\n'
