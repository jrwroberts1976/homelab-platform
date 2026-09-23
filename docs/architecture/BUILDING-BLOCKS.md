# Homelab Building Blocks

This is the technical home for the homelab's building blocks: what each component does, why it was selected, where it operates, how it integrates and how to verify or redeploy it.

> **Deployment truth:** [CURRENT-STATE.md](CURRENT-STATE.md) and [IaC/inventory/estate.json](../../IaC/inventory/estate.json) are authoritative. This is an explanatory catalogue, not an independent live inventory. Reconcile any apparent difference against those sources before acting. Historical identities are not active hosts. Planned tools, including Authelia, must not be described as deployed.

## How the pieces fit together

For central logging: **host and application logs → Grafana Alloy → Loki → Grafana → management-report evidence**. Both DNS resolvers' sanitised Pi-hole events were verified through Alloy to Loki in the original building-blocks record; its aggregate morning-report section was still outstanding at that point. **Do not forward raw DNS domains or client addresses.** Check current evidence before marking that outstanding work complete.

For monitoring: **exporters and service probes → Prometheus → Grafana and Alertmanager**, with **Zabbix Agent 2 → Zabbix** providing complementary host monitoring.

## Platform and operational building blocks

| Component | Purpose and selection rationale | Deployment / verification reference |
|---|---|---|
| Proxmox VE | Clustered management of Linux VMs and LXC workloads, with external quorum voting. Node-local disks do **not** provide automatic shared-storage HA. | [Current-state architecture](CURRENT-STATE.md), [cluster implementation](PROXMOX-CLUSTER-REBUILD-PLAN.md) |
| Pi-hole + Unbound | Two internal DNS resolvers combine domain policy filtering and local recursive resolution. | [Current-state architecture](CURRENT-STATE.md), [installed solutions](INSTALLED-SOLUTIONS-CATALOGUE.md) |
| Grafana Alloy | Consistent host, Docker (where enabled), router, sensor and sanitised DNS log collection and processing. | [Current-state architecture](CURRENT-STATE.md); inspect Alloy service/configuration and recent labelled Loki streams |
| Loki | Searchable operational and security logs with host/job labels. | On `monitor-01`; check ingestion freshness and expected streams in Grafana |
| Grafana | Dashboards and investigation across metrics and logs. | On `monitor-01`; verify datasource health and current panel data |
| Prometheus | Time-series metrics from exporters and service probes. | On `monitor-01`; inspect scrape targets and freshness |
| Alertmanager | Groups and routes actionable Prometheus alerts. | On `monitor-01`; inspect routes, inhibition and active alerts |
| Zabbix | Independent active-agent host and service telemetry. | `zabbix-01`; compare expected hosts with fresh measurements, not merely registered host objects |
| Suricata + Zeek | Signature-based intrusion alerts and protocol-level network evidence from mirrored traffic. | `sensor-01`; verify capture, both services and recent sensor evidence |
| Greenbone | Managed vulnerability scanning, evidence reporting and accepted-risk tracking. | `greenbone-01`; verify feeds, scan completion and report freshness |
| Docker | Reproducible application containers and container lifecycle. Log coverage is host-specific, not assumed universal. | Confirmed on selected hosts including `greenbone-01`, `komodo-01` and `docker-01`; inspect actual containers, drivers and Loki coverage |
| Komodo | Container-management control plane. | `komodo-01`; see [current-state architecture](CURRENT-STATE.md) |
| Backups and recovery | Scheduled Proxmox backups, state exports, restore testing and rollback. | [Backup strategy](BACKUP-STRATEGY.md) and [runbooks](../../runbooks/README.md) |
| Remote access | ASUS router OpenVPN endpoint for controlled LAN access. | [VPN implementation record](../network/VPN-REMOTE-ACCESS-DESIGN.md) |
| Ansible + Git | Reviewed, repeatable configuration and infrastructure change from `admin-01`. | [Repository README](../../README.md), [migration tracker](../migrations/MIGRATION-TRACKER.md) |

## Data formats, templates and test dependencies

These are building blocks **within** the platform, not extra production services.

| Tool | What it does | Where and how to verify |
|---|---|---|
| Jinja2 | Renders host-specific Ansible variables, templates and conditional configuration. Watch for conflicts between Jinja braces and Docker Go-template braces. | Ansible controller and IaC templates; run syntax/check-mode validation and review rendered diffs |
| JSON | Structured format for IaC inventory, APIs, Docker inspection, reports and validation. | Validate schemas and field types; do not commit secrets or sensitive logs |
| Python | Automation, bounded read-only API audits, JSON processing and privacy tests. | Administrative scripts and isolated test environments; run tests before rollout |
| Snappy | Lossless compression of Loki push-request payloads, useful for checking precisely what Alloy sends. | **Test dependency**, originally installed in an isolated environment on `dns-01`; verify the optional privacy test before claiming current availability |
| Protocol Buffers (Protobuf) | Binary format for Loki log batches; synthetic receiver tests can inspect decoded messages for privacy regressions. | **Test dependency**, originally paired with Snappy on `dns-01`; verify the isolated test environment |

## Operational contract for each building block

Each component's IaC and runbook should capture its authoritative inventory entry, installation and configuration paths, pinned versions and dependencies, idempotent deployment method, input/output integration, health and integration checks, monitoring, state/backup needs, upgrades, rollback and recovery. **Missing proof is “not yet verified”, not “complete”.**

### Practical verification checklist

- **Alloy:** `systemctl is-active alloy`, validate the actual Alloy configuration and permissions, and confirm fresh labelled streams in Loki. For DNS privacy, inspect synthetic compressed Loki payloads and verify that no raw domains or client IPs escape.
- **Prometheus / Grafana / Alertmanager:** inspect live targets, data-source health, panel freshness, firing alerts and routing before enabling new rules.
- **Zabbix:** reconcile expected hosts with recent numeric measurements and the actual Agent 2 identities.
- **DNS:** test normal resolution, blocked-domain policy, recursive Unbound forwarding and parity between both resolvers.
- **Network security:** verify mirrored traffic, Suricata and Zeek health, and freshness of exported sensor evidence.
- **Greenbone:** inspect completed scans, feed age, finding evidence and accepted-risk decisions.
- **Docker:** inspect running workloads and log drivers per host; do not assume every container is covered by Alloy.
- **IaC:** run syntax checks, safe check mode, SSH preflight and post-change validation; preserve a documented rollback.

## Deployed, test-only and planned

Current-state architecture and the IaC inventory determine what is deployed **now**. Isolated test dependencies are not production services. Proposed services and designs belong in [TARGET-STATE.md](TARGET-STATE.md) until deployment and validation are complete. In particular, **Authelia is not installed** and must remain a proposal until proven otherwise.

## Documentation ownership

The `homelab-platform` repository owns technical architecture, deployment decisions, IaC, operational verification and runbooks. The professional portfolio provides project summaries and links here rather than maintaining a second technical catalogue. This repository is currently private; a visitor needs GitHub access to read it. Never publish passwords, tokens, internal client browsing history or raw sensitive logs.
