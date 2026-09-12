# Backup Strategy

**Status:** current-state gap documented; target design still to be implemented  
**Reviewed:** 12 September 2026

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

The 12 September estate audit found **no active production backup platform**.

### Proxmox

Both standalone Proxmox nodes currently have:

```text
scheduled guest backup jobs: 0
```

There is no deployed Proxmox Backup Server.

The PBS client tooling being present on a Proxmox host does not mean a PBS server or datastore exists.

### Restic / Backrest

No active Restic/Backrest service, mounted backup repository or current Restic server was found on the audited active estate.

Historical documentation and old backup media may still contain useful Restic repositories or migration evidence. Preserve those until their value has been deliberately assessed, but do not describe them as the current backup platform.

The decommissioned `ids-01` Restic service and the former DietPi backup role are historical only.

### 4 TB WD disk on `PROXMOX`

The WDC WD40EZRX 4 TB-class disk currently attached to `PROXMOX` is:

- blank/unallocated;
- unmounted;
- not a backup repository;
- not the `cloud-01` production data disk;
- suitable only for POC/risk testing unless later reassessed.

Current health evidence:

- SMART overall: PASS;
- reallocated sectors: 0;
- current pending sectors: 0;
- offline uncorrectable sectors: 2;
- UDMA CRC errors: 10;
- recent extended self-test did not complete successfully and was recorded as aborted by host.

This disk must never be the sole copy of important data.

## Backup gap statement

At present:

- VM/LXC recovery depends on rebuild/IaC plus any surviving application data;
- important persistent application data does not yet have a proven estate-wide backup path;
- Terraform state and protected controller configuration require independent protection;
- restore testing is not proven.

A healthy running service is therefore **not equivalent to a recoverable service**.

## Preferred target platform

### Proxmox Backup Server

Proxmox Backup Server remains the preferred direction for VM/LXC backup, subject to a deliberate placement/storage decision.

Reasons:

- native Proxmox VE integration;
- incremental backup and deduplication;
- verification and pruning;
- retention visibility;
- restore support;
- web GUI;
- optional client-side encryption;
- ability to maintain a second copy/remote sync later.

The earlier design that assumed a future `pve-02` rebuild with `pbs-01` as a VM is superseded. `Proxmox-2` is already a live standalone production node. Any PBS placement must now be designed against the actual current estate rather than inherited from the earlier greenfield plan.

## Placement principles

A future backup server/datastore must satisfy these rules:

1. backup storage must be healthy and intentionally selected;
2. the only backup copy must not live solely on the same compute/system disk as the workloads being protected;
3. loss of one Proxmox node should not remove every useful backup of that node's workloads;
4. important application data should have at least two independently useful copies;
5. recovery identities, secrets and Terraform state require protection independent of the normal running controller;
6. a backup platform is not accepted until restore testing succeeds.

Possible PBS placement options should be evaluated later against:

- available physical storage;
- USB/SATA/NVMe reliability;
- compute/RAM headroom;
- failure domains;
- power/network dependency;
- restore performance;
- cost.

No exact PBS host/datastore placement is currently approved by this document.

## Backup scope

### Proxmox guests

Protect:

- VM/LXC disks;
- guest configuration required for restore;
- application-consistent data where required.

Current guests requiring an explicit backup policy include:

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

Not all guests require the same retention or recovery objective.

### `cloud-01`

High-priority persistent assets include:

- Nextcloud user data under `/srv/cloud-01-data`;
- PostgreSQL application database;
- application state required for a consistent restore;
- protected application secrets;
- Terraform state required to manage/rebuild the VM cleanly.

The live 200 GiB cloud data disk is production storage, **not a backup**.

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

User media under `/srv/media` is not reproducible from IaC and needs an intentional protection decision.

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
   - usable if the primary backup datastore fails.

For irreplaceable documents/photos/recovery identities, an off-site or cloud copy should be added where practical.

## Retention starting point

A reasonable initial policy to validate against actual capacity:

- daily: 7
- weekly: 4
- monthly: 12
- yearly: 3

Critical databases or rapidly changing state may require a shorter RPO than one day.

Retention is not considered effective until representative restores have succeeded.

## Verification and restore policy

A successful backup job is not enough.

The target platform must include:

- scheduled datastore/repository verification;
- alerting for failed/stale backups;
- periodic test restores;
- documented restore procedures;
- at least one proven restore for each major workload/data class.

Suggested restore-test classes:

- one Proxmox LXC;
- one Proxmox VM;
- Nextcloud database + files consistency restore;
- controller Terraform state recovery;
- one bare-metal/non-Proxmox application-data restore such as BirdNET or media data.

## Migration / implementation sequence

1. Treat the current no-backup state as an explicit operational risk.
2. Inventory historical Restic/recovery media before discarding it.
3. Confirm protected copies of required secrets/recovery identities without exposing them.
4. Define RPO/RTO priorities by workload.
5. Select healthy primary backup storage.
6. Select PBS placement, or approve another platform if PBS no longer fits.
7. Deploy the platform through Git-managed IaC where practical.
8. Create Proxmox guest backup jobs.
9. Add application-aware protection for `cloud-01` and other stateful workloads.
10. Protect controller Terraform/secrets/recovery state independently.
11. Establish an independent second copy.
12. Configure verification/retention/alerts.
13. Perform test restores.
14. Only after recovery proof, retire historical backup paths or media that are no longer needed.

## Definition of done

Backup/recovery is not complete until:

- a production backup platform is deployed;
- healthy dedicated backup storage is in use;
- all important workloads/data have an explicit policy;
- scheduled jobs run successfully;
- stale/failed jobs alert;
- at least two useful copies exist for important data;
- controller recovery state is protected off-host;
- representative restores have been tested and documented;
- historical repositories/media have been deliberately retained or retired.
