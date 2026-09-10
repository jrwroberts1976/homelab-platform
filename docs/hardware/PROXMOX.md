# PROXMOX Current-State Audit

**Current-state refresh:** 10 September 2026  
**Address:** `192.168.2.70`  
**Role:** primary standalone Proxmox VE host / `ntp-01`

This document began as the 6 September hardware audit. The current-state sections below supersede the original workload-placement conclusions while retaining the useful hardware evidence.

## Identity

| Item | Current state |
|---|---|
| Hostname | `PROXMOX` |
| Address | `192.168.2.70/24` |
| Hardware | HP ProDesk 400 G4 DM |
| OS | Debian GNU/Linux 13 (trixie) |
| Proxmox | pve-manager 9.2.11 |
| Kernel | `7.0.14-15-pve` at latest validation |
| Architecture | x86-64 |
| Cluster | Standalone / no active two-node cluster |
| Normal controller | `admin-01` / `192.168.2.48` |

## Compute

| Item | Current state |
|---|---|
| CPU | Intel Core i5-8500T @ 2.10 GHz |
| Cores / threads | 6 / 6 |
| Virtualization | VT-x |
| RAM | approximately 7.6 GiB |
| Swap | approximately 7.6 GiB |

A 10 September edge-hosting preflight observed approximately 2.3 GiB memory available while the current guest set was running. This host therefore remains the tighter Proxmox node for RAM headroom.

## Storage

### NVMe system disk

- WDC PC SN520 256 GB class NVMe.
- Proxmox root on LVM.
- Root filesystem approximately 68 GiB with roughly 51 GiB free at latest check.
- `local-lvm` approximately 141.5 GiB thin pool and currently effectively unused.
- Historical NVMe health audit reported no critical warning or media errors.

### SATA VM SSD

- Kingston SA400S37 480 GB class SATA SSD.
- `vm-ssd` approximately 424.6 GiB thin pool.
- Latest usage approximately 2.36%.
- Historical SMART overall health: PASSED.

### WD 4 TB USB disk

A WDC WD40EZRX-00SPEB0 4 TB disk is attached as `/dev/sdb`.

Latest status on 10 September 2026:

- SMART overall-health result: PASSED;
- current pending sectors reduced to zero from earlier non-zero evidence;
- offline uncorrectable count remains 2;
- UDMA CRC error count 10;
- temperature approximately 26 C;
- SMART error log reported no entries;
- extended/long self-test is still in progress and must not be interrupted or restarted.

Until the long test completes and the final counters are reviewed, this disk may be useful working storage but is **not** approved as the sole copy of irreplaceable data.

## Network

- Realtek RTL8111/8168-family 1 GbE NIC.
- Interface is bridged through `vmbr0`.
- Management address: `192.168.2.70/24`.
- Default gateway: `192.168.2.1`.
- LAN DNS: `192.168.2.51`, `192.168.2.50`.
- Current bridge is on the main untagged LAN.

## Current guests

### Running QEMU VMs

| VMID | Name | Address | Role |
|---:|---|---:|---|
| 200 | `cloud-01` | `192.168.2.53` | Private cloud/data service platform |
| 201 | `sensor-01` | `192.168.2.55` | Passive network/security sensor platform |

### Running LXC containers

| CTID | Name | Address | Role |
|---:|---|---:|---|
| 100 | `dns-02` | `192.168.2.50` | Secondary Pi-hole + Unbound resolver |
| 102 | `mail-relay-01` | `192.168.2.54` | Internal SMTP relay |

### Templates

- VM9000 `debian-13-cloud-template` — stopped.
- VM9001 `debian-13-cloud-template-qga` — stopped.

The old `zabbix-lxc-01` workload recorded in the original audit is no longer the current placement authority and must not be reintroduced from this historical document.

## Host services

- Proxmox management services are operational.
- Node-exporter/monitoring prerequisites are managed separately from guest workloads.
- Chrony provides the `ntp-01` LAN time-service role.
- Docker is not part of the approved hypervisor workload model and should remain off the host itself.

## Backup posture

The original audit found no configured Proxmox guest-backup job. Guest backup/restore remains a documentation and operational priority even though multiple production guests are now running.

Required next work:

1. define the authoritative guest-backup destination/policy;
2. prove at least one representative guest restore;
3. document node-loss recovery and alternate-node rebuild paths;
4. finish the WD 4 TB SMART investigation before giving that disk any critical backup role.

## Thermals

The original read-only audit observed CPU/package temperatures around the high 30s C with no thermal concern. Re-check under sustained workload if guest density increases materially.

## Current assessment

Strengths:

- six physical CPU cores;
- healthy/ample SSD capacity for the current guest set;
- simple standalone Proxmox role;
- explicit VM/LXC workload ownership;
- Docker kept off the hypervisor.

Constraints:

- 7.6 GiB RAM gives less headroom than `Proxmox-2`;
- no Proxmox HA because the hosts are intentionally standalone;
- guest backup/restore evidence is incomplete;
- WD 4 TB disk still has historical media-error evidence under investigation.

## Status

Hardware audit: **COMPLETE**  
Current workload placement: **ACTIVE / DOCUMENTED**  
Storage/recovery follow-up: **IN PROGRESS**

Historical audit source: TestServer read-only audit of `192.168.2.70` on 6 September 2026. Historical report SHA256: `a4cac78c251e804edbb92d824b9558db46535e0c5f205862a911ef0008654a02`.
