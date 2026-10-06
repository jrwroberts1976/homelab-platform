<!-- estate-authority: IaC/inventory/estate.json -->
# media-01 — Current Hardware Record

**Status:** ACTIVE — KODI ENDPOINT / PRIMARY PROXMOX NFS BACKUP TARGET  
**Current-state review:** 6 October 2026

## Identity

| Item | Current state |
|---|---|
| Hostname | `media-01` |
| Address | `192.168.2.195/24` |
| Hardware | Raspberry Pi 5 Model B Rev 1.0 |
| OS | Debian GNU/Linux 13 (trixie) |
| Architecture | arm64 / aarch64 |
| Virtualization | Bare metal |
| Primary roles | Kodi media endpoint; SMB media share; Proxmox NFS backup target |

Historical identities for this hardware are retained only in canonical inventory/audit history. <!-- historical -->

## Compute

| Item | Current state |
|---|---|
| CPU | ARM Cortex-A76 |
| Cores / threads | 4 / 4 |
| L2 cache | 2 MiB per core |
| L3 cache | 2 MiB |
| RAM | approximately 8 GiB |

## Storage

Primary NVMe:

- WD PC SN740 512 GB-class NVMe;
- ext4;
- media root `/srv/media`;
- also provides the filesystem used for the current Proxmox NFS backup namespaces.

Current backup exports:

```text
/srv/backup/pve-proxmox   -> PROXMOX 192.168.2.70
/srv/backup/pve-proxmox-2 -> Proxmox-2 192.168.2.71
```

NFS is a production infrastructure role on this host, not a future proposal.

## Network

| Item | Current state |
|---|---|
| Primary interface | `eth0` |
| Address | `192.168.2.195/24` |
| Link | 1 GbE full duplex |
| Gateway | `192.168.2.1` |
| Wi-Fi | present; not the intended production path |

The older 12 September physical switch map is historical and must not override the current SPAN/cabling architecture without fresh physical verification.

## Current services

Operational workloads include:

- Kodi via `kodi.service`;
- local media under `/srv/media`;
- authenticated SMB share;
- NFS v4.2 backup service for both Proxmox cluster nodes;
- Chrony client;
- Node Exporter;
- Grafana Alloy;
- Zabbix Agent 2;
- Kodi audio watchdog service/timer.

Docker and k3s are not part of the intended media-host design.

## Backup role

`media-01` is the primary Proxmox guest-backup target.

Current scheduled source jobs are:

```text
PROXMOX
  02:15
  storage: media-backup-proxmox
  guests: 100,102,104,105,200,201,204

Proxmox-2
  03:15
  storage: media-backup-proxmox-2
  guests: 101,103,202,203
```

The node-scoped NFS namespaces are deliberate. This host is therefore infrastructure-critical during Proxmox backup windows and should not be rebooted casually while backups are active.

## Monitoring and patching

Current monitoring/logging includes:

- Prometheus Node Exporter;
- Grafana Alloy to Loki;
- Zabbix Agent 2;
- service-level checks through the central monitoring platform.

The 5 October controlled maintenance cycle left:

- pending updates: 0;
- security updates pending: 0;
- reboot required: no;
- automatic reboot: disabled.

Kodi, SMB/NFS and the audio watchdog were revalidated after package maintenance.

## Role boundaries

`media-01` should remain focused on media playback, media file serving and the primary NFS backup-target function. It should not become a general Docker host, monitoring server, DNS resolver or cluster control-plane node.

## Status

Hardware role: **ACTIVE**  
OS: **Debian 13**  
Kodi: **ACTIVE**  
SMB: **ACTIVE**  
Proxmox NFS backup target: **ACTIVE / PRODUCTION**  
Grafana Alloy: **ACTIVE**  
Zabbix Agent 2: **ACTIVE**
