<!-- estate-authority: IaC/inventory/estate.json -->
# Phase B Hardware and Service Documentation Reconciliation — 6 October 2026

This document records the second remediation phase from `ESTATE-DOCUMENT-AUDIT-2026-10-05.md`.

## Scope

- current hardware records under `docs/hardware/`;
- current production service documents under `production docs/`;
- stale version, placement, backup, cluster and service-state claims only;
- dated historical audit evidence remains unchanged.

Authoritative sources are `IaC/inventory/estate.json`, `docs/architecture/CURRENT-STATE.md`, validated 5 October maintenance evidence and current Git-managed IaC.

## Hardware records reconciled

- `docs/hardware/PROXMOX.md`
- `docs/hardware/Proxmox-2.md`
- `docs/hardware/admin-01.md`
- `docs/hardware/media-01.md`
- `docs/hardware/docker-01.md`

Key corrections include the live `jameshouse-pve` cluster state, current guest placement, PVE 9.2.21 / kernel 7.0.14-20-pve evidence, QDevice/QNetd, current backup schedules, active SPAN/sensor state, `admin-01` kernel/QNetd role, `media-01` production NFS-backup role and `docker-01` Komodo/patch state.

## Production service documents reconciled

- `production docs/MONITORING-SERVICE.md`
- `production docs/PROXMOX-BACKUP-RECOVERY.md`
- `production docs/GREENBONE-SERVICE.md`
- `production docs/NETWORK-SENSOR-SERVICE.md`
- `production docs/BIRDNET-SERVICE.md`
- `production docs/MEDIA-SERVICE.md`
- `production docs/DNS-SERVICE-RECOVERY-PLAN.md`

Key corrections include VM202 placement for `monitor-01`, completed Step 10 dashboards, `monitor-01` discovery ownership, current patch telemetry, VM204 in the PROXMOX backup job, CT105/VM203 unattended proof, CT104/VM204 as the remaining schedule-evidence gaps, live Greenbone scan/evidence/report integration, updated Suricata/Alloy evidence, BirdNET physical-host backup scope, current media/NFS role and resolved DNS cross-resolver local-record parity.

## Preserved evidence

Dated audits and migration records were not rewritten to make them look current. Historical observations remain point-in-time evidence and are superseded operationally by `CURRENT-STATE.md` and these current service/hardware records.

## Validation requirement

Before merge, the repository estate/documentation guard must pass against the complete branch. No infrastructure mutation is part of this phase.
