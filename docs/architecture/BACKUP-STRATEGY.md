# Backup Strategy

Status: working target design, pending completion of the estate-wide hardware audit.

## Requirement

The rebuilt backup platform must have a usable web GUI.

The GUI is for:

- backup status and job visibility
- browsing backup sets and snapshots
- restore operations
- verification/health visibility
- retention and datastore visibility

Git/IaC remains the source of truth for deployment, host enrollment, credentials references, schedules where practical, and backup policy. GUI-only drift is not accepted as authoritative configuration.

## Preferred long-term platform

### Proxmox Backup Server

The preferred long-term target is **Proxmox Backup Server (PBS)**, subject to final host-placement and storage decisions after the hardware audit.

Reasons:

- native Proxmox VE VM/LXC backup integration
- integrated web GUI
- Linux host backup capability through `proxmox-backup-client`
- incremental backups and datastore deduplication
- client-side encryption support
- verification, pruning/retention and datastore management
- remote datastore synchronization for a second copy
- strong fit with the planned Proxmox-based estate

PBS should not be installed merely because a current host happens to have spare capacity. Its final host and datastore must be selected from the post-audit placement matrix.

## Transitional Restic access

The existing Restic repositories are not to be discarded.

**Backrest** is the preferred transitional GUI for Restic if a graphical browser/restore path is needed during migration because it can import existing Restic repositories, browse snapshots, restore files, schedule operations and perform repository health tasks.

Backrest is a migration/compatibility tool, not currently the proposed final estate-wide backup authority.

## Existing backup state

Current known backup state includes:

- a Restic REST server on legacy `ids-01`
- Restic repositories on the DietPi-attached backup disk for:
  - dietpi
  - homelab-vault
  - ids-01
  - historical k3s-node-01
  - testserver
- dated monthly `ids-01` archives on the DietPi backup disk
- backup/retention reports
- SOPS/age recovery material
- a backup replica mount on legacy `media-01`
- no configured Proxmox VE guest-backup job at the time of the hardware audit

The DietPi-attached 4 TB-class WD disk is **DEGRADED** and is not an acceptable long-term primary backup datastore.

## Target backup architecture

The final design should provide at least two independently useful backup copies:

1. **Primary backup datastore**
   - healthy replacement storage
   - managed through the chosen GUI
   - local high-speed connectivity
   - verification and retention enabled

2. **Secondary copy**
   - separate physical storage or separate host/failure domain
   - synchronized automatically
   - not dependent on the primary datastore remaining healthy

An off-site copy should be added where practical for the most important data and recovery material.

The degraded DietPi disk remains read-only/recovery-oriented until its important content has been reconciled and copied elsewhere.

## Backup scope

### Proxmox

Back up:

- VMs
- LXCs
- critical VM/LXC configuration
- application-consistent data where required

### Linux/Docker hosts

Back up persistent state, not replaceable runtime artifacts.

Typical scope:

- application data
- databases using application-aware dump/quiesce hooks where required
- Docker bind-mounted persistent data
- configuration that is not already reconstructable from Git
- selected host state needed for rapid recovery

Do not treat Docker images, build caches or other reproducible artifacts as primary backup data.

### IaC and secrets

Git remains the authoritative source for IaC.

Secrets and recovery identities must remain encrypted/protected. Plaintext recovery identities must never be committed to Git or printed into audit logs.

## Initial retention target

Working policy, to be validated against real datastore usage:

- daily: 7
- weekly: 4
- monthly: 12
- yearly: 3

Critical databases or frequently changing state may require shorter RPO intervals than one day.

Retention is not considered valid until restore tests prove the retained backups are usable.

## Verification and restore policy

A backup job succeeding is not enough.

The rebuilt platform must include:

- scheduled repository/datastore verification
- alerting for failed or stale backups
- periodic test restores
- documented recovery procedures
- at least one proven restore for each major workload class before legacy backup paths are retired

## Migration sequence

1. Complete the remaining hardware/network audits.
2. Reconcile the existing Restic repositories and monthly archives.
3. Confirm protected copies of SOPS/age recovery material without exposing secret contents.
4. Select the backup-server host and healthy datastore from the final placement matrix.
5. Replace the degraded 4 TB-class disk before relying on it for new backups.
6. Deploy the target backup platform through IaC.
7. Enroll hosts through Ansible/IaC.
8. Establish new backups alongside the old system.
9. Run verification and test restores.
10. Migrate Proxmox VM/LXC backup jobs.
11. Retain old Restic repositories read-only until the new platform has proven recovery coverage.
12. Retire old scripts/Restic server paths only after recovery proof.

## Placement boundary

No physical host is assigned the backup role by this document.

The final backup-server hostname, storage attachment and host assignment remain **UNASSIGNED** until the full hardware audit is complete.
