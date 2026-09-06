# Greenfield Rebuild Plan

Status: approved operating direction; execution remains gated by backup/recovery proof and the remaining network audit.

## Principle

The fresh-start programme is allowed to rebuild infrastructure from bare metal / factory defaults where that produces a cleaner, reproducible result than preserving historical state.

This applies to:

- switch configuration
- router configuration
- host operating systems
- Proxmox / backup platform installation
- application stacks

The purpose is not to erase evidence. Existing state is captured first, then the replacement is rebuilt from documented intent and IaC.

## Rebuild rule

A device or host may be factory-reset or reinstalled only when all of the following are true:

1. hardware identity and current role are recorded
2. required persistent data is identified
3. secrets/recovery material are protected
4. a rollback or recovery path exists
5. the target role and hostname are approved
6. the target configuration exists in Git/IaC where practical
7. the rebuild validation checklist is written

Do not perform an in-place clean-up when a fresh installation is safer and easier to reproduce.

## Network rebuild order

### 1. HP ProCurve switch

The switch is intentionally planned for a factory-default rebuild because the existing configuration is too tightly locked down to remain a practical administration baseline.

Before reset, capture whatever evidence remains obtainable:

- physical cabling labels
- known mirror/SPAN destination: **port 24**
- management address: legacy `192.168.2.16`
- firmware/model information
- any accessible configuration/export
- link LEDs / connected-port observations
- MAC/VLAN/mirror information if console access makes it available

After reset:

- establish management access locally
- set management identity/address
- update firmware only through a separately reviewed change
- label ports from physical/MAC evidence
- reserve port 24 as the mirror/SPAN destination
- rebuild VLAN/mirror settings from Git-backed intent
- validate every connected endpoint before moving on

The switch should be rebuilt **before** the router so the wired LAN has a known, documented forwarding layer during the router cutover.

### 2. ASUS router / AiMesh

After the switch is stable and documented:

- capture current WAN/DHCP/DNS/Wi-Fi/AiMesh/VPN/DDNS/port-forward evidence
- perform the planned clean firmware/factory reset
- rebuild DHCP, reservations, DNS advertisement and QoS from documented intent
- rejoin AiMesh nodes deliberately
- restore monitoring/syslog
- validate wired and wireless clients

Do not restore an old full router backup if the objective is to remove configuration drift.

## Compute-host rebuild direction

### HP ProDesk -> `pve-01`

Working direction: clean Proxmox installation/rebuild after RAM, storage and backup design are approved.

Preserve first:

- any VM/LXC data still required
- Terraform/Ansible source
- current Proxmox network/storage configuration as reference
- recovery copies of anything not already authoritative in Git

Target:

- clean Proxmox hypervisor
- no application Docker directly on the hypervisor
- VM/storage/network configuration represented through IaC
- backup configured before production workloads are considered complete

### ASUS ZenBook -> `pbs-01`

Working direction: clean rebuild for the GUI-based backup role.

This host currently carries security, monitoring, DNS and Restic responsibilities, so it must **not** be wiped until those workloads/data are migrated or protected.

Preserve/verify first:

- Restic server repositories
- Greenbone persistent data/configuration required for migration
- monitoring data where retention matters
- secondary Pi-hole/Unbound configuration as reference
- Suricata/CrowdSec evidence/configuration that must migrate
- SOPS/age recovery coverage

Target:

- dedicated backup server role
- healthy backup datastore
- GUI-based administration
- no unrelated legacy service stack

### Raspberry Pi 3 -> `dns-01`

A clean OS rebuild is permitted and likely desirable once `dns-02` is available so DNS resilience is maintained during the rebuild.

Target workload:

- Pi-hole
- Unbound
- required monitoring agents only

The degraded 4 TB-class HDD is not part of the rebuilt DNS appliance.

### Raspberry Pi 4 / legacy TestServer -> `birdnet-01`

A clean OS rebuild is preferred because the current host is heavily consolidated and carries substantial legacy Docker state.

Before wiping, migrate/protect:

- BirdNET-Go configuration/data required for continuity
- any unique Docker persistent data
- Komodo state if still authoritative
- Jenkins backup/reference material until retirement gates are met
- CrowdSec local drift until deliberately reconciled into Git
- any remaining application data not already migrated

Target:

- BirdNET-Go
- microphone/audio device support
- minimal monitoring/management agents
- no general-purpose legacy Docker estate unless explicitly approved

### Raspberry Pi 5 / legacy media-01 -> `media-01`

A clean media-focused OS rebuild is permitted once the media requirements are confirmed.

Preserve first:

- Kodi settings/library state that is actually worth retaining
- backup-replica data on NVMe
- historical `old-k3s-root` evidence until confirmed unnecessary

Target:

- dedicated Kodi/media endpoint
- local HDMI output
- minimal supporting services

The exact media OS is a later implementation decision.

## Virtual workloads

New VMs should be created fresh rather than cloned from legacy hosts unless there is a specific recovery reason.

Working VM set:

- `docker-01`
- `monitoring-01`
- `management-01`
- `security-01` — Greenbone
- `sensor-01` — Suricata with dedicated mirror NIC passthrough
- `dns-02`

Each VM must have:

- an IaC definition
- configuration-management ownership
- backup policy
- monitoring
- documented rollback/rebuild path

## Data migration rule

Applications are migrated by preserving **data and required configuration**, not by preserving an old operating system.

Preferred pattern:

```text
audit old host
    |
    v
identify authoritative data/config
    |
    v
backup + verify
    |
    v
fresh OS / fresh VM
    |
    v
deploy from IaC
    |
    v
restore/import data
    |
    v
validate
    |
    v
retire old state
```

## Rebuild sequence

Working order:

1. finish remaining non-destructive evidence capture
2. reconcile degraded DietPi backup disk contents
3. establish replacement/healthy backup storage
4. factory-reset and document the HP ProCurve
5. clean-reset/rebuild ASUS router and AiMesh
6. finalize target hostnames/IP reservations/port map
7. upgrade/rebuild `pve-01`
8. build core VMs through IaC
9. migrate Greenbone, monitoring, management and DNS workloads
10. establish `pbs-01` and prove restores
11. rebuild `dns-01`
12. rebuild `birdnet-01`
13. rebuild `media-01`
14. retire Jenkins/legacy containers only after replacement proof
15. remove old repositories/configuration only after recovery validation

## Definition of done

A rebuilt component is complete only when:

- intended firmware/OS is installed
- target hostname/address is correct
- configuration is represented in Git/IaC
- monitoring is healthy
- backup/recovery is configured where applicable
- functional validation passes
- old state is retained only as long as required for rollback/recovery
