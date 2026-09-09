# Homelab Network and Service Layout

**Status:** live build + target-state diagram  
**Updated:** 9 September 2026

This diagram shows both what is **already built** and what is **planned next**.

Legend:

- **COMPLETE** = built, live and validated
- **IN PROGRESS** = deployed but still being extended/validated
- **PLANNED** = approved future service, not yet deployed
- **RETIRED** = no longer part of the active design

```mermaid
flowchart TB
  classDef complete fill:#e8f7ec,stroke:#2f8f46,stroke-width:2px,color:#17351e
  classDef progress fill:#fff7db,stroke:#c89518,stroke-width:2px,color:#4c3a05
  classDef planned fill:#eef2f7,stroke:#7b8794,stroke-width:1.5px,color:#26323d,stroke-dasharray: 5 5
  classDef network fill:#e7f3ff,stroke:#3277b3,stroke-width:2px,color:#15324a
  classDef retired fill:#f8e8e8,stroke:#a84c4c,stroke-width:1.5px,color:#4c1f1f,stroke-dasharray: 3 3
  classDef physical fill:#f2ecff,stroke:#6e55b3,stroke-width:2px,color:#2e2351

  WAN["Internet / WAN"]:::network
  ROUTER["COMPLETE<br/>ASUS Router<br/>192.168.2.1<br/>Gateway / NAT / DHCP"]:::complete
  SWITCH["COMPLETE<br/>HP ProCurve 2510G-24<br/>192.168.2.16<br/>Core switch<br/>Port 24 = SPAN destination"]:::complete

  WAN --> ROUTER
  ROUTER --> SWITCH

  subgraph PVE1["PROXMOX — 192.168.2.70 — standalone"]
    direction TB
    PVE1HOST["COMPLETE<br/>PROXMOX<br/>Proxmox VE<br/>NTP: ntp-01<br/>node_exporter"]:::complete
    DNS02["COMPLETE<br/>CT100 dns-02<br/>192.168.2.50<br/>Pi-hole + Unbound<br/>node_exporter"]:::complete
    CLOUD["PLANNED<br/>cloud-01<br/>192.168.2.53<br/>Nextcloud + PostgreSQL + Redis"]:::planned
    MAIL["PLANNED NEXT<br/>mail-relay-01<br/>Postfix SMTP relay<br/>Gmail smart-host"]:::planned
    SECURITY["PLANNED<br/>security-01<br/>Greenbone"]:::planned
    SENSOR["PLANNED<br/>sensor-01<br/>Suricata"]:::planned

    PVE1HOST --> DNS02
    PVE1HOST --> CLOUD
    PVE1HOST --> MAIL
    PVE1HOST --> SECURITY
    PVE1HOST --> SENSOR
  end

  subgraph PVE2["Proxmox-2 — 192.168.2.71 — standalone"]
    direction TB
    PVE2HOST["COMPLETE<br/>Proxmox-2<br/>Proxmox VE<br/>NTP: ntp-02<br/>node_exporter"]:::complete
    DNS01["COMPLETE<br/>CT101 dns-01<br/>192.168.2.51<br/>Pi-hole + Unbound<br/>node_exporter"]:::complete
    MON["IN PROGRESS<br/>VM200 monitor-01<br/>192.168.2.52<br/>Prometheus + Grafana<br/>Alertmanager + Blackbox<br/>node_exporter"]:::progress

    PVE2HOST --> DNS01
    PVE2HOST --> MON
  end

  TEST["EXISTING / MIGRATION SOURCE<br/>TestServer<br/>192.168.2.220<br/>Controller + legacy Docker workloads"]:::physical
  MEDIA["COMPLETE EXISTING<br/>media-01<br/>192.168.2.195<br/>Raspberry Pi 5 / Kodi"]:::physical
  RET48["RETIRED<br/>192.168.2.48<br/>Former DNS host"]:::retired

  SWITCH --> PVE1HOST
  SWITCH --> PVE2HOST
  SWITCH --> TEST
  SWITCH --> MEDIA

  DNS01 -. "primary/secondary DNS pair" .- DNS02

  MON -. "ICMP / DNS / HTTPS / node metrics" .-> DNS01
  MON -. "ICMP / DNS / HTTPS / node metrics" .-> DNS02
  MON -. "node metrics + HTTPS" .-> PVE1HOST
  MON -. "node metrics + HTTPS" .-> PVE2HOST
  MON -. "ICMP" .-> ROUTER
  MON -. "ICMP" .-> TEST
  MON -. "ICMP" .-> MEDIA

  SPAN["COMPLETE RESERVED<br/>Switch port 24<br/>SPAN / mirror destination"]:::network
  CAPNIC["PLANNED<br/>Dedicated capture NIC<br/>No management IP"]:::planned

  SWITCH -. "mirrored traffic" .-> SPAN
  SPAN --> CAPNIC
  CAPNIC --> SENSOR

  MAIL -. "future SMTP" .-> GMAIL["PLANNED EXTERNAL RELAY<br/>smtp.gmail.com:587<br/>one App Password secret"]:::planned
  MON -. "future alert email" .-> MAIL
```

## Completed today

| Service / asset | Placement | Address | State |
|---|---|---:|---|
| ASUS router | Physical | `192.168.2.1` | **COMPLETE** — gateway, NAT and DHCP remain here |
| HP ProCurve 2510G-24 | Physical | `192.168.2.16` | **COMPLETE** — core switch; port 24 reserved for SPAN |
| PROXMOX | Physical | `192.168.2.70` | **COMPLETE** — standalone Proxmox host, NTP server, node exporter |
| Proxmox-2 | Physical | `192.168.2.71` | **COMPLETE** — standalone Proxmox host, NTP server, node exporter |
| dns-01 | CT101 on Proxmox-2 | `192.168.2.51` | **COMPLETE** — Pi-hole + Unbound; node exporter |
| dns-02 | CT100 on PROXMOX | `192.168.2.50` | **COMPLETE** — Pi-hole + Unbound; node exporter |
| monitor-01 | VM200 on Proxmox-2 | `192.168.2.52` | **IN PROGRESS** — Prometheus, Grafana, Alertmanager and Blackbox are live; alerting/dashboard work still being added |
| TestServer | Physical | `192.168.2.220` | **EXISTING** — IaC/controller and legacy workloads during migration |
| media-01 | Physical Raspberry Pi 5 | `192.168.2.195` | **EXISTING / LIVE** — Kodi/media |
| Former DNS host | Retired | `192.168.2.48` | **RETIRED** — must not be used as a resolver |

## Planned services

| Service | Planned placement | Address | Purpose |
|---|---|---:|---|
| mail-relay-01 | PROXMOX | **TBD by preflight** | Internal Postfix SMTP relay; only host holding Gmail App Password |
| cloud-01 | PROXMOX | `192.168.2.53` | Nextcloud + PostgreSQL + Redis |
| security-01 | PROXMOX | TBD | Greenbone vulnerability scanning |
| sensor-01 | PROXMOX | TBD | Suricata IDS fed by switch SPAN port 24 |
| Loki / Alloy | monitor-01 | existing `.52` | Central logging after metrics/alerting is stable |

## Current monitoring coverage

The monitoring platform currently has external service probes and host metrics for the core estate.

**Host metrics (node_exporter):**

- `dns-01` — `192.168.2.51:9100`
- `dns-02` — `192.168.2.50:9100`
- `monitor-01` — `192.168.2.52:9100`
- `PROXMOX` — `192.168.2.70:9100`
- `Proxmox-2` — `192.168.2.71:9100`

**Blackbox probes:**

- router ICMP
- both DNS resolvers ICMP + TCP/53
- both Proxmox hosts ICMP + HTTPS/8006
- monitor-01 ICMP
- TestServer ICMP
- media-01 ICMP

Service-specific Pi-hole/Unbound metrics and Chrony/NTP synchronisation metrics are still to be added.

## Mail flow target

The planned alerting/mail path is:

```text
Prometheus
   |
   v
Alertmanager
   |
   v
mail-relay-01
Postfix
   |
   v
smtp.gmail.com:587
   |
   v
Gmail / notification inbox
```

Only `mail-relay-01` will hold the Gmail App Password. Other homelab services will submit mail to the internal relay without needing Gmail credentials.

## Network design notes

- DHCP remains on the ASUS router.
- The active DNS pair is `.51 + .50`.
- `.48` is retired and must not appear in active resolver configuration.
- The two Proxmox hosts remain standalone; there is no active Proxmox cluster.
- Port 24 on the HP ProCurve remains reserved as the Suricata SPAN destination.
- New workloads are built through Git-managed Terraform/OpenTofu + Ansible wherever practical.
