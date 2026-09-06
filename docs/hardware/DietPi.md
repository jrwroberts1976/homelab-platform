# DietPi Current-State Audit

Audit date: 2026-09-06  
Legacy hostname: `DietPi`  
Address: `192.168.2.48`  
Login account observed: `dietpi`  
Audit method: repository-controlled `scripts/audit-linux-host.sh`, copied from a verified host and executed locally as root in read-only mode.

Audit artifact on DietPi:

`/var/tmp/DietPi-audit-20260906T074300Z.txt`

SHA256:

`d2252d3613d55359fdfa83616eb5f6fed3594fa9b9e73d08ff285b128a170619`

## Identity

| Item | Current state |
|---|---|
| Hardware | Raspberry Pi 3 Model B Rev 1.2 |
| DietPi release | 10.6.2 |
| OS | Debian GNU/Linux 13 (trixie) |
| Kernel | 6.18.39+rpt-rpi-v8 |
| Architecture | arm64 / aarch64 |
| Legacy hostname | `DietPi` |

The current hostname is a discovery identifier only. It does not determine the host's future role.

`hostnamectl` could not use the system bus on this DietPi installation, but hostname, OS, kernel and architecture were captured independently.

## CPU

| Item | Current state |
|---|---|
| CPU | ARM Cortex-A53 |
| Cores | 4 |
| Threads per core | 1 |
| L2 cache | 512 KiB |

## Memory

| Item | Current state |
|---|---|
| RAM | approximately 955 MiB |
| Used during audit | approximately 227 MiB |
| Available during audit | approximately 727 MiB |
| Swap | approximately 1.1 GiB file |
| Swap used | approximately 77 MiB |

This is the smallest-memory audited compute host so far.

## Storage

### Boot/system media

| Item | Current state |
|---|---|
| Device | `/dev/mmcblk0` |
| Capacity | approximately 59.4 GiB |
| Root partition | approximately 59.3 GiB ext4 |
| Used | approximately 4.5 GiB |
| Available | approximately 52 GiB |
| Root usage | approximately 9% |

SMART-style health data is not available for the microSD device through the installed tooling. Boot-media health is therefore **UNKNOWN**.

### Backup disk

| Item | Current state |
|---|---|
| Device | `/dev/sda` |
| Model | WDC WD40EZRX-00SPEB0 |
| Capacity | approximately 3.6 TiB |
| Filesystem | ext4 |
| Mount | `/mnt/backup` |
| Used | approximately 20 GiB |
| Available | approximately 3.4 TiB |
| Usage | approximately 1% |

This is a major estate-level storage asset and must be treated separately from the Raspberry Pi when target roles are designed.

The initial SMART query could not pass through the USB bridge, so health of this HDD remains **UNVERIFIED**. A follow-up read-only SMART device-type discovery is required before the hardware audit is considered fully closed.

## Network

| Item | Current state |
|---|---|
| Primary interface | `eth0` |
| Address | `192.168.2.48/24` |
| Link | 100 Mb/s, full duplex |
| Gateway | `192.168.2.1` |
| DNS | `192.168.2.48`, `192.168.2.242` |

The 100 Mb/s Ethernet ceiling is an important placement constraint if the attached 4 TB-class disk is considered for broader backup or storage duties.

## DNS workload

Pi-hole and Unbound are installed directly on the host, not containerized.

Observed versions:

- Pi-hole Core 6.4.3
- Pi-hole Web 6.6
- Pi-hole FTL 6.7
- Unbound 1.26.0

Observed state:

- Pi-hole FTL listening on port 53 for IPv4 and IPv6.
- Pi-hole blocking enabled.
- Unbound active on localhost port 5335.
- Unbound service active and enabled.

This confirms `192.168.2.48` is the current primary recursive/filtering DNS appliance.

## Current platform services

System-level services observed include:

- Pi-hole FTL
- Unbound
- Alloy
- Prometheus node exporter
- Zabbix Agent 2
- Dropbear SSH
- unattended upgrades

No Docker or k3s runtime was detected.

One failed unit was present:

- `smartmontools.service`

This is consistent with the storage-health detection gap and should be reconciled rather than carried forward automatically.

## Workload detectors

| Detector | Result |
|---|---|
| Docker | NO |
| k3s | NO |
| Pi-hole | YES |
| Unbound | YES |
| BirdNET | NO |

## Raspberry Pi health

- Firmware throttle state: `0x0`.
- Firmware temperature during audit: approximately 45 C.
- Thermal-zone CPU temperature later in the audit: approximately 50.5 C.
- No active throttling was reported.

## Current load snapshot

At audit time:

- load average: approximately `0.25 / 0.14 / 0.16`.
- Alloy used approximately 77 MiB RSS.
- Pi-hole FTL used approximately 67 MiB RSS.
- Unbound used approximately 28 MiB RSS.
- The host had ample free RAM for its current DNS role.

## Role-neutral audit conclusion

Hardware/workload audit: **COMPLETE EXCEPT EXTERNAL HDD HEALTH VERIFICATION**  
Future hostname: **UNASSIGNED**  
Future role: **UNASSIGNED**

Strengths:

- very low current resource use
- stable Pi-hole/Unbound DNS workload
- directly attached 4 TB-class storage with large free capacity
- low thermal load

Constraints:

- Raspberry Pi 3 CPU generation
- approximately 1 GiB RAM
- 100 Mb/s Ethernet
- microSD boot media
- external HDD SMART health not yet verified

No future-role decision should be made until the remaining hosts are audited and the external HDD health gap is closed.
