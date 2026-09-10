# Backup Strategy

**Updated:** 10 September 2026  
**Status:** active design; implementation and restore proof incomplete  
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`

## Requirement

Backups must provide more than successful job messages. The rebuilt estate requires:

- visible backup/job status;
- browsable backup sets where practical;
- scheduled verification;
- documented restore procedures;
- periodic test restores;
- at least two independently useful copies of important data/recovery material;
- Git/IaC authority for policy and deployment wherever practical.

A GUI is desirable for backup status, browsing, verification, retention and restores, but GUI-only configuration drift is not authoritative.

## Current estate context

The old backup architecture was spread across DietPi, ids-01, TestServer and a partial replica on media-01. Those historical copies remain evidence/recovery material until reconciled, but none of those legacy layouts is automatically the new backup authority.

Current platform roles:

- `admin-01 .48`: administration/IaC; must have independent recovery of SSH/SOPS/age material;
- `PROXMOX .70`: hosts `dns-02`, `mail-relay-01`, `cloud-01`, `sensor-01`;
- `Proxmox-2 .71`: hosts `dns-01`, `monitor-01`, `edge-01`;
- `media-01 .195`: physical Raspberry Pi 5 media endpoint; historical replica data may still exist on its NVMe;
- `TestServer .220`: legacy migration source, pending clean rebuild as garden BirdNET-Go host;
- `ids-01`: decommissioned; not an active backup server.

## Existing historical backup material

Known historical material includes:

- Restic repositories originating from the former DietPi-attached WD 4 TB disk;
- repositories/archives for DietPi, homelab-vault, ids-01, historical k3s-node-01 and TestServer;
- dated ids-01 monthly archives;
- protected SOPS/age recovery material;
- a partial backup-replica tree on media-01;
- old backup scripts/services including the currently unresolved TestServer backup-service failure history.

Do not delete these solely because the source host has been repurposed or decommissioned. First identify whether each data set has a current authoritative replacement and whether recovery has been proven.

## WD 4 TB disk

The former DietPi backup disk is now attached to `PROXMOX`:

```text
model: WDC WD40EZRX-00SPEB0
serial: WD-WCC4E0670079
capacity: approximately 4 TB
current device: /dev/sdb
```

Historical SMART evidence:

- Reallocated sectors: 0
- Current pending sectors: previously 7, later 0
- Offline uncorrectable sectors: 2
- UDMA CRC errors: 10

The overall SMART health line currently reports PASSED, but the historical uncorrectable evidence remains relevant. An extended/long SMART self-test is still in progress as of 10 September 2026 and must not be interrupted or restarted.

Until the long test completes and the final self-test log/attributes are reviewed, this disk is not approved as the sole storage location for irreplaceable data.

## Long-term platform direction

Proxmox Backup Server remains a strong candidate because the rebuilt estate now contains multiple Proxmox VMs/LXCs and benefits from native guest backup, verification, retention and restore tooling.

However, **PBS host/datastore placement is not considered final in this document**. Do not assume a new PBS VM or reuse the WD disk until capacity, storage health, failure-domain and recovery design are explicitly approved.

Backrest/Restic can remain useful for browsing/restoring historical Restic repositories during migration, but that does not make the old Restic server architecture the new estate-wide authority.

## Target architecture

Important data should have at least:

1. a primary backup copy on healthy storage managed by the approved backup platform; and
2. a second independent copy on a separate physical disk/host/failure domain.

For the most important household data and recovery secrets, add an off-site or otherwise physically separate copy where practical.

A backup stored only on the same hypervisor/storage that hosts the production workload does not satisfy the independent-copy requirement.

## Backup scope

### Proxmox guests

Protect VMs/LXCs that contain persistent or operationally expensive state. Configuration-only guests should still have a documented rebuild path even when image-level backup is not the primary recovery mechanism.

Current guest estate includes:

```text
PROXMOX .70:
  CT100 dns-02
  CT102 mail-relay-01
  VM200 cloud-01
  VM201 sensor-01

Proxmox-2 .71:
  CT101 dns-01
  CT103 edge-01
  VM200 monitor-01
```

### cloud-01

The VM is rebuildable infrastructure; user files, PostgreSQL data and application state required for a consistent restore are not. Production cloud data must not depend solely on the WD 4 TB disk.

### monitoring / logging

Prometheus/Grafana/Loki state is useful operational data, but configuration should remain reproducible from Git. Decide retention/backup by operational value rather than blindly backing up all time-series/log data.

### DNS, mail relay and edge

These should be rebuildable from Git/IaC plus protected secrets. Restore testing should prove the required secret/configuration material is available independently of the running guest.

### media-01

Protect only user media/configuration that is not reproducible from Git. Historical replica data on its NVMe must be reconciled before deletion or repurpose.

### future birdnet-01

Protect intentionally retained BirdNET configuration/history/recordings separately from the clean OS build. Do not make the old TestServer image the backup strategy.

### IaC and secrets

Git remains authoritative for IaC/documentation. Private SSH identities, SOPS/age identities, application credentials and other recovery secrets require protected recovery copies outside Git and outside a single failing disk.

Never print or commit plaintext recovery identities.

## TestServer hard gate

`homelab-backup-testserver.service` has a failure history that must be understood before destructive TestServer cleanup.

Before reimage:

1. identify what the job was intended to protect;
2. locate current copies of that data;
3. test restore/recovery where important;
4. document what can be discarded;
5. only then remove legacy backup state.

## Retention starting point

A reasonable initial policy, subject to datastore capacity and workload RPO/RTO, is:

- daily: 7
- weekly: 4
- monthly: 12
- yearly: 3

Critical databases or frequently changing household data may require shorter backup intervals. Retention is not considered proven until restore tests show retained backups are usable.

## Verification and restore policy

A successful backup job is necessary but insufficient. The backup platform must include:

- scheduled verification/integrity checks;
- alerting for failed or stale backups;
- restore tests for representative guest/data types;
- written recovery steps;
- recovery validation after infrastructure changes;
- evidence that protected secrets can be recovered without relying on the failed host itself.

## Implementation sequence

1. finish the current WD 4 TB extended SMART review;
2. reconcile historical Restic/monthly/recovery material and media-01 replicas;
3. resolve the TestServer backup-service hard gate;
4. choose the target backup platform and healthy datastore/failure domain;
5. deploy through reviewed IaC where practical;
6. enroll current Proxmox guests and relevant physical hosts;
7. establish independent second-copy policy;
8. run verification and representative restores;
9. document recovery for DNS, monitoring/logging, mail, edge, cloud, media and BirdNET;
10. retire legacy Restic/scripts only after replacement recovery coverage is proven.

## Definition of done

The backup redesign is complete when the current estate has documented scope, schedules and retention; important data has two independent copies; guest/data restores have been proven; recovery secrets are protected independently; the WD disk has an explicit accepted/rejected role; and no critical recovery path depends on decommissioned ids-01 or the unrebuildable legacy TestServer state.
