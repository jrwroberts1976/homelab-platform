# ids-01 — Decommissioned Hardware Record

> **Status: DECOMMISSIONED**  
> `ids-01` is no longer an active homelab host. Do not use it as a deployment, monitoring, DNS, backup, security, or troubleshooting target. This page is retained as historical migration evidence only.

Audit date: 2026-09-06  
Legacy hostname: `ids-01`  
Legacy address: `192.168.2.242`  
Audit method: repository-controlled `scripts/audit-linux-host.sh`, executed locally as root in read-only mode.

Audit artifact on the former host:

`/var/tmp/ids-01-audit-20260906T072950Z.txt`

SHA256:

`9c68b98add0a354a3dbfe7765e3cf0256a42e20405f5e6a842fa6ef2b0ae6981`

## Historical identity

| Item | Final audited state |
|---|---|
| Hardware | ASUS ZenBook UX482EAR |
| OS | Debian GNU/Linux 13 (trixie) |
| Kernel | 6.12.107+deb13-amd64 |
| Architecture | x86-64 |
| CPU | 11th Gen Intel Core i5-1155G7 @ 2.50 GHz |
| Cores / threads | 4 / 8 |
| RAM | approximately 15 GiB |
| Primary storage | HFM512GD3JX013N 512 GB-class NVMe |

## Historical workload summary

Before decommissioning, `ids-01` carried a mixed platform including Docker, Grafana, Prometheus, Loki, Alloy, Suricata, CrowdSec, Greenbone, Pi-hole secondary/Unbound, Nebula Sync, Restic REST server, node exporter and supporting agents/exporters.

Those workloads were migration inputs only. Their presence in this historical record must not be interpreted as current placement.

## Historical network

The host used `192.168.2.242/24`. Wi-Fi was the active path during the final audit, with a gigabit-capable USB Ethernet adapter present but disconnected.

## Historical persistence

Important legacy paths included:

- `/home/james/docker/data/monitoring/`
- `/home/james/docker/stacks/monitoring/`
- `/home/james/docker/stacks/pihole-secondary/`
- `/home/james/docker/stacks/nebula-sync/`
- `/home/homelab-backup/`
- Greenbone Docker volumes

These paths are recorded only for migration/recovery archaeology. They are not current service locations.

## Decommission decision

The host has been removed from the active homelab estate. Future inventories, monitoring configuration, deployment targets and troubleshooting should exclude `ids-01` unless the task is specifically historical or decommission-cleanup work.

## Status

Hardware audit: **HISTORICAL — COMPLETE**  
Host lifecycle: **DECOMMISSIONED**  
Active service role: **NONE**