# media-01 — Current Hardware Record

> **Status: ACTIVE — REBUILT**  
> `media-01` is an active Raspberry Pi 5 media endpoint. The host has been rebuilt with a fresh Debian 13 operating system and is managed from `homelab-platform` IaC.

## Identity

| Item | Current state |
|---|---|
| Hostname | `media-01` |
| FQDN | `media-01.jameshouse` |
| Address | `192.168.2.195/24` |
| Hardware | Raspberry Pi 5 Model B Rev 1.0 |
| OS | Debian GNU/Linux 13 (trixie), rebuilt installation |
| Architecture | arm64 / aarch64 |
| Virtualization | Bare metal |
| Primary role | Dedicated Kodi media endpoint |
| Service status | Operational |

The former `k3s-node-01` identity is historical and must not be used for this host.

## Compute

| Item | Current state |
|---|---|
| CPU | ARM Cortex-A76 |
| Cores / threads | 4 / 4 |
| L2 cache | 2 MiB per core |
| L3 cache | 2 MiB |
| RAM | approximately 8 GiB |

The host has ample capacity for its dedicated media role.

## Storage

### Primary NVMe

| Item | Current state |
|---|---|
| Device | `/dev/nvme0n1` |
| Model | WD PC SN740 512 GB class NVMe |
| Capacity | 476.9 GiB |
| Filesystem | ext4 |
| Media root | `/srv/media` |

Historical SMART evidence showed the NVMe healthy with 1% lifetime used, no media/data-integrity errors and a temperature around 41 C. NVMe SMART/health metrics are planned for continuous monitoring.

### Boot/system media

The pre-rebuild audit recorded a SanDisk USB device as the system disk. Because the host has since been rebuilt, boot-media layout should be treated as current-installation state and re-audited when the next hardware inventory is run rather than inferred from the old image.

## Network

| Item | Current state |
|---|---|
| Primary interface | `eth0` |
| Address | `192.168.2.195/24` |
| Link | 1 GbE full duplex |
| Gateway | `192.168.2.1` |
| Wi-Fi | Present but not the intended production path |

## Current service role

`media-01` is a dedicated living-room/media endpoint. The current platform is reproducible through Git-managed Ansible.

Primary workload:

- Kodi 21 via `kodi.service`
- local media under `/srv/media`
- authenticated SMB share `\\media-01\Media`
- Chrony using the homelab time sources
- Prometheus node_exporter on TCP/9100

Docker and k3s are not part of the intended media host design.

## IaC ownership

Primary deployment:

```text
IaC/ansible/playbooks/media-01.yml
```

Supporting roles:

```text
IaC/ansible/roles/chrony_client/
IaC/ansible/roles/media_endpoint/
IaC/ansible/roles/media_smb/
IaC/ansible/roles/node_exporter/
IaC/ansible/roles/media_firewall/
```

Production service documentation:

```text
production docs/MEDIA-SERVICE.md
```

## Monitoring and remaining gates

Current and planned monitoring includes:

- node_exporter
- Raspberry Pi temperature/throttling metrics
- NVMe SMART/health metrics
- Kodi service availability
- Alloy/Loki logging once the central Loki service is deployed

The nftables policy and final monitoring gates remain follow-up work documented in the production service page.

## Rebuild decision

The previous multi-purpose / legacy state has been replaced by a dedicated, reproducible Debian 13 media build. This hardware page now represents the rebuilt host rather than the 2026-09-06 pre-rebuild workload audit.

## Status

Hardware role: **ACTIVE**  
OS rebuild: **COMPLETE — Debian 13**  
Primary service: **Kodi media endpoint**  
IaC ownership: **ACTIVE**