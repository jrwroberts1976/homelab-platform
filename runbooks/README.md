# Homelab Runbook Catalogue

This directory is the operational index for the homelab.

The authoritative machine-readable catalogue is [`registry.yml`](registry.yml). Existing service and recovery documents remain in their repository locations; this index does not duplicate them.

## Operating model

The registry answers four questions for every runbook:

1. **What procedure is authoritative?**
2. **What host, device or service does it apply to?**
3. **Where is it normally executed from?**
4. **What IaC implements or recovers it?**

`status` describes the lifecycle of the runbook itself. `service_state` describes the current state of the service covered by the runbook.

The normal IaC/recovery controller is now:

```text
admin-01.jameshouse
192.168.2.48
~/projects/homelab-platform
```

`TestServer` (`192.168.2.220`) is a legacy migration source, not the preferred controller. `ids-01` is decommissioned and explicitly excluded from active runbook scope.

## Current runbooks

| ID | Runbook | Category | Applies to | Normally run from | Runbook status | Service state | Last validated |
|---|---|---|---|---|---|---|---|
| `admin_control_plane` | Current architecture / admin baseline | Core infrastructure | `admin-01 .48` | local on `admin-01` | Active | Operational | 2026-09-10 |
| `dns_service_recovery` | [DNS Service Recovery Plan](../production%20docs/DNS-SERVICE-RECOVERY-PLAN.md) | Network | `dns-01 .51`, `dns-02 .50`, Proxmox hosts, ASUS DHCP/DNS | `admin-01 .48` | Active | Operational | 2026-09-10 |
| `router_syslog_service` | [ASUS Router Syslog Service](../production%20docs/ROUTER-SYSLOG-SERVICE.md) | Network | `RT-AC86U .1` -> `monitor-01 .52` | `admin-01 .48` | Active | Operational | 2026-09-10 |
| `monitoring_service` | [Homelab Monitoring Service](../production%20docs/MONITORING-SERVICE.md) | Monitoring | `monitor-01 .52`, estate monitoring targets | `admin-01 .48` | Active | Implementation in progress | 2026-09-10 |
| `central_logging_service` | [Central Logging Service](../production%20docs/CENTRAL-LOGGING-SERVICE.md) | Logging | `monitor-01 .52`, approved log sources | `admin-01 .48` | Active | Planned | — |
| `edge_service` | [Cloudflare Edge Service](../production%20docs/EDGE-SERVICE.md) | Edge / access | `edge-01 .56`, Cloudflare Zero Trust | `admin-01 .48` | Active | Implementation in progress | 2026-09-10 |
| `network_sensor_service` | [Homelab Network Sensor Service](../production%20docs/NETWORK-SENSOR-SERVICE.md) | Security | `sensor-01 .55` on `PROXMOX .70`, SPAN port 24 | `admin-01 .48` | Active | Implementation in progress | — |
| `time_service` | [Homelab Time Service](../production%20docs/TIME-SERVICE.md) | Core infrastructure | `PROXMOX .70`, `Proxmox-2 .71`, LAN clients | `admin-01 .48` | Active | Operational | — |
| `media_service` | [media-01 Production Service](../production%20docs/MEDIA-SERVICE.md) | Media | physical Raspberry Pi 5 `media-01 .195` | `admin-01 .48` | Active | Operational | — |
| `cloud_service` | [Homelab Cloud Data Service](../production%20docs/CLOUD-SERVICE.md) | Cloud | `cloud-01 .53` on `PROXMOX .70` | `admin-01 .48` | Active | Blocked / implementation | — |
| `cloudflare_pages_production` | [Cloudflare Pages Production Pipeline](../production%20docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md) | Public web | engineering portfolio / Cloudflare Pages | GitHub Actions/admin workstation | Active | Operational | 2026-09-07 |
| `testserver_retirement` | [TestServer Retirement Plan](../docs/migrations/TESTSERVER-RETIREMENT.md) | Migration | Pi 4 `TestServer .220` -> future `birdnet-01` | `admin-01 .48` | Active | Implementation in progress | 2026-09-10 |
| `router_clean_rebuild` | [Router Clean-Rebuild Plan](../docs/network/ROUTER-RESET-PLAN.md) | Network | `RT-AC86U .1`, AiMesh nodes | Local wired admin session | Planned | Maintenance planned | — |

## Current coverage gaps

These are deliberately recorded in `registry.yml` so missing recovery coverage is visible.

| Gap | Priority | Applies to | Needed runbook |
|---|---|---|---|
| `proxmox_node_health` | High | `PROXMOX .70`, `Proxmox-2 .71` | Node/service health checks and recovery |
| `proxmox_storage_health` | High | `PROXMOX .70`, `Proxmox-2 .71` | SMART, disk and Proxmox storage diagnosis/recovery |
| `mail_relay_recovery` | Medium | `mail-relay-01 .54` | SMTP relay diagnosis and rebuild/recovery |
| `birdnet_service_recovery` | Medium | future garden `birdnet-01` | Clean build, monitoring, data/config restore and recovery |

The previous `alloy_loki_pipeline` gap is now represented by the planned [Central Logging Service](../production%20docs/CENTRAL-LOGGING-SERVICE.md) runbook rather than remaining an undocumented gap.

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

Not every field is mandatory. Keep **the affected target** separate from **the execution/controller host**.

## Change rules

When adding or changing an operational service:

1. update the authoritative service/recovery document;
2. update `runbooks/registry.yml` in the same change;
3. keep host/IP data aligned with `IaC/ansible/inventory/hosts.yml` where the target is IaC-managed;
4. record a `last_validated` date only after the documented path has been proven against the live service;
5. move obsolete procedures to `deprecated` or `retired` rather than leaving ambiguous active instructions;
6. never add decommissioned hosts to active applicability lists;
7. do not use historical TestServer instructions as the current controller path unless a migration/rollback procedure explicitly requires TestServer itself.

The registry is intended to become the source for generated documentation and CI validation later. Until then, this README is the human-readable view and `registry.yml` remains authoritative.
