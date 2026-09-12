# Proxmox-2 — Current Hardware Record

> **Status: ACTIVE — STANDALONE PROXMOX NODE**  
> Current-state review: 12 September 2026

This page records the current physical and Proxmox-visible state of `Proxmox-2`.

The earlier dated audit at `PVE2-HARDWARE-AUDIT-2026-09-08.md` is retained as historical evidence of the host before its storage/workload configuration was completed. Do not rewrite that dated audit to match today's state.

## Identity

| Item | Current state |
|---|---|
| Hostname | `Proxmox-2` |
| FQDN | `Proxmox-2.jameshouse` |
| Address | `192.168.2.71/24` |
| Manufacturer | ASUSTeK COMPUTER INC. |
| Model | ZenBook UX482EAR |
| Chassis | Laptop |
| OS | Debian GNU/Linux 13 (trixie) |
| Proxmox | VE 9.2.2 |
| Kernel | 7.0.2-6-pve |
| Architecture | x86_64 |
| Cluster state | Standalone by design |

The earlier `pve2` name remains visible in historical evidence and is accepted as a compatibility selector by some deployment tooling, but the current human-facing host identity is `Proxmox-2`.

## Compute

| Item | Current state |
|---|---|
| CPU | 11th Gen Intel Core i5-1155G7 |
| Physical cores | 4 |
| Logical CPUs | 8 |
| RAM | approximately 15 GiB usable |
| Swap | 8 GiB |

Current capacity is adequate for the existing guest set. Continue to monitor memory/IO as monitoring and edge workloads evolve.

## Storage

Physical system device:

- SK hynix HFM512GD3JX013N NVMe;
- approximately 476.9 GiB visible capacity.

Current Proxmox storage objects validated on 12 September:

| Storage | Approximate capacity | State |
|---|---:|---|
| `local` | ~98 GiB | active |
| `local-lvm` | ~348.8 GiB | active |

The earlier 8 September audit recorded `local-lvm` as not yet registered. That was true at the time; the current state above supersedes it operationally.

## Network

Primary management path:

- management address `192.168.2.71/24`;
- bridge/LAN path through the host's wired Ethernet interface;
- current switch mapping: HP ProCurve port 18;
- physical MAC observed: `00:1A:9F:0C:30:3B`;
- switch link observed at 1 Gbps full duplex.

Guest MAC addresses are learned behind the same switch port because the Proxmox bridge carries guest traffic.

## Current guests

Validated 12 September 2026:

| Type | ID | Guest | State |
|---|---:|---|---|
| VM | 200 | `monitor-01` | running |
| LXC | 101 | `dns-01` | running |
| LXC | 103 | `edge-01` | running |

### `monitor-01`

Current VM allocation observed:

- 6144 MiB RAM;
- 80 GiB disk;
- central Prometheus/Grafana/Alertmanager/Blackbox platform.

### `dns-01`

CT 101 provides Pi-hole + Unbound at `192.168.2.51`.

### `edge-01`

CT 103 exists at `192.168.2.56` as a reserved edge host. The Cloudflare Tunnel workload is not deployed; no `cloudflared` package/service/process was found during the estate audit.

## Host services

Validated current host services:

- Proxmox management services healthy;
- Chrony active;
- Node Exporter active on TCP/9100;
- Alloy inactive;
- zero failed systemd units.

The host provides the secondary LAN NTP endpoint:

```text
ntp-02.jameshouse -> 192.168.2.71
```

## Monitoring

Current monitoring includes:

- ICMP probe;
- Proxmox HTTPS probe on TCP/8006;
- Node Exporter scrape on TCP/9100.

All were healthy in the 12 September monitoring audit.

## Backup posture

No scheduled Proxmox guest backup jobs were configured on this node during the 12 September audit.

There is no PBS server on this host today.

Backup/recovery therefore remains an explicit platform gap; see `docs/architecture/BACKUP-STRATEGY.md`.

## Role boundaries

`Proxmox-2` is a hypervisor/core-infrastructure host. Do not turn it into a general-purpose application/Docker server merely because spare resources are available.

Application services should remain in explicitly managed guests.

## Status

Hardware record: **CURRENT**  
Standalone Proxmox role: **ACTIVE**  
Current guest placement: **VALIDATED 12 SEPTEMBER 2026**  
Node Exporter: **ACTIVE**  
Chrony/NTP: **ACTIVE**  
Alloy: **INACTIVE**  
Scheduled PVE backups: **NONE**
