#!/usr/bin/env bash

set -eu

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

TARGET_HOST="${PVE_HOST:-}"
TARGET_NAME="${PVE_NAME:-}"
ROOTFS_STORAGE="${PVE_ROOTFS_STORAGE:-local-lvm}"
VG_NAME="${PVE_VG_NAME:-pve}"
THINPOOL_NAME="${PVE_THINPOOL_NAME:-data}"
TEMPLATE_STORAGE="${PVE_TEMPLATE_STORAGE:-local}"
TEMPLATE_NAME="${PVE_TEMPLATE_NAME:-debian-13-standard_13.6-1_amd64.tar.zst}"
ROOT_KEY="${PVE_ROOT_SSH_KEY:-$HOME/.ssh/proxmox-root}"

[ -n "$TARGET_HOST" ] || die "PVE_HOST is required"
[ -n "$TARGET_NAME" ] || die "PVE_NAME is required"
[ -r "$ROOT_KEY" ] || die "Missing root SSH key: $ROOT_KEY"

SSH=(ssh -i "$ROOT_KEY" -o BatchMode=yes -o ConnectTimeout=5 "root@$TARGET_HOST")

printf '===== PROXMOX NODE BOOTSTRAP =====\n'
printf 'name=%s\n' "$TARGET_NAME"
printf 'host=%s\n' "$TARGET_HOST"
printf 'rootfs_storage=%s\n' "$ROOTFS_STORAGE"
printf 'vg=%s\n' "$VG_NAME"
printf 'thinpool=%s\n' "$THINPOOL_NAME"
printf 'template=%s:%s\n' "$TEMPLATE_STORAGE" "$TEMPLATE_NAME"

printf '\n===== NODE HEALTH =====\n'
"${SSH[@]}" "test \"\$(hostname)\" = '$TARGET_NAME' && systemctl is-active --quiet pve-cluster && mountpoint -q /etc/pve" \
  || die "Node identity or pve-cluster filesystem check failed"

printf '\n===== LVM THINPOOL =====\n'
"${SSH[@]}" "lvs --noheadings -o lv_name,vg_name,lv_attr | awk '\$1==\"$THINPOOL_NAME\" && \$2==\"$VG_NAME\" && \$3 ~ /^twi/ {found=1} END{exit !found}'" \
  || die "Expected LVM-thin pool $VG_NAME/$THINPOOL_NAME does not exist"

printf '\n===== PROXMOX STORAGE =====\n'
if "${SSH[@]}" "pvesh get /storage/$ROOTFS_STORAGE >/dev/null 2>&1"; then
  printf '%s already registered\n' "$ROOTFS_STORAGE"
else
  "${SSH[@]}" "pvesm add lvmthin '$ROOTFS_STORAGE' --vgname '$VG_NAME' --thinpool '$THINPOOL_NAME' --content rootdir,images"
fi

"${SSH[@]}" "pvesh get /storage/$ROOTFS_STORAGE --output-format yaml"

printf '\n===== DEBIAN TEMPLATE =====\n'
if "${SSH[@]}" "pveam list '$TEMPLATE_STORAGE' | awk '{print \$1}' | grep -Fxq '$TEMPLATE_STORAGE:vztmpl/$TEMPLATE_NAME'"; then
  printf '%s already present\n' "$TEMPLATE_NAME"
else
  "${SSH[@]}" "pveam update >/dev/null && pveam download '$TEMPLATE_STORAGE' '$TEMPLATE_NAME'"
fi

"${SSH[@]}" "pveam list '$TEMPLATE_STORAGE' | grep -F '$TEMPLATE_NAME'"

printf '\n===== IAC ROLES =====\n'
"${SSH[@]}" "pveum role add HomelabIaCNode -privs 'Sys.AccessNetwork Sys.Audit Sys.Modify' 2>/dev/null || pveum role modify HomelabIaCNode -privs 'Sys.AccessNetwork Sys.Audit Sys.Modify'"
"${SSH[@]}" "pveum role add HomelabIaCStorage -privs 'Datastore.AllocateSpace Datastore.AllocateTemplate Datastore.Audit' 2>/dev/null || pveum role modify HomelabIaCStorage -privs 'Datastore.AllocateSpace Datastore.AllocateTemplate Datastore.Audit'"
"${SSH[@]}" "pveum role add HomelabIaCVM -privs 'VM.Allocate VM.Audit VM.Clone VM.Config.CDROM VM.Config.CPU VM.Config.Cloudinit VM.Config.Disk VM.Config.HWType VM.Config.Memory VM.Config.Network VM.Config.Options VM.GuestAgent.Audit VM.PowerMgmt' 2>/dev/null || pveum role modify HomelabIaCVM -privs 'VM.Allocate VM.Audit VM.Clone VM.Config.CDROM VM.Config.CPU VM.Config.Cloudinit VM.Config.Disk VM.Config.HWType VM.Config.Memory VM.Config.Network VM.Config.Options VM.GuestAgent.Audit VM.PowerMgmt'"

printf '\n===== IAC USER / ACLS =====\n'
"${SSH[@]}" "pveum user add iac@pve 2>/dev/null || true"
"${SSH[@]}" "pveum acl modify /nodes/$TARGET_NAME -user iac@pve -role HomelabIaCNode -propagate 1"
"${SSH[@]}" "pveum acl modify /storage/$TEMPLATE_STORAGE -user iac@pve -role HomelabIaCStorage -propagate 1"
"${SSH[@]}" "pveum acl modify /storage/$ROOTFS_STORAGE -user iac@pve -role HomelabIaCStorage -propagate 1"
"${SSH[@]}" "pveum acl modify /vms -user iac@pve -role HomelabIaCVM -propagate 1"
"${SSH[@]}" "pveum acl modify /sdn/zones/localnetwork/vmbr0 -user iac@pve -role PVESDNUser -propagate 1"

printf '\n===== TOKEN STATUS =====\n'
if "${SSH[@]}" "pveum user token list iac@pve | awk 'NR>1 {print \$2}' | grep -Fxq opentofu"; then
  printf 'iac@pve!opentofu already exists\n'
else
  printf 'TOKEN_REQUIRED: create iac@pve!opentofu manually or with the approved secret-capture procedure.\n'
  printf 'The bootstrap script deliberately does not print or persist a newly-created token secret.\n'
fi

printf '\n===== RESULT =====\n'
printf 'Node platform prerequisites are ready. API token presence must be confirmed separately.\n'
