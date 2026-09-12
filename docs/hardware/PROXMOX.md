# PROXMOX — Current Hardware Record

Original audit source: TestServer jump-box read-only audit of `192.168.2.70` on 6 September 2026.  
RAM update validated: 11 September 2026.  
Current storage/backup/network review: 12 September 2026.

The original TestServer audit provenance is retained as historical evidence; TestServer itself is now a retired identity.

## Identity

| Item | Current state |
|---|---|
| Hostname | `PROXMOX` |
| Address | `192.168.2.70/24` |
| Hardware | HP ProDesk 400 G4 DM |
| OS | Debian GNU/Linux 13 (trixie) |
| Proxmox | VE 9.2.11 / pve-manager 9.2.11 |
| Kernel | 7.0.14-15-pve |
| Architecture | x86-64 |
| Cluster | Standalone by design |

## Compute

| Item | Current state |
|---|---|
| CPU | Intel Core i5-8500T @ 2.10 GHz |
| Cores / threads | 6 / 6 |
| Virtualization | VT-x |
| Installed RAM | 16 GB |
| RAM visible to Proxmox | approximately 15.47 GiB |
| Swap | approximately 7.6 GiB |

The 11 September memory upgrade doubled the host from approximately 8 GB to 16 GB and cleared the previous capacity gate for the current guest set.

## Storage

### NVMe system disk

- WDC PC SN520 256 GB-class NVMe;
- Proxmox root on LVM;
- root filesystem approximately 68 GiB;
- `local-lvm` approximately 141.5 GiB thin pool;
- original audit showed no NVMe critical warning, low lifetime usage and zero media errors.

### SATA VM SSD

- Kingston SA400S37 480 GB-class SATA SSD;
- `vm-ssd` approximately 424.6 GiB thin pool;
- SMART health passed in the original audit.

### External 4 TB WD USB disk

Device:

```text
WDC WD40EZRX-00SPEB0
~4 TB / 3.64 TiB
```

Current role: **blank/unallocated/unmounted POC/risk storage only**.

It is **not**:

- the `cloud-01` production data disk;
- a mounted backup repository;
- an approved sole copy of important data.

Current health evidence:

- SMART overall: PASS;
- reallocated sectors: 0;
- current pending sectors: 0;
- offline uncorrectable sectors: 2;
- UDMA CRC errors: 10;
- recent extended self-test recorded as aborted by host before completion;
- historical USB/UAS reset events remain part of the risk assessment.

The disk may be useful for controlled testing, but production use requires a separate reviewed storage decision.

## Network

- Realtek RTL8111/8168-family 1 GbE NIC;
- management/guest bridge through `vmbr0`;
- address `192.168.2.70/24`;
- default gateway `192.168.2.1`;
- untagged VLAN 1 in the current design;
- HP ProCurve switch port **21** validated as the current physical uplink;
- host MAC `80:E8:2C:1C:55:D2`;
- switch link observed at 1 Gbps full duplex.

Guest bridge MACs are also learned on port 21.

## Current guests

Validated current placement:

| ID | Guest | Type | Status |
|---:|---|---|---|
| 100 | `dns-02` | LXC | running |
| 102 | `mail-relay-01` | LXC | running |
| 200 | `cloud-01` | VM | running |
| 201 | `sensor-01` | VM | running |
| 9000 | Debian template | VM template | stopped |
| 9001 | Debian/QGA template | VM template | stopped |

The former Zabbix workload from the original audit is no longer part of the current guest inventory.

## Host services

Current validated platform services include:

- Proxmox management services healthy;
- Node Exporter active on TCP/9100;
- Chrony active as the primary LAN NTP endpoint;
- Docker not installed on the hypervisor.

Docker should remain off the Proxmox host itself. Application containers belong inside explicitly provisioned guests.

## Time service

`PROXMOX` provides:

```text
ntp-01.jameshouse -> 192.168.2.70
```

Direct NTP validation from `admin-01` succeeded on 12 September 2026.

## Sensor relationship

`sensor-01` VM 201 is live but has no dedicated capture NIC yet.

Future design:

- dedicated USB Ethernet adapter attached to `PROXMOX`;
- direct USB passthrough into `sensor-01`;
- switch port 24 repurposed as the SPAN destination after the physical network is repatched;
- capture interface has no management IP/route.

Do not add the future capture adapter to `vmbr0`.

## Backup posture

The 12 September audit revalidated that this node has **zero scheduled Proxmox guest backup jobs**.

There is no active PBS server in the estate and the 4 TB WD disk is not an active backup repository.

Backup/recovery remains one of the largest platform gaps. See:

```text
docs/architecture/BACKUP-STRATEGY.md
```

## Monitoring

Current monitoring includes:

- ICMP probe;
- Proxmox HTTPS probe on TCP/8006;
- Node Exporter on TCP/9100.

These were healthy during the latest monitoring audit.

## Capacity assessment

### Strong points

- six physical CPU cores with VT-x;
- 16 GB installed RAM;
- internal NVMe plus large SATA VM thin pool;
- current guest estate running successfully;
- clean hypervisor role with Docker absent;
- current monitoring and NTP service healthy.

### Constraints / risks

- 16 GB is sufficient for the current estate but finite;
- `cloud-01` and future sensor capture/logging should remain capacity-monitored;
- single 1 GbE production NIC means no host network HA;
- external 4 TB USB disk is risk/POC-only;
- no scheduled guest backup coverage or proven restore path;
- future capture NIC work must be isolated from management networking.

## Current priorities

1. preserve hypervisor stability and keep Docker off-host;
2. implement and restore-test backup/recovery;
3. monitor capacity as `cloud-01` and `sensor-01` grow;
4. install/validate the dedicated sensor USB capture NIC only when the physical repatch/SPAN change is ready;
5. retain the 4 TB WD disk as POC/risk storage unless a later review explicitly approves another role.

## Status

Hardware audit: **CURRENT**  
RAM remediation: **COMPLETE — 16 GB**  
Current workload capacity gate: **CLEARED**  
Scheduled Proxmox backups: **NONE**  
4 TB WD production role: **NONE / POC-RISK ONLY**
