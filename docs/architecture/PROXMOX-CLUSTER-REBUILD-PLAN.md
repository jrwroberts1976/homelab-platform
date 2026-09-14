# Proxmox Two-Node Cluster Rebuild Plan

**Status:** design/readiness only — no cluster change approved yet  
**Created:** 14 September 2026

## Purpose

This document defines the safety gates, proposed network/quorum design and migration sequence for rebuilding the two standalone Proxmox VE hosts as one cluster.

No live Corosync, cluster-membership, guest-ID or storage change should be made until the readiness audit and hardware gates in this document pass.

## Current state

The two hypervisors are currently standalone:

```text
PROXMOX    192.168.2.70
Proxmox-2  192.168.2.71
```

Current production guests:

```text
PROXMOX .70
  CT100 dns-02
  CT102 mail-relay-01
  VM200 cloud-01
  VM201 sensor-01

Proxmox-2 .71
  CT101 dns-01
  CT103 edge-01
  VM200 monitor-01
```

Both standalone hosts therefore contain an unrelated VMID `200`. That is valid while they are standalone, but invalid once they are members of one cluster because VMIDs are cluster-wide.

The primary guest-backup platform is already operational using isolated per-node NFS namespaces on `media-01`.

## Why reconsider clustering

A two-node cluster would provide one management plane, cluster-wide guest identity, easier future migration/maintenance workflows and a cleaner basis for HA-related features if later justified.

The design must not trade operational simplicity for fragile quorum or network behaviour. Cluster creation is therefore conditional on dedicated Corosync networking, a QDevice design and proven rollback.

## Proposed topology

```text
                         normal LAN / management / NFS
                              192.168.2.0/24

              192.168.2.70                     192.168.2.71
          +-------------------+             +-------------------+
          |      PROXMOX      |             |     Proxmox-2     |
          |                   |             |                   |
          | onboard NIC       |-------------| onboard NIC       |
          | vmbr0 / LAN       |   switch    | vmbr0 / LAN       |
          |                   |             |                   |
          | scan/capture NIC  |             |                   |
          | dedicated to      |             |                   |
          | sensor workflow   |             |                   |
          |                   |             |                   |
          | StarTech USB GbE  |=============| StarTech USB GbE  |
          | 10.250.0.1/30     | direct link | 10.250.0.2/30     |
          +-------------------+  Corosync   +-------------------+
                    \                              /
                     \                            /
                      +------ admin-01 .48 -------+
                              QNetd / QDevice
                              over normal LAN
```

## NIC roles

### PROXMOX

1. onboard NIC — management, VM/LXC bridge traffic, normal LAN and NFS backup traffic;
2. existing dedicated scan/capture NIC — remains dedicated to the passive network-sensor workflow and must not be reused for Corosync;
3. additional StarTech USB 3.0 Gigabit Ethernet adapter — proposed dedicated Corosync link.

### Proxmox-2

1. onboard NIC — management, VM/LXC bridge traffic, normal LAN and NFS backup traffic;
2. StarTech USB 3.0 Gigabit Ethernet adapter — proposed dedicated Corosync link.

## Proposed Corosync addressing

Working proposal, subject to live interface validation:

```text
PROXMOX    10.250.0.1/30
Proxmox-2  10.250.0.2/30
```

The dedicated link should have no default gateway and no normal guest/service traffic.

The normal management LAN may be considered as a secondary Corosync link only after the primary direct link has been proven stable. The two links must remain distinct physical paths.

## Quorum design

For a two-node cluster, use an external Corosync QDevice/QNetd vote.

Proposed external voter:

```text
admin-01
192.168.2.48
Debian 13 / Raspberry Pi 3
```

`admin-01` is preferred because it is independent of both hypervisors and is not the NFS backup target.

The QDevice uses normal TCP/IP connectivity and therefore does not need to sit on the private Corosync link.

Before adoption, validate:

- `admin-01` uptime and power/network dependency are acceptable;
- `corosync-qnetd` is available and installable;
- both PVE nodes can reach it reliably;
- required SSH/setup access can be provided without weakening the long-term security model;
- quorum remains understood during planned QDevice or node outages.

## Official Proxmox constraints that drive this plan

- Proxmox recommends a dedicated physical NIC for Corosync traffic; 1 Gbit is normally sufficient because latency/packet consistency matters more than throughput.
- A second Corosync link on a different physical network can provide communication redundancy.
- A QDevice is recommended for two-node clusters when higher availability is desired.
- A joining node has its `/etc/pve` configuration overwritten by the cluster configuration and must not hold guests when it joins.
- If a joining node previously held guests, back them up and restore them after joining, using non-conflicting IDs where necessary.
- Final hostnames/IP configuration must be established before cluster creation.

## VMID collision resolution

Preferred cluster-wide identity plan:

```text
100  dns-02
101  dns-01
102  mail-relay-01
103  edge-01
200  cloud-01
201  sensor-01
210  monitor-01   <- proposed replacement for current standalone VM200
```

`cloud-01` keeps VMID `200` because `PROXMOX` is the proposed first cluster node.

`monitor-01` should be restored as VMID `210` after `Proxmox-2` has joined the cluster. Do not attempt to join `Proxmox-2` while any of its current guests remain registered on that node.

The exact replacement ID is not authoritative until the readiness audit confirms `210` is unused everywhere relevant.

## Proposed cluster creation sequence

### Phase 0 — readiness only

1. confirm both PVE versions, kernel state, hostnames and management addresses;
2. capture `/etc/network/interfaces`, interface names/MACs and link capabilities;
3. identify the existing scan/capture interface and prove it remains separate;
4. validate both StarTech adapters and stable interface naming;
5. confirm CPU vendors and migration compatibility expectations;
6. capture full guest and storage inventories;
7. confirm recent backups for every production guest;
8. confirm no unexpected existing Corosync/cluster state;
9. confirm proposed VMID `210` is unused;
10. validate QNetd suitability on `admin-01`.

No destructive action occurs in Phase 0.

### Phase 1 — dedicated Corosync network

1. cable the two StarTech adapters directly;
2. configure `10.250.0.1/30` and `10.250.0.2/30` without gateways;
3. validate MTU, packet loss, latency, link persistence and interface naming across reboot;
4. confirm management/NFS/scanning traffic still uses its original path.

Do not create the cluster until this link is proven.

### Phase 2 — create first cluster node

Use `PROXMOX .70` as the first node because it retains cluster VMID `200` for `cloud-01`.

Before creation:

- take/verify a fresh backup set;
- record all storage/network state;
- confirm `Proxmox-2` remains standalone and untouched;
- preserve the current isolated backup repositories.

Create the cluster using the dedicated Corosync address as the primary cluster link.

### Phase 3 — establish QDevice

Install/configure QNetd on `admin-01` and QDevice support on the cluster nodes using the supported Proxmox workflow.

Validate expected votes/quorum before proceeding to the second node.

### Phase 4 — prepare Proxmox-2 to join

A node joining an existing PVE cluster must not hold guests.

Immediately before evacuation:

1. take fresh backups of CT101, CT103 and VM200 `monitor-01` into `media-backup-proxmox-2`;
2. verify archive visibility/integrity and backup timestamps;
3. stop the three guests in a controlled sequence;
4. verify service impact/alternate service coverage, especially DNS;
5. remove the guest registrations/local guest volumes only after backup proof is explicit;
6. record local storage definitions because `/etc/pve` will be replaced on join.

Do not delete the NFS backup archives.

### Phase 5 — join Proxmox-2

Join `.71` to the existing cluster using its dedicated Corosync link.

After join:

- verify quorum and both Corosync links/state;
- verify node certificates/API access;
- reconcile local storage definitions/node restrictions;
- validate NTP, monitoring and management connectivity;
- do not restore production guests until cluster health is clean.

### Phase 6 — restore Proxmox-2 workloads

Restore:

```text
CT101 dns-01    -> VMID 101
CT103 edge-01   -> VMID 103
VM monitor-01   -> VMID 210
```

Restore/start one workload at a time and validate networking/services before continuing.

Update IaC, monitoring, dashboards and documentation anywhere the monitor VMID is represented.

### Phase 7 — post-cluster backup design

Once the cluster and unique VMIDs are stable, reconsider the per-node NFS namespace split.

A single cluster-wide backup namespace becomes technically viable because guest IDs are then globally unique. Do not simplify the current backup storage until cluster stability and a fresh cluster-era backup/restore proof exist.

## Rollback principles

- Never begin a join without fresh off-node backups.
- Preserve the isolated NFS repositories throughout the cluster rebuild.
- Do not reuse or overwrite backup archives to make the cluster join work.
- Treat `PROXMOX` as the anchor/first node; do not dismantle both standalone nodes simultaneously.
- If the dedicated Corosync link is unstable, stop the project before cluster creation.
- If QDevice behaviour is not understood/proven, stop before evacuating `Proxmox-2`.
- If `Proxmox-2` join fails, restore from the known-good pre-join state rather than improvising guest IDs or storage mappings.

## Readiness gates

Cluster implementation is **not approved** until all of these are true:

- third NIC installed and identified on `PROXMOX`;
- dedicated StarTech NIC identified on `Proxmox-2`;
- direct Corosync link proven stable;
- existing scan/capture NIC positively identified and excluded;
- no duplicate cluster-wide guest IDs remain in the migration plan;
- QDevice host validated;
- fresh backups exist for all production guests;
- at least one QEMU restore proof has been completed or an explicit risk acceptance is recorded;
- storage definitions and node-local differences are captured;
- the exact join/restore procedure has been dry-reviewed from `admin-01`.

## Current decision

Proceed with readiness auditing and documentation only. Do not create the cluster until the final NIC is installed and the readiness gates pass.
