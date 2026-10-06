<!-- estate-authority: IaC/inventory/estate.json -->
# Phase A Documentation Reconciliation — 6 October 2026

**Status:** COMPLETE ON BRANCH; PR/CI VALIDATION REQUIRED

Phase A reconciles the authority/operator documents identified by the 5 October estate documentation audit.

Updated files:

- `README.md`
- `IaC/README.md`
- `IaC/ansible/README.md`
- `docs/architecture/CURRENT-STATE.md`
- `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md`
- `docs/architecture/TARGET-STATE.md`
- `docs/architecture/INSTALLED-SOLUTIONS-CATALOGUE.md`
- `docs/migrations/MIGRATION-TRACKER.md`
- `runbooks/README.md`
- `runbooks/registry.yml`

Key reconciliations:

- `monitor-01` is the single active network-discovery owner after the 27 September cutover;
- `Proxmox-2` source discovery timers are disabled/inactive and retained state is rollback/history evidence;
- current guest placement includes CT104, CT105, VM203 and VM204;
- current backup schedules include VM204 and unattended CT105/VM203 evidence is recorded;
- router-hosted OpenVPN is operational, not implementation-in-progress;
- the DNS cross-resolver local-record parity defect is resolved in current IaC;
- Step 10 Grafana estate foundation is complete;
- final 5 October patch telemetry is 15 reporting, 0 pending, 0 security, 0 reboot, 15 unattended-upgrades installed, 0 automatic reboot;
- CrowdSec, Authelia and Nginx Proxy Manager are not currently deployed;
- Jenkins is already removed;
- historical migration/audit records remain historical evidence rather than current authority.

The previous backlog referenced a 20-step programme but did not authoritatively enumerate Steps 11–20. The reconciled backlog records that gap explicitly and does not invent replacement step names.

No live infrastructure changes are included in Phase A.
