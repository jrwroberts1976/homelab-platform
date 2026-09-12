# Greenfield Rebuild Plan

> **HISTORICAL / SUPERSEDED PLAN**  
> This document records earlier migration intent and is retained for architecture archaeology. Hostnames, placements and sequencing below must **not** be used as current operational instructions.  
> For current truth use `docs/architecture/CURRENT-STATE.md`; for remaining direction use `docs/architecture/TARGET-STATE.md`; for migration progress use `docs/migrations/MIGRATION-TRACKER.md`.

Original status: approved operating direction; execution was gated by backup/recovery proof and the network audit.

## Principle

The fresh-start programme allowed infrastructure to be rebuilt from bare metal / factory defaults where that produced a cleaner, reproducible result than preserving historical state.

This applied to:

- switch configuration
- router configuration
- host operating systems
- Proxmox / backup platform installation
- application stacks

The purpose was not to erase evidence. Existing state was to be captured first, then replacements rebuilt from documented intent and IaC.

## Rebuild rule

A device or host could be factory-reset or reinstalled only when all of the following were true:

1. hardware identity and current role were recorded
2. required persistent data was identified
3. secrets/recovery material were protected
4. a rollback or recovery path existed
5. the target role and hostname were approved
6. target configuration existed in Git/IaC where practical
7. the rebuild validation checklist was written

Do not use the historical plan below as approval for a present-day rebuild.

## Historical network rebuild order

### 1. HP ProCurve switch

The earlier plan intended a factory-default rebuild after evidence capture, including:

- physical cabling labels
- intended mirror/SPAN destination: port 24
- management address `192.168.2.16`
- firmware/model information
- accessible configuration/export
- link/MAC/VLAN/mirror evidence

The 12 September 2026 audit subsequently proved that port mirroring is currently disabled and port 24 currently carries the primary ASUS router link. Current repatching/SPAN intent is documented in `docs/network/SWITCH-PORT-MAP.md`.

### 2. ASUS router / AiMesh

The historical direction was to capture WAN/DHCP/DNS/Wi-Fi/AiMesh/VPN/DDNS/port-forward evidence, then perform a clean reset/rebuild rather than restoring historical drift.

Current router planning is documented separately in `docs/network/ROUTER-RESET-PLAN.md`.

## Historical compute-host direction

### HP ProDesk -> `pve-01`

Earlier plan name: `pve-01`.

The existing Proxmox installation was to be retained, with RAM/capacity remediation and a future dedicated sensor capture NIC.

Current identity is `PROXMOX` at `192.168.2.70`. It now has 16 GB RAM and hosts `dns-02`, `mail-relay-01`, `cloud-01` and `sensor-01`.

### ASUS ZenBook -> `pve-02`

Earlier plan name: `pve-02`.

The historical direction assumed a clean rebuild and future `pbs-01` placement.

That plan has been superseded. The current node is already live as `Proxmox-2` at `192.168.2.71`, hosting `dns-01`, `monitor-01` and `edge-01`. There is currently no PBS server.

### Raspberry Pi 3 -> `dns-01`

Historical target: rebuild the former DietPi Raspberry Pi 3 as DNS.

Superseded outcome: the physical Pi 3 is now `admin-01` at `.48`, while `dns-01` is CT 101 on `Proxmox-2` at `.51`.

### Raspberry Pi 4 / legacy TestServer -> `birdnet-01`

Historical target name: `birdnet-01`.

Superseded/current outcome: the physical Pi 4 is now `docker-01` at `.220`, dedicated to BirdNET-Go. The `TestServer` identity is retired.

### Raspberry Pi 5 / legacy media-01 -> `media-01`

The intended dedicated media role was implemented. `media-01` is now an active Debian 13 Raspberry Pi 5 Kodi endpoint at `.195`.

## Historical virtual-workload placement

The original working model proposed:

```text
pve-01
  docker-01
  security-01
  sensor-01
  dns-02

pve-02
  pbs-01
  monitoring-01
  management-01
```

This block is retained only as historical design evidence.

Current placement is documented in `CURRENT-STATE.md` and differs materially.

## Data migration rule

The principle remains useful even though placements changed:

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

Applications should preserve required data/configuration rather than preserve an old operating system merely for convenience.

## Historical rebuild sequence

The earlier sequence included:

1. finish non-destructive evidence capture
2. reconcile degraded DietPi backup disk contents
3. establish replacement/healthy backup storage
4. factory-reset/document HP ProCurve
5. reset/rebuild ASUS router/AiMesh
6. finalize hostnames/IPs/port map
7. prepare `pve-01`
8. build core VMs
9. migrate roles off `ids-01`
10. rebuild ZenBook as `pve-02`
11. create `pbs-01`
12. move monitoring/management workloads
13. rebuild `dns-01`
14. rebuild `birdnet-01`
15. rebuild `media-01`
16. retire Jenkins/legacy containers after replacement proof
17. remove old repositories/configuration after recovery validation

This order is **not current execution authority**. Many of these steps have already been implemented differently, while backup and network work remain outstanding.

## Enduring completion principle

The following principle still applies to future rebuilds:

- intended firmware/OS is installed;
- target hostname/address is correct;
- configuration is represented in Git/IaC where practical;
- monitoring is healthy;
- backup/recovery is configured where applicable;
- functional validation passes;
- old state is retained only as long as required for rollback/recovery.
