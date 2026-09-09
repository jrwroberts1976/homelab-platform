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

Working placement is now `pbs-01` as a VM on `PROXMOX` (`192.168.2.70`), using service address `192.168.2.52`. The VM system disk may live on normal Proxmox VM storage, but the PBS backup datastore must be healthy dedicated physical storage presented separately to the VM. It must not exist only on the same SSD/storage pool as the guests being protected.

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
  - current read-only inventory: ~12 GiB total under `/home/homelab-backup/replica`
  - `ids-01/repository`: ~2.4 GiB
  - `ids-01/remote-repositories`: ~9.5 GiB
  - Restic-like repositories present for `dietpi`, historical `k3s-node-01`, `testserver`, plus the `ids-01` repository
  - no `homelab-vault` repository was found in this replica tree
  - no recovery identity/recipient file was found in this replica tree
  - no dated monthly archive tree was shown in this replica tree
  - therefore this Pi 5 copy is **not yet accepted as a complete replacement** for the degraded DietPi backup disk
- no configured Proxmox VE guest-backup job at the time of the hardware audit

The DietPi-attached 4 TB-class WD disk is **DEGRADED** and is not an acceptable long-term primary backup datastore.

`DietPi` (`192.168.2.48`) is now **redundant for the target architecture**. Its production DNS role has been replaced by the two IaC-managed virtual resolvers (`dns-01` at `.51` and `dns-02` at `.50`). Keep the Pi powered and unchanged until current DHCP/DNS advertisement is verified not to depend on `.48` and the unique backup/recovery material on its attached disk has been reconciled. After those gates pass, the Pi can be powered down and retained as a spare/reuse candidate. The degraded 4 TB disk remains recovery-only and is not part of the reuse pool.

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
2. Reconcile the existing Restic repositories and monthly archives. Current media-01 evidence proves the Pi 5 replica is incomplete relative to the degraded DietPi disk.
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

## Placement

Working target:

```text
PROXMOX / 192.168.2.70
└── pbs-01 VM / 192.168.2.52
    ├── PBS system disk on normal VM storage
    └── dedicated healthy physical backup datastore
```

The datastore must not be the degraded DietPi 4 TB disk and must not exist only as a virtual disk backed by the same Proxmox storage that contains the guests being protected. The exact healthy backup disk is still to be selected.

### Initial protection scope

- `PROXMOX`: all IaC-managed VMs/LXCs, beginning with `dns-02`.
- `Proxmox-2`: all IaC-managed VMs/LXCs, beginning with `dns-01`.
- physical Linux/Pi hosts: back up selected persistent data/configuration to the backup platform using a supported file-level client/path; ARM clients must not be forced into an unsupported PBS-client workflow.
- TestServer: protect Terraform state, selected non-Git configuration and application data.

### Failure-domain rule

`pbs-01` may run as a VM on `PROXMOX`, but the backup datastore must be a separate physical storage device. A second independent copy remains a target requirement because loss of the `PROXMOX` host must not be capable of destroying both production guests and their only backup copy.
