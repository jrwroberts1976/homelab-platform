# Backup Strategy

**Status:** primary Proxmox guest-backup platform operationally proven; isolated per-node repositories and all seven production guest backups proven; VM/application restore and independent secondary-copy coverage remain open  
**Reviewed:** 14 September 2026

## Requirement

The homelab backup platform must provide clear job/status visibility, browsable backup sets, restore operations, verification/health visibility, deliberate retention, documented recovery and real restore testing.

Git/IaC remains the source of truth for deployment, storage registration, schedule policy and recovery configuration where practical. GUI-only drift is not authoritative configuration.

## Current state

The estate now has a **proven primary Proxmox guest-backup platform** using native Proxmox `vzdump` backups to NFS storage on `media-01`.

The two standalone Proxmox nodes use isolated namespaces because both currently contain an unrelated QEMU VMID `200`. Sharing one `dump/` namespace would allow the two VM200 backup groups to collide under retention/pruning.

```text
PROXMOX .70
  media-backup-proxmox
  -> media-01:/srv/backup/pve-proxmox

Proxmox-2 .71
  media-backup-proxmox-2
  -> media-01:/srv/backup/pve-proxmox-2

Legacy rollback namespace retained temporarily:
  media-backup
  -> media-01:/srv/backup/pve
```

Each isolated export is restricted to its owning hypervisor. The legacy shared export remains available only as rollback evidence until the isolated scheduled path has completed an unattended run and is deliberately retired.

### Proven state on 14 September 2026

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
retention policy in IaC: keep-last=3
schedule cutover IaC: syntax validated
live isolated schedule cutover / first unattended run: not yet evidenced in this close-out record
secondary independent backup copy: not implemented
VM restore proof: pending
application-consistent cloud restore: pending
```

This is no longer a no-backup estate. The remaining work is resilience and recovery-depth work rather than initial backup-platform creation.

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

/srv/backup/pve-proxmox-2
  authorised client: 192.168.2.71
  PVE storage ID: media-backup-proxmox-2
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

## Production guest scope

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

All seven production guests have completed a manual snapshot-mode backup proof against their isolated repository. Services remained running during the backup process; snapshot-mode backup is the approved production method.

## Restore proof

CT103 (`edge-01`) was restored on `Proxmox-2` under temporary VMID `903`.

The restored container was initially kept stopped, production networking was removed, the filesystem was inspected offline, and the temporary guest was then booted without a production network interface.

```text
archive_config_gate=PASS
network_isolation=PASS
offline_filesystem_restore=PASS
isolated_boot=PASS
temporary_restore_removed=PASS
restore_proof=PASS
```

The live CT103 remained running and the temporary restore was removed afterwards.

This proves the LXC backup path is restorable, not merely writable.

A QEMU VM restore proof remains required before VM recovery can be described as equivalently proven.

## Notifications

Both Proxmox nodes use PVE's notification system. The built-in `default-matcher` routes notifications to `mail-to-root`, and `root@pam` has the approved recipient configured.

Both hypervisors relay through:

```text
[192.168.2.54]:25
```

`mail-relay-01` then authenticates to Gmail over TLS on `smtp.gmail.com:587`.

End-to-end notification tests from both PVE nodes completed successfully and stale historical queue items were removed afterwards.

## Schedule and retention policy

Approved schedule policy encoded in IaC:

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
  guests: 101,103,200

mode: snapshot
compression: zstd
retention: keep-last=3
notification-mode: notification-system
```

During the namespace-collision correction both jobs were deliberately disabled. The IaC now implements a fail-closed transition from the disabled legacy job to the correct isolated storage and refuses to enable a job unless the approved storage is active and an existing proven archive is present for every selected guest.

At this documentation close-out, the cutover playbook has passed syntax validation but the conversation evidence does not include the final live cutover result or the first unattended overnight run. Do not record either as proven until observed.

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

## Workload-specific recovery gaps

### `cloud-01`

High-priority persistent assets include Nextcloud user data under `/srv/cloud-01-data`, PostgreSQL state, application secrets and Terraform state.

The VM-level backup is now proven to complete, but that does **not** prove application consistency. A Nextcloud/PostgreSQL recovery test remains required.

### DNS

Pi-hole/Unbound configuration is primarily reproducible from IaC, but recovery still depends on protected Terraform state, SSH/API recovery identities, secret material, Git availability and router access.

### Monitoring

Prometheus/Grafana runtime state is useful but lower priority than Git-managed configuration and irreplaceable application data. Preserve any dashboards/configuration not yet managed in Git.

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

The primary Proxmox guest-backup copy is now proven. The independent second-copy requirement remains open.

For irreplaceable documents, photos and recovery identities, an off-site or cloud copy should be added where practical.

## 4 TB WD disk on `PROXMOX`

The WDC WD40EZRX disk remains unsuitable as the sole trusted backup copy.

Known evidence includes SMART overall PASS but historical offline-uncorrectable sectors and an extended self-test that did not complete successfully. It may be used only as supplementary/non-authoritative storage if deliberately reassessed.

## Proxmox Backup Server

PBS remains a possible future enhancement, not an immediate requirement.

The current NFS/vzdump design is intentionally using available hardware first. A future PBS deployment should be justified by actual retention, deduplication, verification, restore and second-copy requirements rather than introduced merely because it is the Proxmox-native product.

## Future cluster consideration

The two PVE nodes are currently standalone. A future two-node cluster may be reconsidered once dedicated Corosync NICs are available and a quorum/QDevice design is approved.

Do not collapse the isolated backup namespaces while the hosts are standalone and both have an unrelated VMID `200`. If the nodes later become one correctly designed cluster, guest IDs must be made cluster-unique before simplifying storage layout.

## Remaining priorities

The primary guest-backup project can be considered implemented at the manual/proven layer. Remaining work is:

1. observe and record the isolated schedule cutover and first unattended run;
2. review real retention/storage growth after multiple runs;
3. prove at least one QEMU VM restore;
4. prove application-consistent `cloud-01` recovery;
5. protect controller recovery identities/state independently;
6. establish an independent second copy for important data;
7. define protection for `media-01`, `docker-01` and other non-Proxmox persistent state.

## Definition of done

Primary Proxmox guest backup is operationally proven because:

- the NFS target is healthy;
- each standalone PVE node has an isolated backup namespace;
- all seven production guests have successful backup evidence;
- archive integrity checks have passed;
- an LXC restore has been booted safely in isolation;
- notifications have been delivered through the approved relay path;
- retention and scheduled-job policy are encoded in Git-managed IaC.

Estate-wide recovery is not complete until VM, application, non-Proxmox and independent-secondary-copy recovery classes are also proven.
