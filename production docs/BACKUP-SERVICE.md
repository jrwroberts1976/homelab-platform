# Homelab Data Protection Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** target design approved; implementation follows `cloud-01` deployment  
**Primary principle:** rebuild infrastructure from code; back up persistent data

## Current direction

Proxmox Backup Server is deferred.

The immediate platform priority is the private-cloud service `cloud-01.jameshouse` at `192.168.2.52`, with Nextcloud, PostgreSQL and Redis deployed through IaC. The VM and software stack are reproducible; only persistent data and recovery state require backup.

See:

- `production docs/CLOUD-SERVICE.md`
- `docs/architecture/BACKUP-STRATEGY.md`

## Protected data

Initial protection scope:

- Nextcloud user files
- Nextcloud/PostgreSQL database state required for consistent recovery
- Terraform/OpenTofu state
- protected non-Git configuration
- SOPS/age recovery material not reconstructable elsewhere
- selected application data from TestServer and physical Linux/Pi systems
- other user-created household data

Do not spend backup capacity on replaceable operating systems, container images, package caches or other artifacts reproducible from Git/IaC.

## Copies

Important data requires at least two independent copies.

The first copy may live on the `cloud-01` data device. The second must be on separate physical storage or another independent failure domain.

A Nextcloud sync client is not by itself considered the second backup copy.

## Candidate data disk

The former DietPi 4 TB USB disk is currently attached to `PROXMOX` and undergoing a full destructive surface test.

Disk:

- `WDC WD40EZRX-00SPEB0`
- serial `WD-WCC4E0670079`
- 4.00 TB / 3.64 TiB
- UGREEN/Realtek USB bridge

SMART before test:

- reallocated sectors: 0
- pending sectors: 7
- offline uncorrectable sectors: 2
- UDMA CRC errors: 10

Do not create the production filesystem until the surface test finishes and post-test SMART is reviewed.

A passing result may permit use as a primary working data disk, but because the drive has a history of pending/uncorrectable sectors it must not become the only copy of irreplaceable data.

## DietPi retirement

`DietPi` at `192.168.2.48` is no longer part of the target critical-service architecture.

A remaining dependency was found on `PROXMOX`: its resolver configuration still referenced `.48`. That host has now been manually moved to `192.168.2.51` and `192.168.2.50`.

Before DietPi is considered fully retired, verify the ASUS DHCP configuration and representative clients no longer receive or depend on `.48`.

The Pi 3 itself can then be retained as spare/reuse hardware.

## Recovery proof

Before the private cloud is treated as production:

- rebuild `cloud-01` from IaC;
- restore the database;
- restore a representative set of user files;
- prove Nextcloud can read and serve the restored data;
- prove a client can sync again;
- confirm the second independent copy exists.

## Future PBS trigger

Reconsider Proxmox Backup Server later if any of these become valuable enough to justify the storage and operational overhead:

- rapid whole-VM/LXC restore
- native Proxmox snapshot retention
- deduplicated guest backups
- guest-level point-in-time recovery
- a second backup appliance/failure domain

PBS is therefore an optional future recovery accelerator, not a prerequisite for the IaC-first platform.
