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
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / SSH jump / IaC controller / Corosync QNetd host | ACTIVE |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT 100 on `PROXMOX` | ACTIVE |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT 101 on `Proxmox-2` | ACTIVE |
| `monitor-01` | `192.168.2.52` | Prometheus, Grafana, Alertmanager, Blackbox, Loki and router-log ingestion, VM 202 on `Proxmox-2` | ACTIVE |
| `cloud-01` | `192.168.2.53` | Production Nextcloud/PostgreSQL/Redis, VM 200 on `PROXMOX` | ACTIVE |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix SMTP relay, CT 102 on `PROXMOX` | ACTIVE |
| `sensor-01` | `192.168.2.55` | Active Suricata/Zeek passive network sensor, VM 201 on `PROXMOX` | ACTIVE — CAPTURE OPERATIONAL |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT 103 on `Proxmox-2` | HOST ACTIVE — CLOUDFLARED NOT DEPLOYED |
| `PROXMOX` | `192.168.2.70` | Proxmox VE cluster node 1 / cluster anchor | ACTIVE — `jameshouse-pve` MEMBER |
| `Proxmox-2` | `192.168.2.71` | Proxmox VE cluster node 2 / Network Host Collector host | ACTIVE — `jameshouse-pve` MEMBER |
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

The former standalone `monitor-01` VMID `200` was changed to cluster VMID `202`, eliminating the pre-cluster duplicate-ID conflict with `cloud-01`.

### Storage and HA boundary

Production guest disks remain on node-local `local-lvm` storage.

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

Native Alloy is active on `monitor-01`. Router syslog continues to arrive through rsyslog on UDP/5514, is retained under `/var/log/homelab/router/rt-ac86u.log`, and is shipped to Loki through Alloy.

The broader Alloy baseline is deployed across the current managed estate.

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

Before cluster formation all seven production PVE guests had successful snapshot-backup evidence, CT103 had an isolated restore/boot proof, and Proxmox notification delivery through `mail-relay-01` was proven end to end.

Cluster formation changed the monitor VMID and the final workload placement. The old standalone schedule proof must therefore not be represented as final cluster-era proof.

Expected post-cluster job selections are:

```text
PROXMOX .70
  VMIDs 100,102,200,201
  storage media-backup-proxmox

Proxmox-2 .71
  VMIDs 101,103,202
  storage media-backup-proxmox-2
```

The backup-schedule IaC and live job definitions need explicit post-cluster reconciliation to VM202, followed by fresh backup proof and an unattended successful cycle.

Outstanding recovery gaps include:

- fresh cluster-era backup proof for VM202 and the final `.71` placement;
- representative QEMU VM restore proof;
- application-consistent Nextcloud/PostgreSQL recovery;
- independent secondary copy;
- protection of `media-01` user media, BirdNET persistent state and controller recovery state.

The suspect WD 4 TB disk must not be the sole trusted backup copy.

See `docs/architecture/BACKUP-STRATEGY.md` and `production docs/PROXMOX-BACKUP-RECOVERY.md`.

## Migration rollback evidence

The cluster migration deliberately retained the previous `.71` local disks under non-conflicting names:

```text
precluster-20260914-vm-101-disk-0
precluster-20260914-vm-103-disk-0
precluster-20260914-vm-200-cloudinit
precluster-20260914-vm-200-disk-0
```

These LVs are not active guest storage. They remain temporary rollback evidence until fresh cluster-era backups are validated.

Additional pre-cluster guest/storage/job configuration and backup evidence is also retained. Cleanup must be deliberate rather than opportunistic.

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

The package-update backlog identified by the 14 September audit was processed through the controlled patch workflow on 14 September 2026.

The active estate completed the cycle with no known remaining package backlog from that audit and no required reboots. Hosts requiring controlled restart were validated after boot, including `docker-01`, `media-01` and both Proxmox nodes.

The detailed maintenance evidence is recorded in [`PATCH-CYCLE-CLOSEOUT-2026-09-14.md`](PATCH-CYCLE-CLOSEOUT-2026-09-14.md).

Future updates remain operational lifecycle work and must continue through the controlled patch workflow.

## Remaining current-state work

Major outstanding work now includes:

- reconcile backup IaC/live schedules with cluster placement and VM202;
- create fresh cluster-era backup evidence and observe an unattended post-cluster cycle;
- prove a representative QEMU restore and application-consistent `cloud-01` recovery;
- establish an independent second backup copy and non-Proxmox data protection;
- test Corosync link0 loss and link1 fallback in a controlled manner;
- test single-node maintenance/quorum behaviour with QDevice available;
- decide whether local-storage/manual recovery is sufficient or whether replication/shared storage and HA are justified;
- remove retained pre-cluster rollback LVs only after fresh backup confidence is explicit;
- update remaining IaC comments/runbooks that still describe the PVE hosts as standalone;
- deploy `edge-01` Cloudflare Tunnel only when approved;
- refresh the physical switch/router port map after SPAN activation;
- complete remaining switch/router hardening decisions;
- continue service-specific observability and recovery documentation.

Already validated services must not be rolled backwards merely to match older documentation.
