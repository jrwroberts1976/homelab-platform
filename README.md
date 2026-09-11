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

Percentages are planning estimates based on validated live state and merged IaC. They are updated when a workstream reaches a verified milestone.

| Workstream | Tasks / next milestones | Complete | Status |
|---|---|---:|---|
| `docker-01` / BirdNET-Go | Host build, automation access, DNS, BirdNET-Go, USB audio validation, Prometheus monitoring, SMTP trust cleanup, idempotence and merge | **100%** | Complete |
| `cloud-01` baseline | Make Chrony validation check-mode safe; remove unsupported OpenIPMI through IaC; apply baseline; verify zero failed units; prove second-run `changed=0` | **45%** | In progress |
| Nextcloud private cloud | Finalise protected secret handling; confirm storage layout; deploy PostgreSQL, Redis, Nextcloud and cron; configure SMTP/DNS; add backups, restore test, monitoring and idempotence proof | **20%** | Foundation ready |
| Observability standardisation | Standardise Prometheus targets, Alloy agents, Loki labels/retention, host/service log collection, Grafana dashboards, alerting and dashboard-to-runbook links | **55%** | In progress |
| Network Hosts platform | Build richer network-host collector; track identity, IP/MAC/vendor, latency, ports/services, banners, TLS, first/last seen and status changes; recreate Grafana Network Hosts dashboard | **20%** | Planned / design started |
| Web Platform / Analytics | Combine Cloudflare edge/security data, Umami analytics and origin/application health into a dedicated Grafana dashboard | **20%** | Planned / design started |
| Password manager | Select Vaultwarden vs official Bitwarden; choose dedicated host/VM; HTTPS; protected secrets; MFA/recovery; SMTP; backups and restore test; Alloy/Loki; Grafana dashboard and runbook | **5%** | Planned |
| Home automation | Choose dedicated host/VM and Home Assistant OS vs container model; plan Zigbee/Z-Wave/Bluetooth passthrough; backups; MQTT/Zigbee2MQTT/ESPHome as needed; monitoring, logs and dashboard | **0%** | Planned |
| FreeSWITCH / SIP | Choose dedicated `voice-01`/`pbx-01` host and SIP trunk provider; protected credentials; inbound/outbound dial plans; DID/caller ID; RTP/NAT/firewall; brute-force protection; logs, metrics and Grafana dashboard | **0%** | Planned |
| Backup / recovery redesign | Finalise Proxmox Backup Server placement; protect current Restic data; define service backup standards; test restores; document disaster-recovery paths | **25%** | In progress |
| Runbook catalogue | Create a central dictionary of production runbooks, owners, applicable hosts/services, recovery steps and dashboard links | **30%** | In progress |
| Komodo / Renovate migration | Move Docker lifecycle/version management to the approved Komodo model; validate canary deployment and retire superseded update workflows | **40%** | Paused / migration pending |

See [the migration tracker](docs/migrations/MIGRATION-TRACKER.md) for detailed progress and migration evidence.


## Production runbooks

- [DNS service recovery plan](production%20docs/DNS-SERVICE-RECOVERY-PLAN.md) — prerequisites, triage, service repair, CT rebuild, alternate-PVE recovery, validation, protection, DHCP cutover and total-DNS-outage recovery.
- [media-01 production service](production%20docs/MEDIA-SERVICE.md) — Kodi, SMB, Chrony, monitoring, firewall intent, deployment validation and recovery.
