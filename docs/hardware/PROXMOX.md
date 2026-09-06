# PROXMOX Current-State Audit

Audit source: TestServer jump-box read-only audit of `192.168.2.70` on 2026-09-06.

Audit report SHA256:

`a4cac78c251e804edbb92d824b9558db46535e0c5f205862a911ef0008654a02`

## Identity

| Item | Current state |
|---|---|
| Hostname | `PROXMOX` |
| Address | `192.168.2.70/24` |
| Hardware | HP ProDesk 400 G4 DM |
| OS | Debian GNU/Linux 13 (trixie) |
| Proxmox | VE 9.2.0 / pve-manager 9.2.11 |
| Kernel | 7.0.14-14-pve |
| Architecture | x86-64 |
| Cluster | Standalone node |

## Compute

| Item | Current state |
|---|---|
| CPU | Intel Core i5-8500T @ 2.10 GHz |
| Cores / threads | 6 / 6 |
| Virtualization | VT-x |
| RAM | 7.6 GiB |
| RAM available during audit | 5.2 GiB |
| Swap | 7.6 GiB, effectively unused |

CPU capacity is currently lightly used. RAM is the primary capacity constraint for making this node the main homelab compute platform.

## Storage

### NVMe system disk

- WDC PC SN520 256 GB class NVMe.
- Proxmox root on LVM.
- Root filesystem: approximately 68 GiB, 22% used.
- `local-lvm`: approximately 141.5 GiB thin pool, currently empty.
- NVMe health: no critical warning, 6% lifetime used, zero media errors.

### SATA VM SSD

- Kingston SA400S37 480 GB class SATA SSD.
- `vm-ssd`: approximately 424.6 GiB thin pool.
- Thin-pool data usage during audit: 1.66%.
- SMART overall health: PASSED.

Storage capacity is currently strong and is not the limiting factor for the migration.

## Network

- Realtek RTL8111/8168-family 1 GbE NIC.
- Interface `nic0` is bridged through `vmbr0`.
- Link: 1000 Mb/s, full duplex, auto-negotiation enabled.
- Default gateway: `192.168.2.1`.
- Proxmox management address: `192.168.2.70/24`.
- Current bridge is untagged VLAN 1 only.

## Existing guests

### CT 201 — zabbix-lxc-01

| Item | Current state |
|---|---|
| Type | Unprivileged LXC |
| Status | Running |
| Architecture | amd64 |
| vCPU | 2 |
| Memory limit | 4096 MiB |
| Swap | 1024 MiB |
| Root disk | 64 GiB on `vm-ssd` |
| Network | DHCP on `vmbr0` |
| On boot | Yes |
| Tags | container, iac, zabbix |
| Memory observed | approximately 429 MiB |

This workload remains in place during the platform migration.

### VM 9000 / 9001

Two stopped Debian 13 cloud templates exist:

- `debian-13-cloud-template`
- `debian-13-cloud-template-qga`

Each is configured with 2 vCPU, 2 GiB RAM and a 3 GiB base disk. These are suitable candidates to review as the base for future IaC-provisioned VMs.

## Host services

- Proxmox management services are healthy.
- Prometheus node exporter is listening on 9100.
- Alloy is present with a localhost listener on 12345.
- No failed systemd units were reported.
- Docker is **not** installed on the Proxmox host.

Docker should remain off the Proxmox host itself. Application containers should run inside explicitly provisioned guests.

## Backup posture

No `/etc/pve/jobs.cfg` backup job was present during the audit.

This is a migration blocker for placing additional important workloads on Proxmox until an explicit guest-backup policy is defined and tested.

## Thermals

- PCH: approximately 39 C.
- CPU package: approximately 38 C.

No thermal concern was visible during the audit.

## Capacity assessment

### Strong points

- Six physical CPU cores with VT-x.
- Large amount of free SATA thin-pool capacity.
- Healthy NVMe and SATA storage according to the read-only health checks.
- Light current CPU load.
- Clean standalone Proxmox role with Docker absent from the host.

### Constraints

- Only 7.6 GiB physical RAM.
- Existing Zabbix LXC has a 4 GiB configured memory ceiling.
- No configured Proxmox backup job.
- Single 1 GbE NIC and single-node design provide no infrastructure HA.

## Migration decision

**Do not create both `docker-core-01` and `monitoring-01` yet.**

The node has ample CPU and storage, but current RAM does not provide comfortable headroom for the Proxmox host, Zabbix, a core Docker VM, and a separate monitoring VM.

Before Proxmox becomes the primary compute platform:

1. Verify supported RAM upgrade options and increase memory.
2. Define and test Proxmox guest backup/recovery.
3. Review the two Debian cloud templates for IaC use.
4. Keep Docker off the Proxmox host.
5. Recalculate VM sizing after the RAM upgrade.

A 16 GiB total-memory configuration would be the minimum sensible target for consolidation; more memory is preferable if supported and cost-effective.

## Status

Hardware audit: **COMPLETE**

Workload placement decision: **DEFERRED pending full-host inventory and Proxmox memory/backup remediation**
