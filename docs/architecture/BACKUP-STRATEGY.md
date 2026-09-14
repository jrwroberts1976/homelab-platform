# Backup Strategy

**Status:** primary Proxmox guest-backup platform proven before cluster formation; node-scoped NFS repositories remain operational; post-cluster schedule/VM202 reconciliation and fresh unattended proof remain open  
**Reviewed:** 14 September 2026

## Requirement

The homelab backup platform must provide clear job/status visibility, browsable backup sets, restore operations, verification/health visibility, deliberate retention, documented recovery and real restore testing.

Git/IaC remains the source of truth for deployment, storage registration, schedule policy and recovery configuration where practical. GUI-only drift is not authoritative configuration.

## Current state

The estate has a proven primary Proxmox guest-backup platform using native Proxmox `vzdump` backups to NFS storage on `media-01`.

The two hypervisors are now members of the `jameshouse-pve` cluster and all production guest VMIDs are cluster-unique. The pre-cluster repository split remains in service because it is already proven and provides clear node-scoped ownership; there is no requirement to collapse it merely because cluster membership now exists.

```text
PROXMOX .70
  media-backup-proxmox
  -> media-01:/srv/backup/pve-proxmox
  nodes: PROXMOX

Proxmox-2 .71
  media-backup-proxmox-2
  -> media-01:/srv/backup/pve-proxmox-2
  nodes: Proxmox-2

Legacy rollback namespace retained temporarily:
  media-backup
  -> media-01:/srv/backup/pve
```

The separate host-specific exports remain restricted to their intended hypervisor addresses.

### Proven pre-cluster state on 14 September 2026

Before cluster formation the following were proven:

```text
media-01 NFS service: active
NFS v4.2/TCP: proven
per-node isolated exports: active
per-node PVE storage registration: active
legacy media-backup rollback storage: preserved
local vzdump tmpdir: proven on both PVE nodes
all seven production guest backups: proven
archive integrity checks: proven
CT103 isolated LXC restore + boot: proven
notification delivery through mail-relay-01: proven end to end
retention policy: keep-last=3
standalone PROXMOX nightly job: enabled, 02:15, media-backup-proxmox
standalone Proxmox-2 nightly job: enabled, 03:15, media-backup-proxmox-2
schedule mode/compression: snapshot / zstd
schedule notification mode: notification-system
schedule reconciliation: idempotent, changed=0 on both nodes
failed systemd units during final pre-cluster cutover validation: 0
```

That evidence remains valid proof that the backup transport, archives, notification path and LXC restore mechanism worked. It must not be misrepresented as proof that the final cluster-era job definitions are already correct, because cluster formation changed `monitor-01` from VMID `200` to VMID `202` and replaced cluster-wide `/etc/pve` job configuration during the join.

### Current cluster-era guest scope

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

Templates 9000/9001 remain excluded from the production backup schedule.

## Backup target

`media-01` is the phase-one primary guest-backup target.

```text
host: media-01
address: 192.168.2.195
filesystem: NVMe-backed ext4
protocol: NFS v4.2/TCP
content: Proxmox backup only
```

Host-specific exports:

```text
/srv/backup/pve-proxmox
  authorised client: 192.168.2.70
  PVE storage ID: media-backup-proxmox
  cluster node scope: PROXMOX

/srv/backup/pve-proxmox-2
  authorised client: 192.168.2.71
  PVE storage ID: media-backup-proxmox-2
  cluster node scope: Proxmox-2
```

Legacy rollback export:

```text
/srv/backup/pve
  PVE storage ID: media-backup
```

The repositories remain root-owned. Do not make them broadly writable to work around unprivileged-LXC UID mapping.

## Local vzdump workspace

The first unprivileged LXC backup attempt failed because `vzdump` attempted to use an NFS-hosted temporary workspace that the remapped container UID could not enter.

The approved solution is a local workspace on each hypervisor:

```text
tmpdir: /var/lib/vz/vzdump-tmp
```

Required state:

- owner `root`;
- group `root`;
- mode `1777`;
- at least 20 GiB free at deployment time;
- UID 100000 write proof passes;
- workspace is clean after validation.

## Restore proof

CT103 (`edge-01`) completed an isolated restore proof before the cluster migration.

The restored container was created under temporary VMID `903`, kept stopped initially, stripped of production networking, inspected offline, booted without a production network interface and then removed after validation.

```text
archive_config_gate=PASS
network_isolation=PASS
offline_filesystem_restore=PASS
isolated_boot=PASS
temporary_restore_removed=PASS
restore_proof=PASS
```

This proves the LXC backup path is restorable, not merely writable.

A representative QEMU VM restore proof remains required.

## Notifications

Both Proxmox nodes use PVE's notification system. The built-in `default-matcher` routes notifications to `mail-to-root`, and `root@pam` has the approved recipient configured.

Both hypervisors relay through:

```text
[192.168.2.54]:25
```

`mail-relay-01` then authenticates to Gmail over TLS on `smtp.gmail.com:587`.

End-to-end notification tests from both PVE nodes completed successfully.

## Schedule and retention policy

The intended cluster-era policy is:

```text
PROXMOX .70
  job: homelab-nightly-proxmox
  schedule: 02:15
  target: media-backup-proxmox
  guests: 100,102,200,201

Proxmox-2 .71
  job: homelab-nightly-proxmox-2
  schedule: 03:15
  target: media-backup-proxmox-2
  guests: 101,103,202

mode: snapshot
compression: zstd
retention: keep-last=3
notification-mode: notification-system
```

The old standalone IaC/job definition for `Proxmox-2` used VMID `200` for `monitor-01`. That value is now stale and must be changed to VMID `202` before the final cluster-era schedule can be called reconciled.

Cluster formation also replaced `Proxmox-2`'s previous node-local `/etc/pve` view with the cluster configuration. The live `homelab-nightly-proxmox-2` job therefore needs explicit recreation/reconciliation and validation rather than being assumed to have survived the join.

Required post-cluster evidence:

1. IaC updated to `101,103,202` on `Proxmox-2`;
2. both storage IDs active on their intended node and disabled on the other;
3. live jobs match the desired schedule, storage, guest set and retention;
4. fresh successful backups for the final `.71` guest set, especially VM202;
5. archive visibility/integrity checked;
6. an unattended post-cluster cycle observed successfully;
7. notifications confirmed from the reconciled jobs.

Until those gates pass, the **backup platform** is operationally proven but the **final post-cluster schedule state** is still pending reconciliation.

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

Deployment roles use explicit approval gates. Do not bypass those gates for routine changes.

## Cluster migration rollback evidence

The cluster migration deliberately preserved previous `Proxmox-2` local volumes under non-conflicting names:

```text
precluster-20260914-vm-101-disk-0
precluster-20260914-vm-103-disk-0
precluster-20260914-vm-200-cloudinit
precluster-20260914-vm-200-disk-0
```

These are not current guest disks. They are temporary rollback evidence and should remain until fresh cluster-era backups are proven.

Final pre-cluster backup archives, saved guest/storage/job configuration and the migration preservation bundle must also remain until the cluster-era recovery position is explicitly accepted.

## Workload-specific recovery gaps

### `cloud-01`

High-priority persistent assets include Nextcloud user data under `/srv/cloud-01-data`, PostgreSQL state, application secrets and Terraform state.

The VM-level backup is proven to complete, but that does **not** prove application consistency. A Nextcloud/PostgreSQL recovery test remains required.

### `monitor-01`

`monitor-01` is now VM202 on `Proxmox-2`. A fresh VM202 backup is a high-priority post-cluster proof because pre-cluster monitor backups were stored under VMID 200.

### DNS

Pi-hole/Unbound configuration is primarily reproducible from IaC, but recovery still depends on protected Terraform state, SSH/API recovery identities, secret material, Git availability and router access.

### `docker-01` / BirdNET-Go

Protect BirdNET configuration, database/history or user-generated persistent state that cannot be recreated from Git/image deployment. Do not back up reproducible container images and cache merely for completeness.

### `media-01`

`media-01` cannot protect its own `/srv/media` data by writing a backup to the same NVMe that hosts the Proxmox backup repositories. User media needs a different physical failure domain.

### IaC controller

Git does not protect every recovery asset. Independently protect:

```text
~/.local/state/homelab-iac/
~/.config/homelab-iac/
required SSH recovery keys
SOPS/age recovery identities or equivalent protected material
```

Never commit plaintext secrets to Git merely to make backup easier.

## Copy policy

Target minimum for important data remains:

1. a primary automated, verified and retention-managed backup copy;
2. an independent secondary copy on separate physical storage/failure domain.

The primary Proxmox guest-backup mechanism is proven. The independent second-copy requirement remains open.

For irreplaceable documents, photos and recovery identities, an off-site or cloud copy should be added where practical.

## 4 TB WD disk on `PROXMOX`

The WDC WD40EZRX disk remains unsuitable as the sole trusted backup copy.

Known evidence includes SMART overall PASS but historical offline-uncorrectable sectors and an extended self-test that did not complete successfully. It may be used only as supplementary/non-authoritative storage if deliberately reassessed.

## Proxmox Backup Server

PBS remains a possible future enhancement, not an immediate requirement.

The current NFS/vzdump design intentionally uses available hardware first. A future PBS deployment should be justified by actual retention, deduplication, verification, restore and second-copy requirements rather than introduced merely because it is the Proxmox-native product.

## Cluster effect on backup design

The cluster has removed the duplicate-VMID constraint that originally forced separate repositories: `cloud-01` remains VM200 and `monitor-01` is now VM202.

That makes a future shared cluster-wide backup namespace technically possible, but it is **not** an immediate migration requirement. The existing node-scoped repositories are already deployed, understood and proven. Simplification should happen only if it reduces operational risk and after fresh cluster-era recovery proof exists.

Production guest disks remain on node-local `local-lvm`; therefore backup/recovery remains critical even though cluster quorum is now resilient through QDevice.

## Remaining priorities

1. reconcile backup schedule IaC and live `Proxmox-2` job to VM202;
2. take fresh cluster-era backups for the final guest placement;
3. observe and record an unattended post-cluster run;
4. review real retention/storage growth after multiple runs;
5. prove at least one QEMU VM restore;
6. prove application-consistent `cloud-01` recovery;
7. protect controller recovery identities/state independently;
8. establish an independent second copy for important data;
9. define protection for `media-01`, `docker-01` and other non-Proxmox persistent state;
10. remove the retained pre-cluster LVs only after fresh backup confidence is explicit.

## Definition of done

The backup platform is operationally useful today because:

- the NFS target is healthy;
- each PVE node has its intended node-scoped backup storage;
- all seven pre-cluster production guests have successful backup evidence;
- archive integrity checks have passed;
- an LXC restore has been booted safely in isolation;
- notifications have been delivered through the approved relay path.

The **cluster-era schedule** is done only when the live jobs and IaC match the final guest IDs/placement, fresh VM202-era archives exist and at least one unattended post-cluster cycle has succeeded.

Estate-wide recovery is not complete until VM, application, non-Proxmox and independent-secondary-copy recovery classes are also proven.
