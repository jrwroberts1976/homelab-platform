# Homelab Platform

Private migration workspace and future Infrastructure-as-Code authority for the JRW Roberts homelab.

## Status

This repository is currently **private** while the platform is being reviewed and rebuilt.

No legacy repository is authoritative here yet. Existing repositories remain the source of truth until each workload, configuration area, or document is explicitly migrated and validated.

## IaC authority

All new Infrastructure-as-Code is stored under [`IaC/`](IaC/). Terraform provisions infrastructure and Ansible configures operating systems/services. Do not add new IaC outside that directory.

The older top-level `terraform/` path predates this convention and will be migrated separately after its references and state handling are checked.

## Principles

- Git is the source of truth.
- Infrastructure changes are reviewed before deployment.
- Host ownership is explicit.
- Secrets are never stored in plaintext.
- Existing production state is discovered before it is changed.
- Migration is workload-by-workload with rollback paths.
- Legacy repositories are removed only after their useful content has been migrated and verified.

## Migration phases

1. Current-state hardware and workload inventory.
2. Target host-role design.
3. Repository and IaC structure.
4. Public-site migration.
5. Proxmox VM provisioning.
6. Komodo and Renovate rollout.
7. Workload migration by host.
8. Monitoring and security separation.
9. Jenkins / Stage 6 retirement.
10. Legacy repository cleanup.
11. Final documentation and public-readiness review.

## Delivery backlog

Percentages are planning estimates based on validated live state and merged IaC. They are updated when a workstream reaches a verified milestone. Product choices marked **preferred** are the current design choice but still require final deployment validation; **TBD** means no supplier has been approved yet.

| Workstream | Brief description | Product / supplier chosen | Why this choice | Tasks / next milestones | Complete | Status |
|---|---|---|---|---|---:|---|
| `docker-01` / BirdNET-Go | Dedicated bird-audio capture and classification host. | BirdNET-Go on Debian 13 / Raspberry Pi 4 | Lightweight, already proven with the existing USB microphone, easy to automate and monitor, and keeps the specialist workload isolated. | Host build, automation access, DNS, BirdNET-Go, USB audio validation, Prometheus monitoring, SMTP trust cleanup, idempotence and merge | **100%** | Complete |
| `cloud-01` baseline | Reproducible Linux VM foundation for the private-cloud workload. | Proxmox VE VM + Debian 13 + Ansible | Matches the standard homelab VM pattern, gives clean workload isolation, and makes the operating-system baseline reproducible through IaC. | Baseline applied and merged; Chrony check-mode validation corrected; unsupported OpenIPMI removed through IaC; zero failed units and second-run `changed=0` proven | **100%** | Complete |
| Nextcloud private cloud | Self-hosted file, sync and collaboration service on `cloud-01`. | Nextcloud + PostgreSQL + Redis | Mature open-source private-cloud stack; PostgreSQL provides durable relational storage and Redis supplies caching/locking expected for a reliable Nextcloud deployment. | Finalise protected secret handling; confirm storage layout; deploy PostgreSQL, Redis, Nextcloud and cron; configure SMTP/DNS; add backups, restore test, monitoring and idempotence proof | **20%** | Foundation ready |
| Observability standardisation | Common metrics, logs, dashboards and alerting for every service host. | Prometheus + Grafana + Loki + Grafana Alloy | Already established in the homelab, combines metrics and logs in one operational view, and Alloy provides a single modern collection agent that integrates naturally with Loki/Grafana. | Standardise Prometheus targets, Alloy agents, Loki labels/retention, host/service log collection, Grafana dashboards, alerting and dashboard-to-runbook links | **55%** | In progress |
| Network Hosts platform | Discover and enrich LAN hosts with operational and security context. | Custom collector + Prometheus/Loki/Grafana | The required IP/MAC/vendor/service/banner/TLS/history correlation is specific to this network; a small custom collector can feed the existing observability stack without introducing another management platform. | Build richer network-host collector; track identity, IP/MAC/vendor, latency, ports/services, banners, TLS, first/last seen and status changes; recreate Grafana Network Hosts dashboard | **20%** | Planned / design started |
| Web Platform / Analytics | Unified visibility of public-site visitors, edge security and origin health. | Cloudflare + Umami + Grafana | Cloudflare supplies edge/security telemetry, Umami gives lightweight privacy-focused visitor analytics, and Grafana provides one place to correlate those signals with origin/application health. | Combine Cloudflare edge/security data, Umami analytics and origin/application health into a dedicated Grafana dashboard | **20%** | Planned / design started |
| Password manager | Self-hosted secure credential vault with independent recovery and monitoring. | **Preferred:** Vaultwarden with Bitwarden-compatible clients | Much lighter than the full Bitwarden server stack while retaining the widely supported Bitwarden client ecosystem; well suited to a small self-hosted deployment, subject to final security/backup review. | Confirm Vaultwarden as the final choice; choose dedicated host/VM; HTTPS; protected secrets; MFA/recovery; SMTP; backups and restore test; Alloy/Loki; Grafana dashboard and runbook | **5%** | Preferred product selected; deployment not started |
| Home automation | Dedicated household automation platform, kept separate from general cloud workloads. | **Preferred:** Home Assistant OS / Home Assistant project | Appliance-style deployment, strong device/integration ecosystem, straightforward backup/restore, and the cleanest path for Zigbee/Z-Wave/Bluetooth USB passthrough and managed add-ons. | Choose dedicated VM/host; provision Home Assistant OS; plan Zigbee/Z-Wave/Bluetooth passthrough; backups; MQTT/Zigbee2MQTT/ESPHome as needed; monitoring, logs and dashboard | **0%** | Preferred product selected; planned |
| FreeSWITCH / SIP | Dedicated PBX/VoIP service providing extensions and external calling through a SIP trunk. | FreeSWITCH / SignalWire project; **SIP trunk supplier TBD** | FreeSWITCH is a mature, flexible open-source telephony platform with powerful dial-plan and SIP capabilities; the trunk supplier must be selected separately based on UK number, pricing, emergency-calling and interoperability requirements. | Choose dedicated `voice-01`/`pbx-01` host and SIP trunk supplier; protected credentials; inbound/outbound dial plans; DID/caller ID; RTP/NAT/firewall; brute-force protection; logs, metrics and Grafana dashboard | **0%** | PBX product selected; trunk supplier pending |
| Backup / recovery redesign | Replace fragmented backup arrangements with a tested, centrally managed recovery platform. | **Preferred:** Proxmox Backup Server; Restic/Backrest retained during transition | PBS integrates directly with Proxmox and provides incremental, deduplicated VM/CT backups and restore workflows; retaining Restic temporarily protects existing repositories while migration is proven. | Finalise Proxmox Backup Server placement; protect current Restic data; define service backup standards; test restores; document disaster-recovery paths | **25%** | In progress |
| Runbook catalogue | Central index of recovery and operational procedures mapped to hosts and services. | Markdown documentation in GitHub | Keeps procedures version-controlled beside IaC, reviewable through pull requests, searchable, portable and easy to link directly from Grafana dashboards. | Create a central dictionary of production runbooks, owners, applicable hosts/services, recovery steps and dashboard links | **30%** | In progress |
| Komodo / Renovate migration | Standardise container lifecycle management and automated dependency/version updates. | Komodo + Renovate | Komodo provides central Docker deployment/control while Renovate automates version-update proposals in Git, supporting the Git-first operating model without returning to ad-hoc container updates. | Move Docker lifecycle/version management to the approved Komodo model; validate canary deployment and retire superseded update workflows | **40%** | Paused / migration pending |

See [the migration tracker](docs/migrations/MIGRATION-TRACKER.md) for detailed progress and migration evidence.


## Production runbooks

- [DNS service recovery plan](production%20docs/DNS-SERVICE-RECOVERY-PLAN.md) — prerequisites, triage, service repair, CT rebuild, alternate-PVE recovery, validation, protection, DHCP cutover and total-DNS-outage recovery.
- [media-01 production service](production%20docs/MEDIA-SERVICE.md) — Kodi, SMB, Chrony, monitoring, firewall intent, deployment validation and recovery.
