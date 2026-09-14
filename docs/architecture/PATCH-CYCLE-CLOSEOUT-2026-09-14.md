# Estate Patch Cycle Closeout — 14 September 2026

**Status:** COMPLETE
**Date:** 14 September 2026
**Scope:** active homelab Linux and Proxmox estate

## Purpose

The 14 September 2026 estate audit identified package-update backlog across several active hosts.

This document records the controlled patch cycle that followed that audit and provides the closeout evidence for the resulting estate state.

The original audit remains the historical point-in-time record of the backlog that existed before patching.

## Patch outcome

The controlled patch cycle completed successfully across the active estate.

Final state:

- no known host package backlog remains from the 14 September audit;
- no active host requires a reboot;
- hosts that required controlled reboots were validated after restart;
- production DNS, monitoring, media, backup and container services remained operational;
- both Proxmox backup repositories hosted by `media-01` recovered correctly after the media server reboot;
- the `admin-01` Ansible controller remained functional after its own package updates.

## Host results

| Host | Result | Reboot | Validation |
|---|---|---|---|
| `PROXMOX` `.70` | patched | yes | PVE services, guests and storage validated |
| `Proxmox-2` `.71` | patched | yes | PVE services, guests and storage validated |
| `admin-01` `.48` | patched | no | Ansible, inventory, Alloy, network and package state validated |
| `dns-01` `.51` | patched | no | Pi-hole, Unbound and DNS resolution validated |
| `dns-02` `.50` | patched | no | Pi-hole, Unbound and DNS resolution validated |
| `mail-relay-01` `.54` | patched | no | Postfix, SMTP listener, relay configuration and queue validated |
| `edge-01` `.56` | patched | no | network, DNS and system health validated |
| `docker-01` `.220` | patched | yes | Docker and BirdNET-Go autostart/health validated |
| `media-01` `.195` | patched | yes | new kernel, NVMe root, NFS, Samba and Proxmox backup stores validated |
| `cloud-01` `.53` | already current | no | no package backlog identified |
| `monitor-01` `.52` | already current | no | no package backlog identified |
| `sensor-01` `.55` | already current | no | no package backlog identified |

## Proxmox hosts

Both Proxmox nodes completed their patch and reboot lifecycle independently.

The nodes were never rebooted together.

Post-reboot validation confirmed:

- PVE services recovered;
- guest autostart completed;
- expected guests were running;
- storage remained available;
- the nodes returned to the expected patched kernel and PVE state.

The active PVE baseline after this cycle remains:

- PVE `9.2.20`;
- kernel `7.0.14-17-pve`.

## docker-01

`docker-01` completed its OS package update separately from application/container lifecycle management.

Routine Docker application and image updates remain owned by Komodo rather than the OS patch process.

A controlled reboot was performed because package restart analysis showed important services had been deferred even though `/var/run/reboot-required` was not present.

Post-reboot proof confirmed:

- kernel `6.18.39+rpt-rpi-v8`;
- Docker active;
- BirdNET-Go container automatically restarted;
- BirdNET-Go health reached `healthy`;
- the local BirdNET HTTP service responded successfully;
- network and DNS remained healthy;
- no package backlog remained.

## media-01

`media-01` required the largest package transaction in this cycle.

The final simulation reported:

- 259 packages upgraded;
- 10 packages newly installed;
- 0 packages removed.

The update installed the Raspberry Pi `6.18.39` kernel and refreshed Raspberry Pi firmware plus Samba/media-related packages.

Before patching, both Proxmox hosts were explicitly checked to prove:

- their isolated NFS backup stores were active;
- the backup repositories were readable;
- no `vzdump` or QEMU backup process was active.

The controlled reboot subsequently proved:

- boot ID changed;
- kernel `6.18.39+rpt-rpi-2712` became active;
- root remained on `/dev/nvme0n1p2`;
- NFS server and RPC services recovered;
- Samba recovered;
- both isolated NFS exports recovered;
- `media-backup-proxmox` on `.70` returned active and readable;
- `media-backup-proxmox-2` on `.71` returned active and readable;
- no failed systemd units remained;
- package backlog was zero.

This is also a practical recovery proof that the Proxmox backup repositories survive a controlled reboot of their NFS server.

## admin-01

`admin-01` was patched last because it is the primary administration and IaC controller.

The final transaction upgraded 86 packages with:

- 0 new packages;
- 0 removals;
- no new kernel or Raspberry Pi firmware package.

Post-patch validation confirmed:

- `remaining_updates=0`;
- `ansible-core` upgraded from `2.19.4` to `2.19.11`;
- the production Ansible inventory still parsed successfully;
- Alloy remained active;
- network and DNS remained healthy;
- no failed systemd units existed;
- no reboot was required.

The host remained on kernel `6.18.39+rpt-rpi-v8`.

## Service preservation

The patch process deliberately preserved service-specific safety gates.

Validated examples included:

- Pi-hole and Unbound DNS resolution;
- Postfix relay service;
- BirdNET-Go container health;
- Alloy monitoring;
- Samba;
- NFS exports;
- Proxmox guest availability;
- Proxmox backup repository visibility.

`edge-01` remains intentionally without Cloudflare Tunnel deployment. Patching did not change that design decision.

## Final estate state

The package-update backlog identified by the 14 September audit is now closed.

The active estate is at the expected package level from this maintenance cycle, with:

- zero known outstanding host updates from the audited backlog;
- zero known required reboots;
- no failed systemd units identified during final host validation;
- controlled reboot proof completed where necessary.

Future package updates should continue through the same controlled workflow rather than treating this document as a permanent statement that the estate can never drift again.

## Follow-on work

Patching is no longer part of the immediate 14 September backlog.

Remaining higher-value work includes:

- observe and record the first unattended isolated Proxmox backup schedule run;
- prove representative QEMU restore;
- prove application-consistent `cloud-01` recovery;
- establish an independent second backup copy;
- protect non-Proxmox data including `media-01` media content and important `admin-01` recovery identities;
- continue network and service observability improvements;
- revisit Proxmox clustering only after the dedicated Corosync NIC design is physically ready.
