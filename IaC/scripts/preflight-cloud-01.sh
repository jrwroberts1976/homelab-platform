#!/usr/bin/env bash
# Read-only preflight for cloud-01. This script must not create, modify or destroy resources.

set -u

PVE_HOST="${PVE_HOST:-192.168.2.70}"
PVE_NAME="${PVE_NAME:-PROXMOX}"
CLOUD_IP="${CLOUD_IP:-192.168.2.53}"
CLOUD_HOSTNAME="${CLOUD_HOSTNAME:-cloud-01}"
PVE_KEY="${PVE_KEY:-$HOME/.ssh/proxmox-root}"
DATA_BY_ID="${DATA_BY_ID:-/dev/disk/by-id/usb-WDC_WD40_EZRX-00SPEB0_133309270ED2-0:0}"

echo "===== CLOUD-01 GREENFIELD PREFLIGHT ====="
echo "controller=$(hostname -s)"
echo "target_pve=$PVE_NAME"
echo "target_pve_ipv4=$PVE_HOST"
echo "cloud_hostname=$CLOUD_HOSTNAME"
echo "cloud_ipv4=$CLOUD_IP"
echo

echo "===== CONTROLLER TOOLS ====="
for cmd in ssh ping getent awk sed grep sort; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd: PASS"
  else
    echo "$cmd: MISSING"
  fi
done

echo
echo "===== CLOUD IP SAFETY ====="
if ping -c 2 -W 1 "$CLOUD_IP" >/dev/null 2>&1; then
  echo "cloud_ip_ping: RESPONDS"
else
  echo "cloud_ip_ping: no response"
fi
ip neigh show "$CLOUD_IP" 2>/dev/null || true

echo
echo "===== CURRENT DNS ====="
for dns in 192.168.2.51 192.168.2.50; do
  if command -v dig >/dev/null 2>&1; then
    printf 'dns=%s ' "$dns"
    dig @"$dns" "$CLOUD_HOSTNAME.jameshouse" A +short 2>/dev/null || true
  fi
done

echo
echo "===== PROXMOX READ-ONLY AUDIT ====="
ssh   -o BatchMode=yes   -o ConnectTimeout=5   -i "$PVE_KEY"   root@"$PVE_HOST"   "PVE_EXPECTED='$PVE_NAME' CLOUD_IP='$CLOUD_IP' DATA_BY_ID='$DATA_BY_ID' bash -s" <<'REMOTE'
set -u

echo "===== IDENTITY ====="
hostname
pveversion | head -1
systemctl is-active pve-cluster || true
mountpoint /etc/pve || true

echo
echo "===== HOST HEALTH ====="
uptime
free -h
systemctl --failed --no-legend --plain || true

echo
echo "===== NETWORK ====="
ip -br addr
ip route
echo
echo "vmbr0:"
ip -br addr show vmbr0 2>/dev/null || true

echo
echo "===== EXISTING VMS ====="
qm list || true

echo
echo "===== EXISTING CONTAINERS ====="
pct list || true

echo
echo "===== CANDIDATE VM ID ====="
used_ids="$(
  {
    qm list 2>/dev/null | awk 'NR>1 {print $1}'
    pct list 2>/dev/null | awk 'NR>1 {print $1}'
  } | sort -n -u
)"
candidate=""
for id in $(seq 200 299); do
  if ! grep -qx "$id" <<<"$used_ids"; then
    candidate="$id"
    break
  fi
done
echo "candidate_vm_id=${candidate:-NONE}"

echo
echo "===== STORAGE ====="
pvesm status || true

echo
echo "===== BLOCK DEVICES ====="
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL,SERIAL

echo
echo "===== CLOUD DATA DEVICE ====="
if [ -e "$DATA_BY_ID" ]; then
  echo "data_device_present=YES"
  readlink -f "$DATA_BY_ID"
  ls -l "$DATA_BY_ID"
else
  echo "data_device_present=NO"
fi

echo
echo "===== DATA DEVICE TEST PROCESS ====="
ps -eo pid,etime,cmd | grep -E '[b]adblocks|[s]martctl.*(long|test)|[d]d .*WDC|[f]io .*WDC' || true

echo
echo "===== DATA DEVICE SMART SUMMARY ====="
if [ -e "$DATA_BY_ID" ] && command -v smartctl >/dev/null 2>&1; then
  smartctl -a "$DATA_BY_ID" 2>/dev/null |
    grep -E '^(SMART overall-health|SMART Health Status|  5 Reallocated_Sector_Ct|197 Current_Pending_Sector|198 Offline_Uncorrectable|199 UDMA_CRC_Error_Count|Power_On_Hours)' || true
else
  echo "smart_summary=unavailable"
fi

echo
echo "===== AVAILABLE INSTALL MEDIA ====="
find /var/lib/vz/template/iso /var/lib/vz/template/cache   -maxdepth 1 -type f -printf '%p\n' 2>/dev/null | sort || true

echo
echo "===== PROXMOX FIREWALL STATUS ====="
pve-firewall status 2>/dev/null || true
REMOTE

echo
echo "===== PREFLIGHT COMPLETE ====="
echo "No resources were changed."
