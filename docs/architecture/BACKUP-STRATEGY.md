# Backup Strategy

**Status:** primary Proxmox guest-backup platform operational; both cluster-era jobs reconciled through IaC; CT105 and VM203 unattended evidence observed; VM204 scheduled with native/manual backup proof; CT104 and first unattended VM204 proof remain open  
**Reviewed:** 17 September 2026

## Requirement

The homelab backup platform must provide clear job/status visibility, browsable backup sets, restore operations, verification/health visibility, deliberate retention, documented recovery and real restore testing.

Git/IaC remains the source of truth for deployment, storage registration, schedule policy and recovery configuration where practical. GUI-only drift is not authoritative configuration.

## Current state

The estate has a proven primary Proxmox guest-backup platform using native Proxmox `vzdump` backups to NFS storage on `media-01`.

The two hypervisors are members of the `jameshouse-pve` cluster and all production guest VMIDs are cluster-unique. The pre-cluster repository split remains in service because it is already proven and provides clear node-scoped ownership; there is no requirement to collapse it merely because cluster membership now exists.

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
all seven then-production guest backups: proven
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

That evidence remains valid proof that the backup transport, archives, notification path and LXC restore mechanism worked. It must not be misrepresented as proof that every current guest has already completed an unattended cluster-era run, because later commissioning added VM203, CT104, CT105 and VM204.

### Current cluster-era guest scope

```text
PROXMOX .70 -> media-backup-proxmox
  CT100 dns-02
  CT102 mail-relay-01
  CT104 komodo-01
  CT105 zabbix-01
  VM200 cloud-01
  VM201 sensor-01
  VM204 home-01

Proxmox-2 .71 -> media-backup-proxmox-2
  CT101 dns-01
  CT103 edge-01
  VM202 monitor-01
  VM203 greenbone-01
```

Templates 9000/9001 remain excluded from the production backup schedule.

CT104 and CT105 each have successful manual snapshot-mode backup evidence on `media-backup-proxmox`, including compressed archive integrity validation. VM203 has manual snapshot archives with successful Zstandard integrity proof on `media-backup-proxmox-2`.

VM204 has both a native Home Assistant backup and a manual Proxmox snapshot archive. The VM204 archive passed compressed and embedded VMA integrity validation before the nightly schedule was extended to include it.

The 17 September application audit observed unattended CT105 output from the 02:15 `PROXMOX` job and unattended CT101, CT103, VM202 and VM203 output from the 03:15 `Proxmox-2` job. The displayed `PROXMOX` repository tail did not include CT104, so this document does not claim first unattended CT104 proof from that output. VM204's observed archive at approximately 07:59 was the manual validation backup, not an unattended schedule run.

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

The 17 September audit observed approximately 338 GiB free on the underlying `media-01` filesystem and current backup archives in both node-specific repositories.

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

Application-level restore evidence also exists separately for Komodo and Zabbix database state; that does not replace whole-guest restore evidence. Home Assistant currently has native-backup creation plus whole-VM archive integrity proof, but deeper HAOS/native restore validation remains open.

## Notifications

Both Proxmox nodes use PVE's notification system. The built-in `default-matcher` routes notifications to `mail-to-root`, and `root@pam` has the approved recipient configured.

Both hypervisors relay through:

```text
[192.168.2.54]:25
```

`mail-relay-01` then authenticates to Gmail over TLS on `smtp.gmail.com:587`.

End-to-end notification tests from both PVE nodes completed successfully.

## Schedule and retention policy

The current cluster-era policy is:

```text
PROXMOX .70
  job: homelab-nightly-proxmox
  schedule: 02:15
  target: media-backup-proxmox
  guests: 100,102,104,105,200,201,204

Proxmox-2 .71
  job: homelab-nightly-proxmox-2
  schedule: 03:15
  target: media-backup-proxmox-2
  guests: 101,103,202,203

mode: snapshot
compression: zstd
retention: keep-last=3
notification-mode: notification-system
```

The current selections are defined in `IaC/ansible/playbooks/proxmox-backup-schedule.yml`. Reconciliation continues to fail closed on unexpected storage, schedule, node, retention or notification state.

Validated cluster-era evidence:

1. `PROXMOX` IaC/live guest selection is `100,102,104,105,200,201,204`;
2. `Proxmox-2` IaC/live guest selection is `101,103,202,203`;
3. live storage remains `media-backup-proxmox` / `media-backup-proxmox-2` on the intended nodes;
4. schedules remain `02:15` and `03:15`, snapshot mode, zstd and `keep-last=3`;
5. CT105 unattended backup output was observed from the 17 September `PROXMOX` run;
6. CT101, CT103, VM202 and VM203 unattended backup output was observed from the 17 September `Proxmox-2` run;
7. CT104 has manual snapshot backup/integrity proof and is included in the 02:15 job, but the displayed 17 September sample did not prove its unattended run;
8. VM204 has native Home Assistant backup plus manual snapshot/integrity proof and is included in the 02:15 job; first unattended proof remains pending;
9. backup notification delivery remains operational.

Remaining backup closeout:

- observe and record first unattended CT104 proof;
- observe the first unattended 02:15 cycle containing VM204;
- perform a representative isolated QEMU restore proof;
- add an independent secondary copy;
- complete application-consistent Nextcloud/PostgreSQL recovery proof;
- deepen Home Assistant native/VM recovery validation.

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

`monitor-01` is VM202 on `Proxmox-2`. Fresh cluster-era unattended backup evidence exists, including the 17 September cycle.

### `greenbone-01`

`greenbone-01` is VM203 on `Proxmox-2`. Manual snapshot archives exist, integrity was proven with `zstd -t`, the VM is protected, the schedule includes VM203 and the 17 September unattended 03:15 archive was observed.

### `komodo-01`

`komodo-01` is CT104 on `PROXMOX`. A manual whole-container snapshot backup and archive-integrity check are proven, and the 02:15 job includes CT104. Komodo also has application-level backup/isolated database-restore proof. First unattended CT104 proof is still not claimed from the displayed 17 September audit output; Proxmox protection remains a separate decision.

### `zabbix-01`

`zabbix-01` is CT105 on `PROXMOX`. A manual whole-container snapshot backup and archive-integrity check are proven, the 02:15 job includes CT105, PostgreSQL/TimescaleDB logical backup/restore validation is proven and the 17 September unattended CT105 archive was observed.

### `home-01`

`home-01` is VM204 on `PROXMOX`. Native Home Assistant backup creation is proven, a manual whole-VM snapshot archive passed compressed/VMA integrity checks, the 02:15 job includes VM204 and Proxmox protection is enabled. First unattended VM204 execution and deeper restore proof remain open.

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

The cluster has removed the duplicate-VMID constraint that originally forced separate repositories: `cloud-01` remains VM200 and `monitor-01` is VM202.

That makes a future shared cluster-wide backup namespace technically possible, but it is **not** an immediate migration requirement. The existing node-scoped repositories are already deployed, understood and proven. Simplification should happen only if it reduces operational risk and after fresh cluster-era recovery proof exists.

Production guest disks remain on node-local storage; therefore backup/recovery remains critical even though cluster quorum is resilient through QDevice.

## Remaining priorities

1. observe and record first unattended CT104 proof;
2. observe and record the first unattended VM204 backup;
3. review real retention/storage growth after multiple runs;
4. prove at least one QEMU VM restore;
5. prove application-consistent `cloud-01` recovery;
6. deepen Home Assistant native/whole-VM recovery proof;
7. protect controller recovery identities/state independently;
8. establish an independent second copy for important data;
9. define protection for `media-01`, `docker-01` and other non-Proxmox persistent state;
10. remove retained pre-cluster LVs only after fresh backup confidence is explicit.

## Definition of done

The backup platform is operationally useful today because:

- the NFS target is healthy;
- each PVE node has its intended node-scoped backup storage;
- all seven pre-cluster production guests have successful historical backup evidence;
- fresh unattended cluster-era evidence exists for CT105, CT101, CT103, VM202 and VM203;
- VM203, CT104, CT105 and VM204 have manual backup/integrity proof and are included in reconciled schedules where applicable;
- archive integrity checks have passed;
- an LXC restore has been booted safely in isolation;
- Komodo and Zabbix have separate application-level restore proof;
- Home Assistant has a native backup in addition to whole-VM backup evidence;
- notifications have been delivered through the approved relay path.

The **cluster-era schedules** are reconciled through IaC. Remaining schedule proof is first unattended evidence for CT104 and VM204.

Estate-wide recovery is not complete until VM, application, non-Proxmox and independent-secondary-copy recovery classes are also proven.
