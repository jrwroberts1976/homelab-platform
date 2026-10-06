<!-- estate-authority: IaC/inventory/estate.json -->
# Homelab Runbook Catalogue

**Reviewed:** 6 October 2026

This directory is the operational index for the homelab. `runbooks/registry.yml` is the machine-readable catalogue; service/recovery documents remain in their existing repository locations.

## Operating model

The normal controller is:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

`admin-01` also supplies Corosync QNetd for the production Proxmox cluster.

Retired identities `TestServer`, `DietPi`, `ids-01` and the former `k3s-node-01` identity are excluded from active runbook scope. Historical documents may retain those names as evidence only. <!-- historical -->

## Current runbooks

| ID | Runbook | Category | Applies to | Status / service state |
|---|---|---|---|---|
| `dns_service_recovery` | [DNS Service Recovery Plan](../production%20docs/DNS-SERVICE-RECOVERY-PLAN.md) | Network | `dns-01 .51`, `dns-02 .50`, cluster/router | Active / Operational |
| `router_syslog_service` | [ASUS Router Syslog Service](../production%20docs/ROUTER-SYSLOG-SERVICE.md) | Network | RT-AC86U -> `monitor-01 .52` | Active / Operational |
| `remote_access_vpn` | [ASUS Router OpenVPN Remote Access](../docs/network/VPN-REMOTE-ACCESS-DESIGN.md) | Network security | RT-AC86U, `monitor-01` logging | Active / **Operational** |
| `monitoring_service` | [Homelab Monitoring Service](../production%20docs/MONITORING-SERVICE.md) | Monitoring | `monitor-01 .52`, estate targets | Active / Operational |
| `network_sensor_service` | [Homelab Network Sensor Service](../production%20docs/NETWORK-SENSOR-SERVICE.md) | Security | `sensor-01 .55`, HP ProCurve SPAN | Active / Operational |
| `time_service` | [Homelab Time Service](../production%20docs/TIME-SERVICE.md) | Core infrastructure | `.70`, `.71`, LAN clients | Active / Operational |
| `media_service` | [media-01 Production Service](../production%20docs/MEDIA-SERVICE.md) | Media / backup target | `media-01 .195` | Active / Operational |
| `cloud_service` | [Homelab Cloud Data Service](../production%20docs/CLOUD-SERVICE.md) | Cloud | `cloud-01 .53` | Active / Operational |
| `mail_relay_service` | [Homelab Mail Relay Service](../production%20docs/MAIL-RELAY-SERVICE.md) | Core infrastructure | `mail-relay-01 .54`, PVE clients | Active / Operational |
| `proxmox_backup_recovery` | [Proxmox Guest Backup and Recovery](../production%20docs/PROXMOX-BACKUP-RECOVERY.md) | Backup / recovery | `jameshouse-pve`, `media-01` | Active / Operational primary path |
| `birdnet_service` | [BirdNET-Go Production Service](../production%20docs/BIRDNET-SERVICE.md) | Application | `docker-01 .220` | Active / Operational |
| `greenbone_service` | [Greenbone Vulnerability Scanner Service](../production%20docs/GREENBONE-SERVICE.md) | Security | `greenbone-01 .57` | Active / Operational |
| `home_automation` | [Home Automation / Home Assistant Design](../docs/architecture/HOME-AUTOMATION-DESIGN.md) | Application | `home-01 .60` | Active / Operational |
| `cloudflare_pages_production` | [Cloudflare Pages Production Pipeline](../production%20docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md) | Public web | portfolio / Cloudflare Pages | Active / Operational |
| `router_clean_rebuild` | [Router Clean-Rebuild Plan](../docs/network/ROUTER-RESET-PLAN.md) | Network | RT-AC86U + AiMesh | Planned / Maintenance planned |

## Current-state distinctions

- `192.168.2.48` is `admin-01`; it is not a DNS resolver.
- `192.168.2.220` is `docker-01`; the retired TestServer identity is historical only. <!-- historical -->
- `PROXMOX .70` and `Proxmox-2 .71` form `jameshouse-pve`.
- Corosync link0 is the direct `10.255.255.0/30` interconnect; management LAN is fallback link1.
- `admin-01` supplies the QDevice/QNetd third vote.
- production guest disks remain node-local; cluster membership is not automatic guest-data HA.
- `monitor-01` is VM202 on `Proxmox-2`.
- `monitor-01` is the **single active network-discovery owner** after the 27 September cutover; `Proxmox-2` source timers are disabled/inactive.
- `edge-01` exists as CT103, but `cloudflared` is not deployed.
- `sensor-01` capture is operational; switch ports 1–23 are mirrored to port 24.
- `monitor-01` runs the production Prometheus/Grafana/Alertmanager/Blackbox/Loki stack.
- Step 10 Grafana Home/Hosts/Patch/Node Detail estate foundation is complete.
- ASUS router OpenVPN is **fully operational** for the accepted production remote-administration use case.
- `cloud-01` has a proven VM-level backup; application-consistent recovery remains unproven.
- current backup schedules are `100,102,104,105,200,201,204` on `PROXMOX` and `101,103,202,203` on `Proxmox-2`.
- unattended CT105 and VM203 evidence has been observed; do not list VM203 as awaiting first unattended proof.
- `docker-01` remains deliberately focused on BirdNET-Go.
- CrowdSec, Authelia and Nginx Proxy Manager are not currently deployed.

## Current coverage gaps

These are genuine remaining recovery/operations gaps, not completed migrations:

| Gap | Priority | Needed work |
|---|---|---|
| `backup_unattended_evidence` | Medium | Record explicit remaining CT104/VM204 unattended evidence if still required by current evidence set |
| `backup_secondary_copy` | High | Independent second physical/failure-domain copy |
| `application_backup_recovery` | High | Representative QEMU restore and application-consistent Nextcloud/PostgreSQL recovery |
| `proxmox_cluster_resilience` | High | Prove link0->link1 fallback and controlled one-node quorum behaviour |
| `proxmox_node_health` | Medium | Dedicated node/service recovery guidance |
| `proxmox_storage_health` | Medium | SMART/disk/Proxmox storage recovery guidance |
| `edge_cloudflare_tunnel` | Deferred | Deploy only when a real approved service needs it |
| `mail_relay_recovery_testing` | Medium | Full rebuild/credential restoration proof |
| `komodo_hardening` | Medium | HTTPS and low-risk update/rollback ownership proof |
| `runbook_coverage` | Medium | Add dedicated operational service runbooks for Komodo/Zabbix if their existing architecture/IaC docs are not sufficient |

The old `remote_access_vpn_completion` gap is closed for service acceptance. DDNS/router rebuild/client re-enrolment remain maintenance/recovery tasks.

## Validation-date rule

Do not advance a `last_validated` date merely because documentation was edited. Only record a new validation date when the documented live path has actually been proven.

## Change rules

When changing an operational service:

1. update the authoritative service/recovery document;
2. update `runbooks/registry.yml` in the same change where the registry entry is affected;
3. keep host/IP data aligned with `IaC/inventory/estate.json` and Ansible inventory;
4. record validation dates only after proof;
5. mark obsolete procedures deprecated/retired or clearly historical;
6. never add retired identities to active applicability lists.
