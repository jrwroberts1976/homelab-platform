# Proxmox-2 Current-State Audit

**Updated:** 10 September 2026  
**Hostname:** `Proxmox-2`  
**Address:** `192.168.2.71`  
**Role:** secondary standalone Proxmox VE host / `ntp-02`  
**Status:** operational

## Identity

| Item | Current state |
|---|---|
| Hardware | ASUS ZenBook UX482EAR |
| CPU | Intel Core i5-1155G7, 4 cores / 8 threads |
| RAM | approximately 15 GiB |
| Architecture | x86-64 |
| Proxmox | pve-manager 9.2.2 at latest preflight |
| Kernel | `7.0.2-6-pve` at latest preflight |
| Management address | `192.168.2.71/24` |
| Gateway | `192.168.2.1` |
| Cluster | Standalone; no active two-node cluster |
| Normal controller | `admin-01` / `192.168.2.48` |

The hardware previously ran the decommissioned `ids-01` operating system/workloads. That historical state is not the current role and must not be restored accidentally.

## Capacity snapshot

A 10 September hosting preflight observed:

- 8 logical CPUs available;
- approximately 15 GiB RAM total;
- approximately 8.6 GiB RAM available at the time of the check;
- approximately 85 GiB free on the root filesystem;
- `local` storage approximately 94 GiB usable with low utilization;
- `local-lvm` approximately 349 GiB usable with low utilization.

This made Proxmox-2 the preferred placement for the lightweight `edge-01` connector workload.

## Current guests

| ID | Type | Name | Address | Role |
|---:|---|---|---:|---|
| 101 | LXC | `dns-01` | `192.168.2.51` | Primary Pi-hole + Unbound resolver |
| 103 | LXC | `edge-01` | `192.168.2.56` | Cloudflare Tunnel edge connector host |
| 200 | VM | `monitor-01` | `192.168.2.52` | Prometheus, Grafana, Alertmanager, Blackbox; future Loki/Alloy |

## edge-01 hosting notes

`edge-01` is an unprivileged Debian 13 LXC with:

- 1 vCPU;
- 768 MiB RAM;
- 256 MiB swap;
- 8 GiB root disk;
- static `.56/24` address;
- `nesting=1` for Debian 13/systemd mount behaviour;
- `/tmp` tmpfs capped at 192 MiB;
- systemd state `running` with zero failed units after the nesting fix.

The container base is ready; `cloudflared`, tunnel registration and Cloudflare Access/MFA configuration are still pending.

## monitor-01 hosting notes

`monitor-01` is VM200 with approximately:

- 4 vCPU;
- 6 GiB RAM;
- 80 GiB disk;
- static `.52` address.

Prometheus, Grafana, Alertmanager and Blackbox are operational. Fresh central logging with Loki/Alloy remains the next monitoring-platform phase.

## dns-01 hosting notes

`dns-01` is CT101 at `.51` and provides the primary Pi-hole + Unbound resolver role. `dns-02` on the other Proxmox host provides the second resolver, keeping DNS split across physical failure domains.

## Networking

Management uses `vmbr0` on the main `192.168.2.0/24` LAN. The current host remains standalone after the earlier cluster-join trial was rolled back.

A historical USB management-NIC RX error/drop concern should remain documented and rechecked if clustering, migration traffic or heavier east-west traffic is reconsidered.

## Host policy

- Keep application Docker workloads out of the Proxmox host itself.
- Keep guests explicitly represented in Git/IaC/inventory.
- Preserve the standalone-host assumption until a new cluster design is separately validated.
- Use `admin-01` for normal SSH/Ansible/IaC operations.
- Maintain Chrony `ntp-02` as a physical-host service.

## Recovery priorities

1. dedicated Proxmox node-health/service recovery runbook;
2. guest backup and restore testing;
3. storage-health/recovery runbook;
4. revalidate management NIC health before any future clustering/migration-network work;
5. ensure DNS/monitoring/edge guests can be rebuilt from Git/IaC without relying on the historical `ids-01` OS image.

## Historical reference

The earlier hardware audit remains at `docs/hardware/PVE2-HARDWARE-AUDIT-2026-09-08.md`. It is a dated build/audit record; this file is the current role/hosting summary.
