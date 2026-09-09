# Backup Strategy

Status: approved architecture direction; implementation follows the IaC-first rebuild.

## Principle

The homelab does not need full-machine backups for infrastructure that is deliberately reproducible.

> Rebuild infrastructure. Back up data.

Git/IaC is authoritative for VM/LXC definitions, operating-system configuration, service configuration and deployment policy. Backup storage is reserved primarily for information that cannot be recreated from code.

## What is rebuilt rather than backed up

Examples:

- Debian operating systems
- Pi-hole and Unbound installation/configuration held in IaC
- Chrony configuration
- Docker/Compose service definitions
- container images
- VM/LXC definitions
- monitoring configuration stored in Git

These workloads must still have tested rebuild procedures, but copying their complete operating systems is not the primary recovery mechanism.

## What must be protected

Protect persistent, non-reconstructable state, including:

- household documents and photos
- Nextcloud user files
- application databases
- application state required for consistent recovery
- Terraform/OpenTofu state
- protected secrets/recovery material not reconstructable elsewhere
- selected persistent Docker data
- other user-created data

## Private-cloud data platform

The next data service is `cloud-01.jameshouse` at `192.168.2.53`, implemented as an IaC-managed Debian VM on `PROXMOX`.

It will run:

- Nextcloud
- PostgreSQL
- Redis
- Docker/Compose managed through Ansible/IaC

See `production docs/CLOUD-SERVICE.md`.

The VM is disposable infrastructure. Its persistent user data and database are protected assets.

## Candidate 4 TB data disk

The former DietPi USB disk has moved to `PROXMOX` and is being destructively tested before reuse.

Identity:

- model: `WDC WD40EZRX-00SPEB0`
- serial: `WD-WCC4E0670079`
- capacity: 4.00 TB / 3.64 TiB
- USB bridge: UGREEN / Realtek `0bda:9201`

Pre-test SMART baseline:

- reallocated sectors: 0
- current pending sectors: 7
- offline uncorrectable sectors: 2
- UDMA CRC errors: 10
- power-on hours: 28,300

The old contents of this disk were accepted for destructive reuse when the full-surface test was started. It must not be considered production storage until the test completes and post-test SMART values are reviewed.

Even if the disk passes, its previous pending/uncorrectable-sector history means it must never be the sole copy of irreplaceable Nextcloud data.

## Required failure domains

Important data must have at least two independently useful copies.

Working target:

1. primary copy on the `cloud-01` data device;
2. second copy on separate physical storage or another host/failure domain;
3. off-site copy for the most important data where practical.

A synchronised Nextcloud client is not automatically a backup because deletions, corruption or ransomware can synchronise too.

## Existing Restic / PBS direction

Existing Restic tooling may remain useful for selected file-level protection or transitional recovery workflows.

Proxmox Backup Server is no longer the immediate next critical deployment. Because the infrastructure is IaC-rebuildable, PBS is deferred until there is a demonstrated requirement for rapid whole-guest recovery, longer retention or native Proxmox snapshot workflows.

PBS may still be added later, but it is not required for the initial private-cloud build.

## Recovery model

Infrastructure recovery:

```text
Git
 |
 v
Terraform/OpenTofu
 |
 v
VM/LXC created
 |
 v
Ansible / Compose
 |
 v
service rebuilt
```

Persistent-data recovery:

```text
rebuild service from Git
        |
        v
restore database + persistent data
        |
        v
validate application
        |
        v
resume clients
```

## Verification policy

A backup is not accepted merely because a job reports success.

The production data-protection design must include:

- automatic backup schedule
- failure/staleness alerting
- integrity verification where supported
- documented recovery procedure
- periodic test restores
- at least one proven Nextcloud database + file restore before external access
- a second independent copy of important data

## Immediate sequence

1. finish the destructive 4 TB disk test;
2. compare post-test SMART data with the recorded baseline;
3. accept or reject the disk;
4. build `cloud-01` from IaC;
5. deploy Nextcloud/PostgreSQL/Redis LAN-only;
6. prove upload/download/sync;
7. implement and prove data/database restore;
8. establish the second independent copy;
9. only then consider Internet exposure;
10. reconsider PBS later if whole-guest recovery would materially improve recovery objectives.
