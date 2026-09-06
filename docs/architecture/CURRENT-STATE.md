# Current-State Architecture

This document is intentionally incomplete until discovery is performed on each host.

## Hosts and infrastructure to audit

| Asset | Known address | Known role | Audit state |
|---|---|---|---|
| PROXMOX | 192.168.2.70 | Primary x86 virtualization candidate | AUDITED — RAM/backup remediation required |
| TestServer | 192.168.2.220 | Legacy consolidated Docker/BirdNET/CI/monitoring host | AUDITED — future role/hostname unassigned |
| ids-01 | 192.168.2.242 | Legacy security/monitoring/DNS/backup host | AUDITED — future role/hostname unassigned |
| media-01 | 192.168.2.195 | Legacy Kodi/media host; stale `k3s-node-01` DNS alias | AUDITED — future role/hostname unassigned |
| DietPi | 192.168.2.48 | Legacy primary Pi-hole / Unbound DNS appliance with attached 4 TB-class backup disk | AUDITED — HDD DEGRADED (7 pending / 2 uncorrectable sectors); future role/hostname unassigned |
| BirdNET Pi | VERIFY | Garden-room BirdNET workload | NOT AUDITED |
| ASUS RT-AC86U main | 192.168.2.1 | Router / DHCP / AiMesh controller | DISCOVERED — reachable, device audit pending |
| ASUS AiMesh node | 192.168.2.181 | Wireless mesh node | DISCOVERED — reachable, device audit pending |
| ASUS AiMesh node | 192.168.2.218 | Wireless mesh node | DISCOVERED — reachable, device audit pending |
| HP ProCurve switch | 192.168.2.16 | Core managed switch | DISCOVERED — reachable, SSH closed, device audit pending |

The secondary Pi-hole currently associated with ids-01 is a workload, not a separate physical-host audit target. It will be captured during the ids-01 workload audit.

Addresses or identities marked VERIFY are deliberately not assumed; the discovery pass must reconcile them from live evidence.

## Required evidence per host

Every compute/Linux host audit must record the same minimum evidence set:

- hostname, IP and hardware manufacturer/model
- CPU model, architecture, sockets, cores, threads and virtualization capability
- RAM total, used, available and swap
- physical disks, models, serials, sizes and health
- partition/LVM/ZFS/filesystem layout, usage and free capacity
- NICs, addresses, link speed, duplex and routes
- OS, kernel, firmware/BIOS where available
- virtualization and container runtimes
- running services and failed units
- Docker containers, Compose projects, networks, volumes and bind mounts when Docker is present
- k3s/Kubernetes state when present
- appliance/workload state such as Pi-hole, Unbound or BirdNET when present
- exposed/listening ports
- monitoring agents/exporters
- backup and recovery coverage
- temperatures/thermals where available
- current CPU and memory load
- power/location constraints
- intended future role

Network appliances must receive an equivalent device audit, including CPU, memory, storage/flash, firmware, interfaces, link state, VLANs, routing, configuration backup coverage and current role where the platform exposes that information.

No target placement decision is final until the audit is complete.

## Completed audits

- [PROXMOX](../hardware/PROXMOX.md) — CPU and storage capacity are strong; RAM and guest-backup posture must be addressed before it becomes the primary compute platform.
- [TestServer](../hardware/TestServer.md) — Raspberry Pi 4, 4 cores, 3.7 GiB RAM, approximately 1 TB MMC storage; heavy consolidated Docker estate captured; future role and hostname deliberately unassigned.
- [ids-01](../hardware/ids-01.md) — ASUS ZenBook, i5-1155G7, 4C/8T, approximately 16 GiB RAM, healthy 512 GB-class NVMe; security, monitoring, DNS and backup workloads captured; future role and hostname deliberately unassigned.
- [media-01](../hardware/media-01.md) — Raspberry Pi 5, 4 Cortex-A76 cores, approximately 8 GiB RAM, healthy 512 GB-class NVMe plus 32 GB-class USB boot media; current Kodi role captured; future role and hostname deliberately unassigned.
- [DietPi](../hardware/DietPi.md) — Raspberry Pi 3, approximately 1 GiB RAM, 100 Mb/s Ethernet, native Pi-hole/Unbound and attached 4 TB-class backup disk; HDD is DEGRADED with pending/uncorrectable sectors and requires recoverability verification plus replacement planning.


## Fleet discovery

A TestServer jump-box discovery run on 2026-09-06 verified:

- TestServer: `192.168.2.220`, local Debian 13 arm64 host.
- PROXMOX: `192.168.2.70`, reachable with SSH open; hostname is not resolved by TestServer DNS.
- ids-01: `192.168.2.242`, resolves as `ids-01.jameshouse`, SSH open.
- `192.168.2.195` resolves in DNS as `k3s-node-01.jameshouse`, but a direct SSH login on 2026-09-06 proved the live hostname is `media-01`. Treat the DNS name as stale until the rebuild.
- DietPi: `192.168.2.48`, live hostname `DietPi`; Raspberry Pi 3 running native Pi-hole/Unbound with an attached 4 TB-class backup disk.
- ASUS infrastructure at `192.168.2.1`, `192.168.2.181`, and `192.168.2.218` is reachable.
- `192.168.2.16` is reachable but does not expose SSH and remains the switch audit target.
- BirdNET host identity/address is still to be verified from live evidence.

Discovery report on TestServer: `/var/tmp/homelab-fleet-discovery-20260906T071538Z.txt`
SHA256: `04d809dea1c8a3c72532909ddb9b116dee69c7aba576fd91ad666570481edd9f`
