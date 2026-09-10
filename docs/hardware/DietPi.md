# DietPi Historical Audit

**Original audit:** 6 September 2026  
**Lifecycle updated:** 10 September 2026  
**Former hostname:** `DietPi`  
**Former address:** `192.168.2.48`  
**Hardware:** Raspberry Pi 3 Model B Rev 1.2  
**Current identity of the Pi:** rebuilt as `admin-01` / `192.168.2.48`  
**Lifecycle:** historical / retired operating-system role

This file records the pre-rebuild DietPi/Pi-hole state for historical evidence. The DietPi operating-system role and physical DNS service are no longer active.

`192.168.2.48` is now the clean-built `admin-01` administration host. Do **not** use this historical document to configure `.48` as a DNS resolver.

## Historical hardware

| Item | Audited state |
|---|---|
| Hardware | Raspberry Pi 3 Model B Rev 1.2 |
| CPU | ARM Cortex-A53, 4 cores |
| RAM | approximately 955 MiB |
| Boot media | approximately 59 GB microSD |
| Ethernet | 100 Mb/s |
| Former OS | DietPi 10.6.2 / Debian 13 |
| Former hostname | `DietPi` |
| Former address | `192.168.2.48` |

The Pi has since been reimaged and is documented in `admin-01.md`.

## Historical DNS role

Before the rebuild, this host ran native:

- Pi-hole Core/Web/FTL;
- Unbound on localhost port 5335;
- local filtering/recursive DNS;
- monitoring agents.

That service has been replaced by the current dual LXC resolver design:

```text
dns-01  192.168.2.51  CT101 on Proxmox-2
dns-02  192.168.2.50  CT100 on PROXMOX
```

The ASUS router now advertises `.51` and `.50`. `.48` must not appear in active resolver configuration.

## Historical 4 TB backup disk

The Pi previously had a WDC WD40EZRX-00SPEB0 4 TB disk attached and mounted at `/mnt/backup`.

Historical audit evidence showed real backup/recovery material, including:

- dated monthly `ids-01` archives;
- Restic repositories for dietpi, homelab-vault, ids-01, historical k3s-node-01 and testserver;
- SOPS/age recovery material;
- backup/retention reports.

SMART evidence at that time included 7 current-pending sectors and 2 offline-uncorrectable sectors, so the disk was correctly classified as degraded/replacement-candidate despite the overall SMART PASSED line.

The disk is now attached to `PROXMOX` as the WD 4 TB candidate storage device. Later evidence showed pending sectors reduced to zero while `Offline_Uncorrectable` remained 2. An extended SMART test is still in progress as of 10 September 2026.

Do not treat this disk as the sole copy of irreplaceable data until the long test, final SMART attributes and independent backup coverage are reviewed.

## Historical recovery material

The old backup disk contained SOPS/age recovery material. Never print or commit the private recovery identity. Recovery keys must have a second protected copy independent of the WD disk.

## Why this file remains

This document is retained to explain:

- the origin of the old `.48` DNS configuration;
- the pre-rebuild Pi 3 hardware state;
- the provenance of the WD 4 TB backup disk and its historical SMART counters;
- old Restic/monthly/recovery data that may still need reconciliation.

It is **not** an active service runbook.

## Current references

- Current Pi 3 role: `docs/hardware/admin-01.md`
- Current DNS architecture: `production docs/DNS-SERVICE-RECOVERY-PLAN.md`
- Current backup direction: `docs/architecture/BACKUP-STRATEGY.md`
- Current estate: `docs/architecture/CURRENT-STATE.md`

## Historical evidence

Original audit artifact:

```text
/var/tmp/DietPi-audit-20260906T074300Z.txt
```

SHA256:

```text
d2252d3613d55359fdfa83616eb5f6fed3594fa9b9e73d08ff285b128a170619
```

Historical hardware/workload audit: **COMPLETE**  
DietPi service role: **RETIRED**  
Current hardware role: **admin-01 administration host**
