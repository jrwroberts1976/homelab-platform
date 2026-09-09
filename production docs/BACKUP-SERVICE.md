# Homelab Backup Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** target design approved; deployment pending dedicated-disk selection  
**Primary service:** Proxmox Backup Server (PBS)

## Production identity

| Hostname | IPv4 | Platform | Purpose |
|---|---:|---|---|
| `pbs-01.jameshouse` | `192.168.2.52` | VM on `PROXMOX` / `192.168.2.70` | Central backup UI, datastore, verification and restore |
| `PROXMOX` | `192.168.2.70` | Physical Proxmox VE | Source hypervisor; hosts `pbs-01` |
| `Proxmox-2` | `192.168.2.71` | Physical Proxmox VE | Source hypervisor |

The PBS web interface will be exposed on the normal PBS HTTPS management port
after deployment.

## Storage rule

The PBS VM system disk may live on normal Proxmox VM storage. The **backup
datastore may not** be only another virtual disk on the same storage pool that
contains the production guests.

The datastore must be backed by a healthy dedicated physical disk/device
presented separately to `pbs-01`.

The degraded 4 TB disk currently attached to DietPi is explicitly excluded
from production use.

## Initial backup scope

### Proxmox guests

Both standalone Proxmox hosts will register `pbs-01` and send VM/LXC backups
to it.

First protected workloads:

- `dns-01` — CT 101 on `Proxmox-2`
- `dns-02` — CT 100 on `PROXMOX`

Future critical VMs/LXCs are enrolled as part of their IaC definition.

### Physical Linux hosts and Raspberry Pis

Physical Linux systems are backup clients, not backup servers. Protect selected
persistent data, configuration, databases/dumps and recovery state. Do not
archive replaceable package caches, container images or other reproducible
runtime artifacts.

ARM systems must use a supported file-level backup path rather than being
forced into an unsupported PBS-client configuration.

### TestServer / IaC controller

Protect at minimum:

- Terraform state under `~/.local/state/homelab-iac/`;
- protected non-Git configuration required to rebuild services;
- selected application data not reconstructable from Git;
- recovery metadata without exposing secrets in logs or Git.

## DietPi retirement / reuse plan

`DietPi` at `192.168.2.48` is no longer part of the target critical-service
architecture.

Before it is powered down or repurposed:

1. prove the ASUS DHCP configuration no longer advertises `.48` as DNS;
2. prove ordinary clients resolve through `.51 + .50`;
3. reconcile/copy required Restic repositories and monthly archives from its
   attached disk;
4. confirm protected SOPS/age recovery material exists elsewhere;
5. leave the degraded 4 TB disk read-only/recovery-only.

After those gates pass, power down the Raspberry Pi 3 and retain it as spare
hardware. It may be reassigned later to a lightweight non-critical role if a
real requirement appears. Do not invent a workload merely to keep it powered.

## Retention target

Initial policy:

- daily: 7
- weekly: 4
- monthly: 12
- yearly: 3

Retention is provisional until datastore capacity is known and restore testing
has been completed.

## Verification policy

Backup success alone is insufficient. Production acceptance requires:

- scheduled PBS datastore verification;
- prune/garbage-collection policy;
- failure/staleness alerting;
- a tested restore of at least one LXC;
- a tested restore of at least one VM when VMs enter service;
- a tested file-level restore from at least one physical Linux/Pi host;
- a second independent copy for critical recovery material.

## Deployment order

1. choose/attach the healthy dedicated backup disk;
2. define `pbs-01` VM in IaC on `PROXMOX`;
3. install/configure PBS through IaC/Ansible;
4. create the datastore on the dedicated device;
5. add `pbs-01.jameshouse -> 192.168.2.52` to managed DNS;
6. register PBS on both standalone Proxmox hosts;
7. configure the first guest backup jobs;
8. run backup + verification;
9. perform a controlled restore test;
10. enroll physical Linux/Pi data;
11. establish a second independent copy;
12. only then retire legacy backup paths.

## Definition of done

The backup layer is production-ready when the web UI is reachable, both
Proxmox hosts are enrolled, critical guests have successful verified backups,
a restore has been proven, physical-host data has a supported backup path, and
the datastore is on dedicated healthy storage rather than the production guest
storage pool.
