<!-- estate-authority: IaC/inventory/estate.json -->
# Current-State Architecture

This document records the validated current homelab estate through 18 September 2026.

It describes what is live now. Historical host identities and earlier migration assumptions remain useful evidence, but they are not current deployment authority.

## Authority model

`homelab-platform/IaC/` is the authoritative location for infrastructure and service configuration that has been migrated and validated there.

Legacy repositories may remain useful reference sources for areas not yet migrated. They must not be treated as current authority after their workload or configuration has been explicitly migrated and validated in `homelab-platform`.

A detailed reconciliation trail for the 14 September estate snapshot is recorded in `docs/architecture/ESTATE-AUDIT-2026-09-14.md`. The post-commissioning document audit on 16 September is recorded in `docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-09-16.md`. The read-only estate application audit on 17 September is recorded in `docs/architecture/ESTATE-APPLICATION-AUDIT-2026-09-17.md`.

## Active estate

| Asset | Address | Current role | State |
|---|---:|---|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / SSH jump / IaC controller / Corosync QNetd host | ACTIVE |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT 100 on `PROXMOX` | ACTIVE |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT 101 on `Proxmox-2` | ACTIVE |
| `monitor-01` | `192.168.2.52` | Prometheus, Grafana, Alertmanager, Blackbox, Loki and router-log ingestion, VM 202 on `Proxmox-2` | ACTIVE |
| `cloud-01` | `192.168.2.53` | Production Nextcloud/PostgreSQL/Redis, VM 200 on `PROXMOX` | ACTIVE |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix SMTP relay, CT 102 on `PROXMOX` | ACTIVE |
| `sensor-01` | `192.168.2.55` | Active Suricata/Zeek passive network sensor, VM 201 on `PROXMOX` | ACTIVE — CAPTURE OPERATIONAL |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT 103 on `Proxmox-2` | HOST ACTIVE — CLOUDFLARED NOT DEPLOYED |
| `greenbone-01` | `192.168.2.57` | Greenbone Community vulnerability scanner, VM 203 on `Proxmox-2` | ACTIVE — LAN-ONLY SCANNER |
| `komodo-01` | `192.168.2.58` | Komodo control-plane host, unprivileged CT 104 on `PROXMOX` | ACTIVE — KOMODO CORE COMMISSIONED; APP + MANUAL VM BACKUP PROVEN |
| `zabbix-01` | `192.168.2.59` | Zabbix monitoring platform, CT 105 on `PROXMOX` | ACTIVE — PLATFORM + 15-HOST AGENT ESTATE REPORTING; UNATTENDED BACKUP OBSERVED |
| `home-01` | `192.168.2.60` | Home Assistant OS 18.2, VM 204 on `PROXMOX` | ACTIVE — HA CORE/SUPERVISOR HEALTHY; PROTECTED; NATIVE + MANUAL VM BACKUP PROVEN |
| `PROXMOX` | `192.168.2.70` | Proxmox VE cluster node 1 / cluster anchor | ACTIVE — `jameshouse-pve` MEMBER |
| `Proxmox-2` | `192.168.2.71` | Proxmox VE cluster node 2 / Network Host Collector host | ACTIVE — `jameshouse-pve` MEMBER |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target | ACTIVE — CORE WORKLOADS OPERATIONAL; KODI ADD-ON RECONCILIATION OPEN |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host | ACTIVE |
| ASUS RT-AC86U | `192.168.2.1` | Router / DHCP / AiMesh controller / OpenVPN remote-access endpoint | ACTIVE |
| ASUS AiMesh node | `192.168.2.181` | Wireless mesh node | ACTIVE |
| ASUS AiMesh node | `192.168.2.218` | Wireless mesh node | ACTIVE |
| HP ProCurve 2510G-24 | `192.168.2.16` | Core managed switch / SPAN source | ACTIVE |

## Web and service URLs

These are the current LAN/VPN administration and service endpoints that are explicitly defined in IaC or validated during commissioning/audit work. They should not be treated as public endpoints unless separately documented.

| Service | URL | Notes |
|---|---|---|
| Grafana | `http://192.168.2.52:3000/` | Main monitoring UI on `monitor-01` |
| Prometheus | `http://192.168.2.52:9090/` | Metrics/query UI on `monitor-01` |
| Alertmanager | `http://192.168.2.52:9093/` | Alert routing UI on `monitor-01` |
| Blackbox Exporter | `http://192.168.2.52:9115/` | Probe service endpoint on `monitor-01` |
| Loki | `http://192.168.2.52:3100/` | Loki HTTP/API endpoint on `monitor-01` |
| Nextcloud | `http://192.168.2.53:8080/` | Production `cloud-01` frontend |
| Greenbone | `https://192.168.2.57/` | LAN-only scanner UI; current certificate is self-signed |
| Komodo | `http://192.168.2.58:9120/` | LAN/VPN administration UI |
| Zabbix | `http://192.168.2.59:8080/` | Zabbix frontend |
| Home Assistant | `http://home-01/` | Friendly DNS URL validated through both internal resolvers |
| Home Assistant | `http://192.168.2.60/` | Direct-IP fallback |
| Proxmox VE — `PROXMOX` | `https://192.168.2.70:8006/` | Cluster node 1 web UI |
| Proxmox VE — `Proxmox-2` | `https://192.168.2.71:8006/` | Cluster node 2 web UI |
| BirdNET-Go | `http://192.168.2.220:8080/` | `docker-01` web endpoint |

## Retired identities

The following names must not be treated as active production hosts:

- `TestServer` — retired identity for the Raspberry Pi 4 now operating as `docker-01`.
- `DietPi` — retired identity for the Raspberry Pi 3 now operating as `admin-01`.
- `ids-01` — decommissioned.
- historical `k3s-node-01` identity associated with `192.168.2.195` — retired; the host is `media-01`.
- former `dns-02` at `192.168.2.242` — retired.

Historical hardware and audit documents remain useful evidence but are not live configuration authority.

## Proxmox platform

The two PVE hosts form the production two-node cluster:

```text
cluster: jameshouse-pve
node 1:  PROXMOX    192.168.2.70
node 2:  Proxmox-2  192.168.2.71
```

The actual first-node hostname remains `PROXMOX`. Human-facing diagrams may call it Proxmox-1 for readability, but automation and cluster operations must use the real node name.

### Corosync

The cluster uses two Kronosnet links:

```text
link0 — preferred, priority 20
  PROXMOX:   10.255.255.1/30
  Proxmox-2: 10.255.255.2/30
  direct point-to-point USB Ethernet cable
  no switch and no default gateway

link1 — fallback, priority 5
  PROXMOX:   192.168.2.70
  Proxmox-2: 192.168.2.71
  normal management LAN
```

Both links were re-validated connected from both nodes during the 17 September application audit.

Dedicated heartbeat interfaces:

```text
PROXMOX
  enx001a9f0c993b
  00:1a:9f:0c:99:3b
  Microchip/SMSC LAN7500

Proxmox-2
  enx00249b7b346d
  00:24:9b:7b:34:6d
  ASIX AX88179
```

The direct link completed sustained bidirectional packet testing with zero loss before Corosync adoption.

### Quorum / QDevice

`admin-01` at `192.168.2.48` runs `corosync-qnetd` and provides the external third vote over the normal LAN.

Validated cluster quorum on 17 September:

```text
Nodes:            2
Expected votes:   3
Total votes:      3
Quorum:           2
Flags:            Quorate Qdevice
```

`corosync-qdevice` is active on both PVE nodes. QNetd listens on TCP/5403 and saw both cluster clients connected during the audit.

This protects cluster quorum during a single PVE-node loss while QDevice remains reachable. It does not make node-local guest disks automatically available on the surviving hypervisor.

### `PROXMOX` — `192.168.2.70`

Validated on 17 September 2026:

- Debian 13 base;
- Proxmox VE / pve-manager 9.2.20;
- running kernel `7.0.14-17-pve`;
- node ID 1;
- zero failed systemd units;
- Corosync active;
- `pve-cluster` active;
- QDevice client active;
- Chrony active and synchronized;
- Node Exporter active;
- Alloy active;
- Zabbix Agent 2 active.

Live workload placement:

| Type | ID | Name | State |
|---|---:|---|---|
| LXC | 100 | `dns-02` | running |
| LXC | 102 | `mail-relay-01` | running |
| LXC | 104 | `komodo-01` | running |
| LXC | 105 | `zabbix-01` | running |
| VM | 200 | `cloud-01` | running |
| VM | 201 | `sensor-01` | running |
| VM | 204 | `home-01` | running, protected |
| VM | 9000 | Debian cloud template | stopped |
| VM | 9001 | Debian cloud template with QGA | stopped |

An obsolete earlier Network Host Collector installation was removed from this node. The current collector belongs on `Proxmox-2` only.

### `Proxmox-2` — `192.168.2.71`

Validated on 17 September 2026:

- Debian 13 base;
- Proxmox VE / pve-manager 9.2.20;
- running kernel `7.0.14-17-pve`;
- node ID 2;
- zero failed systemd units;
- Corosync active;
- `pve-cluster` active;
- QDevice client active;
- Chrony active and synchronized;
- Node Exporter active;
- Alloy active;
- Zabbix Agent 2 active;
- active timer-driven Network Host Collector with fresh inventory under `/var/lib/homelab-network-hosts/inventory.json`.

Live guests:

| Type | ID | Name | State |
|---|---:|---|---|
| LXC | 101 | `dns-01` | running |
| LXC | 103 | `edge-01` | running |
| VM | 202 | `monitor-01` | running |
| VM | 203 | `greenbone-01` | running, protected |

The former standalone `monitor-01` VMID `200` was changed to cluster VMID `202`, eliminating the pre-cluster duplicate-ID conflict with `cloud-01`.

### Storage and HA boundary

Production guest disks remain on node-local storage, including `local-lvm` and `vm-ssd` depending on the guest.

The cluster therefore provides a common management plane, cluster-wide identity, Corosync/quorum and controlled migration workflows, but it is **not yet a shared-storage/replicated-disk HA platform**. Automatic guest restart after loss of the node owning a local disk must not be assumed.

## DNS

Current resolver pair:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

Both workloads run Pi-hole Core 6.4.3, Pi-hole Web 6.6, Pi-hole FTL 6.7, Unbound 1.22.0, Node Exporter and Alloy.

The 17 September audit proved recursive resolution, valid DNSSEC with AD, broken-DNSSEC SERVFAIL behavior, Pi-hole forwarding through `127.0.0.1#5335`, five enabled adlists and local-record parity on both resolvers. The `home-01.jameshouse` record resolves to `192.168.2.60` on both.

Managed local-record parity remains authoritative through IaC. `192.168.2.48` is `admin-01` and must not be treated as a DNS resolver.

## Zabbix monitoring

`zabbix-01` is the active dedicated Zabbix monitoring platform.

Validated state through 17 September 2026:

- Debian 13 unprivileged LXC at `192.168.2.59`;
- CTID 105 on `PROXMOX`;
- Zabbix 7.0.30;
- PostgreSQL 17 and TimescaleDB 2.29.2 active;
- Zabbix Server active;
- Zabbix Agent 2 active and enabled locally;
- Agent 2 listens on TCP/10050;
- Nginx and PHP-FPM active;
- frontend HTTP health returned 200;
- whole-container manual backup integrity proven;
- application logical backup and restore validation proven;
- CT105 is included in the IaC/live `homelab-nightly-proxmox` 02:15 backup selection;
- an unattended CT105 archive from the 17 September 02:15 cycle was observed on `media-01`;
- the pre-platform rollback snapshot remains retained;
- the `zabbix_agents` inventory group contains all 15 managed Linux systems;
- Zabbix host group `Homelab/Linux` contains matching host objects linked to `Linux by Zabbix agent active`;
- all 15 host objects were observed reporting on 16 September 2026;
- active-agent hostnames match the Ansible inventory identities.

The application is healthy. Three mount-related failed units seen earlier on the unprivileged LXC (`dev-mqueue.mount`, `run-lock.mount`, `tmp.mount`) remain a baseline-cleanup item rather than an active Zabbix outage.

## Monitoring and logging

`monitor-01` is the central metrics, alerting and logging platform and runs as VM202 on `Proxmox-2`.

Validated running containers on 17 September include:

| Service | Image/version | State |
|---|---|---|
| Prometheus | `prom/prometheus:v3.14.0` | running |
| Grafana | `grafana/grafana:13.2.1` | running |
| Alertmanager | `prom/alertmanager:v0.34.0` | running |
| Blackbox Exporter | `prom/blackbox-exporter:v0.28.0` | running |
| Loki | `grafana/loki:3.7.7` | running |

Prometheus and Loki readiness passed, Grafana reported database health `ok`, Alertmanager and Blackbox were reachable, and the expected production alert rules were loaded.

Native Alloy is active on `monitor-01`. Router syslog is received on UDP/5514, retained under `/var/log/homelab/router/rt-ac86u.log`, and shipped to Loki through the dedicated router Alloy role. The router log was present and current during the audit.

Loki heartbeat query/presence metrics were successful for the expected source hosts (`PROXMOX`, `Proxmox-2`, `cloud-01`, `dns-01`, `dns-02`, `docker-01`, `edge-01`, `mail-relay-01`, `media-01`).

The broader Alloy baseline is deployed across the current managed estate according to inventory scope.

## Remote access VPN

The selected remote-access endpoint is the native OpenVPN server on the ASUS RT-AC86U at `192.168.2.1`.

Validated through 18 September 2026:

- **production status: FULLY OPERATIONAL**;
- OpenVPN Server 1 reported running;
- an external client successfully completed username/password authentication;
- the tunnel was established and a `10.8.0.3` client address was allocated during the observed session;
- the router pushed the internal route `192.168.2.0/24`;
- the router pushed DNS servers `192.168.2.51` and `192.168.2.50`;
- the observed session used UDP, TLS 1.3 and AES-256-GCM;
- the VPN events were retained in router syslog on `monitor-01` and are part of the Alloy-to-Loki stream.

The former dedicated `vpn-01` WireGuard design and exploratory WireGuard-on-`docker-01` path are not current production architecture. No VPN VMID or separate LAN address is allocated.

Production acceptance was completed on 18 September 2026 using a Windows laptop from an external network. The client received `10.8.0.2`, the remote homelab administration path was operational, and normal Internet access remained on the external network as intended for split tunnelling. The VPN is therefore **FULLY OPERATIONAL** for its production laptop remote-administration use case. DDNS and router-reset/replacement/client re-enrolment checks remain useful recovery/maintenance work and are not operational acceptance blockers.

## Komodo management host

`komodo-01` is the active Komodo container-management control plane.

Validated state through 17 September 2026:

- Debian 13 unprivileged LXC at `192.168.2.58`;
- CTID 104 on `PROXMOX`;
- 2 CPU cores, 2048 MiB RAM, 512 MiB swap and 32 GiB `vm-ssd` root filesystem;
- fixed MAC `02:00:00:00:01:04`;
- LXC `nesting=1` and root-managed `keyctl=1`;
- Terraform state contains exactly the Komodo LXC resource and reports no drift;
- direct root SSH through the homelab automation key is validated;
- cgroup v2 and nested user namespaces are available;
- Docker Engine 29.8.1 and Docker Compose 5.5.1 are commissioned;
- Docker uses the containerd `overlayfs` snapshotter with cgroup v2;
- container networking, named volumes and LAN port publishing are validated;
- Docker recovery after a CT reboot is validated;
- the Docker Ansible role is idempotent;
- no additional LXC privileges were added;
- MongoDB `8.0.32` is running healthy without a host-exposed TCP/27017 listener;
- Komodo Core `2.3.3` is running and the web UI returned HTTP 200 during the 17 September audit;
- Core is currently LAN/VPN administered over `http://192.168.2.58:9120`;
- the Core deployment has no Docker socket mount and no local Periphery service;
- application backup and isolated database-restore validation are proven;
- CT104 manual Proxmox snapshot backup completed successfully on `media-backup-proxmox` and archive integrity/structure checks passed;
- CT104 is included in the IaC/live `homelab-nightly-proxmox` 02:15 backup selection;
- first unattended CT104 proof remains open from the displayed 17 September audit sample;
- Proxmox protection remains disabled pending deliberate acceptance.

The Proxmox `overlay` filesystem module is loaded and persisted, and its visibility inside CT104 is validated.

On 18 September 2026, `docker-01` became the first commissioned Komodo-managed Docker host. Komodo Periphery `2.3.3` runs on `docker-01` using the outbound Core connection to `http://192.168.2.58:9120`. Remote host and container terminals are disabled. Periphery identity is persisted in the Docker volume mounted at `/config/keys`, and keyless steady-state operation was proven across a forced container recreation. The bootstrap onboarding credential is not retained in the active host environment. The deployment is managed through the `komodo_periphery` Ansible role and completed an idempotent run with `changed=0`. BirdNET-Go remained healthy throughout commissioning.

Remaining Komodo platform work includes first unattended CT104 backup proof, the Proxmox protection decision, HTTPS hardening and controlled onboarding of additional Docker hosts.

## Production cloud service

`cloud-01` is a live production Nextcloud platform.

Validated state on 17 September:

- Debian 13 VM on `PROXMOX`;
- VMID 200;
- dedicated 200 GiB ext4 data disk at `/srv/cloud-01-data`;
- Docker/Compose active;
- Nextcloud `34.0.3-apache` app and cron containers running;
- PostgreSQL `18.6-alpine` healthy;
- Redis `8.2.9-alpine` healthy;
- application endpoint `192.168.2.53:8080`;
- Node Exporter, Alloy and Zabbix Agent 2 active;
- zero failed systemd units.

A complete VM-level snapshot backup is proven on `media-backup-proxmox`. Application-consistent Nextcloud/PostgreSQL recovery remains unproven and is still a separate requirement.

The 17 September application audit identified a configuration-path difference rather than a service failure: live Redis uses a mounted `redis.conf` with `requirepass`, while current IaC models the `.env`/`REDIS_PASSWORD` pattern. Reconcile this deliberately later; do not disrupt the healthy production service merely to remove drift.

## Vulnerability scanning

`greenbone-01` is the dedicated active vulnerability-scanning platform.

Validated state on 17 September 2026:

- Debian 13 VM at `192.168.2.57`;
- VMID 203 on `Proxmox-2`;
- 4 vCPU, 8192 MiB RAM and 80 GiB `local-lvm` disk;
- Greenbone Community Containers deployed through Docker Compose;
- expected Greenbone containers running/healthy where checks are defined;
- HTTPS exposed to the LAN only on `192.168.2.57:443` and returned HTTP 200;
- Node Exporter, Alloy and Zabbix Agent 2 active;
- Greenbone Docker logs proven in Loki;
- VM-level Proxmox protection enabled.

The controlled commissioning self-scan of `greenbone-01` completed with no Critical, High or Medium results. It produced one Low result at severity 2.1 for ICMP Timestamp Reply Information Disclosure and nine informational/log results. The ICMP timestamp item is tracked as a separate hardening follow-up; it did not block scanner commissioning.

VM203 has manual snapshot backup archives on `media-backup-proxmox-2`; archive integrity was proven with `zstd -t`. The nightly `Proxmox-2` job is IaC-managed at 03:15, selects `101,103,202,203`, and an unattended VM203 archive from the 17 September cycle was observed. VM203 is protected in Proxmox.

The scanner is deliberately separate from `sensor-01`. `sensor-01` performs passive Suricata/Zeek network observation; Greenbone performs active endpoint scanning. There is no direct sensor-to-Greenbone feed dependency.

Operational boundaries:

- no public/Cloudflare exposure;
- Greenbone administrator credentials remain outside Git;
- the current TLS certificate is self-signed;
- Alloy's Docker-socket access is privileged and must be treated as root-equivalent access to the Docker host;
- Community Container images use upstream rolling tags, so image immutability must not be assumed;
- future deployments should change the default Greenbone administrator credential before enabling LAN exposure.

## Network sensor

`sensor-01` is an active passive network sensor.

Validated state includes:

- Debian 13 VM at `192.168.2.55`;
- VMID 201 on `PROXMOX`;
- management interface `eth0` up;
- dedicated capture interface `enx00249b63b38a` up in promiscuous mode;
- capture gate present;
- Suricata 8.0.6 active/enabled;
- Zeek 8.0.10 active;
- current Suricata and Zeek logs observed during the 17 September audit;
- Node Exporter, Alloy and Zabbix Agent 2 active;
- zero failed systemd units.

The capture adapter remains dedicated to passive monitoring and must not be repurposed as a normal routed management or Corosync interface.

## Network host discovery

The current Network Host Collector is deployed on `Proxmox-2` only.

The 17 September audit confirmed the collector timer enabled/active, with fresh `inventory.json` and Prometheus textfile metrics generated at approximately 12:23. The collector service is `Type=oneshot`, so it is expected to be inactive between timer executions.

The obsolete collector installation on `PROXMOX` was removed.

Current IaC defaults set `network_host_collector_enable_timer: false`, while validated live state has the timer enabled. Verify whether an intentional inventory/extra-var override exists before changing either side.

## Edge host

`edge-01` is a running Debian 13 LXC, CT103 on `Proxmox-2`, at `192.168.2.56`.

No `cloudflared` workload is deployed. Node Exporter, Alloy and Zabbix Agent 2 are active. The host remains reserved for a future Cloudflare Tunnel connector.

## Mail relay

`mail-relay-01` is CT102 on `PROXMOX` at `192.168.2.54`.

Postfix is active/enabled and remains the approved internal SMTP relay to Gmail. The 17 September audit validated relay configuration, SASL/TLS policy, protected password maps, upstream TCP/587 reachability and an empty queue. No new end-to-end test message was sent during that read-only audit.

Protected Gmail relay credentials remain outside Git.

## Media and primary backup target

`media-01` at `192.168.2.195` is the Raspberry Pi 5 Kodi endpoint and the primary Proxmox guest-backup target.

Validated state on 17 September includes:

- Debian 13 on Raspberry Pi 5;
- Kodi 21.3 active/enabled with exactly one `kodi.bin` process;
- `/srv/media` and Movies/TV/Music/plugins directories present;
- Samba active/enabled, `Media` share mapped to `/srv/media`, TCP/445 listening;
- NFS server active with expected node-specific exports;
- NVMe-backed ext4 filesystem healthy with approximately 338 GiB free during audit;
- Node Exporter, Alloy and Zabbix Agent 2 active;
- zero failed systemd units.

Three IaC-managed Kodi add-ons were absent during the audit:

```text
weather.openmeteo
service.subtitles.opensubtitles-com
plugin.program.autocompletion
```

This is an application-completeness reconciliation item. Kodi itself is installed and operational.

Current backup exports:

```text
/srv/backup/pve-proxmox
  client: 192.168.2.70

/srv/backup/pve-proxmox-2
  client: 192.168.2.71

/srv/backup/pve
  legacy rollback namespace retained temporarily
```

Cluster storage is node-scoped so `.70` uses `media-backup-proxmox` and `.71` uses `media-backup-proxmox-2`. The shared `media-backup` namespace remains available as historical/rollback storage and should be reviewed once confidence in the split repositories is explicitly accepted.

## Administration host

`admin-01` at `192.168.2.48` is the normal controller for homelab administration and IaC.

It is also the QNetd host for `jameshouse-pve` and listens on TCP/5403 for the two PVE QDevice clients. The 17 September audit observed established QNetd connections from both `.70` and `.71`; QNetd reported two clients and one connected cluster.

Current state includes Ansible/Git/Python controller tooling, Alloy, Node Exporter, Zabbix Agent 2 and zero failed systemd units.

The controller-recovery timer and path watcher are enabled/active, the three managed scripts are executable and a fresh encrypted recovery bundle was created at approximately 03:16 on 17 September.

Production Ansible should normally be launched from the checked-out `homelab-platform` repository on this host. During the audit the worktree was clean but remained checked out on `fix/home-01-terraform-output-url`; return it to `main` after branch cleanup.

## Docker / BirdNET host

`docker-01` at `192.168.2.220` remains the dedicated Raspberry Pi 4 BirdNET-Go host and is the first Docker host commissioned for management through Komodo.

Validated application state includes Debian 13/arm64, Docker active, pinned image `ghcr.io/tphakala/birdnet-go:20260823` running healthy, HTTP endpoint responding, and the intended USB microphone operational.

Komodo Periphery `2.3.3` is deployed through the `komodo_periphery` Ansible role. It connects outbound to Komodo Core on `komodo-01` at `http://192.168.2.58:9120`; no Periphery management port is published on the host. Remote host and container terminals are disabled. Periphery identity is persisted through `/config/keys`, and successful Core login with no active onboarding credential was proven after forced container recreation. The steady-state Ansible deployment completed idempotently with `changed=0`.

BirdNET-Go remained running and healthy throughout Periphery commissioning. It is now also declared through the Git-managed `IaC/komodo/resources/docker-01.toml` resource and imported by the `homelab-platform` Komodo Resource Sync. The sync completed with state `OK` and the Deployment is visible as running on `docker-01`. The declaration remains `deploy = false`; live validation confirmed that the existing container was not replaced and remains owned by the `birdnet-go` Compose project at `/opt/birdnet-go/compose.yml`.

Alloy, Node Exporter and Zabbix Agent 2 remain active.

The former TestServer workload estate must not be silently reintroduced. Komodo management does not change the host's deliberately narrow BirdNET-Go workload role.

## Home automation

`home-01` at `192.168.2.60` is the commissioned Home Assistant platform, VM204 on `PROXMOX`.

Validated live state on 17 September:

- Home Assistant OS 18.2;
- Home Assistant Core 2026.9.2;
- Supervisor 2026.09.2, healthy and supported;
- 2 vCPU, 4096 MiB RAM and 32 GiB `vm-ssd` disk;
- OVMF/q35;
- VirtIO networking with fixed MAC `02:00:00:00:02:04`;
- QEMU guest agent enabled and functional;
- `onboot=1`;
- `protection=1`;
- application HTTP endpoint on port 80 returned 200;
- unauthenticated `/api/` returned 401 as expected;
- both DNS resolvers return `home-01.jameshouse -> 192.168.2.60`;
- `http://home-01/` returned 200;
- native Home Assistant backup exists;
- manual Proxmox VM204 snapshot backup completed and passed compressed/VMA integrity checks;
- VM204 is included in the `PROXMOX` 02:15 nightly schedule.

Remaining closeout is external service monitoring, first unattended VM204 backup proof, deeper native/whole-VM recovery validation and any later radio/device-integration decision.

## Backup posture

The primary Proxmox guest-backup platform remains operationally important and the pre-cluster backup/restore evidence remains valid historical proof.

Current storage topology:

```text
backup host: media-01 .195
protocol: NFS v4.2/TCP
PROXMOX storage: media-backup-proxmox -> /srv/backup/pve-proxmox
Proxmox-2 storage: media-backup-proxmox-2 -> /srv/backup/pve-proxmox-2
legacy rollback storage: media-backup -> /srv/backup/pve
backup mode: snapshot
compression: zstd
retention target: keep-last=3
local tmpdir: /var/lib/vz/vzdump-tmp
```

Before cluster formation all seven then-production PVE guests had successful snapshot-backup evidence, CT103 had an isolated restore/boot proof, and Proxmox notification delivery through `mail-relay-01` was proven end to end.

Cluster formation changed the monitor VMID and later commissioning added VM203, CT104, CT105 and VM204. Historical schedule proof must therefore not be represented as proof of unattended execution for the complete current guest set.

Current post-cluster job selections are:

```text
PROXMOX .70
  VMIDs 100,102,104,105,200,201,204
  storage media-backup-proxmox
  schedule 02:15

Proxmox-2 .71
  VMIDs 101,103,202,203
  storage media-backup-proxmox-2
  schedule 03:15
```

Both job definitions are reconciled through IaC. The 17 September audit observed unattended CT105 output from the `PROXMOX` repository and unattended CT101, CT103, VM202 and VM203 output from the `Proxmox-2` repository. The displayed sample did not include CT104, so first unattended CT104 proof remains open. VM204 has manual snapshot/integrity proof and is scheduled; first unattended VM204 proof remains open.

Outstanding recovery gaps include:

- first unattended CT104 proof;
- first unattended VM204 scheduled backup proof;
- representative QEMU VM restore proof;
- application-consistent Nextcloud/PostgreSQL recovery;
- deeper Home Assistant restore proof;
- independent secondary copy;
- protection of `media-01` user media, BirdNET persistent state and controller recovery state.

The suspect WD 4 TB disk must not be the sole trusted backup copy.