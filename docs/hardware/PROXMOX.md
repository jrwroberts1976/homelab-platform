<!-- estate-authority: IaC/inventory/estate.json -->
# PROXMOX — Current Hardware Record

**Status:** ACTIVE — `jameshouse-pve` CLUSTER NODE 1  
**Current-state review:** 6 October 2026  
**Identity/address authority:** `IaC/inventory/estate.json`

Earlier September hardware audits remain useful dated evidence. This page records the current operational state.

## Identity

| Item | Current state |
|---|---|
| Hostname | `PROXMOX` |
| Address | `192.168.2.70/24` |
| Hardware | HP ProDesk 400 G4 DM |
| OS | Debian GNU/Linux 13 (trixie) |
| Proxmox | pve-manager `9.2.21` |
| Running kernel | `7.0.14-20-pve` |
| Architecture | x86-64 |
| Cluster | `jameshouse-pve`, node ID 1 |
| QDevice | external QNetd on `admin-01` |

Latest PVE version/kernel evidence is from the controlled 5 October 2026 maintenance cycle.

## Compute

| Item | Current state |
|---|---|
| CPU | Intel Core i5-8500T @ 2.10 GHz |
| Cores / threads | 6 / 6 |
| Virtualization | VT-x |
| Installed RAM | 16 GB |
| RAM visible to Proxmox | approximately 15.47 GiB |
| Swap | approximately 7.6 GiB |

## Storage

### NVMe system disk

- WDC PC SN520 256 GB-class NVMe;
- Proxmox root on LVM;
- `local-lvm` used for node-local guest storage.

### SATA VM SSD

- Kingston SA400S37 480 GB-class SATA SSD;
- `vm-ssd` provides additional node-local VM storage.

### External 4 TB WD USB disk

The WD 4 TB USB disk remains **POC/risk storage only**. It is not the `cloud-01` production data disk and is not an approved sole backup copy. Historical health concerns remain documented in earlier hardware evidence.

## Cluster networking

Management:

```text
192.168.2.70/24
vmbr0 / normal LAN
gateway 192.168.2.1
```

Corosync:

```text
link0: 10.255.255.1/30 — preferred direct point-to-point interconnect
link1: 192.168.2.70    — management-LAN fallback
```

`admin-01` supplies the external QDevice vote. Validated steady state is two cluster nodes, three total votes, quorum two and QDevice present.

The actual node hostname is `PROXMOX`; “Proxmox-1” is only a human-friendly diagram label.

## Current guests

| ID | Guest | Type | State |
|---:|---|---|---|
| 100 | `dns-02` | LXC | running |
| 102 | `mail-relay-01` | LXC | running |
| 104 | `komodo-01` | LXC | running |
| 105 | `zabbix-01` | LXC | running |
| 200 | `cloud-01` | VM | running |
| 201 | `sensor-01` | VM | running |
| 204 | `home-01` | VM | running / protected |
| 9000 | Debian cloud template | VM template | stopped |
| 9001 | Debian/QGA template | VM template | stopped |

Production guest disks remain node-local. Cluster membership does not by itself provide automatic guest-data HA after loss of this node or its storage.

## Host services

Current platform services include:

- Proxmox cluster services / Corosync;
- `corosync-qdevice`;
- Chrony / NTP (`ntp-01.jameshouse`);
- Node Exporter;
- Grafana Alloy;
- Zabbix Agent 2.

Docker remains intentionally absent from the hypervisor. Application containers belong inside managed guests.

## Sensor relationship

`sensor-01` VM201 is operational with its dedicated passive capture interface. The HP ProCurve SPAN configuration mirrors ports 1–23 to switch port 24. The capture adapter is not a management or Corosync interface.

Older notes describing the capture NIC or SPAN change as future work are superseded.

## Backup posture

Primary node backup target:

```text
media-01:/srv/backup/pve-proxmox
storage: media-backup-proxmox
job: homelab-nightly-proxmox
schedule: 02:15
mode: snapshot
compression: zstd
retention: keep-last=3
guests: 100,102,104,105,200,201,204
```

The backup job is reconciled through IaC. CT105 unattended evidence has been observed; CT104 and VM204 first-unattended proof remain explicit evidence items in the current record. Manual/integrity evidence exists for additional guests as documented in the backup strategy.

A representative QEMU restore, application-consistent `cloud-01` recovery and an independent second copy remain open recovery goals.

## Monitoring and patching

The node is covered by Prometheus/Node Exporter, Grafana Alloy, Zabbix Agent 2 and centralized patch telemetry.

After the 5 October maintenance cycle:

- pending OS updates: 0;
- security updates pending: 0;
- reboot required: no;
- automatic reboot: disabled.

The controlled maintenance validation also confirmed cluster quorum/QDevice health and expected guest state.

## Current risks / boundaries

- node-local guest storage means no automatic storage HA;
- single main production LAN uplink remains a physical availability constraint;
- the 4 TB USB disk remains POC/risk storage;
- cluster link failover and controlled single-node quorum behaviour still deserve explicit test evidence;
- keep Docker/application workloads off the hypervisor.

## Status

Hardware record: **CURRENT — 6 OCTOBER 2026**  
Cluster role: **ACTIVE — NODE 1**  
PVE: **9.2.21**  
Kernel: **7.0.14-20-pve**  
Scheduled Proxmox backups: **ACTIVE**  
Sensor SPAN path: **OPERATIONAL**
