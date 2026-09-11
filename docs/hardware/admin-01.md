# admin-01 — Current Hardware Record

> **Status: ACTIVE — REBUILT**  
> `admin-01` is the dedicated Raspberry Pi administration and SSH jump host for the homelab. It replaces the former `DietPi` role on this hardware.

## Identity

| Item | Current state |
|---|---|
| Hostname | `admin-01` |
| FQDN | `admin-01.jameshouse` |
| Address | `192.168.2.48/24` |
| Hardware | Raspberry Pi 3 Model B Rev 1.2 |
| OS | Debian GNU/Linux 13 (trixie), rebuilt installation |
| Kernel | 6.18.39+rpt-rpi-v8 |
| Architecture | arm64 / aarch64 |
| Login account | `james` |
| Primary role | Administration / SSH jump host |
| Virtualization | Bare metal |

The former `DietPi` hostname and Pi-hole/Unbound role are retired and must not be used as current-state references for this host.

## Compute

| Item | Current state |
|---|---|
| CPU | ARM Cortex-A53 |
| Cores / threads | 4 / 4 |
| L2 cache | 512 KiB |
| RAM | approximately 1 GiB |

The host is intentionally kept lightweight and dedicated to administration rather than application workloads.

## Storage

The pre-rebuild hardware audit recorded a 64 GB-class microSD system device. Because the operating system has since been rebuilt, current filesystem usage should be captured during the next hardware audit rather than inherited from the old DietPi installation.

The former 4 TB WD USB backup disk is **not part of the admin-01 role**. That disk has been moved into the Proxmox/cloud-storage POC workflow and is documented separately.

## Network

| Item | Current state |
|---|---|
| Primary interface | `eth0` |
| Address | `192.168.2.48/24` |
| Link capability | 100 Mb/s full duplex |
| Gateway | `192.168.2.1` |

The 100 Mb/s interface is acceptable for its management/jump-host role because it is not intended to carry bulk storage, monitoring ingestion, or application traffic.

## Current role

`admin-01` provides a stable administrative entry point into the homelab and is used for interactive SSH access and orchestration entry rather than hosting production applications.

Authoritative Ansible inventory entry:

```text
IaC/ansible/inventory/hosts.yml
```

Current inventory policy:

- host: `admin-01`
- address: `192.168.2.48`
- user: `james`
- tags: `homelab`, `iac`, `core`, `admin`, `jump-host`, `raspberry-pi`

## Role boundaries

Do not reintroduce the former DietPi service set onto this host. In particular, `admin-01` is not intended to be:

- a Pi-hole/Unbound resolver
- a backup/storage server
- a Docker application host
- a monitoring platform
- a network sensor

Those functions now belong to dedicated infrastructure.

## Rebuild decision

The Raspberry Pi 3 hardware has been retained but rebuilt from the former DietPi/DNS appliance into a dedicated administration host. The hardware role is therefore current and active, while the DietPi identity and workload are historical only.

## Status

Hardware role: **ACTIVE**  
OS rebuild: **COMPLETE — Debian 13**  
Primary service role: **ADMINISTRATION / SSH JUMP HOST**  
Legacy DietPi role: **DECOMMISSIONED**