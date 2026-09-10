# Current-State Architecture

**Updated:** 10 September 2026
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`

This document records the live estate after the September 2026 rebuild work. Historical audit documents remain useful evidence, but this file is the current architecture summary.

## Network core

| Asset | Address | Role | Current state |
|---|---:|---|---|
| ASUS RT-AC86U | `192.168.2.1` | Gateway, NAT, DHCP, firewall, AiMesh controller | Operational |
| HP ProCurve 2510G-24 | `192.168.2.16` | Core managed switch | Operational; port 24 is mirror/SPAN destination |
| LAN | `192.168.2.0/24` | Main homelab network | Operational |
| Local domain | `jameshouse` | Pi-hole local DNS domain/search suffix | Operational |

The ASUS router remains DHCP authority. The active resolver pair advertised to the LAN is `192.168.2.51` (`dns-01`) and `192.168.2.50` (`dns-02`).

## Administration

`admin-01` is the dedicated administration and IaC jump host:

```text
admin-01.jameshouse
192.168.2.48
Raspberry Pi 3
Debian 13
```

It holds the normal Git/Ansible/SOPS/age toolchain and estate SSH aliases. `TestServer` is no longer the preferred controller.

## Proxmox hosting

The two Proxmox hosts are deliberately **standalone**. There is no active two-node Proxmox cluster.

### PROXMOX — 192.168.2.70

Physical host: HP ProDesk 400 G4 DM, 6-core Intel i5-8500T, approximately 7.6 GiB RAM.

Current guests:

| ID | Type | Name | Address | Role |
|---:|---|---|---:|---|
| 100 | LXC | `dns-02` | `192.168.2.50` | Secondary Pi-hole + Unbound |
| 102 | LXC | `mail-relay-01` | `192.168.2.54` | Internal SMTP relay |
| 200 | VM | `cloud-01` | `192.168.2.53` | Cloud service platform |
| 201 | VM | `sensor-01` | `192.168.2.55` | Passive network/security sensor platform |
| 9000 | VM template | Debian 13 cloud template | — | Stopped template |
| 9001 | VM template | Debian 13 cloud template with QGA | — | Stopped template |

A WD 4 TB USB disk is attached to this host. Its SMART overall health has reported PASSED, but historical offline-uncorrectable evidence remains and an extended SMART test is still in progress as of this update. It is not approved as the sole copy of irreplaceable data.

### Proxmox-2 — 192.168.2.71

Physical host: ASUS ZenBook UX482EAR, Intel i5-1155G7, approximately 15 GiB RAM.

Current guests:

| ID | Type | Name | Address | Role |
|---:|---|---|---:|---|
| 101 | LXC | `dns-01` | `192.168.2.51` | Primary Pi-hole + Unbound |
| 103 | LXC | `edge-01` | `192.168.2.56` | Dedicated Cloudflare edge connector host |
| 200 | VM | `monitor-01` | `192.168.2.52` | Prometheus, Grafana, Alertmanager, Blackbox |

`edge-01` is Debian 13, unprivileged, 1 vCPU, 768 MiB RAM and 8 GiB disk. `nesting=1` is enabled to satisfy Debian 13/systemd mount behaviour; `/tmp` is capped at 192 MiB. The base host is healthy with zero failed units. `cloudflared`, the tunnel and Access policies are still pending.

## Physical Raspberry Pi hosts

| Host | Address | Hardware | Current role | State |
|---|---:|---|---|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 | Administration / SSH jump host | Operational |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 | Kodi/media endpoint | Operational |
| `TestServer` | `192.168.2.220` | Raspberry Pi 4 | Legacy Docker/BirdNET migration source | Retirement in progress |

The Pi 4 currently called `TestServer` is intended to be clean-rebuilt as the dedicated garden BirdNET-Go host after its remaining legacy responsibilities are retired safely.

## Decommissioned hosts

`ids-01` (`192.168.2.242`) is decommissioned. Historical documentation may remain for evidence and migration archaeology, but it must not be treated as an active deployment, monitoring, backup or recovery target.

## DNS

The authoritative local resolver pair is:

```text
dns-01.jameshouse  192.168.2.51  CT101 on Proxmox-2
dns-02.jameshouse  192.168.2.50  CT100 on PROXMOX
```

Both run Pi-hole + Unbound. The old physical DNS role formerly associated with `.48` is gone; `.48` is now `admin-01`.

## Monitoring and logging

`monitor-01` (`192.168.2.52`) is the central metrics/alerting platform and currently runs:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter

Central logging is the next phase. The approved direction is a **fresh** Loki/Alloy deployment on/around `monitor-01`, not migration of the old TestServer logging stack as authoritative state.

The ASUS router already forwards syslog over UDP/5514 to `monitor-01`; messages are stored locally at:

```text
/var/log/homelab/router/rt-ac86u.log
```

Alloy -> Loki -> Grafana ingestion for that file is pending.

## Public / remote access

Public static website hosting has moved to Cloudflare Pages. For selected internal applications, the target ingress model is:

```text
Internet
  -> Cloudflare Zero Trust / Access
  -> Cloudflare Tunnel
  -> edge-01 (192.168.2.56)
  -> explicitly selected LAN service
```

The tunnel is outbound-only from the homelab; no new inbound router port-forward is required for this design. The `edge-01` base host is ready, but the Cloudflare connector and Access/MFA configuration have not yet been completed.

## TestServer retirement boundary

`TestServer` still contains legacy Docker and migration state. Some old dashboards/public-web/monitoring components have already been stopped, but destructive cleanup remains blocked until backup/recovery state is understood and required persistence is protected.

The failed `homelab-backup-testserver.service` history remains a hard gate before deleting data, Compose definitions, volumes or images solely for cleanup.

## Current outstanding work

See [OUTSTANDING-WORK.md](OUTSTANDING-WORK.md) for the active queue. The major items are:

1. complete Cloudflare Tunnel + Access/MFA on `edge-01`;
2. build fresh central Loki/Alloy logging on `monitor-01`;
3. finish TestServer retirement and rebuild the Pi 4 as the garden BirdNET-Go host;
4. complete the WD 4 TB extended SMART review;
5. close Proxmox node/storage and mail-relay recovery documentation gaps.

## Historical evidence

The older host audit documents under `docs/hardware/` remain retained as dated snapshots. Where those snapshots conflict with this file, this current-state document and the live IaC inventory take precedence for present-day placement and role decisions.
