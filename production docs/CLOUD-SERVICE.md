# Homelab Cloud Data Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** operational on LAN; VM-level snapshot backup proven; application-consistent restore and external access remain outstanding  
**Primary service:** Nextcloud  
**Last current-state review:** 14 September 2026

## Production identity

| Hostname | IPv4 | Platform | Purpose |
|---|---:|---|---|
| `cloud-01.jameshouse` | `192.168.2.53` | Debian 13 VM 200 on `PROXMOX .70` | Household private cloud |
| `PROXMOX` | `192.168.2.70` | Physical Proxmox VE | Hypervisor |
| `dns-01` | `192.168.2.51` | CT 101 on `Proxmox-2` | Primary local resolver |
| `dns-02` | `192.168.2.50` | CT 100 on `PROXMOX` | Secondary local resolver |
| `mail-relay-01` | `192.168.2.54` | CT 102 on `PROXMOX` | Internal SMTP relay |

## Current architecture

`cloud-01` is reproducible infrastructure around persistent application/user data.

Validated live layout:

- Debian 13 VM;
- 2 vCPU / 4 GiB-class application VM design;
- 32 GiB OS disk;
- dedicated **200 GiB** application-data disk;
- ext4 filesystem mounted at `/srv/cloud-01-data`;
- Nextcloud data under `/srv/cloud-01-data/data`;
- Docker/Compose application stack;
- application endpoint `192.168.2.53:8080`;
- local DNS record managed through homelab DNS.

The former 4 TB WD USB disk attached to `PROXMOX` is **not** part of the current cloud production storage design.

## Application stack

| Component | Current state |
|---|---|
| Nextcloud | `34.0.3-apache`, operational |
| PostgreSQL | `18.6-alpine`, healthy |
| Redis | `8.2.9-alpine`, healthy |
| Nextcloud cron | running |

Compose location:

```text
/opt/cloud-01/docker-compose.yml
```

The 14 September state confirms the expected application containers are running, PostgreSQL and Redis are healthy, the application responds on `.53:8080`, Node Exporter/Alloy are active and there are no unexpected failed systemd units.

## Redis persistence repair

Redis persistence was previously repaired by reconciling the host bind-directory ownership to the container's numeric UID/GID requirements. The Ansible role now owns that state.

Do not disable Redis `stop-writes-on-bgsave-error` as a workaround for storage/permission faults.

## IaC ownership

Current ownership model:

- Terraform/OpenTofu: VM identity, compute, networking and disk attachment;
- Ansible: Debian baseline, Docker, filesystem/mount preparation and application reconciliation;
- Compose: Nextcloud, PostgreSQL, Redis and cron;
- managed DNS: `cloud-01.jameshouse -> 192.168.2.53`;
- protected controller-side environment: application/database/recovery secrets;
- Git: desired state.

Primary paths include:

```text
IaC/terraform/proxmox/cloud-01/
IaC/ansible/playbooks/cloud-01.yml
IaC/ansible/playbooks/cloud-01-storage.yml
IaC/ansible/playbooks/cloud-stack.yml
IaC/ansible/roles/cloud_baseline/
IaC/ansible/roles/cloud_stack/
IaC/scripts/deploy-cloud-stack.sh
```

Manual GUI/container changes are not authoritative unless reconciled into IaC.

## Storage identity gate

The application role must only operate against the approved dedicated cloud data filesystem at:

```text
/srv/cloud-01-data
```

Do not bypass storage-identity or explicit deployment gates merely because the service is already live.

## SMTP

Nextcloud SMTP uses the internal relay:

```text
mail-relay-01
192.168.2.54:25
```

Gmail smart-host credentials belong on the relay, not in every application workload.

## Rebuild versus backup policy

The service follows:

> Rebuild infrastructure. Back up data.

Reproducible from code:

- Debian operating system;
- VM definition;
- Docker packages/runtime;
- container images;
- managed Compose/service configuration;
- managed DNS/configuration.

Must be protected separately because it is not reconstructable from Git alone:

- Nextcloud user files;
- PostgreSQL database;
- application state required for a consistent restore;
- protected secrets/recovery material;
- Terraform state.

The live 200 GiB data disk is production storage, **not a backup**.

## Backup state

The earlier statement that no production backup platform exists is superseded.

VM200 (`cloud-01`) has completed a successful Proxmox snapshot backup to the isolated storage:

```text
PVE node: PROXMOX .70
storage ID: media-backup-proxmox
NFS target: media-01:/srv/backup/pve-proxmox
mode: snapshot
compression: zstd
```

The VM remained running during the backup proof. This protects the VM disks/configuration at the hypervisor level.

What is **not** yet proven:

- a QEMU VM restore of `cloud-01` or another representative VM;
- application-consistent recovery of Nextcloud files plus PostgreSQL state;
- recovery of protected secrets/Terraform state;
- an independent secondary copy outside the `media-01` NVMe failure domain.

Therefore the service has a proven **VM-level backup**, but it must not yet be described as fully application-recovery-ready.

See `docs/architecture/BACKUP-STRATEGY.md` and `production docs/PROXMOX-BACKUP-RECOVERY.md`.

## External access

Current production access is LAN-only at `.53:8080`.

There is no deployed `cloudflared` connector in `edge-01` and external Cloudflare access is not part of the validated current state.

Any future public access must be separately reviewed for HTTPS/origin policy, authentication, tunnel/reverse-proxy design, credential rotation, rate limiting, recovery readiness, monitoring and rollback.

## Validation

Useful non-destructive checks include:

```bash
ssh cloud-01 'hostname; systemctl --failed --no-pager'
ssh cloud-01 'docker ps'
ssh cloud-01 'findmnt /srv/cloud-01-data'
curl -I http://192.168.2.53:8080/
```

Application-specific checks should use approved wrappers/IaC validation rather than exposing protected credentials in shell history.

## Definition of current operational state

The LAN cloud service is operational because VM identity/placement, dedicated storage, Nextcloud, PostgreSQL, Redis, cron, LAN HTTP access and DNS are proven.

Backup state is now stronger than the original build: the whole VM has a successful snapshot backup on the isolated primary repository.

Outstanding completion work:

- QEMU restore proof;
- application-consistent Nextcloud/PostgreSQL recovery proof;
- independent secondary copy;
- broader observability where useful;
- external access only if later approved.
