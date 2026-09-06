#!/usr/bin/env bash
# Homelab greenfield Linux host audit.
#
# Purpose:
#   Capture a consistent, read-only hardware and workload baseline before any
#   host is renamed, repurposed, rebuilt, or assigned a future role.
#
# Usage:
#   ./scripts/audit-linux-host.sh
#   ./scripts/audit-linux-host.sh | tee /var/tmp/<host>-audit.txt
#
# The script does not intentionally modify host configuration or workload state.
# It avoids dumping environment variables, secret files, Kubernetes secrets, or
# application configuration that may contain credentials.

set -u
set -o pipefail

section() {
  printf '\n================================================================\n%s\n================================================================\n' "$1"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

run() {
  "$@" 2>&1 || true
}

# Prefer non-interactive privilege escalation when available. Never prompt.
as_root() {
  if [ "$(id -u)" -eq 0 ]; then
    "$@" 2>&1 || true
  elif have sudo && sudo -n true >/dev/null 2>&1; then
    sudo -n "$@" 2>&1 || true
  else
    return 126
  fi
}

HOST="$(hostname -s 2>/dev/null || hostname)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

echo "===== HOMELAB LINUX HOST AUDIT ====="
echo "audit_timestamp_utc=$STAMP"
echo "hostname=$HOST"
echo "euid=$(id -u)"
echo "audit_mode=READ_ONLY"

section "IDENTITY"
run hostnamectl
echo
run cat /etc/os-release
echo
printf 'fqdn='
hostname -f 2>/dev/null || true
printf 'machine_arch='
uname -m
printf 'kernel='
uname -r

section "HARDWARE IDENTITY"
if have systemd-detect-virt; then
  VIRT="$(systemd-detect-virt 2>/dev/null || true)"
  [ -n "$VIRT" ] || VIRT="none"
  echo "virtualization_environment=$VIRT"
fi

if [ -r /sys/class/dmi/id/sys_vendor ]; then
  printf 'manufacturer='
  cat /sys/class/dmi/id/sys_vendor
fi

if [ -r /sys/class/dmi/id/product_name ]; then
  printf 'model='
  cat /sys/class/dmi/id/product_name
fi

if [ -r /sys/class/dmi/id/product_version ]; then
  printf 'product_version='
  cat /sys/class/dmi/id/product_version
fi

if [ -r /proc/device-tree/model ]; then
  printf 'device_tree_model='
  tr -d '\000' < /proc/device-tree/model
  echo
fi

if have dmidecode; then
  echo
  echo "--- DMI system ---"
  as_root dmidecode -t system |
    grep -E 'Manufacturer:|Product Name:|Version:|Serial Number:' || true

  echo
  echo "--- BIOS / firmware ---"
  as_root dmidecode -t bios |
    grep -E 'Vendor:|Version:|Release Date:' || true
fi

if have vcgencmd; then
  echo
  echo "--- Raspberry Pi firmware state ---"
  run vcgencmd get_throttled
  run vcgencmd measure_temp
fi

section "CPU"
if have lscpu; then
  lscpu |
    grep -E \
      'Architecture:|CPU\(s\):|On-line CPU|Model name:|Socket|Core|Thread|Virtualization:|L1d cache|L1i cache|L2 cache|L3 cache' \
    || true
else
  run cat /proc/cpuinfo
fi

section "MEMORY"
run free -h
echo
run swapon --show
echo
grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo || true

section "BLOCK DEVICES"
if have lsblk; then
  run lsblk -e7 -o NAME,MODEL,SERIAL,SIZE,TYPE,FSTYPE,FSVER,MOUNTPOINTS
fi

section "FILESYSTEM USAGE"
run df -hT

section "LVM"
if have pvs; then
  echo "--- PV ---"
  as_root pvs
  echo
  echo "--- VG ---"
  as_root vgs
  echo
  echo "--- LV ---"
  as_root lvs -a
else
  echo "LVM tools not installed"
fi

section "ZFS"
if have zpool; then
  as_root zpool status
  echo
  as_root zfs list
else
  echo "ZFS not installed"
fi

section "DISK HEALTH"
DISKS=""
if have lsblk; then
  DISKS="$(lsblk -dn -o PATH,TYPE 2>/dev/null |
  awk '$2 == "disk" && $1 !~ /^\/dev\/ram/ && $1 !~ /^\/dev\/zram/ {print $1}')"
fi

if [ -z "$DISKS" ]; then
  echo "No physical block disks discovered"
else
  for disk in $DISKS; do
    echo
    echo "--- $disk ---"

    if have smartctl; then
      SMART_HEALTH="$(as_root smartctl -H "$disk" 2>&1 || true)"
      SMART_DEVICE_ARGS=()

      if printf '%s\n' "$SMART_HEALTH" |
        grep -qiE 'Unknown USB bridge|Please specify device type'; then
        SMART_DEVICE_ARGS=(-d sat)
        echo "smart_transport_retry=SAT"
        SMART_HEALTH="$(as_root smartctl -d sat -H "$disk" 2>&1 || true)"
      fi

      printf '%s\n' "$SMART_HEALTH"
      as_root smartctl "${SMART_DEVICE_ARGS[@]}" -A "$disk" |
        grep -E \
          'SMART overall-health|PASSED|FAILED|Percentage Used|Media_Wearout|Wear_Leveling|Reallocated|Pending|Offline_Uncorrectable|Power_On_Hours|Temperature|Data Units Written|Media and Data Integrity Errors|UDMA_CRC_Error_Count' \
        || true
    elif have nvme && [[ "$disk" == /dev/nvme* ]]; then
      as_root nvme smart-log "$disk" |
        grep -E \
          'critical_warning|temperature|available_spare|percentage_used|data_units_written|power_on_hours|unsafe_shutdowns|media_errors|num_err_log_entries' \
        || true
    else
      echo "No supported disk-health utility available"
    fi
  done
fi

section "NETWORK ADDRESSES"
run ip -br link
echo
run ip -br addr

section "ROUTING"
run ip route
echo
run ip -6 route

section "DNS"
if have resolvectl; then
  run resolvectl status
else
  run cat /etc/resolv.conf
fi

section "PHYSICAL NETWORK LINKS"
for path in /sys/class/net/*; do
  iface="${path##*/}"

  [ "$iface" = "lo" ] && continue
  [ -e "$path/device" ] || continue

  echo "--- $iface ---"

  if have ethtool; then
    ethtool "$iface" 2>/dev/null |
      grep -E 'Speed:|Duplex:|Auto-negotiation:|Link detected:' || true
  fi

  if [ -r "$path/address" ]; then
    printf 'MAC: '
    cat "$path/address"
  fi

  echo
done

section "LISTENING PORTS"
run ss -lntup

section "SYSTEMD FAILED UNITS"
if have systemctl; then
  run systemctl --failed --no-pager
fi

section "RUNNING SERVICES"
if have systemctl; then
  run systemctl --type=service --state=running --no-pager
fi

section "DOCKER"
if have docker; then
  echo "docker_detected=YES"

  echo
  echo "--- version ---"
  docker version --format \
    'server={{.Server.Version}} client={{.Client.Version}}' 2>/dev/null || true

  echo
  echo "--- engine summary ---"
  docker info --format \
    'containers={{.Containers}} running={{.ContainersRunning}} paused={{.ContainersPaused}} stopped={{.ContainersStopped}} images={{.Images}} driver={{.Driver}} cgroup={{.CgroupDriver}}' \
    2>/dev/null || true

  echo
  echo "--- containers ---"
  docker ps -a --no-trunc \
    --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' \
    2>/dev/null || true

  echo
  echo "--- compose projects ---"
  docker compose ls -a 2>/dev/null || true

  echo
  echo "--- container ownership labels ---"
  docker ps -a \
    --format '{{.Names}}|project={{.Label "com.docker.compose.project"}}|service={{.Label "com.docker.compose.service"}}|workdir={{.Label "com.docker.compose.project.working_dir"}}|config={{.Label "com.docker.compose.project.config_files"}}' \
    2>/dev/null || true

  echo
  echo "--- mounts (no environment variables) ---"
  for cid in $(docker ps -aq 2>/dev/null); do
    docker inspect \
      --format '{{.Name}}{{range .Mounts}}|{{.Type}}:{{.Source}}->{{.Destination}}{{end}}' \
      "$cid" 2>/dev/null || true
  done

  echo
  echo "--- volumes ---"
  docker volume ls 2>/dev/null || true

  echo
  echo "--- networks ---"
  docker network ls 2>/dev/null || true
else
  echo "docker_detected=NO"
fi

section "K3S / KUBERNETES"
if have k3s || { have systemctl && systemctl list-unit-files 2>/dev/null | grep -q '^k3s'; }; then
  echo "k3s_detected=YES"

  if have k3s; then
    run k3s --version
    echo
    echo "--- nodes ---"
    as_root k3s kubectl get nodes -o wide
    echo
    echo "--- pods ---"
    as_root k3s kubectl get pods -A -o wide
    echo
    echo "--- services ---"
    as_root k3s kubectl get services -A
  fi
else
  echo "k3s_detected=NO"
fi

section "PI-HOLE / UNBOUND"
PIHOLE_FOUND=0
UNBOUND_FOUND=0

if have pihole; then
  PIHOLE_FOUND=1
  run pihole -v
  run pihole status
fi

if have unbound; then
  UNBOUND_FOUND=1
  echo
  run unbound -V | head -5
  if have systemctl; then
    run systemctl status unbound --no-pager
  fi
fi

if have docker; then
  if docker ps -a --format '{{.Names}} {{.Image}}' 2>/dev/null |
    grep -qiE 'pihole'; then
    PIHOLE_FOUND=1
    echo
    echo "--- containerized Pi-hole ---"
    docker ps -a --format '{{.Names}} {{.Image}} {{.Status}}' 2>/dev/null |
      grep -iE 'pihole' || true
  fi

  if docker ps -a --format '{{.Names}} {{.Image}}' 2>/dev/null |
    grep -qiE 'unbound'; then
    UNBOUND_FOUND=1
    echo
    echo "--- containerized Unbound ---"
    docker ps -a --format '{{.Names}} {{.Image}} {{.Status}}' 2>/dev/null |
      grep -iE 'unbound' || true
  fi
fi

if [ "$PIHOLE_FOUND" -eq 1 ]; then
  echo "pihole_detected=YES"
else
  echo "pihole_detected=NO"
fi

if [ "$UNBOUND_FOUND" -eq 1 ]; then
  echo "unbound_detected=YES"
else
  echo "unbound_detected=NO"
fi

section "BIRDNET"
BIRDNET_FOUND=0

if have systemctl && systemctl list-unit-files 2>/dev/null |
  grep -qiE 'birdnet|birdnet-go'; then
  BIRDNET_FOUND=1
  systemctl list-unit-files 2>/dev/null |
    grep -iE 'birdnet|birdnet-go' || true
fi

if have docker && docker ps -a --format '{{.Names}} {{.Image}}' 2>/dev/null |
  grep -qi 'birdnet'; then
  BIRDNET_FOUND=1
  docker ps -a --format '{{.Names}} {{.Image}} {{.Status}}' 2>/dev/null |
    grep -i 'birdnet' || true
fi

if [ "$BIRDNET_FOUND" -eq 1 ]; then
  echo "birdnet_detected=YES"
else
  echo "birdnet_detected=NO"
fi

section "MONITORING AGENTS"
if have systemctl; then
  systemctl --type=service --state=running --no-pager 2>/dev/null |
    grep -Ei \
      'alloy|prometheus|node.exporter|grafana|loki|zabbix|telegraf|vector' \
    || true
fi

section "THERMALS"
if have sensors; then
  run sensors
else
  FOUND_THERMAL=0
  for zone in /sys/class/thermal/thermal_zone*; do
    [ -r "$zone/temp" ] || continue
    FOUND_THERMAL=1
    type="$(cat "$zone/type" 2>/dev/null || echo unknown)"
    temp="$(cat "$zone/temp" 2>/dev/null || echo 0)"

    awk \
      -v type="$type" \
      -v temp="$temp" \
      'BEGIN {printf "%s: %.1f C\n", type, temp / 1000}'
  done

  [ "$FOUND_THERMAL" -eq 1 ] || echo "No thermal sensors exposed"
fi

section "CURRENT LOAD"
run uptime
echo
ps -eo pid,comm,%cpu,%mem,rss --sort=-%mem 2>/dev/null |
  head -25 || true

section "AUDIT RESULT"
echo "host=$HOST"
echo "audit_timestamp_utc=$STAMP"

if [ "$(id -u)" -eq 0 ]; then
  echo "privileged_hardware_checks=FULL"
elif have sudo && sudo -n true >/dev/null 2>&1; then
  echo "privileged_hardware_checks=FULL_VIA_SUDO_N"
else
  echo "privileged_hardware_checks=PARTIAL_NO_NONINTERACTIVE_ROOT"
fi

echo "linux_host_audit=PASS"
