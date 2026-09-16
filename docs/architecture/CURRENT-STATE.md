<!-- estate-authority: IaC/inventory/estate.json -->
# Current-State Architecture

This document records the validated current homelab estate as of 16 September 2026.

It describes what is live now. Historical host identities and earlier migration assumptions remain useful evidence, but they are not current deployment authority.

## Authority model

`homelab-platform/IaC/` is the authoritative location for infrastructure and service configuration that has been migrated and validated there.

Legacy repositories may remain useful reference sources for areas not yet migrated. They must not be treated as current authority after their workload or configuration has been explicitly migrated and validated in `homelab-platform`.

A detailed reconciliation trail for the 14 September estate snapshot is recorded in `docs/architecture/ESTATE-AUDIT-2026-09-14.md`. The post-commissioning document audit on 16 September is recorded in `docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-09-16.md`.

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
| `zabbix-01` | `192.168.2.59` | Zabbix monitoring platform, CT 105 on `PROXMOX` | ACTIVE — PLATFORM + 15-HOST AGENT ESTATE REPORTING; MANUAL BACKUP/RESTORE PROVEN |
| `PROXMOX` | `192.168.2.70` | Proxmox VE cluster node 1 / cluster anchor | ACTIVE — `jameshouse-pve` MEMBER |
| `Proxmox-2` | `192.168.2.71` | Proxmox VE cluster node 2 / Network Host Collector host | ACTIVE — `jameshouse-pve` MEMBER |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target | ACTIVE |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host | ACTIVE |
| ASUS RT-AC86U | `192.168.2.1` | Router / DHCP / AiMesh controller / OpenVPN remote-access endpoint | ACTIVE |
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

The two PVE hosts now form the production two-node cluster:

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

Both links reported connected from both nodes after cluster formation.

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

Validated cluster quorum:

```text
Nodes:            2
Expected votes:   3
Total votes:      3
Quorum:           2
Flags:            Quorate Qdevice
```

`corosync-qdevice` is active on both PVE nodes. QNetd listens on TCP/5403 and sees both cluster clients.

This protects cluster quorum during a single PVE-node loss while QDevice remains reachable. It does not make node-local guest disks automatically available on the surviving hypervisor.

### `PROXMOX` — `192.168.2.70`

Validated after the 14 September patch and cluster work:

- Debian 13 base;
- Proxmox VE / pve-manager 9.2.20;
- running kernel `7.0.14-17-pve`;
- node ID 1;
- Corosync active;
- `pve-cluster` active;
- QDevice client active;
- Chrony active;
- Node Exporter active;
- Alloy active.

Live workload placement:

| Type | ID | Name | State |
|---|---:|---|---|
| LXC | 100 | `dns-02` | running |
| LXC | 102 | `mail-relay-01` | running |
| LXC | 104 | `komodo-01` | running |
| LXC | 105 | `zabbix-01` | running |
| VM | 200 | `cloud-01` | running |
| VM | 201 | `sensor-01` | running |
| VM | 9000 | Debian cloud template | stopped |
| VM | 9001 | Debian cloud template with QGA | stopped |

An obsolete earlier Network Host Collector installation was removed from this node. The current collector belongs on `Proxmox-2` only.

### `Proxmox-2` — `192.168.2.71`

Validated after the 14 September patch and cluster work:

- Debian 13 base;
- Proxmox VE / pve-manager 9.2.20;
- running kernel `7.0.14-17-pve`;
- node ID 2;
- Corosync active;
- `pve-cluster` active;
- QDevice client active;
- Chrony active;
- Node Exporter active;
- Alloy active;
- active Network Host Collector with inventory under `/var/lib/homelab-network-hosts/inventory.json`.

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

Managed local-record parity remains authoritative through IaC. `192.168.2.48` is `admin-01` and must not be treated as a DNS resolver.

After CT101 migrated back to `Proxmox-2`, Pi-hole and Unbound were active, no failed units were present, DNS returned `NOERROR`, and network reachability was clean.

## Zabbix monitoring

`zabbix-01` is the active dedicated Zabbix monitoring platform.

Validated state on 16 September 2026:

- Debian 13 unprivileged LXC at `192.168.2.59`;
- CTID 105 on `PROXMOX`;
- Zabbix API version `7.0.30` observed during host onboarding;
- PostgreSQL and TimescaleDB active;
- Zabbix Server active;
- Zabbix Agent 2 active and enabled locally;
- Agent 2 listens on TCP/10050;
- Nginx and PHP-FPM active;
- frontend HTTP health returned 200;
- whole-container manual backup integrity proven;
- application logical backup and restore validation proven;
- CT105 is included in the IaC/live `homelab-nightly-proxmox` 02:15 backup selection;
- the first unattended 02:15 cycle including CT105 remains to be observed;
- the pre-platform rollback snapshot remains retained;
- the `zabbix_agents` inventory group contains all 15 managed Linux systems;
- Zabbix host group `Homelab/Linux` contains matching host objects linked to `Linux by Zabbix agent active`;
- all 15 host objects were observed reporting on 16 September 2026;
- active-agent hostnames match the Ansible inventory identities.

The first estate-wide Agent2 play encountered an `admin-01` sudo/become-password issue, but that host subsequently reported to Zabbix. This is an Ansible privilege-escalation housekeeping item rather than an active Zabbix reporting gap.

## Monitoring and logging

`monitor-01` is the central metrics, alerting and logging platform and now runs as VM202 on `Proxmox-2`.

Validated running containers include:

| Service | Image/version | State |
|---|---|---|
| Prometheus | `prom/prometheus:v3.14.0` | running |
| Grafana | `grafana/grafana:13.2.1` | running |
| Alertmanager | `prom/alertmanager:v0.34.0` | running |
| Blackbox Exporter | `prom/blackbox-exporter:v0.28.0` | running |
| Loki | `grafana/loki:3.7.7` | running |

Native Alloy is active on `monitor-01`. Router syslog continues to arrive through rsyslog on UDP/5514, is retained under `/var/log/homelab/router/rt-ac86u.log`, and is shipped to Loki through the dedicated router Alloy role.

On 16 September 2026 the live router log contained OpenVPN authentication, tunnel-establishment, client-address and disconnect/error messages from an external test session, and the live Alloy configuration was verified to tail that router log.

The broader Alloy baseline is deployed across the current managed estate.

## Remote access VPN

The selected remote-access endpoint is the native OpenVPN server on the ASUS RT-AC86U at `192.168.2.1`.

Validated on 16 September 2026:

- OpenVPN Server 1 reported running;
- an external client successfully completed username/password authentication;
- the tunnel was established and a `10.8.0.3` client address was allocated during the observed session;
- the router pushed the internal route `192.168.2.0/24`;
- the router pushed DNS servers `192.168.2.51` and `192.168.2.50`;
- the observed session used UDP, TLS 1.3 and AES-256-GCM;
- the VPN events were retained in router syslog on `monitor-01` and are part of the Alloy-to-Loki stream.

The former dedicated `vpn-01` WireGuard design and exploratory WireGuard-on-`docker-01` path are not current production architecture. No VPN VMID or separate LAN address is allocated.

Remaining acceptance work is explicit end-to-end access to intended internal management services from outside the LAN, internal DNS proof, DDNS endpoint validation and router-reset/replacement recovery/client re-enrolment documentation.

## Komodo management host

`komodo-01` is the active Komodo container-management control plane.

Validated state on 16 September 2026:

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
- Komodo Core `2.3.3` is running and the web UI login is validated;
- Core is currently LAN/VPN administered over `http://192.168.2.58:9120`;
- the Core deployment has no Docker socket mount and no local Periphery service;
- a Komodo application backup was created in `/var/backups/komodo/2026-09-16_10-33-04` and all 22 gzip collection files passed integrity validation;
- that backup was restored into the isolated `komodo_restore_validation` database and the populated `User`, `Tag`, `Procedure` and `Update` collections matched the live backup baseline;
- the live `komodo` database remained unchanged during restore validation and the temporary restore database was removed afterward;
- CT104 manual Proxmox snapshot backup completed successfully on `media-backup-proxmox` and archive integrity/structure checks passed;
- CT104 is included in the IaC/live `homelab-nightly-proxmox` 02:15 backup selection;
- the first unattended 02:15 cycle including CT104 remains to be observed;
- Proxmox protection remains disabled pending deliberate acceptance.

The Proxmox `overlay` filesystem module is loaded and persisted, and its visibility inside CT104 is validated. Komodo application backup, isolated recovery and manual whole-container backup are proven. Remaining platform work is the first unattended backup proof, protection decision, HTTPS hardening and deliberate Periphery/managed-host onboarding.

## Production cloud service

`cloud-01` is a live production Nextcloud platform.

Validated state:

- Debian 13 VM on `PROXMOX`;
- VMID 200;
- dedicated 200 GiB ext4 data disk at `/srv/cloud-01-data`;
- Docker/Compose active;
- Nextcloud `34.0.3-apache` app and cron containers running;
- PostgreSQL `18.6-alpine` healthy;
- Redis `8.2.9-alpine` healthy;
- application endpoint `192.168.2.53:8080`;
- Node Exporter and Alloy active;
- zero failed systemd units in the last validation.

A complete VM-level snapshot backup is proven on `media-backup-proxmox`. Application-consistent Nextcloud/PostgreSQL recovery remains unproven and is still a separate requirement.

## Vulnerability scanning

`greenbone-01` is the dedicated active vulnerability-scanning platform.

Validated state on 16 September 2026:

- Debian 13 VM at `192.168.2.57`;
- VMID 203 on `Proxmox-2`;
- 4 vCPU, 8192 MiB RAM and 80 GiB `local-lvm` disk;
- Greenbone Community Containers deployed through Docker Compose;
- HTTPS exposed to the LAN only on `192.168.2.57:443`;
- Greenbone internal web/GMP listeners remain loopback-bound where intended;
- feed readiness `4/4`;
- OpenVAS VT feed version `202609140600`;
- 187151 vulnerability tests loaded during commissioning;
- Node Exporter and Alloy active;
- Greenbone Docker logs proven in Loki;
- VM-level Proxmox protection enabled.

The controlled commissioning self-scan of `greenbone-01` completed with no Critical, High or Medium results. It produced one Low result at severity 2.1 for ICMP Timestamp Reply Information Disclosure and nine informational/log results. The ICMP timestamp item is tracked as a separate hardening follow-up; it did not block scanner commissioning.

VM203 has two manual snapshot backup archives on `media-backup-proxmox-2`; archive integrity was proven with `zstd -t`. The nightly `Proxmox-2` job is IaC-managed at 03:15 and now selects `101,103,202,203`. VM203 is protected in Proxmox and the temporary `pre-greenbone-stack` commissioning snapshot has been removed.

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
- Node Exporter and Alloy active;
- zero failed systemd units in the last validation.

The capture adapter remains dedicated to passive monitoring and must not be repurposed as a normal routed management or Corosync interface.

## Network host discovery

The current Network Host Collector is deployed on `Proxmox-2` only.

Validated state includes the five-minute discovery collector, enrichment timer, one-time deep profiler for new hosts, current inventory under `/var/lib/homelab-network-hosts/inventory.json`, first-seen notification and Git-managed Grafana Network Hosts dashboards.

The obsolete collector installation on `PROXMOX` was removed.

## Edge host

`edge-01` is a running Debian 13 LXC, CT103 on `Proxmox-2`, at `192.168.2.56`.

No `cloudflared` workload is deployed. Node Exporter and Alloy are active. The host remains reserved for a future Cloudflare Tunnel connector.

## Mail relay

`mail-relay-01` is CT102 on `PROXMOX` at `192.168.2.54`.

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
- Alloy active;
- zero failed systemd units in the last validation.

Current backup exports:

```text
/srv/backup/pve-proxmox
  client: 192.168.2.70

/srv/backup/pve-proxmox-2
  client: 192.168.2.71

/srv/backup/pve
  legacy rollback namespace retained temporarily
```

Cluster storage is node-scoped so `.70` uses `media-backup-proxmox` and `.71` uses `media-backup-proxmox-2`. The shared `media-backup` namespace remains available as historical/rollback storage.

The intended nftables policy remains a separate follow-up until deliberately deployed and remotely validated.

## Administration host

`admin-01` at `192.168.2.48` is the normal controller for homelab administration and IaC.

It is also the QNetd host for `jameshouse-pve` and listens on TCP/5403 for the two PVE QDevice clients.

Current state includes Alloy, Node Exporter and zero failed systemd units after the inapplicable smartd daemon was disabled/stopped on the SD-card-based Raspberry Pi.

Production Ansible should normally be launched from the checked-out `homelab-platform` repository on this host.

## Docker / BirdNET host

`docker-01` at `192.168.2.220` remains the dedicated Raspberry Pi 4 BirdNET-Go host.

Validated state includes Debian 13/aarch64, Docker active, one intended BirdNET-Go application container, Node Exporter and Alloy active, and zero failed systemd units.

The former TestServer workload estate must not be silently reintroduced.

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

Cluster formation changed the monitor VMID and later commissioning added VM203, CT104 and CT105. Historical schedule proof must therefore not be represented as proof of unattended execution for the complete current guest set.

Current post-cluster job selections are:

```text
PROXMOX .70
  VMIDs 100,102,104,105,200,201
  storage media-backup-proxmox
  schedule 02:15

Proxmox-2 .71
  VMIDs 101,103,202,203
  storage media-backup-proxmox-2
  schedule 03:15
```

Both job definitions are reconciled through IaC. CT104 and CT105 have successful manual snapshot/integrity proof and are included in the 02:15 job; their first unattended scheduled run remains to be observed. The unattended 03:15 cycle on 16 September succeeded for `101,103,202`; VM203 has separate manual snapshot/integrity proof and the first unattended cycle including VM203 remains to be observed.

Outstanding recovery gaps include:

- first unattended `PROXMOX` scheduled cycle including CT104 and CT105;
- first unattended `Proxmox-2` scheduled cycle including VM203;
- representative QEMU VM restore proof;
- application-consistent Nextcloud/PostgreSQL recovery;
- independent secondary copy;
- protection of `media-01` user media, BirdNET persistent state and controller recovery state.

The suspect WD 4 TB disk must not be the sole trusted backup copy.
