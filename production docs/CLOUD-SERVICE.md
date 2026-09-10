# Homelab Cloud Data Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** read-only deployment preflight passed; VM build preparation active; 4 TB production-data placement remains blocked pending completion of destructive disk validation  
**Primary service:** Nextcloud

## Production identity

| Hostname | IPv4 | Platform | Purpose |
|---|---:|---|---|
| `cloud-01.jameshouse` | `192.168.2.53` | Debian 13 VM on `PROXMOX` / `192.168.2.70` | Household private cloud, file sync and browser access |
| `PROXMOX` | `192.168.2.70` | Physical Proxmox VE | Hypervisor for `cloud-01` |
| `dns-01.jameshouse` | `192.168.2.51` | LXC on `Proxmox-2` | Primary local DNS resolver |
| `dns-02.jameshouse` | `192.168.2.50` | LXC on `PROXMOX` | Secondary local DNS resolver |

## Service design

`cloud-01` is intentionally disposable infrastructure around persistent user data.

Initial VM target:

- 2 vCPU
- 4 GiB RAM
- 32 GiB OS disk on normal Proxmox VM storage
- Debian 13
- Docker Engine / Compose
- Nextcloud
- PostgreSQL
- Redis
- separate persistent data device for Nextcloud user files

The operating system, packages, VM definition and service configuration are rebuilt from Git/IaC. User-created data is not treated as reproducible and must be protected separately.

## IaC ownership

The target ownership model is:

- Terraform/OpenTofu: VM identity, CPU, RAM, network, system disk and attachment declarations
- Ansible: Debian baseline, Docker, filesystem/mount preparation, service directories and health validation
- Compose: Nextcloud, PostgreSQL and Redis service definitions
- managed DNS: `cloud-01.jameshouse -> 192.168.2.53`
- SOPS/encrypted secrets: application/database credentials and recovery material
- Git: authoritative desired state

GUI-only configuration drift is not authoritative.

## Data storage

The candidate data device is the former DietPi-attached 4 TB USB disk:

- model: `WDC WD40EZRX-00SPEB0`
- drive serial: `WD-WCC4E0670079`
- USB bridge: UGREEN / Realtek `0bda:9201`
- capacity: 4.00 TB / 3.64 TiB
- stable current USB identity: `usb-WDC_WD40_EZRX-00SPEB0_133309270ED2-0:0`

The disk is currently undergoing a full destructive surface test before any production filesystem is created.

SMART baseline before testing:

- `Reallocated_Sector_Ct = 0`
- `Current_Pending_Sector = 7`
- `Offline_Uncorrectable = 2`
- `UDMA_CRC_Error_Count = 10`
- `Power_On_Hours = 28300`

Because the drive has recorded pending and uncorrectable sectors, a successful surface test does not make it an acceptable sole copy of irreplaceable data. Production acceptance requires a second independent copy of important Nextcloud data.

The device must be referenced by stable `/dev/disk/by-id/` identity, never by a transient `/dev/sdX` name.

## Rebuild versus backup policy

The platform follows this rule:

> Rebuild infrastructure. Back up data.

Rebuild from code rather than backing up:

- Debian operating system
- Docker packages
- Nextcloud container image
- PostgreSQL/Redis container images
- VM definition
- DNS/service configuration already held in Git

Protect because it is not reconstructable:

- Nextcloud user files
- PostgreSQL application database
- Nextcloud application state required for a consistent restore
- Terraform state
- protected secrets/recovery material not reconstructable elsewhere
- other user-created documents, photos and application data

## Recovery model

A full recovery should be possible as:

```text
Git / homelab-platform
        |
        v
Terraform creates cloud-01
        |
        v
Ansible configures Debian + Docker
        |
        v
Compose starts Nextcloud + PostgreSQL + Redis
        |
        v
Restore database + persistent data
        |
        v
Validate Nextcloud and client sync
```

The VM itself is therefore replaceable; the persistent data and database are the protected assets.

## Initial deployment sequence

1. complete the destructive 4 TB disk surface test;
2. compare post-test SMART values with the recorded baseline;
3. accept or reject the disk for service use;
4. partition and format only after the disk passes the agreed health gate;
5. define `cloud-01` in Terraform/OpenTofu;
6. configure Debian and Docker through Ansible;
7. deploy Nextcloud, PostgreSQL and Redis through Compose;
8. add managed DNS for `cloud-01.jameshouse`;
9. validate LAN-only web access and file sync;
10. create test data and prove a complete application restore;
11. establish a second independent copy of important data;
12. only then consider external Internet access.

## External access

Initial deployment is LAN-only.

Public access must not be enabled until:

- the LAN deployment is stable;
- HTTPS/reverse-proxy design is approved;
- authentication and rate-limit controls are in place;
- backup/restore has been proven;
- monitoring is active.

The eventual public name may be `cloud.jrwroberts.co.uk`, but external exposure is a later controlled change rather than part of the first deployment.

## Definition of done

The private-cloud layer is production-ready when:

- `cloud-01` is reproducibly built from IaC;
- Nextcloud, PostgreSQL and Redis are healthy;
- local DNS resolves the service correctly;
- client upload/download/sync tests pass;
- persistent data survives a controlled application rebuild;
- database + data restore is proven;
- the data disk has passed the agreed health gate;
- important data has a second independent copy;
- no critical dependency remains on DietPi `192.168.2.48`.


## Preflight evidence — 9 September 2026

The first live read-only preflight passed without changing resources.

Validated:

- `cloud-01` address `192.168.2.53` did not respond and had no resolved neighbour;
- target hypervisor is `PROXMOX` at `192.168.2.70`, Proxmox VE 9.2.11;
- `pve-cluster` is active and `/etc/pve` is mounted;
- candidate VM ID `200` is free;
- `vm-ssd` has approximately 420 GiB free;
- `local-lvm` has approximately 141 GiB free;
- Debian 13 genericcloud media is present at `/var/lib/vz/template/iso/debian-13-genericcloud-amd64.qcow2`;
- the 4 TB WDC data-device identity resolves correctly to the current `/dev/sdb`.

The destructive `badblocks` test was still running at the time of preflight and therefore the disk is not approved for cloud data use.

Interim SMART during the destructive test:

- Reallocated sectors: 0
- Current pending sectors: 0
- Offline uncorrectable sectors: 2
- UDMA CRC errors: 10

The fall in pending sectors is useful evidence but does not override the completion gate. Do not format, mount as production data, pass through to `cloud-01`, or treat this disk as a sole copy until the destructive test has completed and final SMART/badblocks evidence has been reviewed.
