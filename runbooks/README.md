# Homelab Runbook Catalogue

This directory is the operational index for the homelab.

The authoritative machine-readable catalogue is [`registry.yml`](registry.yml). Existing service and recovery documents remain in their current repository locations; this index does not duplicate them.

## Operating model

The registry answers four questions for every runbook:

1. **What procedure is authoritative?**
2. **What host, device or service does it apply to?**
3. **Where is it normally executed from?**
4. **What IaC implements or recovers it?**

`status` describes the lifecycle of the runbook itself. `service_state` describes the current state of the service covered by the runbook.

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
| `router_syslog_service` | [ASUS Router Syslog Service](../production%20docs/ROUTER-SYSLOG-SERVICE.md) | Network | `RT-AC86U .1` -> `monitor-01 .52` | `admin-01 .48` | Active | Operational | 2026-09-14 |
| `monitoring_service` | [Homelab Monitoring Service](../production%20docs/MONITORING-SERVICE.md) | Monitoring | `monitor-01 .52`, estate monitoring targets | `admin-01 .48` | Active | Operational | 2026-09-14 |
| `network_sensor_service` | [Homelab Network Sensor Service](../production%20docs/NETWORK-SENSOR-SERVICE.md) | Security | `sensor-01 .55` on `PROXMOX .70`, HP ProCurve SPAN | `admin-01 .48` | Active | Operational | 2026-09-14 |
| `time_service` | [Homelab Time Service](../production%20docs/TIME-SERVICE.md) | Core infrastructure | `PROXMOX .70`, `Proxmox-2 .71`, LAN clients | `admin-01 .48` | Active | Operational | 2026-09-12 |
| `media_service` | [media-01 Production Service](../production%20docs/MEDIA-SERVICE.md) | Media / backup target | `media-01 .195` | `admin-01 .48` | Active | Operational | 2026-09-14 |
| `cloud_service` | [Homelab Cloud Data Service](../production%20docs/CLOUD-SERVICE.md) | Cloud | `cloud-01 .53` on `PROXMOX .70` | `admin-01 .48` | Active | Operational | 2026-09-14 |
| `mail_relay_service` | [Homelab Mail Relay Service](../production%20docs/MAIL-RELAY-SERVICE.md) | Core infrastructure | `mail-relay-01 .54`, both PVE notification clients | `admin-01 .48` | Active | Operational | 2026-09-14 |
| `proxmox_backup_recovery` | [Proxmox Guest Backup and Recovery](../production%20docs/PROXMOX-BACKUP-RECOVERY.md) | Backup / recovery | both Proxmox nodes, `media-01`, `mail-relay-01` | `admin-01 .48` | Active | Operational primary path | 2026-09-14 |
| `birdnet_service` | [BirdNET-Go Production Service](../production%20docs/BIRDNET-SERVICE.md) | Application | `docker-01 .220` | `admin-01 .48` | Active | Operational | 2026-09-12 |
| `cloudflare_pages_production` | [Cloudflare Pages Production Pipeline](../production%20docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md) | Public web | `engineering-portfolio`, Cloudflare Pages | GitHub Actions/admin workstation | Active | Operational | 2026-09-07 |
| `router_clean_rebuild` | [Router Clean-Rebuild Plan](../docs/network/ROUTER-RESET-PLAN.md) | Network | `RT-AC86U .1`, AiMesh nodes | Local wired admin session | Planned | Maintenance planned | — |

## Important current-state distinctions

- `192.168.2.48` is `admin-01`; it is not a DNS resolver.
- `192.168.2.220` is `docker-01`; the retired `TestServer` identity must not be used as the controller.
- `edge-01` exists as CT103 at `192.168.2.56`, but `cloudflared` is not deployed.
- `sensor-01` capture is operational; Suricata and Zeek are active and HP ProCurve port 24 is the live SPAN destination for ports 1–23.
- `monitor-01` runs the production Prometheus/Grafana/Alertmanager/Blackbox/Loki stack and Alloy logging pipeline.
- `cloud-01` is live on its dedicated 200 GiB VM data disk and has a proven VM-level snapshot backup; application-consistent Nextcloud/PostgreSQL recovery is still unproven.
- `media-01` is both the Kodi endpoint and the primary Proxmox NFS backup target.
- the two standalone Proxmox nodes both currently have an unrelated VMID `200`; their active backup namespaces must remain isolated until guest IDs become cluster-unique.
- all seven production Proxmox guests have successful backup evidence in isolated repositories.
- CT103 has a proven isolated LXC restore/boot path.
- the isolated nightly backup jobs are live and policy-validated: `PROXMOX` runs at 02:15 to `media-backup-proxmox`; `Proxmox-2` runs at 03:15 to `media-backup-proxmox-2`; both use snapshot mode, zstd, `keep-last=3` and the notification system.
- the schedule reconciliation is idempotent (`changed=0` on both nodes on 14 September 2026) and zero failed systemd units were observed.
- the first unattended overnight run remains to be observed before unattended execution history is called proven.
- `docker-01` remains deliberately single-purpose for BirdNET-Go.

## Current coverage gaps

These are intentionally recorded in `registry.yml` so missing recovery proof is visible rather than silently assumed.

| Gap | Priority | Applies to | Needed work |
|---|---|---|---|
| `backup_secondary_copy` | High | primary backup target and important data | Independent second physical/failure-domain copy |
| `application_backup_recovery` | High | `cloud-01`, `docker-01`, `media-01`, `admin-01` | Application-consistent and non-Proxmox recovery proof |
| `proxmox_node_health` | High | `PROXMOX .70`, `Proxmox-2 .71` | Node health, Proxmox service checks and recovery |
| `proxmox_storage_health` | High | `PROXMOX .70`, `Proxmox-2 .71` | SMART, disk and Proxmox storage diagnosis/recovery |
| `edge_cloudflare_tunnel` | Medium | `edge-01 .56` | Cloudflare Tunnel deployment/recovery once approved |
| `mail_relay_recovery_testing` | Medium | `mail-relay-01 .54` | Full rebuild/credential restoration/recovery proof |

The former `alloy_loki_pipeline` gap is closed: Loki and Alloy are operational on `monitor-01`, and router syslog is ingested while retaining the local file.

## Registry conventions

Every new runbook should have a stable snake-case ID and record relevant target, controller, IaC, monitoring, validation and last-validated data.

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

## Validation-date rule

Do not advance `last_validated` merely because a document was edited. Use the date only when the documented path has been proven at the appropriate level.

For example, CT103's LXC restore path and the final isolated schedule cutover were both proven on 14 September 2026, while the first unattended overnight execution remains pending observation.

## Change rules

When adding or changing an operational service:

1. update the authoritative service/recovery document;
2. update `runbooks/registry.yml` in the same change;
3. keep host/IP data aligned with `IaC/ansible/inventory/hosts.yml` where the target is IaC-managed;
4. record a `last_validated` date only after the documented path has been proven against the live service;
5. move obsolete procedures to `deprecated` or `retired` rather than leaving ambiguous active instructions;
6. never add decommissioned or retired identities to active applicability lists.

The registry is intended to become the source for automatically generated documentation and CI path validation later. Until generation is automated, this README is the human-readable view and `registry.yml` remains authoritative.
