<!-- estate-authority: IaC/inventory/estate.json -->
# Proxmox-2 — Current Hardware Record

**Status:** ACTIVE — `jameshouse-pve` CLUSTER NODE 2  
**Current-state review:** 6 October 2026  
**Identity/address authority:** `IaC/inventory/estate.json`

Earlier September hardware audits remain useful dated evidence. This page records the current operational state.

## Identity

| Item | Current state |
|---|---|
| Hostname | `Proxmox-2` |
| Address | `192.168.2.71/24` |
| Manufacturer | ASUSTeK COMPUTER INC. |
| Model | ZenBook UX482EAR |
| Chassis | Laptop |
| OS | Debian GNU/Linux 13 (trixie) |
| Proxmox | pve-manager `9.2.21` |
| Running kernel | `7.0.14-20-pve` |
| Architecture | x86_64 |
| Cluster | `jameshouse-pve`, node ID 2 |
| QDevice | external QNetd on `admin-01` |

Latest PVE version/kernel evidence is from the controlled 5 October 2026 maintenance cycle.

## Compute

| Item | Current state |
|---|---|
| CPU | 11th Gen Intel Core i5-1155G7 |
| Physical cores | 4 |
| Logical CPUs | 8 |
| RAM | approximately 15 GiB usable |
| Swap | 8 GiB |

## Storage

Physical system device:

- SK hynix HFM512GD3JX013N NVMe;
- `local` and `local-lvm` active;
- production guest disks remain node-local.

Historical pre-cluster rollback volumes are retained only where separately documented and are not active guest disks.

## Cluster networking

Management:

```text
192.168.2.71/24
normal LAN / Proxmox bridge
```

Corosync:

```text
link0: 10.255.255.2/30 — preferred direct point-to-point interconnect
link1: 192.168.2.71    — management-LAN fallback
```

`admin-01` supplies the external QDevice vote. Validated steady state is two cluster nodes, three total votes, quorum two and QDevice present.

## Current guests

| Type | ID | Guest | State |
|---|---:|---|---|
| LXC | 101 | `dns-01` | running |
| LXC | 103 | `edge-01` | running |
| VM | 202 | `monitor-01` | running |
| VM | 203 | `greenbone-01` | running / protected |

`monitor-01` is VM202. The older VM200 reference is obsolete.

Production guest disks remain node-local. Cluster membership does not by itself provide automatic guest-data HA after loss of this node or its storage.

## Host services

Current platform services include:

- Proxmox cluster services / Corosync;
- `corosync-qdevice`;
- Chrony / NTP (`ntp-02.jameshouse`);
- Node Exporter;
- Grafana Alloy;
- Zabbix Agent 2.

Docker/application workloads should remain inside explicit guests rather than on the hypervisor.

## Network-discovery relationship

`Proxmox-2` is the **former** Network Host Collector source.

The production discovery/identification owner moved to `monitor-01` on 27 September 2026. The source-side collector/enricher/OS-evidence/guest-refresh discovery timers are disabled/inactive. Retained source files and protected snapshots are rollback/history evidence only.

Do not re-enable source scanning while `monitor-01` owns production discovery.

## Backup posture

Primary node backup target:

```text
media-01:/srv/backup/pve-proxmox-2
storage: media-backup-proxmox-2
job: homelab-nightly-proxmox-2
schedule: 03:15
mode: snapshot
compression: zstd
retention: keep-last=3
guests: 101,103,202,203
```

The backup job is reconciled through IaC. Unattended evidence has been observed for CT101, CT103, VM202 and VM203. VM203 also has manual snapshot/integrity proof and Proxmox protection enabled.

## Monitoring and patching

The node is covered by Prometheus/Node Exporter, Grafana Alloy, Zabbix Agent 2 and centralized patch telemetry.

After the 5 October maintenance cycle:

- pending OS updates: 0;
- security updates pending: 0;
- reboot required: no;
- automatic reboot: disabled.

The maintenance validation confirmed expected guest state, no failed systemd units, Alloy/Zabbix health and cluster quorum/QDevice health.

## Current risks / boundaries

- node-local guest storage means no automatic storage HA;
- the laptop platform is a non-server chassis and should remain capacity/thermal monitored;
- retained pre-cluster rollback volumes should be removed only after explicit backup/recovery confidence;
- cluster link failover and controlled single-node quorum behaviour still deserve explicit test evidence;
- former discovery state is rollback evidence, not an active service role.

## Status

Hardware record: **CURRENT — 6 OCTOBER 2026**  
Cluster role: **ACTIVE — NODE 2**  
PVE: **9.2.21**  
Kernel: **7.0.14-20-pve**  
Grafana Alloy: **ACTIVE**  
Scheduled Proxmox backups: **ACTIVE**  
Network discovery: **FORMER SOURCE / TIMERS DISABLED**
