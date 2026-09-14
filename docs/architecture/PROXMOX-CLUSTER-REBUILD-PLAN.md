# Proxmox Two-Node Cluster Rebuild — Implementation Record

**Status:** COMPLETE — production cluster formed and validated  
**Implemented:** 14 September 2026

## Purpose

This document was originally the safety/readiness plan for converting the two standalone Proxmox VE hosts into one cluster. The work is now complete, so this file records the implemented design, migration evidence, deliberate rollback protections and remaining post-cluster follow-up.

The live current-state authority is `docs/architecture/CURRENT-STATE.md`. This document preserves the cluster build history and the decisions that produced that state.

## Implemented cluster

```text
Cluster: jameshouse-pve

Node 1
  hostname: PROXMOX
  management: 192.168.2.70
  Corosync link0: 10.255.255.1/30
  node ID: 1

Node 2
  hostname: Proxmox-2
  management: 192.168.2.71
  Corosync link0: 10.255.255.2/30
  node ID: 2

QDevice / QNetd
  host: admin-01
  address: 192.168.2.48
  qnetd TCP port: 5403
```

The actual PVE hostnames remain `PROXMOX` and `Proxmox-2`. Human-facing diagrams may describe the first node as Proxmox-1, but that is not the cluster node name and must not be used as an automation target.

## Corosync network

The production design uses two Kronosnet links:

```text
link0 — preferred
  priority: 20
  PROXMOX:   10.255.255.1
  Proxmox-2: 10.255.255.2
  topology: direct point-to-point cable, no switch in path

link1 — fallback
  priority: 5
  PROXMOX:   192.168.2.70
  Proxmox-2: 192.168.2.71
  topology: normal home LAN
```

The dedicated link is a `/30` network with no gateway and no guest/service traffic.

Validated before cluster creation:

- 300-packet tests in both directions completed with zero packet loss;
- later pre-create tests again completed with zero loss on both the dedicated link and LAN fallback;
- dedicated-link latency remained sub-millisecond on average;
- the PVE API was reachable across the dedicated path;
- normal management/LAN connectivity remained available independently.

### Physical adapters

`PROXMOX`:

```text
interface: enx001a9f0c993b
MAC:       00:1a:9f:0c:99:3b
chipset:   Microchip/SMSC LAN7500
address:   10.255.255.1/30
```

`Proxmox-2`:

```text
interface: enx00249b7b346d
MAC:       00:24:9b:7b:34:6d
chipset:   ASIX AX88179
address:   10.255.255.2/30
```

The original design assumed matching StarTech adapters. The implemented design instead uses the two validated USB Ethernet adapters above. The requirement was stable dedicated connectivity, not matching branding.

## Quorum design

`admin-01` is the external QNetd host and third vote.

Validated production quorum state after setup:

```text
Nodes:            2
Expected votes:   3
Total votes:      3
Quorum:           2
Flags:            Quorate Qdevice
```

Both PVE nodes run `corosync-qdevice`, and `admin-01` runs `corosync-qnetd` on TCP/5403.

QNetd sees both cluster clients and grants the expected ACK vote. Root SSH access used for the supported Proxmox QDevice setup is key-based; root password login was not enabled.

The QDevice improves quorum behaviour for the two-node cluster. It does not make locally stored guest disks highly available by itself.

## Cluster-wide guest identity

The duplicate standalone VMID collision was resolved during migration.

Final production IDs:

```text
100  dns-02
101  dns-01
102  mail-relay-01
103  edge-01
200  cloud-01
201  sensor-01
202  monitor-01
```

`cloud-01` retained VMID `200` on the cluster seed node.

`monitor-01`, formerly standalone VMID `200` on `Proxmox-2`, was restored as cluster VMID `202` while temporarily hosted on `PROXMOX`. The originally proposed ID `210` was not used.

## Final workload placement

After cluster formation and controlled migrations, the intended placement is:

```text
PROXMOX .70
  CT100  dns-02
  CT102  mail-relay-01
  VM200  cloud-01
  VM201  sensor-01
  VM9000 Debian cloud template
  VM9001 Debian cloud template with QGA

Proxmox-2 .71
  CT101  dns-01
  CT103  edge-01
  VM202  monitor-01
```

All production guest IDs are now cluster-unique.

## Migration sequence actually used

### 1. Readiness and backup proof

Before cluster creation:

- both PVE nodes and network interfaces were inventoried;
- fresh off-node backups of the `Proxmox-2` guests were created on `media-01`;
- CT101, CT103 and monitor VM200 backup archives completed successfully;
- backup archives were copied/staged and integrity-tested before restoration;
- `monitor-01` cloud-init snippet content was preserved separately;
- current storage/job configuration and guest configuration were preserved on `admin-01` and `Proxmox-2`.

### 2. Temporary restore on PROXMOX

Before evacuating the joining node:

- CT101 was restored as CT101 on `PROXMOX`;
- CT103 was restored as CT103 on `PROXMOX`;
- monitor VM200 was restored as VM202 on `PROXMOX`;
- each restored workload was booted and service-validated;
- DNS, monitoring and Loki readiness were explicitly tested.

### 3. Evacuate Proxmox-2 without destroying rollback disks

Fresh final backups were taken immediately before the join.

The old guest registrations were removed from `/etc/pve` on `Proxmox-2`, but their local LVM-thin volumes were deliberately retained as rollback evidence.

The node was confirmed to have no registered VMs or containers before joining the cluster.

### 4. Create cluster seed

`PROXMOX` created cluster `jameshouse-pve` with:

```text
link0 10.255.255.1 priority 20
link1 192.168.2.70 priority 5
```

The seed validated as a one-node quorate cluster before any join was attempted.

### 5. Join Proxmox-2

The join bootstrap used the certificate-valid hostname `PROXMOX.jameshouse` while assigning the local Corosync addresses explicitly:

```text
link0 10.255.255.2
link1 192.168.2.71
```

After the join:

- both nodes reported two-node membership;
- both Corosync links reported connected in both directions;
- `pve-cluster` and `corosync` were active on both nodes;
- the cluster remained quorate;
- running production workloads remained healthy.

### 6. Configure QDevice

`corosync-qnetd` was installed on `admin-01` and `corosync-qdevice` on both PVE nodes.

After key-based SSH trust and supported `pvecm qdevice setup`, both nodes reported three expected/total votes with quorum two and the `Qdevice` flag.

### 7. Reconcile storage and migrate workloads back

The cluster-wide storage configuration was corrected so the per-node backup exports are explicitly node-scoped:

```text
media-backup-proxmox
  node: PROXMOX
  export: /srv/backup/pve-proxmox

media-backup-proxmox-2
  node: Proxmox-2
  export: /srv/backup/pve-proxmox-2
```

The old local guest volumes on `Proxmox-2` were renamed before migration rather than deleted:

```text
precluster-20260914-vm-101-disk-0
precluster-20260914-vm-103-disk-0
precluster-20260914-vm-200-cloudinit
precluster-20260914-vm-200-disk-0
```

That preserved rollback evidence while freeing normal Proxmox volume names for the incoming cluster guests.

CT101 was migrated to `Proxmox-2` and validated with Pi-hole, Unbound, network reachability and quorum checks. CT103 and VM202 were subsequently placed on `Proxmox-2` through the cluster migration workflow/GUI.

## Backup implications

The original isolated per-node NFS repositories remain in service for now.

The cluster removes the historical duplicate-VMID problem, but there is no operational need to collapse the repositories immediately. Keeping the proven per-node namespaces preserves rollback and failure-domain clarity while the new cluster state is observed.

The pre-cluster schedule evidence remains historical evidence. Post-cluster backup policy must use the new monitor VMID `202` and must be revalidated against the final cluster placement before it is described as proven current state.

Expected post-cluster guest sets are:

```text
PROXMOX
  100,102,200,201

Proxmox-2
  101,103,202
```

A fresh cluster-era backup of VM202 is an explicit follow-up gate.

## What the cluster does not provide

The cluster currently uses node-local `local-lvm` storage for production guest disks.

Therefore cluster membership provides:

- one management plane;
- cluster-wide guest identity;
- controlled migration workflows;
- Corosync membership and quorum;
- a basis for future HA decisions.

It does **not** currently provide automatic restart of a guest on the surviving node after loss of the node that owns its local disk.

Any future HA design requires an explicit storage/replication decision rather than assuming the cluster alone provides guest failover.

## Rollback evidence still retained

Do not remove the following until fresh post-cluster backup/recovery evidence is satisfactory:

- renamed `precluster-20260914-*` LVs on `Proxmox-2`;
- final pre-cluster backup archives on `media-01`;
- saved pre-cluster guest/storage/job configuration;
- the `admin-01` migration preservation bundle;
- monitor-01 cloud-init snippet preservation copy.

Once fresh cluster-era backups are proven, the retained local rollback LVs can be reviewed for deliberate removal.

## Remaining follow-up

The cluster build itself is closed. Remaining work is operational hardening rather than cluster creation:

1. reconcile backup schedule IaC and live jobs to final cluster placement and VM202;
2. take and validate fresh cluster-era backups, especially VM202;
3. observe the first successful unattended post-cluster backup cycle;
4. test Corosync link0 loss and prove link1 fallback without creating a node outage;
5. perform a controlled single-node outage/quorum exercise with QDevice available;
6. decide whether local-storage/manual recovery remains sufficient or whether replication/shared storage and HA are justified;
7. remove retained pre-cluster LVs only after backup confidence is explicit;
8. update remaining inventory/comments/runbooks that still describe the PVE hosts as standalone.

## Final decision

The two-node Proxmox cluster is now approved, implemented and operational.

Do not repeat the standalone-to-cluster migration process unless rebuilding from a future disaster. Future changes should treat `jameshouse-pve` as the production platform and preserve the dedicated Corosync link, LAN fallback, QDevice and cluster-wide guest IDs.
