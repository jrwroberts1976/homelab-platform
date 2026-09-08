# Proxmox Second-Node Build and Cluster Trial — 7 September 2026

## Purpose

This record captures the rebuild of the second Proxmox host, the controlled cluster-join trial, the failure mode observed during `pmxcfs` synchronisation, and the deliberate rollback to a standalone node.

The outcome is important because the node itself was healthy as a standalone Proxmox installation. The cluster trial exposed a synchronisation problem, but the observed USB-NIC receive errors are **not yet proven to be the root cause**.

## Existing primary node

Primary node:

- Hostname: `PROXMOX`
- Address: `192.168.2.70`
- Cluster: `Home-lab`
- Current cluster membership after rollback: one node
- Proxmox VE: 9.2.0
- `pve-manager`: 9.2.11
- `pve-cluster`: 9.1.6
- Corosync: 3.1.10-pve3
- `qemu-server`: 9.2.7

The original node remained the authoritative cluster member throughout the rollback. After removal of the second node, cluster configuration advanced to version 5 and only `PROXMOX` remains in membership.

## Second node rebuild

Second node:

- Hostname: `pve2`
- Address: `192.168.2.71/24`
- Management bridge: `vmbr0`
- Current management NIC: USB Gigabit Ethernet, interface `nic0`
- Current NIC MAC: `00:1a:9f:0c:30:3b`

The node was reinstalled from the Proxmox VE ISO and initially came up with installer hostname `pve`. It was corrected to `pve2`, including local hostname resolution:

```text
192.168.2.71 pve2.jameshouse pve2
```

After restarting `pve-cluster`, `/etc/pve` mounted successfully and the stale installer identity was removed.

## Package alignment

The fresh install was moved to the Proxmox no-subscription repository and fully patched before any new cluster join was attempted.

Post-upgrade versions:

- Proxmox VE: 9.2.0
- Running kernel: `7.0.14-15-pve`
- `pve-manager`: 9.2.11
- `pve-cluster`: 9.1.6
- Corosync: 3.1.10-pve3
- `libpve-common-perl`: 9.2.1
- `qemu-server`: 9.2.7

This aligned the important cluster components with the existing primary node before the join was attempted.

## Router reservation

The router DHCP configuration was updated so that `192.168.2.71` is reserved for the current `pve2` management NIC MAC. The Proxmox host itself remains statically configured; the reservation exists to prevent another DHCP client being issued the same address.

## Cluster join trial

The second node was joined with:

```bash
pvecm add 192.168.2.70 --link0 192.168.2.71
```

The join was accepted by the primary node and Corosync reached quorum.

Observed state included:

- cluster name `Home-lab`
- two nodes
- two expected votes
- two total votes
- quorate state
- both `192.168.2.70` and `192.168.2.71` visible in membership

However, the local `pmxcfs` database on `pve2` did not complete normal synchronisation.

## Failure mode

The join progressed far enough to establish Corosync membership, but `pve2` repeatedly stalled while synchronising the Proxmox configuration database.

Symptoms included:

- `/etc/pve/priv` initially missing, then later appearing
- `/etc/pve/nodes` remaining absent during the broken cluster state
- `pvecm updatecerts --silent` blocking
- `pveproxy` unable to complete its start-pre phase
- port 8006 not listening on `pve2`
- GUI errors including SSL verification failure and connection refused
- `pmxcfs` logging:
  - `starting data syncronisation`
  - `received all states`
  - `leader is 1/...`
  - `waiting for updates from leader`
- a subsequent read from `/etc/pve` becoming uninterruptibly blocked

This produced a state where Corosync could report quorum while the local Proxmox configuration filesystem was not usable.

## Network observations

During troubleshooting, the current USB Ethernet adapter on `pve2` showed receive errors and drops.

Examples observed during testing:

- RX errors increased over time
- RX drops increased over time
- a 1500-byte path ping test showed a small amount of packet loss
- the HP ProCurve switch reported zero FCS, alignment, collision, or receive-drop errors on ports 21 and 22
- the primary Proxmox NIC showed zero RX/TX errors

These observations make the current USB NIC or USB path a valid concern, but they do **not** prove that it caused the original `pmxcfs` synchronisation failure. The serious Proxmox failure was already present before intensive network troubleshooting began.

## Rollback

The cluster trial was deliberately rolled back instead of repeatedly forcing the broken state.

On `PROXMOX`:

1. quorum was temporarily reduced to one expected vote while `pve2` was offline
2. `pvecm delnode pve2` removed the second node
3. cluster configuration advanced to version 5
4. stale `/etc/pve/nodes/pve2` state was checked and removed
5. final membership contained only `PROXMOX`

On `pve2`:

1. `pve-cluster` and Corosync were stopped
2. `pmxcfs -l` was used for local-mode recovery
3. `/etc/pve/corosync.conf` was removed
4. `/etc/corosync/*` was cleared
5. local `pmxcfs` was stopped
6. normal `pve-cluster` was started again

The recovered standalone state showed:

```text
/etc/pve/nodes/
└── pve2
```

and:

```text
Error: Corosync config '/etc/pve/corosync.conf' does not exist - is this node part of a cluster?
```

That is the expected standalone result.

## Current decision

For now:

- `PROXMOX` remains the only node in the `Home-lab` cluster.
- `pve2` remains standalone.
- The existing USB NIC can continue as a management interface.
- A new NIC is expected and will be tested independently before any further cluster work.
- The likely long-term design is to keep the current NIC for management and use the new NIC for Corosync and VM migration traffic.
- No further cluster join should be attempted until the new interface has been proven stable.
- Do not treat the current USB NIC as the confirmed root cause unless later testing proves it.

## Next validation

Before retrying clustering:

1. confirm standalone `pve2` web/API services are healthy
2. install and identify the new NIC
3. assign a dedicated static cluster/migration address with no default gateway
4. run sustained packet and error-counter tests
5. confirm no RX/TX errors or recurring packet loss
6. confirm the primary node remains healthy
7. only then perform a fresh cluster-join test

## Architecture implication

The preferred target becomes:

```text
pve2 current USB NIC
  -> management LAN
  -> 192.168.2.71
  -> vmbr0

pve2 new NIC
  -> dedicated cluster / migration network
  -> separate subnet
  -> no default gateway
```

This keeps management traffic separate from latency-sensitive Corosync and higher-volume VM migration traffic.


## Hardware audit update — 8 September 2026

A fresh read-only hardware audit confirms `pve2` is an ASUS ZenBook UX482EAR with an Intel Core i5-1155G7 (4 cores / 8 threads), approximately 16 GiB RAM, and a 476.9 GiB SK hynix NVMe. VT-x and VT-d/DMAR are active.

The NVMe contains a `pve/data` LVM-thin pool of approximately 347.9 GiB, but only the directory storage `local` is currently registered in the Proxmox storage API. No Debian 13 LXC template is currently present. These are platform-preparation items for the first reusable DNS-resolver build, not hardware-capacity blockers.

The standalone `pve-cluster` service and `/etc/pve` FUSE mount are healthy.

See `docs/hardware/PVE2-HARDWARE-AUDIT-2026-09-08.md`.
