<!-- estate-authority: IaC/inventory/estate.json -->
# Current-State Architecture

**Status:** CURRENT OPERATIONAL TRUTH  
**Current-state review:** 6 October 2026  
**Identity/address authority:** `IaC/inventory/estate.json`  
**Configuration authority:** `IaC/`

This document records what is live now. Dated audits, migration notes and commissioning records remain evidence, but they do not override validated live state or the canonical estate inventory.

## Authority model

Use this precedence when documents disagree:

1. validated live state;
2. `IaC/inventory/estate.json` for identity, address and lifecycle state;
3. this `CURRENT-STATE.md` for human-readable architecture;
4. Git-managed IaC for intended/deployed configuration;
5. production service/runbook documents;
6. dated audits and historical migration evidence.

The 5 October repository audit is recorded in `docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-10-05.md`.

## Active estate

| Asset | Address | Current role | State |
|---|---:|---|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / SSH jump / IaC controller / Corosync QNetd | ACTIVE |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT100 on `PROXMOX` | ACTIVE |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT101 on `Proxmox-2` | ACTIVE |
| `monitor-01` | `192.168.2.52` | Prometheus/Grafana/Alertmanager/Blackbox/Loki + active network discovery, VM202 on `Proxmox-2` | ACTIVE |
| `cloud-01` | `192.168.2.53` | Nextcloud/PostgreSQL/Redis, VM200 on `PROXMOX` | ACTIVE |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix relay, CT102 on `PROXMOX` | ACTIVE |
| `sensor-01` | `192.168.2.55` | Suricata/Zeek passive sensor, VM201 on `PROXMOX` | ACTIVE |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT103 on `Proxmox-2`; `cloudflared` absent | ACTIVE HOST |
| `greenbone-01` | `192.168.2.57` | Greenbone vulnerability scanner, VM203 on `Proxmox-2` | ACTIVE |
| `komodo-01` | `192.168.2.58` | Komodo Core control plane, CT104 on `PROXMOX` | ACTIVE |
| `zabbix-01` | `192.168.2.59` | Zabbix platform, CT105 on `PROXMOX` | ACTIVE |
| `home-01` | `192.168.2.60` | Home Assistant OS, VM204 on `PROXMOX` | ACTIVE |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` node 1 / NTP | ACTIVE |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` node 2 / NTP; former discovery source retained for rollback evidence | ACTIVE |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint / primary Proxmox NFS backup target | ACTIVE |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host | ACTIVE |
| ASUS RT-AC86U | `192.168.2.1` | Router / DHCP / AiMesh controller / OpenVPN endpoint | ACTIVE |
| ASUS AiMesh node | `192.168.2.181` | Wireless mesh node | ACTIVE |
| ASUS AiMesh node | `192.168.2.218` | Wireless mesh node | ACTIVE |
| HP ProCurve 2510G-24 | `192.168.2.16` | Core switch / active SPAN source | ACTIVE |

The normal Ansible-managed Linux baseline is **15 hosts**. `home-01` is active but is HAOS and intentionally outside that 15-host Linux/Ansible baseline.

## Retired identities

These names are historical only and must not be used as active deployment, monitoring or recovery targets:

- `TestServer` -> hardware now `docker-01`; <!-- historical -->
- `DietPi` -> hardware now `admin-01`; <!-- historical -->
- `ids-01` -> decommissioned; <!-- historical -->
- former `k3s-node-01` identity -> hardware now `media-01`; <!-- historical -->
- former `dns-02` address `192.168.2.242` -> retired. <!-- historical -->

## Proxmox platform

The live virtualization platform is the two-node cluster:

```text
cluster: jameshouse-pve
node 1:  PROXMOX    192.168.2.70
node 2:  Proxmox-2  192.168.2.71
```

Corosync links:

```text
link0 — preferred direct interconnect
  PROXMOX:   10.255.255.1/30
  Proxmox-2: 10.255.255.2/30

link1 — fallback
  management LAN 192.168.2.0/24
```

`admin-01` runs QNetd and supplies the external third vote. Validated quorum is 3 total votes with quorum 2 and QDevice present.

Latest controlled maintenance evidence from 5 October 2026:

```text
PROXMOX:   pve-manager 9.2.21, running kernel 7.0.14-20-pve
Proxmox-2: pve-manager 9.2.21, running kernel 7.0.14-20-pve
```

Current production guest placement:

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

Production guest disks remain node-local. Cluster membership and quorum do not by themselves provide automatic guest-data HA after loss of the node that owns a guest disk.

## DNS

Current resolver pair:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

Both run Pi-hole + Unbound and forward Pi-hole to local Unbound at `127.0.0.1#5335`.

`admin-01` at `.48` is **not** a DNS resolver.

The former cross-resolver local-record parity defect is resolved in current IaC. The managed host set contains both `dns-01.jameshouse` and `dns-02.jameshouse`.

## Monitoring, logging and dashboards

`monitor-01` hosts the production monitoring/logging stack:

- Prometheus;
- Grafana;
- Alertmanager;
- Blackbox Exporter;
- Loki;
- Grafana Alloy pipelines.

The 15 managed Linux systems report through the host-monitoring baseline and Zabbix Agent 2. Zabbix Server runs on `zabbix-01`.

Step 10 estate-wide Grafana work is complete. Production navigation includes:

- Homelab Home / operations overview;
- Homelab Hosts;
- Homelab Patch & Reboot Status;
- Node Detail;
- Network Hosts / per-device views.

The monitoring playbook was deployed successfully and a repeat run completed idempotently with:

```text
changed=0
unreachable=0
failed=0
```

## Automated patching

The managed Linux estate uses security-only unattended upgrades with **automatic reboot disabled**.

Final validated 5 October 2026 estate telemetry after controlled patching:

```text
reporting hosts:            15
pending updates:            0
security updates pending:   0
reboots required:           0
unattended-upgrades present:15
automatic reboots enabled:  0
```

Current exporter metrics use the `homelab_patch_*` namespace. Retired dashboard metrics must not be reintroduced.

## Network discovery and host identification

The single-owner migration completed on **27 September 2026**.

Production owner: `monitor-01`.

Active responsibilities on `monitor-01` include:

- network collector;
- selective enricher;
- read-only OS-evidence publisher;
- trusted Proxmox guest refresh;
- targeted deep profiling;
- first-seen notifier;
- Network Hosts Grafana publication;
- persistent host-page generation;
- bounded DNS evidence correlation;
- bounded AI host assessment where enabled by the reviewed workflow.

`Proxmox-2` is the former source. Its discovery timers are disabled/inactive and its retained files are rollback/history evidence. Do not re-enable source scanning while `monitor-01` is the active owner.

The detailed staged migration and cutover evidence remains in `docs/operations/network-discovery-monitor01-migration.md` and dated audit records. Pre-cutover statements in those files are historical evidence only.

## Network sensor and switch SPAN

`sensor-01` is the active passive sensor. Suricata and Zeek consume the dedicated capture interface.

Current switch monitoring design:

```text
HP ProCurve 2510G-24
mirror destination: port 24
mirror sources:     ports 1-23
```

The older 12 September switch-port map that shows port 24 as the router uplink is a historical pre-repatch snapshot and must not be used as current cabling authority.

## Vulnerability management

`greenbone-01` is the active LAN-only Greenbone scanner.

Current operating model includes:

- managed daily vulnerability scan;
- machine-readable evidence generation;
- restricted evidence transfer to `monitor-01`;
- schema/freshness validation;
- management-report integration.

Missing, invalid or stale evidence is an evidence problem and must not be represented as zero vulnerabilities.

## Container management

`komodo-01` runs Komodo Core and MongoDB and is the container-management control plane.

Komodo Periphery is commissioned on explicitly managed Docker hosts, including the currently documented production hosts. Additional onboarding is a deliberate per-host decision rather than a platform prerequisite.

Komodo adoption must not silently recreate existing production Compose workloads.

## Remote access

The production remote-access path is the native OpenVPN server on the ASUS RT-AC86U.

Production acceptance completed on 18 September 2026 from a Windows laptop on an external network. The client established the tunnel, reached the homelab LAN and retained normal split-tunnel Internet access.

DDNS and router/client recovery checks remain maintenance/recovery work rather than blockers to operational acceptance.

No dedicated `vpn-01` VM is allocated.

## Cloud / Nextcloud

`cloud-01` is the production Nextcloud platform:

- VM200 on `PROXMOX`;
- dedicated 200 GiB application-data disk;
- `/srv/cloud-01-data`;
- Nextcloud + PostgreSQL + Redis + cron;
- service endpoint `192.168.2.53:8080`;
- SMTP through `mail-relay-01`.

VM-level backup is proven. Application-consistent Nextcloud/PostgreSQL recovery remains outstanding.

## Home Assistant

`home-01` is active as VM204 on `PROXMOX` using Home Assistant OS.

Commissioned evidence includes:

- fixed production identity at `192.168.2.60`;
- HTTP service on port 80;
- DNS on both managed resolvers;
- native Home Assistant backup;
- manual Proxmox snapshot/integrity proof;
- Proxmox protection enabled;
- inclusion in the nightly `PROXMOX` backup schedule.

Still open: first unattended VM204 schedule proof, external monitoring and deeper recovery validation.

## Backup platform

Primary Proxmox guest backups use NFS on `media-01`.

Current schedule:

```text
PROXMOX
  job: homelab-nightly-proxmox
  schedule: 02:15
  storage: media-backup-proxmox
  guests: 100,102,104,105,200,201,204

Proxmox-2
  job: homelab-nightly-proxmox-2
  schedule: 03:15
  storage: media-backup-proxmox-2
  guests: 101,103,202,203

mode: snapshot
compression: zstd
retention: keep-last=3
```

Observed evidence includes unattended CT105 and VM203 backups. CT104 and VM204 still require explicit first-unattended-run proof in the current evidence set.

An isolated LXC restore proof exists for CT103. A representative QEMU restore, application-consistent `cloud-01` recovery and an independent second copy remain open.

## Administration and recovery control plane

`admin-01` is the normal Git/Ansible controller and QNetd host. It is intentionally lightweight and should not become an application server, DNS resolver, monitoring server or backup target.

Protected recovery state and secret material remain outside Git.

## Public / edge services

`edge-01` exists as CT103 but `cloudflared` is not deployed. Do not describe a Cloudflare Tunnel as live until it is explicitly deployed and validated.

Authelia is not part of the deployed architecture. Cloudflare is the intended MFA boundary for future public service exposure unless that decision is changed explicitly.

CrowdSec is not currently deployed and must not be listed as an active signal source.

## Important service endpoints

| Service | URL |
|---|---|
| Grafana | `http://192.168.2.52:3000/` |
| Prometheus | `http://192.168.2.52:9090/` |
| Alertmanager | `http://192.168.2.52:9093/` |
| Loki | `http://192.168.2.52:3100/` |
| Nextcloud | `http://192.168.2.53:8080/` |
| Greenbone | `https://192.168.2.57/` |
| Komodo | `http://192.168.2.58:9120/` |
| Zabbix | `http://192.168.2.59:8080/` |
| Home Assistant | `http://192.168.2.60/` |
| PROXMOX | `https://192.168.2.70:8006/` |
| Proxmox-2 | `https://192.168.2.71:8006/` |
| BirdNET-Go | `http://192.168.2.220:8080/` |

These are LAN/VPN administration/service endpoints unless another document explicitly defines public exposure.

## Open architecture/recovery items

The following remain genuine future work and must not be confused with completed migrations:

- Proxmox link0 -> link1 failover proof and controlled one-node quorum testing;
- first unattended CT104 and VM204 backup evidence;
- representative QEMU restore proof;
- application-consistent Nextcloud/PostgreSQL restore proof;
- independent second backup copy/failure domain;
- `home-01` external availability monitoring and deeper recovery proof;
- Cloudflare Tunnel only when a real service requirement exists;
- password-manager product/design selection;
- network/switch hardening where separately reviewed.

## Historical evidence

Detailed evidence is intentionally retained in dated files, including:

- `docs/architecture/ESTATE-AUDIT-2026-09-14.md`;
- `docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-09-16.md`;
- `docs/architecture/ESTATE-APPLICATION-AUDIT-2026-09-17.md`;
- `docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-10-05.md`;
- `docs/operations/network-discovery-monitor01-migration.md`;
- migration/commissioning records under `docs/` and `production docs/`.

Those records should preserve the state observed at the time. They must not be read as current deployment authority when they conflict with this document or `IaC/inventory/estate.json`.
