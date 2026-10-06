<!-- estate-authority: IaC/inventory/estate.json -->
# Estate Documentation Audit Closure — 6 October 2026

**Status:** COMPLETE  
**Audit baseline:** `docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-10-05.md`

## Closure summary

The repository-wide documentation audit identified current-looking pages that had drifted behind the validated estate. The audit baseline was merged in PR #182. Remediation was then completed in three reviewed phases.

### Phase A — authority and planning documents

**PR #183** reconciled:

- `docs/architecture/CURRENT-STATE.md`;
- `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md`;
- `docs/architecture/TARGET-STATE.md`;
- `docs/architecture/INSTALLED-SOLUTIONS-CATALOGUE.md`;
- `docs/migrations/MIGRATION-TRACKER.md`;
- repository and IaC README files;
- `runbooks/README.md` and `runbooks/registry.yml`.

Key outcomes included correct `monitor-01` discovery ownership, complete cluster guest placement, current backup selections, resolved DNS parity, router-hosted VPN operational state, Step 10 closure and removal of absent CrowdSec/Authelia/NPM from deployed-state wording.

### Phase B — hardware and production service records

**PR #184** reconciled current hardware pages and production service/recovery documents.

Key outcomes included:

- both PVE nodes recorded as `jameshouse-pve` members at pve-manager 9.2.21 / kernel `7.0.14-20-pve`;
- current guest placement and QDevice/QNetd state;
- current NFS backup schedules including VM204;
- CT105/VM203 unattended backup proof and CT104/VM204 remaining evidence gaps;
- current `admin-01`, `media-01` and `docker-01` roles;
- current monitoring/Step 10 state;
- operational Greenbone scan/evidence/report integration;
- updated sensor/Alloy/Suricata evidence;
- BirdNET physical-host backup scope;
- resolved DNS cross-resolver local-record parity.

### Phase C — network and operations documents

**PR #185** reconciled:

- the switch port map as a historical pre-SPAN-repatch snapshot while recording current port-24 mirror destination state;
- Grafana production dashboard documentation for the completed Step 10 deployment;
- selective device-identification documentation for live `monitor-01` profiling, bounded DNS evidence, generated host pages and persisted AI assessment.

## Validation

Each remediation phase passed the repository estate/documentation guard before merge.

The canonical authority remains:

1. validated live state;
2. `IaC/inventory/estate.json` for identity/address/lifecycle;
3. `docs/architecture/CURRENT-STATE.md` for human current architecture;
4. Git-managed IaC;
5. current service/runbook documentation;
6. dated audit/migration evidence.

## Historical evidence policy

Dated audits, commissioning records and migration logs were deliberately preserved as point-in-time evidence. They may contain superseded versions, placements or intermediate states and should not be rewritten merely to match today's estate.

Where a dated record conflicts with current authority, the current authority wins operationally.

## Remaining work is not documentation drift

Open technical work still recorded after this documentation closure includes:

- representative QEMU restore proof;
- application-consistent Nextcloud/PostgreSQL recovery;
- independent second backup copy/failure domain;
- CT104/VM204 first-unattended backup evidence;
- Proxmox link-fallback/single-node quorum exercises;
- optional Komodo/host-intelligence quality refinement;
- optional/deferred ingress/password-manager/web-analytics work.

Those are genuine engineering backlog items, not unresolved documentation contradictions from this audit.
