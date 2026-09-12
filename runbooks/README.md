# Homelab Runbook Catalogue

This directory is the operational index for the homelab.

The authoritative machine-readable catalogue is [`registry.yml`](registry.yml). Existing service and recovery documents remain in their current repository locations; this index does not duplicate them.

## Operating model

The registry answers four questions for every runbook:

1. **What procedure is authoritative?**
2. **What host, device or service does it apply to?**
3. **Where is it normally executed from?**
4. **What IaC implements or recovers it?**

`status` describes the lifecycle of the runbook itself. `service_state` describes the current state of the service covered by the runbook. A runbook can therefore be active while a service is still under implementation or planned maintenance.

The normal IaC/recovery controller is:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired identities `TestServer` and `DietPi`, and the decommissioned host `ids-01`, are excluded from active runbook scope. Historical documents may retain those names as evidence, but they must not be used as current deployment, monitoring or recovery targets.

## Current runbooks

| ID | Runbook | Category | Applies to | Normally run from | Runbook status | Service state | Last validated |
|---|---|---|---|---|---|---|---|
| `dns_service_recovery` | [DNS Service Recovery Plan](../production%20docs/DNS-SERVICE-RECOVERY-PLAN.md) | Network | `dns-01 .51`, `dns-02 .50`, both Proxmox hosts, ASUS DHCP/DNS | `admin-01 .48` | Active | Operational | 2026-09-08 |
| `router_syslog_service` | [ASUS Router Syslog Service](../production%20docs/ROUTER-SYSLOG-SERVICE.md) | Network | `RT-AC86U .1` -> `monitor-01 .52` | `admin-01 .48` | Active | Operational | 2026-09-10 |
| `monitoring_service` | [Homelab Monitoring Service](../production%20docs/MONITORING-SERVICE.md) | Monitoring | `monitor-01 .52`, estate monitoring targets | `admin-01 .48` | Active | Operational | 2026-09-12 |
| `network_sensor_service` | [Homelab Network Sensor Service](../production%20docs/NETWORK-SENSOR-SERVICE.md) | Security | `sensor-01 .55` on `PROXMOX .70`; future SPAN path | `admin-01 .48` | Active | Implementation in progress | 2026-09-12 |
| `time_service` | [Homelab Time Service](../production%20docs/TIME-SERVICE.md) | Core infrastructure | `PROXMOX .70`, `Proxmox-2 .71`, LAN clients | `admin-01 .48` | Active | Operational | 2026-09-12 |
| `media_service` | [media-01 Production Service](../production%20docs/MEDIA-SERVICE.md) | Media | `media-01 .195` | `admin-01 .48` | Active | Operational | 2026-09-12 |
| `cloud_service` | [Homelab Cloud Data Service](../production%20docs/CLOUD-SERVICE.md) | Cloud | `cloud-01 .53` on `PROXMOX .70` | `admin-01 .48` | Active | Operational | 2026-09-12 |
| `mail_relay_service` | [Homelab Mail Relay Service](../production%20docs/MAIL-RELAY-SERVICE.md) | Core infrastructure | `mail-relay-01 .54` | `admin-01 .48` | Active | Operational | 2026-09-12 |
| `birdnet_service` | [BirdNET-Go Production Service](../production%20docs/BIRDNET-SERVICE.md) | Application | `docker-01 .220` | `admin-01 .48` | Active | Operational | 2026-09-12 |
| `cloudflare_pages_production` | [Cloudflare Pages Production Pipeline](../production%20docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md) | Public web | `engineering-portfolio`, Cloudflare Pages | GitHub Actions/admin workstation | Active | Operational | 2026-09-07 |
| `router_clean_rebuild` | [Router Clean-Rebuild Plan](../docs/network/ROUTER-RESET-PLAN.md) | Network | `RT-AC86U .1`, AiMesh nodes | Local wired admin session | Planned | Maintenance planned | — |

## Important current-state distinctions

- `192.168.2.48` is `admin-01`; it is **not** a DNS resolver or fallback resolver.
- `192.168.2.220` is `docker-01`; the retired `TestServer` identity must not be used as the controller.
- `edge-01` exists as CT 103 at `192.168.2.56`, but `cloudflared` / the Cloudflare Tunnel workload is **not deployed**.
- `sensor-01` Phase 1 is deployed and validated. Phase 2 waits for the dedicated USB capture NIC and switch repatching.
- HP ProCurve port 24 is the **planned future SPAN destination**. Port mirroring is currently disabled and port 24 currently carries the primary ASUS router link.
- `cloud-01` is live and operational on its dedicated 200 GiB VM data disk. Backup/restore proof remains outstanding.
- `monitor-01` is operational. The latest audit found 23 active Prometheus targets, all 23 healthy, with zero active alerts. Loki and Alloy are not deployed on `monitor-01`.
- `mail-relay-01` is operational, but Node Exporter/Prometheus coverage and end-to-end recovery testing remain gaps.
- `docker-01` is deliberately single-purpose for BirdNET-Go; do not recreate the old TestServer container estate on it.

## Current coverage gaps

These are intentionally recorded in `registry.yml` so missing documentation or recovery proof is visible rather than silently assumed to exist.

| Gap | Priority | Applies to | Needed work |
|---|---|---|---|
| `backup_recovery` | High | Proxmox estate, `cloud-01`, persistent data | Active backup architecture plus tested restore procedures |
| `proxmox_node_health` | High | `PROXMOX .70`, `Proxmox-2 .71` | Node health, Proxmox service checks and recovery |
| `proxmox_storage_health` | High | `PROXMOX .70`, `Proxmox-2 .71` | SMART, disk and Proxmox storage diagnosis/recovery |
| `alloy_loki_pipeline` | High | `monitor-01 .52` | Alloy ingestion, Loki delivery and query validation after deployment |
| `edge_cloudflare_tunnel` | Medium | `edge-01 .56` | Cloudflare Tunnel deployment/recovery once approved and deployed |
| `mail_relay_recovery_testing` | Medium | `mail-relay-01 .54` | Prove rebuild/credential restoration/end-to-end relay recovery |

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

For example, the router syslog runbook applies to the ASUS router and `monitor-01`, while deployment and most recovery commands are normally launched from `admin-01`.

## Validation-date rule

Do not advance `last_validated` merely because a document was edited.

Use the date only when the documented path has been proven at the appropriate level. For example, the DNS service itself was healthy during the 12 September estate audit, but the destructive DNS recovery workflow was not re-executed; its runbook therefore retains its earlier recovery-validation date.

## Change rules

When adding or changing an operational service:

1. update the authoritative service/recovery document;
2. update `runbooks/registry.yml` in the same change;
3. keep host/IP data aligned with `IaC/ansible/inventory/hosts.yml` where the target is IaC-managed;
4. record a `last_validated` date only after the documented path has been proven against the live service;
5. move obsolete procedures to `deprecated` or `retired` rather than leaving ambiguous active instructions;
6. never add decommissioned or retired identities to active applicability lists.

The registry is intended to become the source for automatically generated documentation and CI path validation later. Until generation is automated, this README is the human-readable view and `registry.yml` remains authoritative.
