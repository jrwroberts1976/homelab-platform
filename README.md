# Homelab Platform

Private Infrastructure-as-Code, operational documentation and migration workspace for the JRW Roberts homelab.

## Status

This repository is currently **private** while the platform, recovery model and documentation are being consolidated.

The estate has moved beyond the original “future authority” phase. `IaC/` is authoritative for infrastructure and service configuration that has been explicitly migrated and validated here. Legacy repositories may still remain useful reference sources for areas that have **not** yet been reconciled; they are retired only after unique content and recovery dependencies are reviewed.

For the current estate, start with:

- [Current-State Architecture](docs/architecture/CURRENT-STATE.md)
- [Target-State Architecture](docs/architecture/TARGET-STATE.md)
- [Proxmox Cluster Implementation Record](docs/architecture/PROXMOX-CLUSTER-REBUILD-PLAN.md)
- [Backup Strategy](docs/architecture/BACKUP-STRATEGY.md)
- [Migration Tracker](docs/migrations/MIGRATION-TRACKER.md)
- [Runbook Catalogue](runbooks/README.md)
- [14 September 2026 Estate Audit](docs/architecture/ESTATE-AUDIT-2026-09-14.md)

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

`admin-01` is also the external Corosync QNetd host for the Proxmox cluster.

The retired `TestServer` identity must not be used as the current controller. Its Raspberry Pi 4 hardware is now `docker-01` at `192.168.2.220`.

## Current core estate

| Host / service | Address | Current role |
|---|---:|---|
| `admin-01` | `192.168.2.48` | Administration / SSH jump / IaC controller / QNetd |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT100 on `PROXMOX` |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT101 on `Proxmox-2` |
| `monitor-01` | `192.168.2.52` | Prometheus/Grafana/Alertmanager/Blackbox/Loki, VM202 on `Proxmox-2` |
| `cloud-01` | `192.168.2.53` | Production Nextcloud/PostgreSQL/Redis, VM200 on `PROXMOX` |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix SMTP relay, CT102 on `PROXMOX` |
| `sensor-01` | `192.168.2.55` | Active Suricata/Zeek passive sensor, VM201 on `PROXMOX` |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT103 on `Proxmox-2`; Cloudflare Tunnel not deployed |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` cluster node 1 |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` cluster node 2 / Network Host Collector |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint / Proxmox NFS backup target |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host |

Retired identities include `TestServer`, `DietPi`, `ids-01`, the former `k3s-node-01` identity and the old `.242` DNS resolver.

## Proxmox cluster

The live Proxmox platform is the two-node cluster:

```text
jameshouse-pve

PROXMOX
  management: 192.168.2.70
  Corosync link0: 10.255.255.1/30
  node ID: 1

Proxmox-2
  management: 192.168.2.71
  Corosync link0: 10.255.255.2/30
  node ID: 2
```

Corosync uses:

- direct point-to-point USB Ethernet `link0`, priority 20;
- normal LAN `link1`, priority 5, as fallback;
- `admin-01` as QDevice/QNetd third vote on TCP/5403.

Validated quorum is three expected/total votes with quorum two and `Quorate Qdevice`.

Current workload placement:

```text
PROXMOX
  CT100 dns-02
  CT102 mail-relay-01
  VM200 cloud-01
  VM201 sensor-01
  VM9000 / VM9001 templates

Proxmox-2
  CT101 dns-01
  CT103 edge-01
  VM202 monitor-01
```

The actual node hostname is still `PROXMOX`; “Proxmox-1” is only a human-friendly diagram label.

Production guest disks remain on node-local `local-lvm`, so cluster membership does not by itself provide automatic guest HA after loss of a node-local disk owner.

## Current platform position

### Monitoring and logging

`monitor-01` provides the central observability platform:

- Prometheus;
- Grafana;
- Alertmanager;
- Blackbox Exporter;
- Loki;
- native Grafana Alloy;
- ASUS router syslog ingestion and retention.

Alloy is deployed across the managed estate. Network Hosts discovery/enrichment/deep profiling and HP ProCurve telemetry are operational.

### Cloud

`cloud-01` is a live production Nextcloud service using PostgreSQL, Redis and a dedicated ext4 data disk.

VM-level snapshot backup proof exists. Application-consistent Nextcloud/PostgreSQL recovery remains a separate outstanding proof.

### Network sensor

`sensor-01` is an active passive-sensor platform. Suricata and Zeek are operational and consume traffic from the dedicated capture path fed by the HP ProCurve mirror configuration.

The switch currently mirrors ports 1–23 to port 24.

### Edge

`edge-01` exists as a healthy LXC at `.56`, but no `cloudflared` package/service/process is deployed. Cloudflare Tunnel implementation remains future work until there is a real service requirement.

### Backup / recovery

`media-01` is the primary Proxmox guest-backup target using NFS v4.2/TCP.

Current cluster storage uses node-scoped namespaces:

```text
PROXMOX   -> media-backup-proxmox   -> /srv/backup/pve-proxmox
Proxmox-2 -> media-backup-proxmox-2 -> /srv/backup/pve-proxmox-2
```

Pre-cluster backup/restore evidence is strong, including all seven production guests and an isolated CT103 restore/boot proof.

Cluster formation changed `monitor-01` from standalone VMID 200 to cluster VMID 202. The immediate backup follow-up is therefore to reconcile the live schedule/IaC to final placement, take fresh cluster-era backups and observe an unattended successful post-cluster cycle.

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
- Cluster membership, quorum and guest-data HA are separate concerns and must not be conflated.

## Delivery backlog

The current high-value work is now:

| Workstream | Current position | Next milestone |
|---|---|---|
| Proxmox cluster | Two-node cluster + dual Corosync links + QDevice operational | Prove link fallback and controlled single-node maintenance behaviour |
| Cluster backup reconciliation | Node-scoped NFS storage retained; VM202 is new cluster identity | Update job/IaC guest set to `101,103,202`, take fresh backups, observe unattended run |
| Recovery depth | LXC restore proof exists; VM/application proof incomplete | QEMU restore + application-consistent `cloud-01` recovery |
| Second-copy resilience | Primary NFS backup target operational | Add independent second copy for important data |
| Core monitoring | Prometheus/Grafana/Alertmanager/Blackbox/Loki operational | Add cluster/QDevice/link health and useful service telemetry |
| Network Hosts platform | Discovery/enrichment/deep profiling/notifications/dashboards operational | Correlate with switch topology and keep data actionable |
| Web Platform / Analytics | Cloudflare + Umami + Grafana design direction defined | Build unified dashboard |
| Network hardening | SPAN and telemetry operational | Refresh physical port map; restrict legacy SNMP/Telnet exposure |
| Komodo / container operations | Preferred direction agreed | Prove workflow and retire superseded update paths |
| Edge / Cloudflare Tunnel | `edge-01` host provisioned; cloudflared absent | Deploy only when approved/needed |
| Password manager | Future work | Final security/backup review and host decision |
| Home automation | Future project | Host/platform and device-integration design |
| FreeSWITCH / SIP | Future project | Select host/supplier and define security/network design |

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
- [Proxmox Backup Recovery](production%20docs/PROXMOX-BACKUP-RECOVERY.md)
- [Cloudflare Pages Production Pipeline](production%20docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md)

## Documentation rule

Current-state, target-state and historical evidence must remain distinct:

- current operational truth -> `CURRENT-STATE.md` / service docs / runbook registry;
- future design -> `TARGET-STATE.md` and explicitly planned runbooks;
- dated migration/audit evidence -> retained as historical records, with superseded banners where ambiguity would otherwise be dangerous.
