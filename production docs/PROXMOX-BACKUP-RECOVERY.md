<!-- estate-authority: IaC/inventory/estate.json -->
# Proxmox Guest Backup and Recovery

**Status:** OPERATIONAL PRIMARY GUEST-BACKUP PATH  
**Last current-state review:** 6 October 2026

## Purpose

This runbook documents the current `jameshouse-pve` guest-backup architecture, safety gates and recovery procedure.

The two PVE nodes are cluster members. Production IDs are cluster-unique and backups remain intentionally node-scoped onto `media-01` NFS exports.

## Architecture

```text
PROXMOX .70
  storage: media-backup-proxmox
  -> NFS v4.2/TCP -> media-01 .195:/srv/backup/pve-proxmox

Proxmox-2 .71
  storage: media-backup-proxmox-2
  -> NFS v4.2/TCP -> media-01 .195:/srv/backup/pve-proxmox-2
```

Exports are client-restricted to their corresponding PVE nodes.

## Current scheduled guest scope

```text
PROXMOX .70
  CT100 dns-02
  CT102 mail-relay-01
  CT104 komodo-01
  CT105 zabbix-01
  VM200 cloud-01
  VM201 sensor-01
  VM204 home-01

Proxmox-2 .71
  CT101 dns-01
  CT103 edge-01
  VM202 monitor-01
  VM203 greenbone-01
```

Templates 9000/9001 are excluded.

## Schedule and retention

```text
PROXMOX
  id: homelab-nightly-proxmox
  time: 02:15
  storage: media-backup-proxmox
  guests: 100,102,104,105,200,201,204

Proxmox-2
  id: homelab-nightly-proxmox-2
  time: 03:15
  storage: media-backup-proxmox-2
  guests: 101,103,202,203

mode: snapshot
compression: zstd
retention: keep-last=3
notification-mode: notification-system
```

The job definitions are reconciled through IaC.

## Current evidence state

Observed/proven evidence includes:

- CT103 isolated LXC restore/boot proof;
- CT104 manual snapshot/integrity proof;
- CT105 manual proof and unattended scheduled evidence;
- VM203 manual proof and unattended scheduled evidence;
- unattended CT101/CT103/VM202 evidence;
- VM204 native Home Assistant backup and manual Proxmox snapshot/integrity proof;
- notification delivery through `mail-relay-01`.

Current explicit schedule-evidence gaps:

- first unattended scheduled CT104 proof;
- first unattended scheduled VM204 proof;
- representative isolated QEMU VM restore proof.

Do not continue to list CT105 or VM203 first-unattended proof as pending.

## Service availability during backup

Production mode is `snapshot`.

VMs remain running. LXC guests remain running, although Proxmox may briefly freeze a container while creating a snapshot. This is not a stop-mode schedule.

## Local vzdump workspace

Approved local temporary workspace on both hypervisors:

```text
/var/lib/vz/vzdump-tmp
```

Required state:

- owner/group `root:root`;
- mode `1777`;
- adequate local free space;
- unprivileged LXC remapped-UID write validation where applicable.

Do not weaken NFS repository permissions to solve temporary-workspace problems.

## IaC authority

Relevant automation includes:

```text
IaC/ansible/playbooks/media-backup-target.yml
IaC/ansible/playbooks/proxmox-backup-storage.yml
IaC/ansible/playbooks/proxmox-vzdump-runtime.yml
IaC/ansible/playbooks/proxmox-notification-recipient.yml
IaC/ansible/playbooks/proxmox-mail-relay-client.yml
IaC/ansible/playbooks/proxmox-backup-schedule.yml
```

Deployment roles use identity/approval checks and should fail closed on unexpected storage or schedule state.

## Notification path

Both PVE nodes use the Proxmox notification system and relay mail through:

```text
mail-relay-01 192.168.2.54:25
```

The external delivery path is:

```text
Proxmox -> mail-relay-01 -> Gmail SMTP relay -> recipient
```

## Manual backup commands

Confirm current placement and storage health before running a manual backup.

`PROXMOX`:

```bash
vzdump 100 102 104 105 200 201 204 \
  --storage media-backup-proxmox \
  --mode snapshot \
  --compress zstd \
  --prune-backups 'keep-last=3' \
  --notification-mode notification-system
```

`Proxmox-2`:

```bash
vzdump 101 103 202 203 \
  --storage media-backup-proxmox-2 \
  --mode snapshot \
  --compress zstd \
  --prune-backups 'keep-last=3' \
  --notification-mode notification-system
```

Normal commands use the approved `/etc/vzdump.conf` tmpdir.

## Proven LXC restore method

CT103 was restored under a temporary unused VMID with production networking removed before boot. The proof demonstrated:

```text
archive_config_gate=PASS
network_isolation=PASS
offline_filesystem_restore=PASS
isolated_boot=PASS
temporary_restore_removed=PASS
restore_proof=PASS
```

This proves the LXC archive path is restorable rather than merely writable.

## Manual restore procedure

1. Verify the intended source node/storage and list candidate backup volumes.
2. Inspect embedded guest configuration before restore.
3. Select a confirmed-unused temporary VMID for a test restore.
4. Restore to suitable local storage while keeping the guest stopped.
5. Remove or replace production networking before first test boot.
6. Inspect the restored filesystem/configuration offline where practical.
7. Boot only after identity/network isolation is verified.
8. Validate OS/application data appropriate to the test scope.
9. Destroy temporary test restores after evidence capture.
10. For real production recovery, deliberately reconcile hostname, MAC/IP, secrets, dependencies and service ownership before reconnecting to the LAN.

Never boot a cloned restore with the original production network identity while the live source still exists.

## Failure handling

If a backup fails:

1. preserve the last known-good archive;
2. verify the source guest is healthy and on the expected node;
3. inspect the PVE task/vzdump log;
4. validate the correct node-scoped `pvesm` storage;
5. verify the matching `media-01` NFS export/capacity;
6. verify the local tmpdir permissions/free space;
7. verify notification delivery;
8. compare scheduled VMIDs with current cluster placement;
9. correct configuration drift through IaC;
10. repeat a controlled manual proof if the backup path itself was affected.

## Cluster migration rollback state

Pre-cluster local rollback LVs on `Proxmox-2` are retained only as historical/rollback evidence and are **not active guest disks**. Remove them only through a separately reviewed cleanup after backup/recovery confidence is explicit.

## Known limitations

- `media-01` is the primary guest-backup target, so this is not an independent second failure domain;
- representative QEMU VM restore is not yet proven;
- `cloud-01` still needs application-consistent Nextcloud/PostgreSQL recovery proof;
- non-Proxmox persistent data such as BirdNET application state requires its own protection strategy;
- a VM/LXC image backup does not by itself prove application-consistent database recovery;
- cluster quorum does not make node-local guest disks available on the surviving node after storage/node loss.

## Current recovery goals

1. capture unattended CT104 and VM204 schedule evidence;
2. perform a representative isolated QEMU restore;
3. prove application-consistent `cloud-01` recovery;
4. add an independent second copy/failure domain for important data and recovery material.
