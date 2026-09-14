# Current-State Architecture

This document records the validated current homelab estate as of 14 September 2026.

It describes what is live now. Historical host identities and earlier migration assumptions remain useful evidence, but they are not current deployment authority.

## Authority model

`homelab-platform/IaC/` is the authoritative location for infrastructure and service configuration that has been migrated and validated there.

Legacy repositories may remain useful reference sources for areas not yet migrated. They must not be treated as current authority after their workload or configuration has been explicitly migrated and validated in `homelab-platform`.

A detailed reconciliation trail for the 14 September estate snapshot is recorded in `docs/architecture/ESTATE-AUDIT-2026-09-14.md`.

## Active estate

| Asset | Address | Current role | State |
|---|---:|---|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / SSH jump / IaC controller | ACTIVE |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT 100 on `PROXMOX` | ACTIVE |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT 101 on `Proxmox-2` | ACTIVE |
| `monitor-01` | `192.168.2.52` | Prometheus, Grafana, Alertmanager, Blackbox, Loki and router-log ingestion, VM 200 on `Proxmox-2` | ACTIVE |
| `cloud-01` | `192.168.2.53` | Production Nextcloud/PostgreSQL/Redis, VM 200 on `PROXMOX` | ACTIVE |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix SMTP relay, CT 102 on `PROXMOX` | ACTIVE |
| `sensor-01` | `192.168.2.55` | Active Suricata/Zeek passive network sensor, VM 201 on `PROXMOX` | ACTIVE — CAPTURE OPERATIONAL |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT 103 on `Proxmox-2` | HOST ACTIVE — CLOUDFLARED NOT DEPLOYED |
| `PROXMOX` | `192.168.2.70` | Primary standalone Proxmox VE node | ACTIVE |
| `Proxmox-2` | `192.168.2.71` | Secondary standalone Proxmox VE node and network-host collector | ACTIVE |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target | ACTIVE |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host | ACTIVE |
| ASUS RT-AC86U | `192.168.2.1` | Router / DHCP / AiMesh controller | ACTIVE |
| ASUS AiMesh node | `192.168.2.181` | Wireless mesh node | ACTIVE |
| ASUS AiMesh node | `192.168.2.218` | Wireless mesh node | ACTIVE |
| HP ProCurve 2510G-24 | `192.168.2.16` | Core managed switch / SPAN source | ACTIVE |

## Retired identities

The following names must not be treated as active production hosts:

- `TestServer` — retired identity for the Raspberry Pi 4 now operating as `docker-01`.
- `DietPi` — retired identity for the Raspberry Pi 3 now operating as `admin-01`.
- `ids-01` — decommissioned.
- historical `k3s-node-01` identity associated with `192.168.2.195` — retired; the host is `media-01`.
- former `dns-02` at `192.168.2.242` — retired.

Historical hardware and audit documents remain useful evidence but are not live configuration authority.

## Proxmox platform

The two Proxmox nodes are currently standalone. No current production design depends on Corosync or shared cluster membership.

A future cluster rebuild is under consideration once dedicated Corosync networking and a quorum/QDevice design are available. Until such a design is approved and implemented, all documentation and backup policy must treat the hosts as standalone systems.

### `PROXMOX` — `192.168.2.70`

Validated 14 September 2026:

- Debian 13 base;
- Proxmox VE 9.2.11;
- running kernel `7.0.14-15-pve`;
- Chrony active;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units during the latest backup validation.

Live workload placement:

| Type | ID | Name | State |
|---|---:|---|---|
| LXC | 100 | `dns-02` | running |
| LXC | 102 | `mail-relay-01` | running |
| VM | 200 | `cloud-01` | running |
| VM | 201 | `sensor-01` | running |
| VM | 9000 | Debian cloud template | stopped |
| VM | 9001 | Debian cloud template with QGA | stopped |

An obsolete earlier Network Host Collector installation was found on this node during the 14 September audit, backed up and removed. The current collector belongs on `Proxmox-2` only.

### `Proxmox-2` — `192.168.2.71`

Validated 14 September 2026:

- Debian 13 base;
- Proxmox VE 9.2.2;
- running kernel `7.0.2-6-pve`;
- Chrony active;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units during the latest backup validation;
- active Network Host Collector with inventory under `/var/lib/homelab-network-hosts/inventory.json`.

Live guests:

| Type | ID | Name | State |
|---|---:|---|---|
| VM | 200 | `monitor-01` | running |
| LXC | 101 | `dns-01` | running |
| LXC | 103 | `edge-01` | running |

Both standalone nodes currently contain an unrelated VMID `200`. This is why their NFS backup namespaces are kept separate.

## DNS

Current resolver pair:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

Both workloads run Pi-hole Core 6.4.3, Pi-hole Web 6.6, Pi-hole FTL 6.7, Unbound 1.22.0, Node Exporter and Alloy 1.19.2.

Managed local-record parity remains authoritative through IaC. `192.168.2.48` is `admin-01` and must not be treated as a DNS resolver.

## Monitoring and logging

`monitor-01` is the central metrics, alerting and logging platform.

Validated running containers include:

| Service | Image/version | State |
|---|---|---|
| Prometheus | `prom/prometheus:v3.14.0` | running |
| Grafana | `grafana/grafana:13.2.1` | running |
| Alertmanager | `prom/alertmanager:v0.34.0` | running |
| Blackbox Exporter | `prom/blackbox-exporter:v0.28.0` | running |
| Loki | `grafana/loki:3.7.7` | running |

Native Alloy 1.19.2 is active on `monitor-01`. Router syslog continues to arrive through rsyslog on UDP/5514, is retained under `/var/log/homelab/router/rt-ac86u.log`, and is shipped to Loki through Alloy.

The broader Alloy baseline is deployed across the current managed estate.

## Production cloud service

`cloud-01` is a live production Nextcloud platform.

Validated state:

- Debian 13 VM on `PROXMOX`;
- dedicated 200 GiB ext4 data disk at `/srv/cloud-01-data`;
- Docker/Compose active;
- Nextcloud `34.0.3-apache` app and cron containers running;
- PostgreSQL `18.6-alpine` healthy;
- Redis `8.2.9-alpine` healthy;
- application endpoint `192.168.2.53:8080`;
- Node Exporter and Alloy active;
- zero failed systemd units.

A complete VM-level snapshot backup of VM200 is proven on the isolated `media-backup-proxmox` repository. Application-consistent Nextcloud/PostgreSQL recovery remains unproven and is still a separate requirement.

## Network sensor

`sensor-01` is an active passive network sensor.

Validated state includes:

- Debian 13 VM at `192.168.2.55`;
- management interface `eth0` up;
- dedicated capture interface `enx00249b63b38a` up in promiscuous mode;
- capture gate present;
- Suricata 8.0.6 active/enabled;
- Zeek 8.0.10 active;
- Node Exporter and Alloy active;
- zero failed systemd units.

The capture adapter remains dedicated to passive monitoring and must not be repurposed as a normal routed management or future Corosync interface.

## Network host discovery

The current Network Host Collector is deployed on `Proxmox-2` only.

Validated state includes the five-minute discovery collector, enrichment timer, one-time deep profiler for new hosts, current inventory under `/var/lib/homelab-network-hosts/inventory.json`, first-seen notification and Git-managed Grafana Network Hosts dashboards.

The obsolete collector installation on `PROXMOX` was removed.

## Edge host

`edge-01` is a running Debian 13 LXC, CT 103 on `Proxmox-2`, at `192.168.2.56`.

No `cloudflared` workload is deployed. Node Exporter and Alloy are active. The host remains reserved for a future Cloudflare Tunnel connector.

## Mail relay

`mail-relay-01` is CT 102 on `PROXMOX` at `192.168.2.54`.

Postfix is active/enabled and remains the approved internal SMTP relay to Gmail. The relay path was also proven for Proxmox notification delivery from both hypervisors.

Protected Gmail relay credentials remain outside Git.

## Media and primary backup target

`media-01` at `192.168.2.195` is the Raspberry Pi 5 Kodi endpoint and the primary Proxmox guest-backup target.

Validated state includes:

- Kodi 21.3 active/enabled;
- Samba active/enabled;
- NFS server active;
- NVMe-backed ext4 filesystem healthy with substantial free capacity during backup proof;
- Chrony active;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units.

Current backup exports:

```text
/srv/backup/pve-proxmox
  client: 192.168.2.70

/srv/backup/pve-proxmox-2
  client: 192.168.2.71

/srv/backup/pve
  legacy rollback namespace retained temporarily
```

The intended nftables policy remains a separate follow-up until deliberately deployed and remotely validated.

## Administration host

`admin-01` at `192.168.2.48` is the normal controller for homelab administration and IaC.

Current state includes Alloy 1.19.2, Node Exporter and zero failed systemd units after the inapplicable smartd daemon was disabled/stopped on the SD-card-based Raspberry Pi.

Production Ansible should normally be launched from the checked-out `homelab-platform` repository on this host.

## Docker / BirdNET host

`docker-01` at `192.168.2.220` remains the dedicated Raspberry Pi 4 BirdNET-Go host.

Validated state includes Debian 13/aarch64, Docker active, one intended BirdNET-Go application container, Node Exporter and Alloy active, and zero failed systemd units.

The former TestServer workload estate must not be silently reintroduced.

## Backup posture

The previous no-backup assessment is superseded.

The primary Proxmox guest-backup platform is operationally proven:

```text
backup host: media-01 .195
protocol: NFS v4.2/TCP
PROXMOX storage: media-backup-proxmox -> /srv/backup/pve-proxmox
Proxmox-2 storage: media-backup-proxmox-2 -> /srv/backup/pve-proxmox-2
legacy rollback storage: media-backup -> /srv/backup/pve
backup mode: snapshot
compression: zstd
retention: keep-last=3
local tmpdir: /var/lib/vz/vzdump-tmp
```

All seven production PVE guests have successful backup evidence in the isolated namespaces. CT103 has also completed an isolated restore/boot proof. Proxmox notification delivery through `mail-relay-01` is proven end to end.

The nightly backup jobs are now live and policy-validated:

```text
PROXMOX .70
  homelab-nightly-proxmox
  02:15
  media-backup-proxmox
  VMIDs 100,102,200,201

Proxmox-2 .71
  homelab-nightly-proxmox-2
  03:15
  media-backup-proxmox-2
  VMIDs 101,103,200
```

Both jobs are enabled, use snapshot mode, zstd, `keep-last=3` and `notification-system`. Re-running the IaC reconciliation on 14 September produced `changed=0` on both nodes and zero failed systemd units, proving the live schedule policy matches Git-managed desired state. The first unattended overnight execution remains to be observed.

Outstanding recovery gaps are now narrower:

- QEMU VM restore proof;
- application-consistent Nextcloud/PostgreSQL recovery;
- independent secondary copy;
- protection of `media-01` user media, BirdNET persistent state and controller recovery state.

The suspect WD 4 TB disk must not be the sole trusted backup copy.

See `docs/architecture/BACKUP-STRATEGY.md` and `production docs/PROXMOX-BACKUP-RECOVERY.md`.

## Network infrastructure

### HP ProCurve

Current known platform:

- HP ProCurve 2510G-24 / J9279A;
- firmware Y.11.52;
- management address `192.168.2.16`;
- VLAN 1 untagged on ports 1–24;
- management configured as `dhcp-bootp`;
- SNMP community `public` configured as `Unrestricted`;
- Telnet administration available;
- SSH unavailable;
- port 24 is the mirror destination;
- ports 1–23 are monitoring sources.

The older physical port map must not be treated as current after SPAN activation. Capture a new map rather than infer it.

### ASUS

The ASUS RT-AC86U remains gateway, DHCP authority and AiMesh controller. AiMesh nodes are at `.181` and `.218`.

Router syslog forwarding to `monitor-01 .52:5514/udp` remains operational and integrated into Alloy/Loki while retaining the local rsyslog file.

## Time service

The physical Proxmox hosts provide redundant LAN NTP:

```text
ntp-01.jameshouse -> 192.168.2.70
ntp-02.jameshouse -> 192.168.2.71
```

Chrony is active on both nodes.

## Patch state

The 14 September audit identified package-update backlog on several hosts. Those counts are a point-in-time audit observation, not an architecture property. Apply updates through the normal controlled patch workflow.

## Remaining current-state work

Major outstanding work now includes:

- observe and record the first unattended isolated backup run;
- prove a representative QEMU restore and application-consistent `cloud-01` recovery;
- establish an independent second backup copy and non-Proxmox data protection;
- revisit a two-node Proxmox cluster only after dedicated Corosync NICs and quorum/QDevice design are ready;
- deploy `edge-01` Cloudflare Tunnel only when approved;
- refresh the physical switch/router port map after SPAN activation;
- complete remaining switch/router hardening decisions;
- process package updates through the controlled patch workflow;
- continue service-specific observability and recovery documentation.

Already validated services must not be rolled backwards merely to match older documentation.
