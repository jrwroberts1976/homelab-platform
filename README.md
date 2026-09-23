# Homelab Platform

Private Infrastructure-as-Code, operational documentation and migration workspace for the JRW Roberts homelab.

## Current status

The platform is now operating from the Git-managed `homelab-platform` model rather than the former consolidated/legacy layout. `IaC/` is the authority for infrastructure and service configuration that has been explicitly migrated and validated here.

The main current-state references are:

- [Homelab Building Blocks](docs/architecture/BUILDING-BLOCKS.md)
- [Current-State Architecture](docs/architecture/CURRENT-STATE.md)
- [Target-State Architecture](docs/architecture/TARGET-STATE.md)
- [Home Automation / Home Assistant Design](docs/architecture/HOME-AUTOMATION-DESIGN.md)
- [VPN Remote-Access Design and Implementation Record](docs/network/VPN-REMOTE-ACCESS-DESIGN.md)
- [Network Terms & Reference](docs/network/TERMS-AND-REFERENCE.md)
- [Installed Solutions Catalogue](docs/architecture/INSTALLED-SOLUTIONS-CATALOGUE.md)
- [Proxmox Cluster Implementation Record](docs/architecture/PROXMOX-CLUSTER-REBUILD-PLAN.md)
- [Backup Strategy](docs/architecture/BACKUP-STRATEGY.md)
- [Migration Tracker](docs/migrations/MIGRATION-TRACKER.md)
- [Runbook Catalogue](runbooks/README.md)
- [14 September 2026 Estate Audit](docs/architecture/ESTATE-AUDIT-2026-09-14.md)
- [16 September 2026 Documentation Audit](docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-09-16.md)
- [17 September 2026 Application Audit](docs/architecture/ESTATE-APPLICATION-AUDIT-2026-09-17.md)

Machine identity/address truth is recorded in `IaC/inventory/estate.json` and must be checked before allocating a new hostname, LAN address or VMID.

## Control plane

Normal administration and production Ansible execution use:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

`admin-01` is also the external Corosync QNetd host for the Proxmox cluster.

The retired controller identity must not be used as the current controller; the Raspberry Pi 4 hardware is now `docker-01` at `192.168.2.220`.

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
| `komodo-01` | `192.168.2.58` | Komodo container-management control plane, CT104 on `PROXMOX` |
| `zabbix-01` | `192.168.2.59` | Zabbix monitoring platform, CT105 on `PROXMOX` |
| `home-01` | `192.168.2.60` | Home Assistant OS 18.2, VM204 on `PROXMOX` |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` cluster node 1 |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` cluster node 2 / Network Host Collector |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint / Proxmox NFS backup target |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host |
| ASUS RT-AC86U | `192.168.2.1` | Router / DHCP / AiMesh controller / OpenVPN remote-access endpoint |

Retired identities remain recorded in `IaC/inventory/estate.json`; they are historical evidence only and must not be reused as current deployment targets.

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
  CT104 komodo-01
  CT105 zabbix-01
  VM200 cloud-01
  VM201 sensor-01
  VM204 home-01
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
  guests: 100,102,104,105,200,201,204

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

Both job definitions are reconciled through IaC. CT104, CT105 and VM203 have manual snapshot/integrity proof. The 17 September audit observed an unattended CT105 backup from the `PROXMOX` job and unattended CT101/CT103/VM202/VM203 backups from the `Proxmox-2` job. The displayed audit sample did not include CT104, so first unattended CT104 proof remains open.

VM204 (`home-01`) has a native Home Assistant backup plus a manual Proxmox snapshot archive with compressed/VMA integrity proof and is included in the 02:15 schedule. Its first unattended scheduled backup remains to be observed.

Pre-cluster restore evidence includes an isolated CT103 restore/boot proof. A representative QEMU restore and application-consistent `cloud-01` recovery remain separate recovery goals.

## Platform services

### Monitoring and logging

`monitor-01` provides Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki. Native Grafana Alloy is deployed across the managed estate. Router syslog, Network Hosts discovery/enrichment/deep profiling, first-seen notification and HP ProCurve telemetry are operational.

The ASUS router stream is received on UDP/5514, retained in `/var/log/homelab/router/rt-ac86u.log` and shipped to Loki by the dedicated Alloy router-syslog pipeline. OpenVPN connection/authentication events are present in that stream.

### Zabbix

`zabbix-01` is the dedicated Zabbix 7.0 monitoring platform. The managed Linux estate contains 15 Zabbix Agent 2 targets. Matching host objects are grouped under `Homelab/Linux`, use `Linux by Zabbix agent active`, and all 15 were observed reporting on 16 September 2026. An unattended CT105 Proxmox backup was observed on 17 September.

### Komodo

`komodo-01` is the commissioned Komodo control plane. Docker, MongoDB and Komodo Core are operational, application backup/isolated restore are proven, and Komodo is the preferred path for routine Docker application/version management as managed-host onboarding proceeds. Periphery onboarding and HTTPS hardening remain later work.

### Home automation

`home-01` is the commissioned Home Assistant platform. HAOS 18.2 runs as VM204 on `PROXMOX`; Home Assistant Core 2026.9.2 and Supervisor 2026.09.2 were healthy during the 17 September audit. The application is reachable on HTTP port 80 at `192.168.2.60` and `home-01`, both DNS resolvers return the correct record, native and manual VM backup evidence exists, and Proxmox protection is enabled. External monitoring, the first unattended VM204 backup and deeper restore proof remain follow-up items.

### Remote access

The selected remote-access implementation is the native OpenVPN server on the ASUS RT-AC86U rather than a separate VPN VM.

**VPN status: FULLY OPERATIONAL — accepted 18 September 2026.** The ASUS RT-AC86U OpenVPN service is the production remote-access path. A Windows laptop was validated from an external network with a `10.8.0.x` tunnel address, homelab LAN access and normal split-tunnel Internet access. DDNS and router/client recovery checks are retained as maintenance/recovery documentation rather than blockers to operational acceptance.

### Cloud

`cloud-01` is a live production Nextcloud service using PostgreSQL, Redis and a dedicated ext4 data disk. VM-level snapshot backup is proven; application-consistent Nextcloud/PostgreSQL recovery remains outstanding. The 17 September audit also recorded a live/IaC Redis configuration-path difference for later reconciliation; the running service is healthy.

### Network sensor

`sensor-01` is an active passive-sensor platform. Suricata and Zeek consume mirrored traffic from the HP ProCurve SPAN path, with ports 1–23 mirrored to port 24.

### Vulnerability scanning

`greenbone-01` is the active LAN-only vulnerability scanner. Greenbone Community Containers are deployed on VM203, feed readiness reached 4/4, the commissioning self-scan completed with no Critical/High/Medium findings, VM backup integrity is proven and Proxmox protection is enabled.

### Edge

`edge-01` is a healthy LXC at `.56`, but `cloudflared` is not deployed. Tunnel implementation remains future work until there is a real service requirement.

## Planned service expansion

One optional application workstream remains explicitly planned:

- **Password manager** — product not selected. The design must cover protected recovery material, HTTPS, MFA/passkey capability where supported, backup/restore proof and an emergency-access path that does not depend solely on the running homelab.

Home Assistant is no longer a planned reservation: `home-01` is active and commissioned. See [Home Automation / Home Assistant Design](docs/architecture/HOME-AUTOMATION-DESIGN.md) for current implementation and remaining closeout items.

## Delivery priorities

| Workstream | Current position | Next milestone |
|---|---|---|
| Home automation | `home-01` active on `.60` as VM204; HAOS/Core/Supervisor healthy; native + manual VM backup evidence; protection enabled | Add external monitoring, observe first unattended VM204 backup, then decide radio/device integration |
| Proxmox cluster | Two-node cluster, dual Corosync links and QDevice operational | Prove link0 -> link1 fallback and controlled single-node quorum behaviour |
| Backup schedule | Both IaC jobs include current production guests; unattended CT105 and VM203 evidence observed; VM204 scheduled with manual proof | Observe unattended CT104 and VM204 runs |
| Recovery depth | LXC restore proof exists | QEMU restore proof + application-consistent `cloud-01` recovery |
| Second-copy resilience | Primary NFS backup target operational | Add an independent second copy for important data |
| Zabbix | Server + 15 active-agent hosts reporting | Tune actionable templates/alerts and add service-specific coverage |
| Core monitoring | Prometheus/Grafana/Alertmanager/Blackbox/Loki operational | Add useful cluster/QDevice/link health telemetry and `home-01` external availability checks |
| Komodo / container operations | Komodo Core commissioned; application backup/restore proven | Onboard managed Docker hosts, prove update/rollback ownership, then retire superseded paths |
| Network Hosts | Discovery/enrichment/deep profiling/notifications/dashboards operational | Continue switch/topology correlation and operational tuning |
| Vulnerability management | `greenbone-01` commissioned and protected | Tune hardening/update policy as needed |
| Remote-access VPN | **FULLY OPERATIONAL** — router-hosted OpenVPN accepted 18 September 2026 for external laptop administration with split tunnelling | Maintain DDNS/router recovery/client re-enrolment documentation; no operational acceptance work remains |
| Password manager | Planned; product and placement unallocated | Compare/select product and produce deployment/recovery design |
| Web Platform / Analytics | Cloudflare + Umami + Grafana design direction defined | Build unified dashboard |
| Network hardening | SPAN and telemetry operational | Refresh physical port map and restrict legacy SNMP/Telnet exposure |
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
