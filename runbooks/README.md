# Homelab Runbook Catalogue

This directory is the operational index for the homelab.

The authoritative machine-readable catalogue is [`registry.yml`](registry.yml). Existing service and recovery documents remain in their current repository locations; this index does not duplicate them.

## Operating model

The registry answers four questions for every runbook:

1. **What procedure is authoritative?**
2. **What host, device or service does it apply to?**
3. **Where is it normally executed from?**
4. **What IaC implements or recovers it?**

`status` describes the lifecycle of the runbook itself. `service_state` describes the current state of the service covered by the runbook. A runbook can therefore be `active` while the service is still `planned`, `blocked`, or under implementation.

The normal IaC/recovery controller is:

```text
TestServer
192.168.2.220
~/projects/homelab-platform
```

`ids-01` is explicitly excluded from active runbook scope because it has been decommissioned. Historical documentation may remain in Git for evidence, but it must not be treated as a deployment, monitoring or recovery target.

## Current runbooks

| ID | Runbook | Category | Applies to | Normally run from | Runbook status | Service state | Last validated |
|---|---|---|---|---|---|---|---|
| `dns_service_recovery` | [DNS Service Recovery Plan](../production%20docs/DNS-SERVICE-RECOVERY-PLAN.md) | Network | `dns-01 .51`, `dns-02 .50`, Proxmox hosts, ASUS DHCP/DNS | `TestServer .220` | Active | Operational | 2026-09-08 |
| `router_syslog_service` | [ASUS Router Syslog Service](../production%20docs/ROUTER-SYSLOG-SERVICE.md) | Network | `RT-AC86U .1` -> `monitor-01 .52` | `TestServer .220` | Active | Operational | 2026-09-10 |
| `monitoring_service` | [Homelab Monitoring Service](../production%20docs/MONITORING-SERVICE.md) | Monitoring | `monitor-01 .52`, estate monitoring targets | `TestServer .220` | Active | Implementation in progress | — |
| `network_sensor_service` | [Homelab Network Sensor Service](../production%20docs/NETWORK-SENSOR-SERVICE.md) | Security | `sensor-01 .55` on `PROXMOX .70`, SPAN port 24 | `TestServer .220` | Active | Planned | — |
| `time_service` | [Homelab Time Service](../production%20docs/TIME-SERVICE.md) | Core infrastructure | `PROXMOX .70`, `Proxmox-2 .71`, LAN clients | `TestServer .220` | Active | Operational | — |
| `media_service` | [media-01 Production Service](../production%20docs/MEDIA-SERVICE.md) | Media | `media-01 .195` | `TestServer .220` | Active | Operational | — |
| `cloud_service` | [Homelab Cloud Data Service](../production%20docs/CLOUD-SERVICE.md) | Cloud | `cloud-01 .53` on `PROXMOX .70` | `TestServer .220` | Active | Blocked | — |
| `cloudflare_pages_production` | [Cloudflare Pages Production Pipeline](../production%20docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md) | Public web | `engineering-portfolio`, Cloudflare Pages | GitHub Actions/admin workstation | Active | Operational | 2026-09-07 |
| `router_clean_rebuild` | [Router Clean-Rebuild Plan](../docs/network/ROUTER-RESET-PLAN.md) | Network | `RT-AC86U .1`, AiMesh nodes | Local wired admin session | Planned | Maintenance planned | — |

## Current coverage gaps

These are intentionally recorded in `registry.yml` so missing documentation is visible rather than silently assumed to exist.

| Gap | Priority | Applies to | Needed runbook |
|---|---|---|---|
| `proxmox_node_health` | High | `PROXMOX .70`, `Proxmox-2 .71` | Node health, cluster/service checks and recovery |
| `proxmox_storage_health` | High | `PROXMOX .70`, `Proxmox-2 .71` | SMART, disk and Proxmox storage diagnosis/recovery |
| `alloy_loki_pipeline` | High | `monitor-01 .52` | Alloy ingestion, Loki delivery and query validation |
| `mail_relay_recovery` | Medium | `mail-relay-01 .54` | SMTP relay diagnosis and rebuild/recovery |

## Registry conventions

Every new runbook should have a stable snake-case ID and should record, where relevant:

```yaml
runbook_id:
  title:
  category:
  document_type:
  document:
  status:
  service_state:
  applies_to:
  run_from:
  network:
  paths:
  iac:
  monitoring:
  triggers:
  validation:
  last_validated:
```

Not every field is mandatory for every procedure. The important rule is to keep **the affected target** separate from **the execution/controller host**.

For example, the router syslog runbook applies to the ASUS router and `monitor-01`, while deployment and most recovery commands are launched from TestServer.

## Change rules

When adding or changing an operational service:

1. update the authoritative service/recovery document;
2. update `runbooks/registry.yml` in the same change;
3. keep host/IP data aligned with `IaC/ansible/inventory/hosts.yml` where the target is IaC-managed;
4. record a `last_validated` date only after the documented path has been proven against the live service;
5. move obsolete procedures to `deprecated` or `retired` rather than leaving ambiguous active instructions;
6. never add decommissioned hosts to active applicability lists.

The registry is intended to become the source for automatically generated documentation and CI path validation later. Until generation is automated, this README is the human-readable view and `registry.yml` remains authoritative.
