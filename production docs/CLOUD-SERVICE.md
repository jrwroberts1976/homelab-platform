# Homelab Cloud Data Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** operational on LAN; backup/restore proof and external access remain outstanding  
**Primary service:** Nextcloud  
**Last current-state review:** 12 September 2026

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

Current Compose stack:

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

The 12 September audit confirmed:

- four expected containers running;
- PostgreSQL accepting connections;
- Redis authenticated health checks passing;
- Nextcloud installed/current;
- no maintenance mode;
- no database upgrade pending;
- HTTP response on `.53:8080`;
- zero failed systemd units.

A raw unauthenticated `redis-cli ping` returning `NOAUTH` is expected because Redis authentication is enabled.

## Redis persistence repair

During the estate audit, Redis persistence had failed because the host bind directory was owned by `root:root` while the container writes as numeric UID/GID `999:1000`.

The live directory ownership was corrected and the Ansible role was updated in the earlier production fix so IaC now reconciles the required numeric ownership.

After repair, validation confirmed:

- authenticated `PING` succeeds;
- `BGSAVE` succeeds;
- persistence status is healthy;
- container health is healthy.

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

The deployment wrapper includes storage-identity and explicit-deployment approval gates. Do not bypass those controls merely because the service is already live.

## SMTP

The current IaC design routes Nextcloud SMTP through the internal relay:

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

## Backup/recovery gap

As of 12 September 2026, cloud backup/restore proof is **not complete**.

The estate audit found no active PBS/Restic production backup platform and no proven end-to-end Nextcloud restore.

Do not describe the cloud service as fully recovery-ready until:

- important user data has an independent backup;
- PostgreSQL has an application-consistent protection/restore path;
- protected secrets/state are recoverable;
- a representative restore has been tested.

See `docs/architecture/BACKUP-STRATEGY.md`.

## External access

Current production access is LAN-only at `.53:8080`.

There is no deployed `cloudflared` connector in `edge-01` and external Cloudflare access is not part of the validated current state.

Any future public access must be a separately reviewed change covering:

- HTTPS/origin policy;
- authentication controls;
- tunnel/reverse-proxy design;
- credential storage/rotation;
- rate limiting where appropriate;
- backup/recovery readiness;
- monitoring/logging;
- rollback.

## Validation

Useful non-destructive service checks include:

```bash
ssh cloud-01 'hostname; systemctl --failed --no-pager'
ssh cloud-01 'docker ps'
ssh cloud-01 'findmnt /srv/cloud-01-data'
curl -I http://192.168.2.53:8080/
```

Application-specific checks should use the approved wrapper/IaC validation rather than exposing protected credentials in shell history.

## Definition of current operational state

The LAN cloud service is operational because:

- VM identity/placement are proven;
- dedicated 200 GiB data storage is mounted;
- Nextcloud is running;
- PostgreSQL is healthy;
- Redis is healthy and persistence works;
- cron is running;
- LAN HTTP access works;
- DNS works;
- zero failed systemd units were observed.

Outstanding completion work:

- production backup implementation;
- restore testing;
- broader observability/logging where useful;
- external access only if later approved.
