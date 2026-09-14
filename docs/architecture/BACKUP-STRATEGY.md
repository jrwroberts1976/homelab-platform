# Backup Strategy

**Status:** phase-one Proxmox guest-backup path operationally proven; scheduled production jobs and secondary-copy coverage still pending  
**Reviewed:** 14 September 2026

## Requirement

The homelab needs a backup platform that provides:

- clear job/status visibility;
- browsable backup sets/snapshots;
- restore operations;
- verification/health visibility;
- retention and datastore visibility;
- documented recovery procedures;
- actual restore testing.

Git/IaC remains the source of truth for deployment, enrollment, schedules and policy where practical. GUI-only drift is not authoritative configuration.

## Current state

The estate now has a **proven primary Proxmox guest-backup path**.

Both standalone Proxmox nodes register an NFS backup storage named `media-backup`, hosted by `media-01`:

```text
PROXMOX .70 ---------\
                      +---- NFS v4.2/TCP ----> media-01 .195
Proxmox-2 .71 -------/                         /srv/backup/pve
```

The storage definition is backup-only and is managed through IaC.

Current state on 14 September 2026:

```text
media-backup storage: active on both PVE nodes
NFS target health: proven
NFS write/read/delete: proven from both PVE nodes
local vzdump tmpdir: proven on both PVE nodes
manual LXC backup: proven
archive integrity test: proven
isolated LXC restore + boot: proven
Proxmox notification delivery: proven end to end
scheduled guest backup jobs: 0
secondary independent backup copy: not yet implemented
```

This is no longer a no-backup estate, but backup/recovery is **not yet complete estate-wide**.

### Proxmox guest backup platform

The approved phase-one design uses native Proxmox `vzdump` backups to NFS storage on `media-01`.

Storage target:

```text
host: media-01
address: 192.168.2.195
path: /srv/backup/pve
PVE storage ID: media-backup
protocol: NFS v4.2/TCP
content: backup only
```

The NFS export is restricted to:

```text
192.168.2.70
192.168.2.71
```

The target remains root-owned. It is not made broadly writable to solve LXC UID-remapping problems.

### Local vzdump workspace

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
- workspace is empty after validation.

This design preserves restrictive permissions on the NFS backup repository.

### Backup proof

On 14 September 2026 `edge-01` LXC CT103 on `Proxmox-2` was backed up successfully while running.

Observed result:

```text
backup mode: snapshot
archive compression: zstd
archive size: approximately 568 MiB
source guest after backup: running
zstd archive integrity test: PASS
backup inventory visibility: PASS
```

### Restore proof

The CT103 archive was restored under temporary VMID 903 on `Proxmox-2`.

The restored guest was kept stopped initially, all restored production networking was removed, the filesystem was inspected offline, and the temporary guest was then booted without a production network interface.

Validation result:

```text
archive_config_gate=PASS
network_isolation=PASS
offline_filesystem_restore=PASS
isolated_boot=PASS
temporary_restore_removed=PASS
restore_proof=PASS
```

The live CT103 remained running throughout and the temporary restore was removed cleanly afterwards.

This proves the primary LXC guest-backup path is **restorable**, not merely writable.

### Notifications

Both Proxmox nodes use the built-in `mail-to-root` notification target and the approved `root@pam` email recipient.

Both nodes relay mail through:

```text
[192.168.2.54]:25
```

`mail-relay-01` then authenticates to Gmail over TLS on `smtp.gmail.com:587`.

End-to-end tests on 14 September 2026 showed successful delivery from both hypervisors with `dsn=2.0.0` and `status=sent`.

Direct delivery from Proxmox to Gmail is not the approved design.

### Restic / Backrest

No active Restic/Backrest service, mounted backup repository or current Restic server was found on the audited active estate.

Historical documentation and old backup media may still contain useful Restic repositories or migration evidence. Preserve those until their value has been deliberately assessed, but do not describe them as the current backup platform.

The decommissioned `ids-01` Restic service and the former DietPi backup role are historical only.

### 4 TB WD disk on `PROXMOX`

The WDC WD40EZRX 4 TB-class disk currently attached to `PROXMOX` is:

- blank/unallocated;
- unmounted;
- not the primary backup repository;
- not the `cloud-01` production data disk;
- suitable only for supplementary/POC use unless later reassessed.

Current health evidence:

- SMART overall: PASS;
- reallocated sectors: 0;
- current pending sectors: 0;
- offline uncorrectable sectors: 2;
- UDMA CRC errors: 10;
- recent extended self-test did not complete successfully and was recorded as aborted by host.

This disk must never be the sole copy of important data.

## Remaining backup gap statement

The primary Proxmox LXC path is proven, but important gaps remain:

- there are still no scheduled guest backup jobs;
- no independent secondary copy exists yet for important guest backups;
- VM restore proof is still outstanding;
- `cloud-01` requires application-consistent Nextcloud/PostgreSQL recovery proof;
- Terraform state and protected controller configuration still require independent protection;
- `media-01` cannot protect its own irreplaceable `/srv/media` data by backing up to the same physical disk;
- non-Proxmox persistent state on `docker-01` and the IaC controller still needs explicit policy.

A healthy running service is therefore still **not equivalent to a recoverable service** unless its relevant recovery class has been proven.

## Platform direction

### Current approved platform

For the present estate and available hardware, the approved production direction is:

- native Proxmox `vzdump` guest backups;
- `media-01` NFS storage as the primary guest-backup target;
- local `vzdump` temporary workspace on each hypervisor;
- Proxmox notification delivery via `mail-relay-01`;
- Git-managed IaC for storage, runtime and mail configuration;
- conservative retention initially while real archive sizes are measured.

This avoids purchasing dedicated hardware before the actual capacity and recovery requirements justify it.

### Proxmox Backup Server

Proxmox Backup Server remains a possible future enhancement rather than an immediate requirement.

Potential benefits remain:

- native Proxmox VE integration;
- incremental backup and deduplication;
- verification and pruning;
- retention visibility;
- restore support;
- web GUI;
- optional client-side encryption;
- remote sync/second-copy options.

Any future PBS deployment must be justified against the proven phase-one platform, actual capacity, restore requirements and available hardware. There is currently no approved dedicated PBS host/datastore placement.

## Placement principles

Backup storage must satisfy these rules:

1. backup storage must be healthy and intentionally selected;
2. the only backup copy must not live solely on the same compute/system disk as the workloads being protected;
3. loss of one Proxmox node should not remove every useful backup of that node's workloads;
4. important application data should have at least two independently useful copies;
5. recovery identities, secrets and Terraform state require protection independent of the normal running controller;
6. a backup platform is not accepted until restore testing succeeds.

The current `media-01` design satisfies the first Proxmox-node failure-domain objective, but not yet the independent-secondary-copy objective.

## Backup scope

### Proxmox guests

Protect:

- VM/LXC disks;
- guest configuration required for restore;
- application-consistent data where required.

Current guests requiring an explicit production backup policy:

```text
PROXMOX .70
  CT100 dns-02
  CT102 mail-relay-01
  VM200 cloud-01
  VM201 sensor-01

Proxmox-2 .71
  CT101 dns-01
  CT103 edge-01
  VM200 monitor-01
```

Templates 9000/9001 are not part of the initial production guest-backup schedule unless explicitly approved.

Not all guests require the same retention or recovery objective.

### `cloud-01`

High-priority persistent assets include:

- Nextcloud user data under `/srv/cloud-01-data`;
- PostgreSQL application database;
- application state required for a consistent restore;
- protected application secrets;
- Terraform state required to manage/rebuild the VM cleanly.

The live 200 GiB cloud data disk is production storage, **not a backup**.

A successful VM-level backup will not by itself prove application consistency. A Nextcloud/PostgreSQL recovery test remains required.

### DNS

Pi-hole/Unbound configuration is primarily reproducible from IaC, but recovery still depends on:

- protected Terraform state;
- SSH/API recovery identities;
- Pi-hole secret material;
- Git availability;
- router access.

Guest backups may shorten recovery but do not replace IaC/recovery documentation.

### Monitoring

Prometheus/Grafana runtime state is useful but lower priority than Git-managed configuration and irreplaceable application data.

Back up any dashboards/configuration that are not yet Git-managed before relying on rebuild-only recovery.

### `docker-01` / BirdNET-Go

Protect any BirdNET-Go configuration, database/history or user-generated persistent state that cannot be recreated from Git/image deployment.

Do not waste backup capacity on container images or reproducible build/runtime cache.

### `media-01`

User media under `/srv/media` is not reproducible from IaC and needs a backup destination in a different physical failure domain.

The current `/srv/backup/pve` repository is on the same `media-01` NVMe and therefore **cannot count as protection for `media-01` itself**.

Kodi configuration already managed in Ansible is reproducible; unmanaged personal state is not.

### IaC, secrets and controller state

Git protects repository source but **does not** protect every recovery asset.

Protect independently:

```text
~/.local/state/homelab-iac/
~/.config/homelab-iac/
required SSH recovery keys
SOPS/age recovery identities or equivalent protected material
```

Never commit plaintext secret material to Git merely to make backup easier.

## Copy policy

Target minimum for important data:

1. **Primary backup copy**
   - automated;
   - verified;
   - retention managed;
   - browsable/restorable.

2. **Independent secondary copy**
   - separate physical storage and preferably separate failure domain;
   - synchronized or backed up independently;
   - usable if the primary backup repository fails.

The phase-one Proxmox platform currently has a proven primary copy only. The second-copy requirement remains open.

For irreplaceable documents/photos/recovery identities, an off-site or cloud copy should be added where practical.

## Retention starting point

Until representative estate-wide backups have run and actual archive sizes are known, use a conservative initial policy:

```text
keep-last=3
```

After capacity and backup-duration evidence has been collected, consider expanding to a deliberate daily/weekly/monthly policy.

A possible later target remains:

- daily: 7;
- weekly: 4;
- monthly: 12;
- yearly: 3.

Do not adopt the larger policy merely because it fits syntactically; validate it against real storage consumption and recovery objectives.

Critical databases or rapidly changing state may require a shorter RPO than one day.

## Verification and restore policy

A successful backup job is not enough.

The platform must include:

- alerting for failed/stale backups;
- periodic archive/repository health checks;
- periodic test restores;
- documented restore procedures;
- at least one proven restore for each major workload/data class.

Current restore-test state:

```text
Proxmox LXC: proven (CT103 edge-01, 2026-09-14)
Proxmox VM: pending
Nextcloud database + files consistency: pending
controller Terraform/state recovery: pending
bare-metal/non-Proxmox data: pending
```

The detailed LXC restore procedure is documented in:

```text
production docs/PROXMOX-BACKUP-RECOVERY.md
```

## Implementation sequence

Completed:

1. inventory current storage and historical backup state;
2. select `media-01` NVMe as the phase-one primary guest-backup target;
3. deploy restricted NFS export through IaC;
4. register `media-backup` on both PVE nodes through IaC;
5. deploy local `vzdump` workspace through IaC;
6. prove manual LXC backup and archive integrity;
7. prove isolated LXC restore and boot;
8. configure and prove Proxmox notification delivery through `mail-relay-01`.

Next:

9. create scheduled Proxmox guest backup jobs with conservative retention;
10. prove scheduled runs on both hypervisors;
11. review actual archive sizes, duration and capacity;
12. prove at least one VM restore;
13. add application-aware protection and recovery testing for `cloud-01`;
14. protect controller Terraform/secrets/recovery state independently;
15. establish an independent second copy for important data;
16. define protection for `media-01` and other non-Proxmox persistent state;
17. only then retire historical backup paths/media that no longer have recovery value.

## Definition of done

Backup/recovery is not estate-wide complete until:

- scheduled guest backup jobs run successfully;
- failed/stale jobs alert through the proven notification path;
- all important workloads/data have an explicit policy;
- at least two useful copies exist for important data;
- controller recovery state is protected off-host;
- representative LXC, VM, application and non-Proxmox restores have been tested and documented;
- historical repositories/media have been deliberately retained or retired.

The phase-one **Proxmox LXC primary backup and restore path is already operationally proven**; the remaining items above are expansion and resilience work, not a return to the previous no-backup state.
