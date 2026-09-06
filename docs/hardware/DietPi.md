# DietPi Current-State Audit

Audit date: 2026-09-06  
Legacy hostname: `DietPi`  
Address: `192.168.2.48`  
Login account observed: `dietpi`  
Audit method: repository-controlled `scripts/audit-linux-host.sh`, copied from a verified host and executed locally as root in read-only mode.

Audit artifact on DietPi:

`/var/tmp/DietPi-audit-20260906T074300Z.txt`

SHA256:

`d2252d3613d55359fdfa83616eb5f6fed3594fa9b9e73d08ff285b128a170619`

## Identity

| Item | Current state |
|---|---|
| Hardware | Raspberry Pi 3 Model B Rev 1.2 |
| DietPi release | 10.6.2 |
| OS | Debian GNU/Linux 13 (trixie) |
| Kernel | 6.18.39+rpt-rpi-v8 |
| Architecture | arm64 / aarch64 |
| Legacy hostname | `DietPi` |

The current hostname is a discovery identifier only. It does not determine the host's future role.

`hostnamectl` could not use the system bus on this DietPi installation, but hostname, OS, kernel and architecture were captured independently.

## CPU

| Item | Current state |
|---|---|
| CPU | ARM Cortex-A53 |
| Cores | 4 |
| Threads per core | 1 |
| L2 cache | 512 KiB |

## Memory

| Item | Current state |
|---|---|
| RAM | approximately 955 MiB |
| Used during audit | approximately 227 MiB |
| Available during audit | approximately 727 MiB |
| Swap | approximately 1.1 GiB file |
| Swap used | approximately 77 MiB |

This is the smallest-memory audited compute host so far.

## Storage

### Boot/system media

| Item | Current state |
|---|---|
| Device | `/dev/mmcblk0` |
| Capacity | approximately 59.4 GiB |
| Root partition | approximately 59.3 GiB ext4 |
| Used | approximately 4.5 GiB |
| Available | approximately 52 GiB |
| Root usage | approximately 9% |

SMART-style health data is not available for the microSD device through the installed tooling. Boot-media health is therefore **UNKNOWN**.

### Backup disk

| Item | Current state |
|---|---|
| Device | `/dev/sda` |
| Model | WDC WD40EZRX-00SPEB0 |
| Capacity | approximately 3.6 TiB |
| Filesystem | ext4 |
| Mount | `/mnt/backup` |
| Used | approximately 20 GiB |
| Available | approximately 3.4 TiB |
| Usage | approximately 1% |

This is a major estate-level storage asset and must be treated separately from the Raspberry Pi when target roles are designed.

A follow-up read-only SMART query using SAT passthrough succeeded. The disk reports SMART capability enabled and an overall attribute-based result of PASSED, but important media-error attributes are non-zero:

- Power-on hours: 28,228.
- Reallocated sectors: 0.
- Current pending sectors: **7**.
- Offline uncorrectable sectors: **2**.
- UDMA CRC errors: 10.
- Temperature: 24 C.
- Last recorded short self-tests completed without error.

Because pending and offline-uncorrectable sectors are present, this disk is classified **DEGRADED / REPLACEMENT CANDIDATE** despite the overall SMART "PASSED" line. It must not be treated as the sole authoritative backup target. Verify recoverability/copies before any stress test, filesystem repair, destructive migration, or repurposing.

## Attached backup-disk content

A read-only inventory of `/mnt/backup` showed approximately **20 GiB** of current data:

| Top-level path | Approximate size |
|---|---:|
| `monthly/` | 19 GiB |
| `restic/` | 860 MiB |
| `recovery/` | 16 KiB |
| `reports/` | 16 KiB |
| `yearly/` | 4 KiB |
| `lost+found/` | 16 KiB |

The filesystem is `/dev/sda1` mounted as ext4 at `/mnt/backup` with `rw,noatime`.

The backup disk therefore contains real backup/recovery state, not just an empty spare volume. The dominant data set is under `monthly/`, with a smaller Restic repository or Restic-related data set under `restic/`.

Before replacing, stress-testing, reformatting or repurposing the degraded disk, the contents of `monthly/` and `restic/` must be identified and their recoverability/duplicate copies verified.

## Backup-content structure

A deeper read-only inventory of the degraded backup disk established the following:

### Monthly archives

`/mnt/backup/monthly/` currently contains two dated archives, both for `ids-01`:

- `2026-08-18/ids-01`: approximately 7.5 GiB.
- `2026-09-01/ids-01`: approximately 12 GiB.

These account for essentially all of the approximately 19 GiB under `monthly/`.

### Restic repositories

`/mnt/backup/restic/` contains Restic repository structures for:

- `dietpi`
- `homelab-vault`
- `ids-01`
- `k3s-node-01`
- `testserver`

Each has the normal Restic repository directory layout including `data/`, `index/`, `keys/`, `locks/`, `snapshots/` and a repository `config` file.

The `k3s-node-01` repository name is historical evidence and must not be assumed to match the current hostname of `192.168.2.195`, which is now `media-01`.

### Recovery material

`/mnt/backup/recovery/sops-age/` contains SOPS/age recovery material.

**Do not print or commit the contents of the recovery identity file.** Its presence on a degraded disk raises the priority of confirming a second protected copy before this disk is stressed or retired.

### Reports

`/mnt/backup/reports/` contains:

- `monthly-archive.log`
- `monthly-vault.log`
- `retention.log`

The contents have not yet been reviewed.

### Recovery interpretation

This disk is not just a destination for one host. It contains:

- dated `ids-01` archive copies,
- multi-host Restic repositories,
- a homelab-vault Restic repository,
- SOPS/age recovery material,
- backup/retention reports.

Before the disk is replaced, stress-tested, reformatted or disconnected permanently, these datasets must be reconciled against the current Restic server on `ids-01` and any other authoritative backup copies.

## Network

| Item | Current state |
|---|---|
| Primary interface | `eth0` |
| Address | `192.168.2.48/24` |
| Link | 100 Mb/s, full duplex |
| Gateway | `192.168.2.1` |
| DNS | `192.168.2.48`, `192.168.2.242` |

The 100 Mb/s Ethernet ceiling is an important placement constraint if the attached 4 TB-class disk is considered for broader backup or storage duties.

## DNS workload

Pi-hole and Unbound are installed directly on the host, not containerized.

Observed versions:

- Pi-hole Core 6.4.3
- Pi-hole Web 6.6
- Pi-hole FTL 6.7
- Unbound 1.26.0

Observed state:

- Pi-hole FTL listening on port 53 for IPv4 and IPv6.
- Pi-hole blocking enabled.
- Unbound active on localhost port 5335.
- Unbound service active and enabled.

This confirms `192.168.2.48` is the current primary recursive/filtering DNS appliance.

## Current platform services

System-level services observed include:

- Pi-hole FTL
- Unbound
- Alloy
- Prometheus node exporter
- Zabbix Agent 2
- Dropbear SSH
- unattended upgrades

No Docker or k3s runtime was detected.

One failed unit was present:

- `smartmontools.service`

This is consistent with the storage-health detection gap and should be reconciled rather than carried forward automatically.

## Workload detectors

| Detector | Result |
|---|---|
| Docker | NO |
| k3s | NO |
| Pi-hole | YES |
| Unbound | YES |
| BirdNET | NO |

## Raspberry Pi health

- Firmware throttle state: `0x0`.
- Firmware temperature during audit: approximately 45 C.
- Thermal-zone CPU temperature later in the audit: approximately 50.5 C.
- No active throttling was reported.

## Current load snapshot

At audit time:

- load average: approximately `0.25 / 0.14 / 0.16`.
- Alloy used approximately 77 MiB RSS.
- Pi-hole FTL used approximately 67 MiB RSS.
- Unbound used approximately 28 MiB RSS.
- The host had ample free RAM for its current DNS role.

## Role-neutral audit conclusion

Hardware/workload audit: **COMPLETE — EXTERNAL HDD DEGRADED**  
Future hostname: **UNASSIGNED**  
Future role: **UNASSIGNED**

Strengths:

- very low current resource use
- stable Pi-hole/Unbound DNS workload
- directly attached 4 TB-class storage with large free capacity
- low thermal load

Constraints:

- Raspberry Pi 3 CPU generation
- approximately 1 GiB RAM
- 100 Mb/s Ethernet
- microSD boot media
- attached 4 TB-class HDD has 7 pending sectors and 2 offline-uncorrectable sectors; replacement/migration planning required

No future-role decision should be made until the remaining hosts are audited. The attached HDD is now a known storage-risk item and must have recoverability verified before it is replaced, stressed, reformatted, or reused.
