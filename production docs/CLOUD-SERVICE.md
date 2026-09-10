# Homelab Cloud Data Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Primary service:** Nextcloud
**Host:** `cloud-01.jameshouse` / `192.168.2.53`
**Placement:** VM200 on `PROXMOX` / `192.168.2.70`
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`
**Status:** VM deployed/running; production data placement remains blocked pending final WD 4 TB disk acceptance and independent backup

## Production identity

| Hostname | IPv4 | Platform | Purpose |
|---|---:|---|---|
| `cloud-01.jameshouse` | `192.168.2.53` | Debian 13 VM200 on `PROXMOX` | Household private cloud/data service |
| `PROXMOX` | `192.168.2.70` | Physical Proxmox VE | Hypervisor for `cloud-01` |
| `dns-01.jameshouse` | `192.168.2.51` | LXC CT101 on `Proxmox-2` | Primary local resolver |
| `dns-02.jameshouse` | `192.168.2.50` | LXC CT100 on `PROXMOX` | Secondary local resolver |

## Service design

`cloud-01` is disposable infrastructure around persistent user data.

Current VM design:

- 2 vCPU class workload target;
- 4 GiB RAM class workload target;
- 32 GiB system disk;
- Debian 13;
- Docker/Compose application layer;
- Nextcloud;
- PostgreSQL;
- Redis;
- separate persistent data storage for user files when approved.

The operating system, VM definition and service configuration are rebuilt from Git/IaC. User-created data and application/database state are protected separately.

## IaC ownership

- Terraform/OpenTofu: VM identity, compute, network, system disk and attachment declarations;
- Ansible: Debian baseline, Docker, filesystem/mount preparation, directories and validation;
- Compose: Nextcloud, PostgreSQL and Redis;
- managed DNS: `cloud-01.jameshouse -> 192.168.2.53`;
- SOPS/encrypted/protected secret sources: application/database credentials and recovery material;
- Git: authoritative desired state.

GUI-only configuration drift is not authoritative.

## WD 4 TB candidate data disk

The candidate device attached to `PROXMOX` is:

```text
WDC WD40EZRX-00SPEB0
serial WD-WCC4E0670079
current device /dev/sdb
capacity approximately 4 TB
```

Historical SMART evidence included:

- reallocated sectors: 0;
- current pending sectors: previously 7, later 0;
- offline uncorrectable sectors: 2;
- UDMA CRC errors: 10.

The latest SMART overall-health result is PASSED, but an extended/long self-test is still running as of 10 September 2026 and the historical uncorrectable count remains relevant.

Do not interrupt or start another long test while the current one is running.

The disk is not approved as the sole copy of irreplaceable data. Final acceptance requires:

1. long self-test completion and log review;
2. stable/reviewed post-test SMART attributes;
3. a deliberate decision on whether the historical uncorrectable-sector evidence is acceptable for the intended role;
4. an independent second copy of important cloud data.

Use stable `/dev/disk/by-id/` identity for any production attachment/mount rather than relying on `/dev/sdX` naming.

## Rebuild versus backup policy

> Rebuild infrastructure. Back up data.

Rebuild from code:

- Debian OS;
- Docker packages/images;
- VM definition;
- Nextcloud/PostgreSQL/Redis service definitions;
- DNS/service configuration held in Git.

Protect because it is not reconstructable:

- Nextcloud user files;
- PostgreSQL application database;
- application state required for a consistent restore;
- Terraform/OpenTofu state where required for infrastructure management;
- protected secrets/recovery material;
- user-created household data.

## Recovery model

```text
Git / homelab-platform
        |
        v
Terraform/OpenTofu creates cloud-01
        |
        v
Ansible configures Debian + Docker
        |
        v
Compose starts application stack
        |
        v
Restore database + persistent data
        |
        v
Validate Nextcloud and client sync
```

## Production-data activation sequence

1. allow the current WD extended SMART test to finish;
2. review the self-test log and attributes;
3. accept or reject the disk for this service;
4. define stable disk identity/mount/passthrough in IaC if accepted;
5. deploy/validate Nextcloud, PostgreSQL and Redis on LAN-only access;
6. create representative test data;
7. prove database + file-data restore;
8. establish an independent second copy of important data;
9. add monitoring for service and storage health;
10. only then consider remote/public access.

## External access

Initial/normal validation is LAN-only.

If remote access is approved, use the new edge architecture:

```text
Internet
  -> Cloudflare Access
  -> Cloudflare Tunnel
  -> edge-01 192.168.2.56
  -> cloud-01 192.168.2.53
```

Do not expose Nextcloud by adding an ad-hoc router port-forward. Cloudflare Access/Tunnel is a separate controlled change after backup/restore and local service stability are proven.

## Monitoring and logging

`monitor-01` is the monitoring authority. Add application/storage health only after the underlying service is stable enough that alerts are actionable.

Central logs should use the fresh Alloy/Loki platform on `monitor-01` when available, not the old TestServer logging configuration.

## Definition of done

The private-cloud layer is production-ready when:

- `cloud-01` is reproducibly built from IaC;
- Nextcloud, PostgreSQL and Redis are healthy;
- local DNS resolves the service correctly;
- client upload/download/sync tests pass;
- persistent data survives a controlled application rebuild;
- database + data restore is proven;
- the chosen data disk/storage has passed its acceptance gate;
- important data has an independent second copy;
- monitoring/recovery are documented;
- no critical dependency remains on TestServer or a decommissioned host.
