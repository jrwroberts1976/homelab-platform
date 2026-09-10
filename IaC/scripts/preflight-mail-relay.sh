#!/usr/bin/env bash

set -u

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

MAIL_RELAY_HOSTNAME="${MAIL_RELAY_HOSTNAME:-mail-relay-01}"
MAIL_RELAY_IPV4="${MAIL_RELAY_IPV4:-192.168.2.54}"
MAIL_RELAY_CT_ID="${MAIL_RELAY_CT_ID:-102}"

PVE1="192.168.2.70"
PVE2="192.168.2.71"
PVE_ROOT_SSH_KEY="$HOME/.ssh/proxmox-root"
TEMPLATE="local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"
DATASTORE="vm-ssd"

for cmd in ssh ping dig; do
  command -v "$cmd" >/dev/null 2>&1 || die "Required command not found: $cmd"
done

[ -r "$PVE_ROOT_SSH_KEY" ] || die "Missing root SSH key: $PVE_ROOT_SSH_KEY"

printf '===== MAIL RELAY PREFLIGHT =====\n'
printf 'hostname=%s\n' "$MAIL_RELAY_HOSTNAME"
printf 'candidate_ipv4=%s\n' "$MAIL_RELAY_IPV4"
printf 'candidate_ct_id=%s\n' "$MAIL_RELAY_CT_ID"
printf 'target=PROXMOX (%s)\n' "$PVE1"

printf '\n===== ROOT SSH =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$PVE1" true   || die "Cannot reach PROXMOX with root automation key"
printf 'PROXMOX=PASS\n'

ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$PVE2" true   || die "Cannot reach Proxmox-2 with root automation key"
printf 'Proxmox-2=PASS\n'

printf '\n===== CT ID CHECK =====\n'
for host in "$PVE1" "$PVE2"; do
  if ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$host"       "pct config '$MAIL_RELAY_CT_ID' >/dev/null 2>&1"; then
    die "CT/VM ID $MAIL_RELAY_CT_ID already exists on $host"
  fi
  printf '%s id_%s=FREE\n' "$host" "$MAIL_RELAY_CT_ID"
done

printf '\n===== IP CHECK FROM TESTSERVER =====\n'
if ping -c 1 -W 1 "$MAIL_RELAY_IPV4" >/dev/null 2>&1; then
  die "$MAIL_RELAY_IPV4 answers ICMP"
fi
printf 'icmp=NO_REPLY\n'

printf '\n===== IP CHECK FROM PROXMOX =====\n'
NEIGH="$(ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE1"   "ping -c 1 -W 1 '$MAIL_RELAY_IPV4' >/dev/null 2>&1 || true; ip neigh show '$MAIL_RELAY_IPV4'")"

if printf '%s\n' "$NEIGH" | grep -q 'lladdr'; then
  printf '%s\n' "$NEIGH"
  die "$MAIL_RELAY_IPV4 has a LAN neighbour entry and is not safe to claim"
fi
printf 'arp_neighbour=NONE\n'

printf '\n===== DNS NAME CHECK =====\n'
for resolver in 192.168.2.51 192.168.2.50; do
  answer="$(dig +short "@$resolver" "$MAIL_RELAY_HOSTNAME.jameshouse" A)"
  [ -z "$answer" ] || die "$MAIL_RELAY_HOSTNAME.jameshouse already resolves via $resolver to $answer"
  printf '%s name=FREE\n' "$resolver"
done

printf '\n===== STORAGE / TEMPLATE =====\n'
ssh -i "$PVE_ROOT_SSH_KEY" -o BatchMode=yes "root@$PVE1"   "pvesm status --storage '$DATASTORE' >/dev/null && pvesm path '$TEMPLATE' >/dev/null"   || die "Required vm-ssd datastore or Debian 13 template is unavailable"
printf 'datastore=%s PASS\n' "$DATASTORE"
printf 'template=%s PASS\n' "$TEMPLATE"

printf '\n===== RESULT: PASS =====\n'
printf 'Approved candidate: %s = %s, CT %s on PROXMOX.\n'   "$MAIL_RELAY_HOSTNAME" "$MAIL_RELAY_IPV4" "$MAIL_RELAY_CT_ID"
printf 'No infrastructure changes were made.\n'
