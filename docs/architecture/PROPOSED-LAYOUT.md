# Homelab Network and Service Layout

**Status:** current estate plus approved next work
**Updated:** 10 September 2026

This document is the text/mermaid counterpart to the network overview image. It deliberately distinguishes **live**, **in progress**, **planned** and **retired** state.

```mermaid
flowchart TB
  classDef live fill:#e8f7ec,stroke:#2f8f46,stroke-width:2px,color:#17351e
  classDef progress fill:#fff7db,stroke:#c89518,stroke-width:2px,color:#4c3a05
  classDef planned fill:#eef2f7,stroke:#7b8794,stroke-width:1.5px,color:#26323d,stroke-dasharray: 5 5
  classDef network fill:#e7f3ff,stroke:#3277b3,stroke-width:2px,color:#15324a
  classDef retired fill:#f8e8e8,stroke:#a84c4c,stroke-width:1.5px,color:#4c1f1f,stroke-dasharray: 3 3
  classDef physical fill:#f2ecff,stroke:#6e55b3,stroke-width:2px,color:#2e2351

  WAN["Internet"]:::network
  CF["Cloudflare<br/>Pages + Zero Trust / Access"]:::network
  ROUTER["ASUS RT-AC86U<br/>192.168.2.1<br/>Gateway / NAT / DHCP"]:::network
  SWITCH["HP ProCurve 2510G-24<br/>192.168.2.16<br/>Core switch<br/>Port 24 = SPAN"]:::network

  WAN --> CF
  WAN --> ROUTER
  ROUTER --> SWITCH

  ADMIN["LIVE<br/>admin-01<br/>192.168.2.48<br/>Raspberry Pi 3<br/>Admin / SSH / IaC"]:::physical
  MEDIA["LIVE<br/>media-01<br/>192.168.2.195<br/>Raspberry Pi 5<br/>Kodi / media"]:::physical
  TEST["RETIRING<br/>TestServer<br/>192.168.2.220<br/>Raspberry Pi 4<br/>Legacy Docker / BirdNET"]:::progress
  IDS["RETIRED<br/>ids-01<br/>former 192.168.2.242"]:::retired

  SWITCH --> ADMIN
  SWITCH --> MEDIA
  SWITCH --> TEST

  subgraph PVE1["PROXMOX — 192.168.2.70 — standalone"]
    direction TB
    PVE1HOST["LIVE<br/>PROXMOX<br/>NTP ntp-01"]:::live
    DNS02["LIVE<br/>CT100 dns-02<br/>192.168.2.50<br/>Pi-hole + Unbound"]:::live
    MAIL["LIVE<br/>CT102 mail-relay-01<br/>192.168.2.54<br/>SMTP relay"]:::live
    CLOUD["IN PROGRESS<br/>VM200 cloud-01<br/>192.168.2.53"]:::progress
    SENSOR["IN PROGRESS<br/>VM201 sensor-01<br/>192.168.2.55"]:::progress
    PVE1HOST --> DNS02
    PVE1HOST --> MAIL
    PVE1HOST --> CLOUD
    PVE1HOST --> SENSOR
  end

  subgraph PVE2["Proxmox-2 — 192.168.2.71 — standalone"]
    direction TB
    PVE2HOST["LIVE<br/>Proxmox-2<br/>NTP ntp-02"]:::live
    DNS01["LIVE<br/>CT101 dns-01<br/>192.168.2.51<br/>Pi-hole + Unbound"]:::live
    MON["LIVE<br/>VM200 monitor-01<br/>192.168.2.52<br/>Prometheus / Grafana<br/>Alertmanager / Blackbox"]:::live
    EDGE["BASE READY<br/>CT103 edge-01<br/>192.168.2.56<br/>Cloudflare connector host"]:::progress
    PVE2HOST --> DNS01
    PVE2HOST --> MON
    PVE2HOST --> EDGE
  end

  SWITCH --> PVE1HOST
  SWITCH --> PVE2HOST

  DNS01 -. "resolver pair" .- DNS02
  ADMIN -. "SSH / Ansible / IaC" .-> PVE1HOST
  ADMIN -. "SSH / Ansible / IaC" .-> PVE2HOST
  ADMIN -. "SSH / Ansible / IaC" .-> DNS01
  ADMIN -. "SSH / Ansible / IaC" .-> DNS02
  ADMIN -. "SSH / Ansible / IaC" .-> MON
  ADMIN -. "SSH / Ansible / IaC" .-> EDGE

  CF -. "planned outbound tunnel" .-> EDGE
  EDGE -. "selected internal services only" .-> MON

  ROUTER -. "UDP/5514 syslog" .-> MON
  LOKI["PLANNED<br/>Fresh Loki + Alloy<br/>central logging on monitor-01"]:::planned
  MON --> LOKI

  SPAN["Port 24<br/>SPAN / mirror destination"]:::network
  SWITCH -. "mirrored traffic" .-> SPAN
  SPAN -. "capture path" .-> SENSOR

  BIRD["PLANNED<br/>birdnet-01<br/>garden Raspberry Pi 4<br/>clean BirdNET-Go build"]:::planned
  TEST -. "after retirement / clean rebuild" .-> BIRD
```

## Current hosting

### PROXMOX (`192.168.2.70`)

| ID | Type | Workload | Address | State |
|---:|---|---|---:|---|
| 100 | LXC | `dns-02` | `192.168.2.50` | Operational |
| 102 | LXC | `mail-relay-01` | `192.168.2.54` | Operational |
| 200 | VM | `cloud-01` | `192.168.2.53` | Running / service work continues |
| 201 | VM | `sensor-01` | `192.168.2.55` | Running / sensor work continues |
| 9000 | VM template | Debian 13 cloud template | — | Stopped |
| 9001 | VM template | Debian 13 cloud template + QGA | — | Stopped |

### Proxmox-2 (`192.168.2.71`)

| ID | Type | Workload | Address | State |
|---:|---|---|---:|---|
| 101 | LXC | `dns-01` | `192.168.2.51` | Operational |
| 103 | LXC | `edge-01` | `192.168.2.56` | Base host operational; cloudflared pending |
| 200 | VM | `monitor-01` | `192.168.2.52` | Operational metrics/alerting; logging pending |

## Physical Raspberry Pi roles

| Host | Address | Hardware | Role |
|---|---:|---|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 | Administration / SSH / Ansible / Git |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 | Kodi/media endpoint |
| `TestServer` | `192.168.2.220` | Raspberry Pi 4 | Legacy migration source; future garden BirdNET-Go rebuild |

## Central logging

Current:

```text
RT-AC86U
  -> UDP/5514
  -> monitor-01 / rsyslog
  -> /var/log/homelab/router/rt-ac86u.log
```

Target:

```text
approved hosts / dedicated logs
  -> Alloy
  -> Loki on monitor-01
  -> Grafana
```

The old TestServer Alloy/Loki configuration is not the desired-state source.

## Cloudflare edge

`edge-01` is ready as an unprivileged Debian 13 LXC on `Proxmox-2`. The remaining work is to install/configure `cloudflared`, create the tunnel, define public hostnames and put Cloudflare Access/MFA in front of selected administrative applications.

No inbound router port-forward is part of this design.

## Outstanding work

See [OUTSTANDING-WORK.md](OUTSTANDING-WORK.md). The current order is:

1. Cloudflare Tunnel + Access on `edge-01`;
2. fresh Loki/Alloy central logging on `monitor-01`;
3. finish TestServer retirement with backup gates satisfied;
4. clean-build the Pi 4 as the garden BirdNET-Go host;
5. finish Proxmox storage/SMART and recovery documentation.
