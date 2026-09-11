# PROXMOX Current-State Audit

Original audit source: TestServer jump-box read-only audit of `192.168.2.70` on 2026-09-06.

Hardware update validated on 2026-09-11 after installation of the second memory module. The host booted successfully, Proxmox VE returned normally, and the upgraded memory was confirmed from both Linux and the Proxmox GUI.

Original audit report SHA256:

`a4cac78c251e804edbb92d824b9558db46535e0c5f205862a911ef0008654a02`

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
| Cluster | Standalone node |

## Compute

| Item | Current state |
|---|---|
| CPU | Intel Core i5-8500T @ 2.10 GHz |
| Cores / threads | 6 / 6 |
| Virtualization | VT-x |
| Installed RAM | 16 GB |
| RAM visible to Proxmox | 15.47 GiB |
| Linux-reported memory | 16,216,968 KiB |
| Available memory after reboot and guest startup | approximately 12.5 GiB |
| Swap | 7.6 GiB, unused at validation |

The 2026-09-11 memory upgrade doubled the host from approximately 8 GB to 16 GB. The previous RAM capacity gate is therefore cleared. Immediately after the upgrade the host was using approximately 2.97 GiB of 15.47 GiB, leaving substantial headroom for the current guest estate.

## Storage

### NVMe system disk

- WDC PC SN520 256 GB class NVMe.
- Proxmox root on LVM.
- Root filesystem: approximately 68 GiB.
- `local-lvm`: approximately 141.5 GiB thin pool.
- NVMe health at the original audit: no critical warning, 6% lifetime used, zero media errors.

### SATA VM SSD

- Kingston SA400S37 480 GB class SATA SSD.
- `vm-ssd`: approximately 424.6 GiB thin pool.
- SMART overall health at the original audit: PASSED.

### External 4 TB WD USB disk

Current cloud-storage POC candidate:

- model: `WDC WD40EZRX-00SPEB0`
- serial: `WD-WCC4E0670079`
- USB identity: `usb-WDC_WD40_EZRX-00SPEB0_133309270ED2-0:0`
- capacity: 4.00 TB / 3.64 TiB
- SMART overall health: PASSED
- reallocated sectors: 0
- current pending sectors: 0
- offline uncorrectable sectors: 2
- UDMA CRC errors: 10

The disk is suitable for continued proof-of-concept testing but must not be treated as the sole copy of important data. USB/UAS reset events were observed during destructive testing, so its bridge/cabling path also remains part of the storage risk assessment.

Storage capacity is currently strong and is not the limiting factor for the rebuild.

## Network

- Realtek RTL8111/8168-family 1 GbE NIC.
- Interface `nic0` is bridged through `vmbr0`.
- Link: 1000 Mb/s, full duplex, auto-negotiation enabled.
- Default gateway: `192.168.2.1`.
- Proxmox management address: `192.168.2.70/24`.
- Current bridge is untagged VLAN 1 only.

## Current guests

Validated from the Proxmox GUI after the 2026-09-11 RAM upgrade:

| ID | Guest | Type | Status |
|---:|---|---|---|
| 100 | `dns-02` | LXC | Running |
| 102 | `mail-relay-01` | LXC | Running |
| 200 | `cloud-01` | VM | Running |
| 201 | `sensor-01` | VM | Running |
| 9000 | `debian-13-cloud-template` | VM template | Stopped |
| 9001 | `debian-13-cloud-template-qga` | VM template | Stopped |

The former Zabbix workload recorded in the original 2026-09-06 audit is no longer part of the current guest inventory.

## Host services

- Proxmox management services are healthy.
- Prometheus node exporter is listening on 9100.
- Alloy is present with a localhost listener on 12345.
- Docker is **not** installed on the Proxmox host.

Docker should remain off the Proxmox host itself. Application containers should run inside explicitly provisioned guests.

## Backup posture

The original 2026-09-06 audit found no `/etc/pve/jobs.cfg` backup job.

This item should be revalidated separately before considering the backup/recovery work complete. Important application data must not rely solely on guest availability or the 4 TB POC disk.

## Thermals

Original audit values:

- PCH: approximately 39 C.
- CPU package: approximately 38 C.

No thermal concern was visible during the audit. A post-memory-upgrade thermal baseline can be captured during the next hardware audit.

## Capacity assessment

### Strong points

- Six physical CPU cores with VT-x.
- 16 GB installed RAM, with 15.47 GiB visible to Proxmox.
- Approximately 12.5 GiB available after the 2026-09-11 reboot and current guest startup.
- Large amount of SATA thin-pool capacity.
- Healthy internal NVMe and SATA storage according to the read-only health checks.
- Light current CPU load.
- Clean standalone Proxmox role with Docker absent from the host.

### Constraints

- 16 GB is now sufficient for the current estate but remains a finite resource; `cloud-01` and `sensor-01` should continue to be capacity-monitored as their workloads grow.
- The 4 TB USB disk is a POC/storage candidate, not a sole production copy of important data.
- Proxmox guest backup configuration still requires explicit revalidation and recovery testing.
- Single 1 GbE NIC and single-node design provide no infrastructure HA.

## Migration decision

**The Proxmox RAM remediation gate is complete.**

The previous 8 GB memory constraint has been removed. The host now meets the 16 GB minimum consolidation target identified in the original audit and has successfully booted with the current guest estate running.

Next infrastructure priorities are therefore no longer blocked by physical RAM. Continue to:

1. monitor host memory as `cloud-01` and `sensor-01` workloads grow;
2. define and test Proxmox guest backup/recovery;
3. keep Docker off the Proxmox host;
4. treat the current 4 TB USB disk as POC storage until the long-term storage design is funded and implemented;
5. re-run a focused hardware/capacity audit after major guest or storage changes.

## Status

Hardware audit: **COMPLETE**

RAM upgrade/remediation: **COMPLETE — 16 GB installed and validated 2026-09-11**

RAM capacity gate for current workload placement: **CLEARED**
