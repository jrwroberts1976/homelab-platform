# Proxmox Guest Backup and Recovery

**Status:** operationally proven primary guest-backup path; final cluster-era schedule requires VM202/job reconciliation and fresh unattended proof  
**Last validated:** 14 September 2026

## Purpose

This runbook documents the current Proxmox VE guest-backup architecture, validation gates and proven restore procedure.

The two PVE nodes are now members of `jameshouse-pve`. Production guest IDs are cluster-unique, with `monitor-01` now VM202 on `Proxmox-2`.

The two existing NFS backup namespaces remain intentionally node-scoped because they are already deployed and proven. Cluster membership makes a single shared namespace technically possible, but there is no operational requirement to collapse the current design before fresh cluster-era backup evidence exists.

## Architecture

```text
PROXMOX .70
  media-backup-proxmox
  node scope: PROXMOX
  -> NFS v4.2/TCP -> media-01 .195:/srv/backup/pve-proxmox

Proxmox-2 .71
  media-backup-proxmox-2
  node scope: Proxmox-2
  -> NFS v4.2/TCP -> media-01 .195:/srv/backup/pve-proxmox-2

Legacy rollback
  media-backup
  -> media-01 .195:/srv/backup/pve
```

The host-specific exports are client-restricted:

```text
/srv/backup/pve-proxmox   -> 192.168.2.70 only
/srv/backup/pve-proxmox-2 -> 192.168.2.71 only
```

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
  VM202 monitor-01
```

Templates 9000/9001 are excluded from the production schedule.

All seven workloads had successful snapshot-mode backup evidence before cluster formation. CT101 and CT103 have since moved back to `Proxmox-2`, and monitor has changed from the old standalone VMID 200 to cluster VMID 202. Fresh cluster-era backup evidence is therefore required for the final `.71` set.

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

All deployment roles use explicit approval gates and should fail closed on unexpected host/storage/schedule state.

The backup schedule IaC must be reconciled from the former `Proxmox-2` VMID 200 monitor entry to VMID 202 before it is treated as current authority for the cluster-era `.71` job.

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

## Historical backup proof

### Pre-cluster Proxmox-2

A complete production backup set was proven for the then-current standalone identities:

```text
CT101 dns-01
CT103 edge-01
VM200 monitor-01
```

That VM200 archive remains useful historical recovery evidence for the pre-cluster monitor identity. It does not replace the need for a new VM202 backup.

### PROXMOX

A complete production backup set was proven directly to `media-backup-proxmox` for:

```text
CT100 dns-02
CT102 mail-relay-01
VM200 cloud-01
VM201 sensor-01
```

### Cluster migration backups

Fresh stop-mode migration backups of CT101, CT103 and the old monitor VM200 were also taken immediately before the `Proxmox-2` join. Those archives and saved guest configuration were retained as rollback evidence during cluster formation.

## Proven restore test

CT103 (`edge-01`) was restored on `Proxmox-2` under temporary VMID `903` before cluster formation.

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

Use the node-scoped storage ID.

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
vzdump 101 103 202 \
  --storage media-backup-proxmox-2 \
  --mode snapshot \
  --compress zstd \
  --prune-backups 'keep-last=3' \
  --notification-mode notification-system
```

Because `/etc/vzdump.conf` defines the approved local tmpdir, normal commands do not need a separate `--tmpdir` argument.

Before running a cluster-era manual backup, verify that the storage is active on the intended node and that the guest IDs are currently placed there.

## Manual restore procedure

1. Identify the correct node-scoped backup storage.
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

Intended post-cluster policy:

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
  guests: 101,103,202

mode: snapshot
compression: zstd
retention: keep-last=3
notification-mode: notification-system
```

The old standalone schedule was previously proven with `Proxmox-2` guests `101,103,200`. Cluster formation changed that identity to VM202 and replaced the joining node's `/etc/pve` state with the cluster filesystem.

Therefore do **not** claim the final `Proxmox-2` job is proven merely from the old pre-cluster validation.

Post-cluster schedule closeout requires:

```text
PROXMOX storage=media-backup-proxmox
PROXMOX schedule=02:15
PROXMOX vmids=100,102,200,201

Proxmox-2 storage=media-backup-proxmox-2
Proxmox-2 schedule=03:15
Proxmox-2 vmids=101,103,202

mode=snapshot
compression=zstd
notification-mode=notification-system
keep-last=3
```

Then prove:

- IaC reconciliation is idempotent;
- fresh backup archives exist for final cluster-era identities;
- VM202 archive is readable and integrity-checked;
- the first unattended post-cluster run succeeds;
- notifications are delivered.

## Cluster migration rollback state

The old `Proxmox-2` local volumes were renamed before guest migration rather than deleted:

```text
precluster-20260914-vm-101-disk-0
precluster-20260914-vm-103-disk-0
precluster-20260914-vm-200-cloudinit
precluster-20260914-vm-200-disk-0
```

They are **not active guest disks**. They are temporary rollback evidence.

Do not delete them until fresh cluster-era backups and the final placement have been explicitly accepted. Once they are retired, record the removal so the LVs cannot later be mistaken for active or unexplained storage.

## Failure handling

If a backup fails:

1. do not delete the last known-good backup;
2. verify the source guest is healthy and on the expected cluster node;
3. inspect the `vzdump` task log and local tmpdir;
4. inspect the correct node-scoped storage with `pvesm status --storage <storage-id>`;
5. inspect the matching NFS export and `media-01` capacity;
6. verify `/var/lib/vz/vzdump-tmp` remains mode `1777` with sufficient free space;
7. verify notification delivery through `mail-relay-01`;
8. verify the scheduled VMID list has not drifted from cluster placement;
9. correct drift through IaC where practical;
10. repeat a controlled manual proof if the fault affected the backup path itself.

## Known limitations

- `media-01` is the primary guest-backup target, so its own `/srv/media` data is not protected by these repositories.
- There is no independent secondary copy yet.
- QEMU VM restore is not yet proven.
- `cloud-01` still needs application-consistent Nextcloud/PostgreSQL recovery proof.
- `docker-01`, controller recovery state and other non-Proxmox persistent data need explicit protection.
- The suspect 4 TB WD disk on `PROXMOX` must not become the sole trusted copy of important data.
- A successful VM/LXC image backup does not automatically prove application-consistent database recovery.
- Cluster quorum does not make node-local `local-lvm` disks available on another node after a hardware failure.

## Cluster note

`jameshouse-pve` is now the production Proxmox platform. It uses dedicated Corosync link0, LAN fallback link1 and a QDevice on `admin-01`.

The cluster has removed the old duplicate-VMID constraint: `cloud-01` is VM200 and `monitor-01` is VM202.

The current node-scoped backup namespaces may be retained indefinitely if they remain operationally useful. Any future consolidation to one cluster-wide namespace must be treated as a separate controlled change with fresh backup/restore proof rather than assumed to be necessary.
