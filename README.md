# Homelab Platform

Private Infrastructure-as-Code, operational documentation and migration workspace for the JRW Roberts homelab.

## Status

This repository is currently **private** while the platform, recovery model and documentation are being consolidated.

The estate has moved beyond the original “future authority” phase. `IaC/` is now authoritative for infrastructure and service configuration that has been explicitly migrated and validated here. Legacy repositories may still remain authoritative or useful reference sources for areas that have **not** yet been reconciled; they are retired only after unique content and recovery dependencies are reviewed.

For the current estate, start with:

- [Current-State Architecture](docs/architecture/CURRENT-STATE.md)
- [Target-State Architecture](docs/architecture/TARGET-STATE.md)
- [Migration Tracker](docs/migrations/MIGRATION-TRACKER.md)
- [Runbook Catalogue](runbooks/README.md)
- [12 September 2026 Documentation Review](docs/DOCUMENTATION-REVIEW-2026-09-12.md)

## IaC authority

All new Infrastructure-as-Code belongs under [`IaC/`](IaC/).

Terraform provisions supported infrastructure and Ansible reconciles operating systems/services. Existing production state is discovered and validated before it is changed.

The older top-level `terraform/` path predates this convention and remains a legacy area until its references and state handling are deliberately reconciled.

## Current control point

Normal homelab administration and production Ansible execution use:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired `TestServer` identity must not be used as the current controller. Its Raspberry Pi 4 hardware is now `docker-01` at `192.168.2.220`.

## Current core estate

| Host / service | Address | Current role |
|---|---:|---|
| `admin-01` | `192.168.2.48` | Administration / SSH jump / IaC controller |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT100 on `PROXMOX` |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT101 on `Proxmox-2` |
| `monitor-01` | `192.168.2.52` | Prometheus/Grafana/Alertmanager/Blackbox |
| `cloud-01` | `192.168.2.53` | Production Nextcloud/PostgreSQL/Redis |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix SMTP relay |
| `sensor-01` | `192.168.2.55` | Suricata/Zeek platform; Phase 1 complete |
| `edge-01` | `192.168.2.56` | Reserved edge LXC; Cloudflare Tunnel not deployed |
| `PROXMOX` | `192.168.2.70` | Primary standalone Proxmox VE node |
| `Proxmox-2` | `192.168.2.71` | Secondary standalone Proxmox VE node |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host |

Retired identities include `TestServer`, `DietPi`, `ids-01`, the former `k3s-node-01` identity and the old `.242` DNS resolver.

## Current platform position

### Monitoring

The core metrics platform on `monitor-01` is operational.

Latest validated state:

```text
Prometheus active targets: 25
Healthy targets:           25
Active alerts:             0
```

Prometheus, Grafana, Alertmanager and Blackbox Exporter are live. `mail-relay-01` now has both ICMP and Node Exporter coverage. Loki and Alloy are **not deployed on `monitor-01`**; central logging remains future work.

### Cloud

`cloud-01` is a live production Nextcloud service using a dedicated 200 GiB VM data disk at `/srv/cloud-01-data`.

The former 4 TB WD USB disk is not the cloud production data disk.

Backup and restore proof remain outstanding.

### Network sensor

`sensor-01` Phase 1 is complete: VM, toolchain, management network and Node Exporter are live. Suricata and Zeek remain deliberately stopped until the dedicated USB capture NIC, switch repatching and SPAN path are ready.

HP ProCurve port 24 is a **future** SPAN destination. It currently carries the primary ASUS router link and switch mirroring is disabled.

### Edge

`edge-01` exists as a healthy LXC at `.56`, but no `cloudflared` package/service/process is deployed. Cloudflare Tunnel implementation is future work.

### Backup / recovery

The current estate does **not** yet have an active production backup platform:

- no PBS server;
- zero scheduled Proxmox guest backup jobs on either node;
- no active estate-wide Restic/Backrest platform found in the latest audit;
- restore testing not proven.

Backup/recovery is therefore a top-priority platform gap rather than a completed migration.

## Principles

- Git is the desired-state authority for migrated areas.
- Infrastructure changes are reviewed before deployment.
- Host/workload ownership is explicit.
- Secrets and Terraform state are never stored in plaintext Git.
- Existing production state is discovered before it is changed.
- Reconciliation should be idempotent.
- Migration remains workload-by-workload with rollback/recovery paths.
- Historical evidence is preserved rather than rewritten to look current.
- Legacy repositories are retired only after useful content and recovery dependencies are understood.
- A healthy service is not considered fully recovery-ready until important data has a proven restore path.

## Delivery backlog

Percentages are planning estimates, not health scores. “Operational” means the current service is live; it does not imply backup/recovery or every planned observability layer is complete.

| Workstream | Current position | Next milestone | Planning completion |
|---|---|---|---:|
| `docker-01` / BirdNET-Go | Dedicated host operational; Docker/BirdNET-Go and Node Exporter healthy | Protect persistent BirdNET state and prove recovery | 100% host/service build |
| `cloud-01` baseline | VM/storage/OS baseline operational | Maintain IaC/idempotence and integrate recovery | 100% |
| Nextcloud private cloud | Nextcloud/PostgreSQL/Redis/cron operational on 200 GiB data disk | Backup + representative restore + broader observability | 80% |
| Core monitoring | Prometheus/Grafana/Alertmanager/Blackbox operational, 25/25 targets up | Add useful service telemetry; logging remains separate | 70% |
| Central logging | Router syslog local receiver works; no central Loki/Alloy on monitor-01 | Design/deploy Alloy + Loki if still required | 20% |
| Network Hosts platform | Enriched collector/dashboard design defined | Build collector and dashboard | 20% |
| Web Platform / Analytics | Cloudflare + Umami + Grafana design direction defined | Build unified dashboard | 20% |
| Backup / recovery redesign | Current no-backup risk documented; target principles defined | Select storage/PBS placement, deploy jobs, test restores | 20% design / implementation pending |
| Network sensor Phase 2 | Phase 1 complete; capture NIC not yet available | USB NIC + repatch + SPAN + packet proof | 50% overall sensor programme |
| Edge / Cloudflare Tunnel | `edge-01` host provisioned; cloudflared absent | Design/deploy connector if approved | 25% host-only |
| Runbook catalogue | Core operational services indexed and current-state reconciliation completed | Add Proxmox/backup recovery procedures and test runbooks | 70% |
| Komodo / container operations | Preferred direction agreed | Prove workflow and retire superseded update paths | 40% |
| Password manager | Preferred product direction remains future work | Final security/backup review and host decision | 5% |
| Home automation | Future project | Host/platform and device-integration design | 0% |
| FreeSWITCH / SIP | PBX direction identified; SIP supplier TBD | Select host/supplier and define security/network design | 0% |

## Production runbooks

The authoritative index is [runbooks/README.md](runbooks/README.md) / [runbooks/registry.yml](runbooks/registry.yml).

Current service/recovery documents include:

- [DNS Service Recovery Plan](production%20docs/DNS-SERVICE-RECOVERY-PLAN.md)
- [Monitoring Service](production%20docs/MONITORING-SERVICE.md)
- [Cloud Data Service](production%20docs/CLOUD-SERVICE.md)
- [Network Sensor Service](production%20docs/NETWORK-SENSOR-SERVICE.md)
- [Mail Relay Service](production%20docs/MAIL-RELAY-SERVICE.md)
- [BirdNET-Go Service](production%20docs/BIRDNET-SERVICE.md)
- [media-01 Service](production%20docs/MEDIA-SERVICE.md)
- [Router Syslog Service](production%20docs/ROUTER-SYSLOG-SERVICE.md)
- [Time Service](production%20docs/TIME-SERVICE.md)
- [Cloudflare Pages Production Pipeline](production%20docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md)

## Documentation rule

Current-state, target-state and historical evidence must remain distinct:

- current operational truth -> `CURRENT-STATE.md` / service docs / runbook registry;
- future design -> `TARGET-STATE.md` and explicitly planned runbooks;
- dated migration/audit evidence -> retained as historical records, with superseded banners where ambiguity would otherwise be dangerous.
