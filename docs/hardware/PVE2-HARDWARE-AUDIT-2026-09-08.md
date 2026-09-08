# pve2 Hardware Audit — 8 September 2026

## Purpose

This audit records the current physical and Proxmox-visible state of `pve2` before using it as the first target for the reusable one-click DNS-resolver build.

## Platform

| Item | Current state |
|---|---|
| Hostname | `pve2` |
| Manufacturer | ASUSTeK COMPUTER INC. |
| Model | ZenBook UX482EAR_UX482EAR |
| Chassis | Laptop |
| OS | Debian GNU/Linux 13 (trixie) |
| Proxmox | pve-manager 9.2.11 |
| Kernel | 7.0.14-15-pve |
| Architecture | x86_64 |
| Firmware | UX482EAR.308 |
| Firmware date | 2023-10-05 |

Hardware serial and product UUID are intentionally omitted from repository documentation.

## CPU / virtualisation

- 11th Gen Intel Core i5-1155G7 @ 2.50 GHz
- 1 socket
- 4 physical cores
- 8 logical CPUs / threads
- 2 threads per core
- Intel VT-x present
- Intel VT-d / DMAR is active and IOMMU groups are being created

## Memory

- Approximately 15 GiB usable RAM
- Approximately 13 GiB available at audit time
- 8 GiB swap

## Storage

Physical device:

- SK hynix HFM512GD3JX013N NVMe
- 476.9 GiB visible capacity

Current partition/LVM layout:

- EFI: 1 GiB
- LVM PV: approximately 475 GiB
- `pve/root`: 96 GiB ext4 mounted at `/`
- `pve/swap`: 8 GiB
- `pve/data`: approximately 347.9 GiB LVM-thin pool
- VG free space: approximately 16 GiB

### Proxmox storage registration

At audit time, only the directory storage `local` is registered through the Proxmox storage API:

- path: `/var/lib/vz`
- type: `dir`
- content: `iso,rootdir,snippets,vztmpl,backup,images`
- approximately 98.5 GiB total filesystem capacity
- approximately 87.9 GiB available

The `pve/data` thin pool exists and is healthy at the LVM layer, but it is **not yet registered as a Proxmox storage object**. A normal `local-lvm` storage entry therefore does not currently exist.

This must be resolved before the reusable DNS-resolver workflow uses `local-lvm` as its default rootfs datastore on `pve2`.

## LXC template state

No Debian 13 LXC template is currently present on `local`.

The reusable resolver build expects:

`local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst`

The template must be downloaded or the workflow must be adjusted to a verified available template before the first one-click build.

## Network

Current interfaces:

- `nic0`: USB Gigabit Ethernet management interface, UP
- `vmbr0`: UP, `192.168.2.71/24`
- `wlo1`: Intel Wi-Fi 6E AX210/AX1675, DOWN

The existing USB NIC remains the current management path. Previous RX errors/drops remain a known concern but have not been proven to be the cause of the earlier cluster synchronisation failure.

## Proxmox configuration filesystem

The standalone Proxmox configuration filesystem is healthy at audit time:

- `pve-cluster`: active
- `/etc/pve`: mounted via FUSE
- local node directory: `/etc/pve/nodes/pve2`
- LXC/QEMU node directories present

The absence of `/etc/pve/storage.cfg` reflects the current minimal standalone storage configuration rather than an unmounted `pmxcfs`; the Proxmox storage API reports the single `local` storage object successfully.

## DNS build readiness

Planned first reusable resolver build:

- hostname: `dns-01`
- IPv4: `192.168.2.51`
- PVE: `pve2`
- CT ID: `101`

Hardware capacity is more than sufficient for the planned 1 vCPU / 512 MiB RAM / 8 GiB resolver.

Outstanding one-time platform preparation before build:

1. register the intended LXC datastore (prefer the existing `pve/data` thin pool as `local-lvm`, after validation)
2. download/verify the Debian 13 LXC template
3. create the scoped IaC roles/user/token on standalone `pve2`
4. complete the local runner secret files
5. run the one-click build and validate the result before any DHCP/DNS cutover
