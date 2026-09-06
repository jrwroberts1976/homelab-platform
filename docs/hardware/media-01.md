# media-01 Current-State Audit

Audit date: 2026-09-06  
Legacy hostname: `media-01`  
Address: `192.168.2.195`  
Audit method: repository-controlled `scripts/audit-linux-host.sh`, copied from TestServer and executed locally as root in read-only mode.

Audit artifact on media-01:

`/var/tmp/media-01-audit-20260906T073637Z.txt`

SHA256:

`a8e00978294a31b1aeb066a654f2880ae96234ecbfe0663eff7a6e8f311a82d8`

## Identity

| Item | Current state |
|---|---|
| Hardware | Raspberry Pi 5 Model B Rev 1.0 |
| OS | Debian GNU/Linux 13 (trixie) |
| Kernel | 6.18.34+rpt-rpi-2712 |
| Architecture | arm64 / aarch64 |
| Virtualization environment | Bare metal |
| Legacy hostname | `media-01` |

The previous DNS alias `k3s-node-01.jameshouse` pointing to this address is stale. Live evidence proves the host is currently named `media-01`.

## CPU

| Item | Current state |
|---|---|
| CPU | ARM Cortex-A76 |
| Cores | 4 |
| Threads per core | 1 |
| L2 cache | 2 MiB per core |
| L3 cache | 2 MiB |

## Memory

| Item | Current state |
|---|---|
| RAM | approximately 7.9 GiB |
| Used during audit | approximately 949 MiB |
| Available during audit | approximately 6.9 GiB |
| Swap | 2.0 GiB zram |
| Swap used | 0 |

This host currently has substantial free memory.

## Storage

### System disk

| Item | Current state |
|---|---|
| Device | `/dev/sda` |
| Media | SanDisk USB 3.2 Gen1 |
| Capacity | 28.7 GiB |
| Root partition | 28.1 GiB ext4 |
| Root filesystem usable size | approximately 28 GiB |
| Used | approximately 9.8 GiB |
| Available | approximately 17 GiB |
| Root usage | 37% |

SMART could not interrogate the SanDisk device through its USB bridge, so health of this boot device is currently **UNKNOWN**.

### NVMe

| Item | Current state |
|---|---|
| Device | `/dev/nvme0n1` |
| Model | WD PC SN740 512 GB class NVMe |
| Capacity | 476.9 GiB |
| Data partition | 476.4 GiB ext4 |
| Mounted at | `/home/homelab-backup/replica` and `/mnt/old-k3s-root` |
| Filesystem used | approximately 240 GiB |
| Filesystem available | approximately 206 GiB |
| Filesystem usage | 54% |

NVMe SMART health passed.

- Percentage used: 1%.
- Data written: approximately 11.9 TB.
- Media/data integrity errors: 0.
- Temperature: approximately 41 C.

The `/mnt/old-k3s-root` mount is direct evidence of previous k3s-related state on this machine and should be reviewed before any destructive rebuild.

## Network

| Item | Current state |
|---|---|
| Primary interface | `eth0` |
| Address | `192.168.2.195/24` |
| MAC | `2c:cf:67:30:be:1f` |
| Link | 1000 Mb/s, full duplex |
| Gateway | `192.168.2.1` |
| DNS | `192.168.2.48`, `192.168.2.242` |
| Wi-Fi | Present but down |

## Current platform services

System-level services observed include:

- Alloy
- Prometheus node exporter
- Zabbix Agent 2
- Kodi / desktop session
- LightDM
- NetworkManager
- smartmontools
- SSH
- unattended upgrades
- RPC/NFS support services

One failed unit was present:

- `openipmi.service`

This is likely irrelevant to a Raspberry Pi but should be intentionally removed or disabled during rebuild rather than silently carried forward.

## Workload detectors

| Detector | Result |
|---|---|
| Docker | NO |
| k3s | NO |
| Pi-hole | NO |
| Unbound | NO |
| BirdNET | NO |

This confirms the machine is **not currently a k3s node**, despite the stale DNS alias.

## Media workload

Kodi is the dominant current workload.

Observed listeners included ports associated with Kodi, and the process snapshot showed `kodi.bin` consuming approximately 109% CPU and around 518 MiB RSS at audit time.

The current media role is treated only as migration input. It does not determine this host's future assignment.

## Raspberry Pi health

- Firmware throttle state: `0x0`.
- Initial firmware temperature: approximately 51.6 C.
- Thermal-zone CPU temperature later in the audit: approximately 53.5 C.
- No active throttling was reported.

## Current load snapshot

At audit time:

- load average: approximately `1.53 / 1.56 / 1.54`.
- Kodi was the dominant CPU consumer.
- Alloy used approximately 278 MiB RSS.
- Zabbix Agent 2 and node exporter were lightweight.

## Role-neutral audit conclusion

Hardware audit: **COMPLETE**  
Workload inventory: **CAPTURED FOR MIGRATION ANALYSIS**  
Future hostname: **UNASSIGNED**  
Future role: **UNASSIGNED**

Strengths:

- Raspberry Pi 5 class CPU
- approximately 8 GiB RAM
- healthy 512 GB-class NVMe
- gigabit Ethernet
- substantial free RAM and NVMe capacity
- no Docker or k3s dependency currently active

Constraints:

- system currently boots from a small USB flash device whose health could not be assessed
- NVMe holds backup-replica data and an old k3s-root mount
- current media workload must be migrated or deliberately retained before rebuild

No future-role decision should be made until the remaining physical hosts have been audited to the same standard.
