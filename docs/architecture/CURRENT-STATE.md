# Current-State Architecture

This document records the validated current homelab estate as of 14 September 2026.

It describes what is live now. Historical host identities and earlier migration assumptions remain useful evidence, but they are not current deployment authority.

## Authority model

`homelab-platform/IaC/` is the authoritative location for infrastructure and service configuration that has been migrated and validated there.

Legacy repositories may remain useful reference sources for areas not yet migrated. They must not be treated as current authority after their workload or configuration has been explicitly migrated and validated in `homelab-platform`.

A detailed reconciliation trail for this snapshot is recorded in `docs/architecture/ESTATE-AUDIT-2026-09-14.md`.

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
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi media endpoint | ACTIVE |
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

The two Proxmox nodes are intentionally standalone. No production design depends on Corosync or shared cluster membership.

### `PROXMOX` — `192.168.2.70`

Validated 14 September 2026:

- Debian 13 base;
- Proxmox VE 9.2.11;
- running kernel `7.0.14-15-pve`;
- Chrony active;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units during the compact estate audit.

Live workload placement:

| Type | ID | Name | State |
|---|---:|---|---|
| LXC | 100 | `dns-02` | running |
| LXC | 102 | `mail-relay-01` | running |
| VM | 200 | `cloud-01` | running |
| VM | 201 | `sensor-01` | running |
| VM | 9000 | Debian cloud template | stopped |
| VM | 9001 | Debian cloud template with QGA | stopped |

An obsolete earlier Network Host Collector installation was found on this node during the 14 September audit. Its timer was enabled but inactive, there was no inventory file, and the unit referenced the superseded `/usr/local/bin/homelab-network-host-collector.py` implementation. It was backed up under `/root/legacy-network-host-collector-20260914-060957` and removed. The current collector belongs on `Proxmox-2` only.

### `Proxmox-2` — `192.168.2.71`

Validated 14 September 2026:

- Debian 13 base;
- Proxmox VE 9.2.2;
- running kernel `7.0.2-6-pve`;
- Chrony active;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units during the compact estate audit;
- active Network Host Collector timer with current inventory under `/var/lib/homelab-network-hosts/inventory.json`.

Live guests:

| Type | ID | Name | State |
|---|---:|---|---|
| VM | 200 | `monitor-01` | running |
| LXC | 101 | `dns-01` | running |
| LXC | 103 | `edge-01` | running |

The two Proxmox nodes are on different current patch levels and should continue through the normal controlled patch workflow rather than being assumed identical.

## DNS

Current resolver pair:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

Both workloads run:

- Pi-hole Core 6.4.3;
- Pi-hole Web 6.6;
- Pi-hole FTL 6.7;
- Unbound 1.22.0;
- Node Exporter;
- Alloy 1.19.2.

Both reported zero failed systemd units in the 14 September compact audit.

Managed local-record parity remains authoritative through IaC. `192.168.2.48` is `admin-01` and must not be treated as a DNS resolver.

## Monitoring and logging

`monitor-01` is the central metrics, alerting and logging platform.

Direct validation on 14 September 2026 proved these containers running:

| Service | Image/version | State |
|---|---|---|
| Prometheus | `prom/prometheus:v3.14.0` | running |
| Grafana | `grafana/grafana:13.2.1` | running |
| Alertmanager | `prom/alertmanager:v0.34.0` | running |
| Blackbox Exporter | `prom/blackbox-exporter:v0.28.0` | running |
| Loki | `grafana/loki:3.7.7` | running |

Native Alloy 1.19.2 is also active on `monitor-01` and listens locally on TCP/12345.

Validated listeners include:

```text
3000  Grafana
3100  Loki
9090  Prometheus
9093  Alertmanager
9115  Blackbox Exporter
12345 Alloy local UI/API
```

Direct local health checks returned HTTP 200 for Prometheus, Grafana, Alertmanager and Loki.

Router syslog still arrives through rsyslog on UDP/5514 and is stored at:

```text
/var/log/homelab/router/rt-ac86u.log
```

Alloy now ships that dedicated log into the local Loki service on `monitor-01`. The old statement that Loki/Alloy are future-only is superseded.

The broader Alloy baseline is deployed across the current managed estate. During this audit `admin-01` was the one identified drift item and was reconciled successfully to Alloy 1.19.2.

## Production cloud service

`cloud-01` is a live production Nextcloud platform.

Validated 14 September state:

- Debian 13 VM on `PROXMOX`;
- dedicated 200 GiB ext4 data disk at `/srv/cloud-01-data`;
- Docker/Compose active;
- Nextcloud `34.0.3-apache` app and cron containers running;
- PostgreSQL `18.6-alpine` healthy;
- Redis `8.2.9-alpine` healthy;
- application endpoint `192.168.2.53:8080`;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units.

The former 4 TB WD USB disk is not the cloud production data disk. Backup and restore proof for important cloud data remains outstanding.

## Network sensor

`sensor-01` is now an active passive network sensor; the earlier Phase 1-only description is superseded.

Validated 14 September 2026:

- Debian 13 VM at `192.168.2.55`;
- management interface `eth0` up;
- dedicated capture interface `enx00249b63b38a` up with promiscuous mode enabled;
- capture gate `/etc/homelab-network-sensor/capture-enabled` present;
- Suricata 8.0.6 active and enabled;
- Zeek 8.0.10 installed under `/opt/zeek`;
- `homelab-zeek.service` active and enabled;
- `zeekctl status` reports the standalone Zeek process running;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units.

The capture path must continue to preserve separation between the management interface and the passive capture interface. The capture adapter must not be repurposed as a normal routed management interface.

## Network host discovery

The current Network Host Collector is deployed on `Proxmox-2` only.

Validated state on 14 September 2026:

- `homelab-network-host-collector.timer` enabled and active;
- approximately five-minute scan cadence;
- inventory updating under `/var/lib/homelab-network-hosts/inventory.json`;
- deep-profiling and enrichment components are managed separately through the current IaC roles.

The obsolete earlier collector installation on `PROXMOX` was removed during the audit.

## Edge host

`edge-01` is a running Debian 13 LXC, CT 103 on `Proxmox-2`, at `192.168.2.56`.

Current evidence shows:

- no `cloudflared` package/binary/service;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units.

The host remains reserved for a future Cloudflare Tunnel connector. The connector workload is not deployed.

## Mail relay

`mail-relay-01` is CT 102 on `PROXMOX` at `192.168.2.54`.

Validated state includes:

- Debian 13;
- Postfix active/enabled;
- SMTP relay design through Gmail smart host retained;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units.

The internal relay ACL remains intentionally restricted. Protected Gmail relay credentials remain outside Git.

## Media

`media-01` at `192.168.2.195` is the Raspberry Pi 5 Kodi endpoint.

Validated 14 September state includes:

- Kodi 21.3 active/enabled;
- Samba active/enabled;
- Chrony active;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units.

The intended nftables policy remains a separate follow-up until deliberately deployed and remotely validated.

## Administration host

`admin-01` at `192.168.2.48` is the normal controller for homelab administration and IaC.

During the 14 September audit:

- Node Exporter was healthy;
- Alloy was found missing despite `admin-01` being part of the Ansible Alloy baseline;
- `smartmontools.service` was the only failed unit because the Raspberry Pi boots from SD (`mmcblk0`) and no SMART-capable device was available to monitor.

The SMART daemon was disabled/stopped and its failed state cleared. The package remains installed for future SMART-capable storage. The existing Alloy playbook was then applied with interactive become authentication and completed successfully.

Current state:

- Alloy 1.19.2 installed;
- Alloy enabled and active;
- Node Exporter active;
- zero failed systemd units.

Production Ansible should normally be launched from the checked-out `homelab-platform` repository on this host.

## Docker / BirdNET host

`docker-01` at `192.168.2.220` remains the dedicated Raspberry Pi 4 BirdNET-Go host.

Validated state:

- Debian 13 / aarch64;
- Docker active/enabled;
- exactly one intended application container;
- `birdnet-go` using `ghcr.io/tphakala/birdnet-go:20260823`;
- container healthy;
- Node Exporter active;
- Alloy 1.19.2 active;
- zero failed systemd units.

The former TestServer workload estate must not be silently reintroduced.

## Backup posture

The 12 September backup audit remains the latest evidence-backed backup assessment:

- no active production Proxmox Backup Server;
- no proven production Restic/Backrest platform;
- no proven end-to-end restore workflow for the important production data sets;
- no production design should treat the WD 4 TB disk as the sole copy of important data.

Backup implementation and restore proof remain outstanding work.

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
- SSH unavailable.

The earlier 12 September statement that port mirroring was disabled is superseded. Current switch configuration shows:

```text
mirror-port 24
interface 1-23
   monitor
```

`show monitor` confirms port 24 as the mirror destination with ports 1 through 23 as monitoring sources.

The earlier dated physical port map, including the old port-24 router mapping, must not be treated as current after activation of the mirror configuration. A new physical port map should be captured separately rather than inferred.

### ASUS

The ASUS RT-AC86U remains gateway, DHCP authority and AiMesh controller. AiMesh nodes are at `.181` and `.218`.

Router syslog forwarding to `monitor-01 .52:5514/udp` remains operational and is now integrated into the Alloy/Loki logging path while retaining the local rsyslog file.

## Time service

The physical Proxmox hosts provide redundant LAN NTP:

```text
ntp-01.jameshouse -> 192.168.2.70
ntp-02.jameshouse -> 192.168.2.71
```

Chrony is active on both nodes and remains the intended local time-service design.

## Patch state

The 14 September compact audit identified a non-trivial package-update backlog on several hosts, particularly `media-01`, `Proxmox-2`, `admin-01` and `docker-01`.

Those counts are an audit snapshot from the hosts' then-current APT metadata rather than an architecture property. Apply them through the normal patch-management workflow; do not treat them as documentation configuration drift.

## Remaining current-state work

Major outstanding work now includes:

- design and deploy the `edge-01` Cloudflare Tunnel connector only when approved;
- build a real backup platform and prove representative restores;
- refresh the physical switch/router port map after the SPAN activation;
- complete remaining switch/router hardening decisions;
- process the package-update backlog through the controlled patch workflow;
- continue service-specific observability, Network Hosts enrichment and recovery documentation;
- validate and document restore paths for cloud, BirdNET and media user data.

Already validated services must not be rolled backwards merely to match older documentation.
