<!-- estate-authority: IaC/inventory/estate.json -->
# admin-01 — Current Hardware Record

**Status:** ACTIVE — ADMINISTRATION / IaC CONTROLLER / QNETD  
**Current-state review:** 6 October 2026

## Identity

| Item | Current state |
|---|---|
| Hostname | `admin-01` |
| FQDN | `admin-01.jameshouse` |
| Address | `192.168.2.48/24` |
| Hardware | Raspberry Pi 3 Model B Rev 1.2 |
| OS | Debian GNU/Linux 13 (trixie) |
| Running kernel | `6.18.50+rpt-rpi-v8` |
| Architecture | arm64 / aarch64 |
| Login account | `james` |
| Virtualization | Bare metal |

## Compute

| Item | Current state |
|---|---|
| CPU | ARM Cortex-A53 |
| Cores / threads | 4 / 4 |
| L2 cache | 512 KiB |
| RAM | approximately 1 GiB |

The host is intentionally lightweight and dedicated to administration/control-plane support rather than application workloads.

## Network

| Item | Current state |
|---|---|
| Primary interface | `eth0` |
| Address | `192.168.2.48/24` |
| Link capability | 100 Mb/s full duplex |
| Gateway | `192.168.2.1` |

The interface is sufficient for Git/Ansible/SSH/QNetd duties; bulk storage and telemetry ingestion belong elsewhere.

## Current roles

`admin-01` is the normal control point for:

- Git checkout and reviewed homelab changes;
- production Ansible execution;
- SSH jump/administrative access;
- controller recovery tooling;
- external Corosync QNetd/QDevice third vote for `jameshouse-pve`.

QNetd listens on TCP/5403 and provides the independent third vote used by `PROXMOX` and `Proxmox-2`.

The host is **not** a DNS resolver. The active resolver pair is `dns-01` (`192.168.2.51`) and `dns-02` (`192.168.2.50`).

## Monitoring and patching

Current baseline includes:

- Node Exporter;
- Grafana Alloy;
- Zabbix Agent 2;
- controlled patch-status exporter;
- unattended security updates with automatic reboot disabled.

After the controlled October maintenance cycle:

- pending updates: 0;
- security updates pending: 0;
- reboot required: no;
- automatic reboot: disabled.

The 5 October kernel update was followed by a controlled reboot and QNetd/cluster quorum revalidation.

## Role boundaries

Do not place application, DNS, backup-storage, monitoring-server or network-sensor workloads on this Raspberry Pi. Its value is as a small independent administration/quorum control point.

Historical identities for this hardware are retained in `IaC/inventory/estate.json` and dated audits only. <!-- historical -->

## Status

Hardware role: **ACTIVE**  
OS: **Debian 13**  
Kernel: **6.18.50+rpt-rpi-v8**  
Primary roles: **ADMINISTRATION / SSH / IaC / QNETD**  
DNS role: **NONE**
