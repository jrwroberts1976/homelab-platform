# Proxmox Guest Backup and Recovery

**Status:** operationally proven primary guest-backup path; all seven production guests backed up to isolated per-node repositories; final schedule cutover and first unattended run not yet evidenced in this close-out  
**Last validated:** 14 September 2026

## Purpose

This runbook documents the current Proxmox VE guest-backup architecture, validation gates and proven restore procedure.

The two Proxmox nodes are standalone and both contain an unrelated QEMU VMID `200`. Their backup repositories are therefore intentionally isolated so retention/pruning cannot mix the two VM200 backup groups.

## Architecture

```text
PROXMOX .70
  media-backup-proxmox
  -> NFS v4.2/TCP -> media-01 .195:/srv/backup/pve-proxmox

Proxmox-2 .71
  media-backup-proxmox-2
  -> NFS v4.2/TCP -> media-01 .195:/srv/backup/pve-proxmox-2

Legacy rollback only
  media-backup
  -> media-01 .195:/srv/backup/pve
```

The isolated exports are client-specific:

```text
/srv/backup/pve-proxmox   -> 192.168.2.70 only
/srv/backup/pve-proxmox-2 -> 192.168.2.71 only
```

The legacy `/srv/backup/pve` export remains temporarily available as rollback evidence. Do not use it for new production retention while the hosts are standalone and both contain VMID 200.

## Current guest scope

```text
PROXMOX .70 -> media-backup-proxmox
  CT100 dns-02
  CT102 mail-relay-01
  VM200 cloud-01
  VM201 sensor-01

Proxmox-2 .71 -> media-backup-proxmox-2
  CT101 dns-01
  CT103 edge-01
  VM200 monitor-01
```

Templates 9000/9001 are excluded from the initial production schedule.

All seven production guests have completed a successful snapshot-mode manual backup proof to the correct isolated namespace.

## Service availability during backup

Production backup mode is `snapshot`.

VMs remain running during backup. LXC containers remain running; Proxmox may briefly freeze them while taking the snapshot. This is not a stop-mode backup and services should not be offline for the duration of the archive copy.

## Local vzdump workspace

Unprivileged LXC backup initially failed when `vzdump` used an NFS-hosted temporary workspace that the remapped UID could not enter.

The approved local temporary workspace on both hypervisors is:

```text
tmpdir: /var/lib/vz/vzdump-tmp
```

Required state:

- owner `root`;
- group `root`;
- mode `1777`;
- deployment free-space gate: 20 GiB;
- UID 100000 write test passes;
- workspace is clean after validation.

Do not make the NFS backup repository broadly writable to solve an LXC temporary-workspace problem.

## IaC authority

Relevant playbooks:

```text
IaC/ansible/playbooks/media-backup-target.yml
IaC/ansible/playbooks/media-backup-split-prep.yml
IaC/ansible/playbooks/proxmox-backup-storage.yml
IaC/ansible/playbooks/proxmox-backup-storage-split.yml
IaC/ansible/playbooks/proxmox-vzdump-runtime.yml
IaC/ansible/playbooks/proxmox-notification-recipient.yml
IaC/ansible/playbooks/proxmox-mail-relay-client.yml
IaC/ansible/playbooks/proxmox-backup-schedule.yml
```

Relevant roles:

```text
IaC/ansible/roles/media_backup_target/
IaC/ansible/roles/media_backup_split_prep/
IaC/ansible/roles/proxmox_backup_storage/
IaC/ansible/roles/proxmox_backup_storage_split/
IaC/ansible/roles/proxmox_vzdump_runtime/
IaC/ansible/roles/proxmox_notification_recipient/
IaC/ansible/roles/proxmox_mail_relay_client/
IaC/ansible/roles/proxmox_backup_schedule/
```

All deployment roles use explicit approval gates and fail closed on unexpected host/storage/schedule state.

## Notification path

Both PVE nodes use PVE's notification system. The built-in `default-matcher` routes notifications to `mail-to-root`.

Both nodes relay through:

```text
relayhost = [192.168.2.54]:25
```

`mail-relay-01` authenticates upstream to Gmail over TLS on `smtp.gmail.com:587`.

The complete path was proven from both hypervisors:

```text
Proxmox -> mail-relay-01 -> Gmail relay -> recipient
```

Historical stale queue entries on `Proxmox-2` were removed after the successful delivery proof.

## Backup proof

### Proxmox-2

A complete production backup set was proven for:

```text
CT101 dns-01
CT103 edge-01
VM200 monitor-01
```

The resulting legacy-source artifacts were copied into `/srv/backup/pve-proxmox-2/dump` and validated by matching names and byte sizes before `media-backup-proxmox-2` was registered.

### PROXMOX

A complete isolated production backup set was proven directly to `media-backup-proxmox` for:

```text
CT100 dns-02
CT102 mail-relay-01
VM200 cloud-01
VM201 sensor-01
```

Post-backup storage remained healthy with substantial free capacity and zero failed systemd units.

## Proven restore test

CT103 (`edge-01`) was restored on `Proxmox-2` under temporary VMID `903`.

Safety controls:

1. source CT103 confirmed running;
2. temporary VMID confirmed unused;
3. embedded backup configuration inspected;
4. restore performed to `local-lvm`;
5. restored guest kept stopped initially;
6. restored production network interfaces removed before boot;
7. hostname changed to a restore-test identity;
8. filesystem inspected offline;
9. restored container booted without a production network interface;
10. OS/filesystem verified;
11. temporary guest stopped and destroyed;
12. temporary VMID/LV absence confirmed;
13. live CT103 and source backup confirmed intact.

Result:

```text
archive_config_gate=PASS
network_isolation=PASS
offline_filesystem_restore=PASS
isolated_boot=PASS
temporary_restore_removed=PASS
restore_proof=PASS
```

This proves the LXC backup path is restorable, not merely writable.

A QEMU VM restore proof remains pending.

## Manual backup commands

Use the host-specific storage ID.

`PROXMOX`:

```bash
vzdump 100 102 200 201 \
  --storage media-backup-proxmox \
  --mode snapshot \
  --compress zstd \
  --prune-backups 'keep-last=3' \
  --notification-mode notification-system
```

`Proxmox-2`:

```bash
vzdump 101 103 200 \
  --storage media-backup-proxmox-2 \
  --mode snapshot \
  --compress zstd \
  --prune-backups 'keep-last=3' \
  --notification-mode notification-system
```

Because `/etc/vzdump.conf` defines the approved local tmpdir, normal commands do not need a separate `--tmpdir` argument.

## Manual restore procedure

1. Identify the correct host-specific backup storage.
2. List candidate volumes with `pvesm list <storage-id> --content backup`.
3. Inspect embedded configuration with `pvesm extractconfig <volid>` where applicable.
4. Select a proven-unused temporary VMID for a test restore.
5. Restore to suitable local storage while keeping the guest stopped.
6. Remove/replace production networking before first test boot.
7. Inspect the restored filesystem offline where possible.
8. Boot only after network isolation is verified.
9. For test restores, destroy the temporary guest after evidence is captured.
10. For production recovery, deliberately reconcile hostname, MAC/IP identity, secrets, dependencies and service ownership before returning the guest to the LAN.

Never boot a cloned restore with the original production network identity while the live source guest still exists.

## Schedule and retention

Approved IaC policy:

```text
PROXMOX
  id: homelab-nightly-proxmox
  time: 02:15
  storage: media-backup-proxmox
  guests: 100,102,200,201

Proxmox-2
  id: homelab-nightly-proxmox-2
  time: 03:15
  storage: media-backup-proxmox-2
  guests: 101,103,200

mode: snapshot
compression: zstd
retention: keep-last=3
notification-mode: notification-system
```

The jobs were deliberately disabled when the shared-namespace collision was found. The current IaC allows only a controlled transition from the disabled legacy job to its approved isolated storage and validates a proven archive for every guest before enabling the job.

At this close-out the cutover playbook is syntax-valid, but the supplied evidence does not include the final live cutover result or first unattended run. Keep those as operational validation items rather than documenting them as already proven.

## Failure handling

If a backup fails:

1. do not delete the last known-good backup;
2. verify the source guest is healthy;
3. inspect the `vzdump` task log and local tmpdir;
4. inspect the correct isolated storage with `pvesm status --storage <storage-id>`;
5. inspect the matching NFS export and `media-01` capacity;
6. verify `/var/lib/vz/vzdump-tmp` remains mode `1777` with sufficient free space;
7. verify notification delivery through `mail-relay-01`;
8. correct drift through IaC where practical;
9. repeat a controlled manual proof if the fault affected the backup path itself.

## Known limitations

- `media-01` is the primary guest-backup target, so its own `/srv/media` data is not protected by these repositories.
- There is no independent secondary copy yet.
- QEMU VM restore is not yet proven.
- `cloud-01` still needs application-consistent Nextcloud/PostgreSQL recovery proof.
- `docker-01`, controller recovery state and other non-Proxmox persistent data need explicit protection.
- The suspect 4 TB WD disk on `PROXMOX` must not become the sole trusted copy of important data.
- A successful VM/LXC image backup does not automatically prove application-consistent database recovery.

## Future cluster note

The two PVE nodes are currently standalone. A future cluster may be reconsidered when dedicated Corosync networking and quorum/QDevice design are approved.

Until then, preserve the isolated backup namespaces because both hosts contain an unrelated VMID `200`.
