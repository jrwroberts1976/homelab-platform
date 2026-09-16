# Homelab Platform

Private Infrastructure-as-Code, operational documentation and migration workspace for the JRW Roberts homelab.

## Current status

The platform is now operating from the Git-managed `homelab-platform` model rather than the former consolidated/legacy layout. `IaC/` is the authority for infrastructure and service configuration that has been explicitly migrated and validated here.

The main current-state references are:

- [Current-State Architecture](docs/architecture/CURRENT-STATE.md)
- [Target-State Architecture](docs/architecture/TARGET-STATE.md)
- [VPN Remote-Access Design and Project Plan](docs/network/VPN-REMOTE-ACCESS-DESIGN.md)
- [Proxmox Cluster Implementation Record](docs/architecture/PROXMOX-CLUSTER-REBUILD-PLAN.md)
- [Backup Strategy](docs/architecture/BACKUP-STRATEGY.md)
- [Migration Tracker](docs/migrations/MIGRATION-TRACKER.md)
- [Runbook Catalogue](runbooks/README.md)
- [14 September 2026 Estate Audit](docs/architecture/ESTATE-AUDIT-2026-09-14.md)

Machine identity/address truth is recorded in `IaC/inventory/estate.json` and must be checked before allocating a new hostname, LAN address or VMID.

## Control plane

Normal administration and production Ansible execution use:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

`admin-01` is also the external Corosync QNetd host for the Proxmox cluster.

The retired `TestServer` identity must not be used as the current controller. Its Raspberry Pi 4 hardware is now `docker-01` at `192.168.2.220`.

## Core estate

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
| `greenbone-01` | `192.168.2.57` | Greenbone Community vulnerability scanner, VM203 on `Proxmox-2` |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` cluster node 1 |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` cluster node 2 / Network Host Collector |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint / Proxmox NFS backup target |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host |

Retired identities include `TestServer`, `DietPi`, `ids-01`, the former `k3s-node-01` identity and the old `.242` DNS resolver.

## Proxmox cluster

The live Proxmox platform is the two-node `jameshouse-pve` cluster:

```text
PROXMOX
  management: 192.168.2.70
  Corosync link0: 10.255.255.1/30
  node ID: 1

Proxmox-2
  management: 192.168.2.71
  Corosync link0: 10.255.255.2/30
  node ID: 2
```

Corosync uses the direct point-to-point USB Ethernet path as preferred `link0`, the management LAN as `link1` fallback, and `admin-01` as the QDevice/QNetd third vote.

Validated quorum is:

```text
Nodes:          2
Expected votes: 3
Total votes:    3
Quorum:         2
Flags:          Quorate Qdevice
```

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
  VM203 greenbone-01
```

The actual node hostname remains `PROXMOX`; “Proxmox-1” is only a human-friendly diagram label.

Production guest disks remain on node-local storage, so cluster membership and quorum do not by themselves provide automatic guest-data HA after loss of a node-local disk owner.

## Backup and recovery

`media-01` is the primary Proxmox guest-backup target using NFS v4.2/TCP.

```text
PROXMOX
  job: homelab-nightly-proxmox
  time: 02:15
  storage: media-backup-proxmox
  guests: 100,102,200,201

Proxmox-2
  job: homelab-nightly-proxmox-2
  time: 03:15
  storage: media-backup-proxmox-2
  guests: 101,103,202,203

mode: snapshot
compression: zstd
retention: keep-last=3
notification-mode: notification-system
```

The cluster-era `Proxmox-2` schedule is reconciled through IaC and an immediate repeat run returned `changed=0`. The unattended 16 September cycle succeeded for CT101, CT103 and VM202. VM203 has two manual snapshot archives with successful Zstandard integrity proof and is now included in the nightly schedule.

The remaining immediate schedule proof is the first unattended 03:15 cycle that includes VM203. Pre-cluster restore evidence includes an isolated CT103 restore/boot proof; a representative QEMU restore and application-consistent `cloud-01` recovery remain separate recovery goals.

## Platform services

### Monitoring and logging

`monitor-01` provides Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki. Native Grafana Alloy is deployed across the managed estate. Router syslog, Network Hosts discovery/enrichment/deep profiling, first-seen notification and HP ProCurve telemetry are operational.

### Cloud

`cloud-01` is a live production Nextcloud service using PostgreSQL, Redis and a dedicated ext4 data disk. VM-level snapshot backup is proven; application-consistent Nextcloud/PostgreSQL recovery remains outstanding.

### Network sensor

`sensor-01` is an active passive-sensor platform. Suricata and Zeek consume mirrored traffic from the HP ProCurve SPAN path, with ports 1–23 mirrored to port 24.

### Vulnerability scanning

`greenbone-01` is the active LAN-only vulnerability scanner. Greenbone Community Containers are deployed on VM203, feed readiness reached 4/4, the commissioning self-scan completed with no Critical/High/Medium findings, VM backup integrity is proven and Proxmox protection is enabled.

### Edge

`edge-01` is a healthy LXC at `.56`, but `cloudflared` is not deployed. Tunnel implementation remains future work until there is a real service requirement.

## Delivery priorities

| Workstream | Current position | Next milestone |
|---|---|---|
| Proxmox cluster | Two-node cluster, dual Corosync links and QDevice operational | Prove link0 -> link1 fallback and controlled single-node quorum behaviour |
| Backup schedule | Cluster-era jobs reconciled; VM203 manual backup/integrity proven and scheduled | Observe first unattended run including VM203 |
| Recovery depth | LXC restore proof exists | QEMU restore proof + application-consistent `cloud-01` recovery |
| Second-copy resilience | Primary NFS backup target operational | Add an independent second copy for important data |
| Core monitoring | Prometheus/Grafana/Alertmanager/Blackbox/Loki operational | Add useful cluster/QDevice/link health telemetry |
| Network Hosts | Discovery/enrichment/deep profiling/notifications/dashboards operational | Continue switch/topology correlation and operational tuning |
| Vulnerability management | `greenbone-01` commissioned and protected | Observe scheduled backup, tune hardening/update policy as needed |
| Remote-access VPN | Dedicated WireGuard VM design retained; address and VMID deliberately unallocated | Allocate collision-free identity during deployment preflight, then build/test |
| Web Platform / Analytics | Cloudflare + Umami + Grafana design direction defined | Build unified dashboard |
| Network hardening | SPAN and telemetry operational | Refresh physical port map and restrict legacy SNMP/Telnet exposure |
| Komodo / container operations | Preferred direction agreed | Prove workflow and retire superseded update paths |
| Edge / Cloudflare Tunnel | Host provisioned, tunnel absent | Deploy only when approved/needed |

## Operating principles

- Git is the desired-state authority for migrated areas.
- `IaC/inventory/estate.json` is the canonical machine-readable identity/address source.
- Existing production state is discovered before it is changed.
- Infrastructure changes are reviewed and validated incrementally.
- Reconciliation should be idempotent.
- Secrets and Terraform state are never stored in plaintext Git.
- Historical evidence is preserved but clearly separated from current operational truth.
- Cluster membership, quorum, workload placement and guest-data HA are separate concerns.
- A healthy service is not considered recovery-ready until important data has a proven restore path.

## Production runbooks

The authoritative index is [runbooks/README.md](runbooks/README.md) and [runbooks/registry.yml](runbooks/registry.yml).

Key service and recovery documents include:

- [DNS Service Recovery Plan](production%20docs/DNS-SERVICE-RECOVERY-PLAN.md)
- [Monitoring Service](production%20docs/MONITORING-SERVICE.md)
- [Cloud Data Service](production%20docs/CLOUD-SERVICE.md)
- [Network Sensor Service](production%20docs/NETWORK-SENSOR-SERVICE.md)
- [Greenbone Vulnerability Scanner Service](production%20docs/GREENBONE-SERVICE.md)
- [Mail Relay Service](production%20docs/MAIL-RELAY-SERVICE.md)
- [BirdNET-Go Service](production%20docs/BIRDNET-SERVICE.md)
- [media-01 Service](production%20docs/MEDIA-SERVICE.md)
- [Router Syslog Service](production%20docs/ROUTER-SYSLOG-SERVICE.md)
- [Time Service](production%20docs/TIME-SERVICE.md)
- [Proxmox Backup Recovery](production%20docs/PROXMOX-BACKUP-RECOVERY.md)
- [Cloudflare Pages Production Pipeline](production%20docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md)

## Documentation rule

Current state, future design and historical evidence remain distinct:

- current operational truth -> `IaC/inventory/estate.json`, `CURRENT-STATE.md`, service docs and runbook registry;
- future design -> `TARGET-STATE.md` and explicitly planned runbooks;
- dated migration/audit evidence -> retained as historical records, with superseded context where necessary.
