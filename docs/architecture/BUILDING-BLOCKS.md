# Homelab Building Blocks

This is the technical home for the homelab's building blocks: what each component does, why it was selected, where it operates, how it integrates and how to verify or redeploy it.

> **Deployment truth:** [CURRENT-STATE.md](CURRENT-STATE.md) and [IaC/inventory/estate.json](../../IaC/inventory/estate.json) are authoritative. This is an explanatory catalogue, not an independent live inventory. Reconcile any apparent difference against those sources before acting. Historical identities are not active hosts. Planned tools, including Authelia, must not be described as deployed.

## How the pieces fit together

For central logging: **host and application logs → Grafana Alloy → Loki → Grafana → management-report evidence**. Do not forward raw DNS domains or client addresses.

For monitoring: **exporters and service probes → Prometheus → Grafana and Alertmanager**, with **Zabbix Agent 2 → Zabbix** providing complementary host monitoring.

For trusted browser administration: **Cloudflare DNS validation → Certbot / Let's Encrypt → service-specific deploy hook → trusted HTTPS endpoint**.

## Platform and operational building blocks

| Component | Purpose and selection rationale | Deployment / verification reference |
|---|---|---|
| Proxmox VE | Clustered management of Linux VMs and LXC workloads, with external quorum voting. Node-local disks do **not** provide automatic shared-storage HA. | [Current-state architecture](CURRENT-STATE.md), cluster implementation records |
| Pi-hole + Unbound | Two internal DNS resolvers combine domain policy filtering and local recursive resolution. | [Current-state architecture](CURRENT-STATE.md), [installed solutions](INSTALLED-SOLUTIONS-CATALOGUE.md) |
| Grafana Alloy | Consistent host, Docker (where enabled), router, sensor and sanitised DNS log collection and processing. | [Current-state architecture](CURRENT-STATE.md); inspect Alloy service/configuration and recent labelled Loki streams |
| Loki | Searchable operational and security logs with host/job labels. | On `monitor-01`; check ingestion freshness and expected streams in Grafana |
| Grafana | Dashboards and investigation across metrics and logs. Browser access is through trusted nginx HTTPS; the container listener is localhost-only. | `https://grafana.home.jrwroberts.co.uk/`; verify datasource health and current panel data |
| Prometheus | Time-series metrics from exporters and service probes. | On `monitor-01`; inspect scrape targets and freshness |
| Alertmanager | Groups and routes actionable Prometheus alerts. | On `monitor-01`; inspect routes, inhibition and active alerts |
| Zabbix | Independent active-agent host and service telemetry with trusted browser-facing HTTPS. | `https://zabbix.home.jrwroberts.co.uk/`; compare expected hosts with fresh measurements |
| Suricata + Zeek | Signature-based intrusion alerts and protocol-level network evidence from mirrored traffic. | `sensor-01`; verify capture, both services and recent sensor evidence |
| Greenbone | Managed vulnerability scanning, evidence reporting and accepted-risk tracking. | `greenbone-01`; verify feeds, scan completion, report freshness and accepted-risk reconciliation |
| Certbot + Let's Encrypt | Renewable trusted certificates using Cloudflare DNS validation and service-specific deploy hooks. | dns-01, dns-02, greenbone-01, monitor-01, zabbix-01, PROXMOX, Proxmox-2; dry-run renewal matrix validated 16 Oct 2026 |
| Raspberry Pi TF-A hardening | Trusted Firmware-A boot path for validated Cortex-A72 speculative-execution mitigations on `docker-01`. | `roles/raspberry_pi_tfa_hardening`; verify artifact SHA-256, managed boot block and kernel vulnerability files |
| Docker | Reproducible application containers and container lifecycle. Log coverage is host-specific, not assumed universal. | Confirmed on selected hosts; inspect actual containers, drivers and Loki coverage |
| Komodo | Container-management control plane. | `komodo-01`; see [current-state architecture](CURRENT-STATE.md) |
| Backups and recovery | Scheduled Proxmox backups, state exports, restore testing and rollback. | [Backup strategy](BACKUP-STRATEGY.md) and runbooks |
| Remote access | ASUS router OpenVPN endpoint for controlled LAN access. | VPN implementation records |
| Ansible + Git | Reviewed, repeatable configuration and infrastructure change from `admin-01`. | Repository IaC and migration/closure records |

## Data formats, templates and test dependencies

These are building blocks **within** the platform, not extra production services.

| Tool | What it does | Where and how to verify |
|---|---|---|
| Jinja2 | Renders host-specific Ansible variables, templates and conditional configuration. | Ansible controller and IaC templates; run syntax/check-mode validation and review rendered diffs |
| JSON | Structured format for IaC inventory, APIs, Docker inspection, reports and validation. | Validate schemas and field types; do not commit secrets or sensitive logs |
| Python | Automation, bounded read-only API audits, JSON processing and privacy tests. | Administrative scripts and isolated test environments; run tests before rollout |
| Snappy | Lossless compression of Loki push-request payloads for privacy/testing workflows. | Test dependency; verify current availability before use |
| Protocol Buffers (Protobuf) | Binary format for Loki log batches used by synthetic receiver/privacy tests. | Test dependency; verify current test environment |

## Operational contract for each building block

Each component's IaC and runbook should capture its authoritative inventory entry, installation and configuration paths, pinned versions and dependencies, idempotent deployment method, input/output integration, health and integration checks, monitoring, state/backup needs, upgrades, rollback and recovery. **Missing proof is “not yet verified”, not “complete”.**

### Practical verification checklist

- **Alloy:** validate the actual Alloy configuration and permissions and confirm fresh labelled streams in Loki.
- **Prometheus / Grafana / Alertmanager:** inspect live targets, datasource health, panel freshness, firing alerts and routing.
- **Zabbix:** reconcile expected hosts with recent numeric measurements and actual Agent 2 identities.
- **DNS:** test normal resolution, policy blocking, Unbound recursion and parity between resolvers.
- **Network security:** verify mirrored traffic, Suricata/Zeek health and freshness of exported sensor evidence.
- **Greenbone:** inspect completed scans, feed age, finding evidence and accepted-risk decisions; never treat missing/stale evidence as zero findings.
- **Trusted HTTPS:** verify the browser-facing FQDN, certificate chain, service health after deploy hooks and periodic Certbot dry-run renewal.
- **Pi TF-A:** verify the vendored checksum, target identity guards, managed `/boot/firmware/config.txt` block and kernel mitigation state.
- **Docker:** inspect running workloads and log drivers per host; do not assume every container is covered by Alloy.
- **IaC:** run syntax checks, safe check mode, SSH preflight and post-change validation; preserve a documented rollback.

## Deployed, test-only and planned

Current-state architecture and the IaC inventory determine what is deployed **now**. Isolated test dependencies are not production services. Proposed services and designs remain proposals until deployment and validation are complete. In particular, Authelia, CrowdSec and Cloudflare Tunnel are not current production services.

Raspberry Pi overclocking is a **future investigation only** as of 16 October 2026. No overclock should be described as deployed until model-specific thermal, power, throttling and stability evidence has been gathered and a reversible configuration is approved.

## Documentation ownership

The `homelab-platform` repository owns technical architecture, deployment decisions, IaC, operational verification and runbooks. The professional portfolio may summarise projects and link here rather than maintaining a second technical authority. Never publish passwords, tokens, private keys, internal browsing history or raw sensitive logs.
