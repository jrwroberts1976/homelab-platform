# Active Infrastructure Backlog

**Last reconciled:** 2026-10-07  
**Authority:** Planning register only. Validate implementation claims against `docs/architecture/CURRENT-STATE.md`, `IaC/inventory/estate.json` and live evidence.  
**Current documentation work:** repository-wide documentation audit/remediation COMPLETE through PRs #182–#185.

## Working rules

- Work in priority order unless James explicitly reprioritises.
- Update this file when a project closes, changes scope or is reprioritised.
- Verify live state before marking implementation complete.
- Keep accepted risks and deliberately deferred work out of the active implementation queue.
- Do not silently reopen completed work based on stale historical plans.
- Do not invent missing roadmap steps or names.
- Estimates are hands-on engineering effort, excluding observation time and unexpected failures.

## Closed priority override — estate patching

**Status:** COMPLETE — 5 October 2026

Final validated telemetry:

```text
reporting hosts:             15
pending updates:             0
security updates pending:    0
reboots required:            0
unattended-upgrades present: 15
automatic reboots enabled:   0
```

Both PVE nodes were upgraded one at a time and validated at pve-manager 9.2.21 / kernel `7.0.14-20-pve`. Required Raspberry Pi kernel maintenance was completed with controlled reboots and post-change validation. Docker application image lifecycle remains owned separately by the Komodo/container workflow.

## Prioritised projects

| # | Project | Status | Estimated effort | Remaining outcome |
|---|---|---|---|---|
| 1 | Greenbone and AI-assisted morning management report | COMPLETE | — | Operational factual + AI-assisted reporting with fail-safe factual fallback, source provenance and factual network-inventory v1 pinned to `monitor-01` |
| 2 | Security and monitoring integration | BASELINE COMPLETE / TUNING | **2–4 hours when resumed** | Add only demonstrated actionable gaps; CrowdSec remains absent and must not be treated as a current source |
| 3 | Grafana dashboards and AI host intelligence | FOUNDATION COMPLETE / QUALITY REFINEMENT | **2–5 days** | Estate dashboard/patch/node foundation complete; continue host-intelligence/manual-review/version-history refinement without treating missing telemetry as healthy |
| 4 | Homelab documentation audit | **COMPLETE — 6 OCTOBER 2026** | — | Audit baseline PR #182; remediation PRs #183, #184 and #185 completed and guard-validated |
| 5 | Password manager | PLANNED / OPTIONAL | **1–2 days** | Select product/design deliberately; HTTPS/MFA, off-host backup, restore proof and emergency access required |
| 6 | Backup and disaster recovery | OUTSTANDING | **2–4 days** | Representative QEMU restore, application-consistent Nextcloud/PostgreSQL recovery, independent second copy and protected recovery identities |
| 7 | Komodo hardening | OUTSTANDING | **1–3 days** | HTTPS, low-risk update/rollback proof and only justified additional onboarding |
| 8 | Legacy infrastructure cleanup | REVIEW REQUIRED | **1–2 days** | Remove unreferenced pre-cluster rollback LVs only after explicit confidence review; reconcile superseded paths where still justified; Jenkins already removed |
| 9 | Web analytics | OPTIONAL | **1–3 days** | Portfolio/Cloudflare/Umami/Grafana-Loki evidence-led analytics work |
| 10 | Cloudflare Tunnel | DEFERRED | **1–2 days if approved** | `edge-01` reserved; deploy `cloudflared` only for a real approved service requirement |

### Current sequence

1. Documentation audit/remediation is closed.
2. Return to Project 3 host-intelligence quality/refinement if desired.
3. Continue backup/recovery depth and Komodo hardening according to priority.
4. Optional/deferred items are not automatic commitments.

## Delivery-step history

The repository backlog contains authoritative named/evidenced entries through Step 10 only. A historical 20-step programme was referenced, but authoritative names for Steps 11–20 are not present here. Do not invent them.

### Steps 1–8

**COMPLETE.** Management-report verification, AI-assisted interpretation/fallback, source provenance, end-to-end delivery, security-signal audit, Zabbix/Loki freshness, and privacy-safe Pi-hole evidence integration were implemented and verified during 23–24 September 2026. Detailed evidence remains in Git history and dated records.

### Management-report network inventory v1 extension — COMPLETE

Completed 7 October 2026 and recorded in `docs/architecture/MANAGEMENT-REPORT-NETWORK-V1-CLOSURE-2026-10-07.md`.

Delivered/verified:

- factual network inventory sourced only from the active `monitor-01` network collector;
- retained inventory total, currently-online count and first-observed-in-24h count;
- freshness derived from the `homelab_network_hosts.prom` textfile mtime with a 15-minute threshold;
- stale, missing or invalid evidence suppresses counts instead of presenting them as current facts;
- explicit guards against impossible counts such as online hosts exceeding retained inventory;
- no `enrichment.json` dependency;
- no OS-change, port-change or device-identity-change claims;
- 9 management-report tests passed;
- Ansible syntax check passed;
- live production report and provenance validated;
- repeat deployment completed with `changed=0`, `unreachable=0`, `failed=0`;
- implementation committed as `abb5c90`.

### Step 9/20 — Representative integration and regression tests — COMPLETE

PR #137 merged at `8b1db383066ccbe43d83a239a5aa2540c219eb42`. Collector/renderer regressions, production deployment, idempotence, live 24-hour Pi-hole evidence and scheduled/manual mail delivery were verified.

### Step 10/20 — Estate-wide Grafana overview — COMPLETE

Closure evidence is recorded in `docs/architecture/STEP-10-ESTATE-GRAFANA-CLOSURE-2026-10-05.md`.

Delivered/verified:

- Home/operations overview;
- Hosts dashboard;
- Patch & Reboot Status dashboard;
- Node Detail navigation;
- current `homelab_patch_*` metrics only;
- live visual validation using `now-24h -> now`;
- patch telemetry `15 / 0 / 0 / 0 / 15 / 0`;
- production monitoring deployment succeeded;
- repeat Ansible run `changed=0`, `unreachable=0`, `failed=0`;
- PRs #179, #180 and #181 merged.

**Step 10 status: CLOSED.**

### Steps 11–20

**STATUS: NOT AUTHORITATIVELY ENUMERATED IN THIS REPOSITORY.**

Recover/reconcile an authoritative prior checklist before using those step numbers. Do not create substitute names merely to fill the sequence.

## Completed / accepted decisions

| Area | Decision | Backlog treatment |
|---|---|---|
| Router VPN | ASUS router-hosted OpenVPN operational and accepted | CLOSED; maintenance/recovery documentation only |
| Proxmox storage / HA | Node-local guest storage + two-node cluster + QDevice; manual backup-based recovery accepted | SHARED STORAGE / AUTOMATIC HA OUT OF SCOPE unless explicitly reopened |
| Legacy HP ProCurve | Existing hardware retained; legacy management risk acknowledged | HARDENING only if deliberately reopened |
| `media-01` | Kodi/media service operational; NFS backup-target role retained | NORMAL OPERATIONS |
| Home Assistant | `home-01` commissioned and operational | NORMAL OPERATIONS; only explicitly requested monitoring/recovery work |
| Jenkins | Already removed | CLOSED — do not create retirement task |
| Network discovery | Single-owner cutover to `monitor-01` completed 27 September | CLOSED MIGRATION; source timers on `Proxmox-2` remain disabled/inactive |
| Management-report network inventory v1 | Factual inventory/presence/freshness evidence pinned to `monitor-01`; no enrichment/change claims | CLOSED — future richer change detection requires a separately reviewed evidence model |
| CT105 / VM203 unattended backup evidence | Observed | CLOSED EVIDENCE GAP |
| CrowdSec | Not installed anywhere in active estate | ABSENT / DEFERRED; do not list as current telemetry |
| Authelia | Not deployed | ABSENT; Cloudflare remains intended MFA boundary for future public exposure |

## Documentation audit / remediation closure

The audit baseline is `docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-10-05.md` (PR #182).

Remediation completed in three phases:

- **Phase A — PR #183:** authority/current-state/backlog/migration/target-state/catalogue/README/runbook indexes;
- **Phase B — PR #184:** current hardware records and production service/recovery documents;
- **Phase C — PR #185:** switch-map historical/current boundary, Grafana production documentation and device-identification implementation state.

Each remediation PR passed the repository estate/documentation guard before merge.

Historical audits and migration records remain point-in-time evidence and are intentionally not rewritten to look current.

## Completion-notification rule

Historical numbered steps used one completion email per closed step. For any future numbered plan, record whether notification was actually sent; do not claim delivery merely because a step was closed. A planning register does not itself send mail.

## Maintenance note

Current operational truth is `IaC/inventory/estate.json` plus `CURRENT-STATE.md`. This backlog describes intent/priorities and must not override those authorities.
