# Homelab Platform

Authoritative Infrastructure-as-Code, operational documentation and recovery guidance for the JRW Roberts homelab.

## Current control plane

The normal administration and IaC controller is now:

```text
admin-01.jameshouse
192.168.2.48
Raspberry Pi 3 / Debian 13
~/projects/homelab-platform
```

`TestServer` (`192.168.2.220`) is no longer the preferred administration host. It remains online only as a legacy migration source while its remaining workloads are retired or rebuilt.

## Current estate

| Asset | Address | Placement / role | State |
|---|---:|---|---|
| ASUS RT-AC86U | `192.168.2.1` | Router, DHCP, NAT/firewall | Operational |
| HP ProCurve 2510G-24 | `192.168.2.16` | Core switch; port 24 mirror/SPAN | Operational / rebuild planned |
| admin-01 | `192.168.2.48` | Physical Raspberry Pi 3 administration / SSH jump host | Operational |
| dns-02 | `192.168.2.50` | LXC CT100 on `PROXMOX` | Operational |
| dns-01 | `192.168.2.51` | LXC CT101 on `Proxmox-2` | Operational |
| monitor-01 | `192.168.2.52` | VM200 on `Proxmox-2`; Prometheus/Grafana/Alertmanager/Blackbox | Operational; central logging pending |
| cloud-01 | `192.168.2.53` | VM200 on `PROXMOX` | Service work in progress |
| mail-relay-01 | `192.168.2.54` | LXC CT102 on `PROXMOX` | Operational |
| sensor-01 | `192.168.2.55` | VM201 on `PROXMOX` | Sensor tooling work in progress |
| edge-01 | `192.168.2.56` | LXC CT103 on `Proxmox-2`; Cloudflare edge connector host | Base host operational; tunnel/access pending |
| PROXMOX | `192.168.2.70` | Primary standalone Proxmox VE host | Operational |
| Proxmox-2 | `192.168.2.71` | Secondary standalone Proxmox VE host | Operational |
| media-01 | `192.168.2.195` | Physical Raspberry Pi 5 Kodi/media endpoint | Operational |
| TestServer | `192.168.2.220` | Physical Raspberry Pi 4 legacy Docker/BirdNET host | Retirement in progress |
| ids-01 | former `.242` | Decommissioned legacy host | Retired |

The two Proxmox hosts are deliberately standalone; there is no active Proxmox cluster.

## IaC authority

All new Infrastructure-as-Code belongs under [`IaC/`](IaC/). Terraform/OpenTofu provisions infrastructure and Ansible configures operating systems and services. Git contains desired state; plaintext secrets and local Terraform state do not belong in the repository.

## Current priorities

1. Install and configure `cloudflared` on `edge-01`, then create Cloudflare Tunnel and Access/MFA policies for selected internal services.
2. Build fresh central logging on `monitor-01` using Alloy and Loki; do not migrate the old TestServer logging stack as authoritative state.
3. Finish TestServer retirement only after backup/recovery dependencies are safe, then rebuild the Raspberry Pi 4 as the dedicated garden BirdNET-Go host.
4. Complete the WD 4 TB extended SMART review on `PROXMOX` before treating that disk as dependable storage.
5. Continue Proxmox node/storage recovery documentation and mail-relay recovery coverage.

## Documentation

- [Current-state architecture](docs/architecture/CURRENT-STATE.md)
- [Target-state architecture](docs/architecture/TARGET-STATE.md)
- [Network and service layout](docs/architecture/PROPOSED-LAYOUT.md)
- [Outstanding work](docs/architecture/OUTSTANDING-WORK.md)
- [Migration tracker](docs/migrations/MIGRATION-TRACKER.md)
- [Runbook catalogue](runbooks/README.md)
- [Authoritative runbook registry](runbooks/registry.yml)

## Operating principles

- Git is the source of truth for desired state and operational documentation.
- Discover live production state before changing it.
- Prefer read-only evidence and reversible changes first.
- Infrastructure changes require explicit target ownership, validation and rollback.
- Secrets are never stored in plaintext or printed into logs/documentation.
- Legacy workloads are removed only after their useful data, configuration and recovery path are accounted for.
- Decommissioned hosts are historical evidence only and must not re-enter active deployment or monitoring scope by accident.
