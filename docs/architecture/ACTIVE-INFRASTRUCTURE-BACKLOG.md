# Active Infrastructure Backlog

**Last reconciled:** 2026-10-06  
**Authority:** Planning register only. Validate implementation claims against `docs/architecture/CURRENT-STATE.md`, `IaC/inventory/estate.json` and live evidence.  
**Current documentation work:** Phase A reconciliation from `ESTATE-DOCUMENT-AUDIT-2026-10-05.md` is IN PROGRESS.

## Working rules

- Work in priority order unless James explicitly reprioritises.
- Update this file when a project closes, changes scope or is reprioritised.
- Verify live state before marking implementation complete.
- Keep accepted risks and deliberately deferred work out of the active implementation queue.
- Do not silently reopen completed work based on stale historical plans.
- Do not invent missing roadmap steps or names. If a historical roadmap cannot be recovered from authoritative evidence, record the gap explicitly.
- Estimates are hands-on engineering effort, excluding observation time and unexpected failures.

## Closed priority override — estate patching

**Status:** COMPLETE — 5 October 2026

The controlled Debian/Proxmox patch cycle is closed.

Final validated telemetry:

```text
reporting hosts:            15
pending updates:            0
security updates pending:   0
reboots required:           0
unattended-upgrades present:15
automatic reboots enabled:  0
```

Both PVE nodes were upgraded one at a time and validated at pve-manager 9.2.21 / kernel `7.0.14-20-pve`. `admin-01` and `docker-01` completed required Raspberry Pi kernel updates; service-specific validation passed. Docker application image lifecycle remains owned separately by the Komodo/container workflow.

## Prioritised projects

| # | Project | Status | Estimated effort | Remaining outcome |
|---|---|---|---|---|
| 1 | Greenbone and AI-assisted morning management report | COMPLETE | — | Operational factual + AI-assisted reporting with fail-safe factual fallback and source provenance |
| 2 | Security and monitoring integration | BASELINE COMPLETE / TUNING | **2–4 hours when resumed** | Only add demonstrated actionable gaps; CrowdSec is absent and must not be treated as a current source |
| 3 | Grafana dashboards and AI host intelligence | FOUNDATION COMPLETE / AI QUALITY REMAINS | **2–5 days for remaining refinement** | Step 10 estate Home/Hosts/Patch/Node Detail foundation complete; continue evidence-linked host intelligence/manual-review/version-history refinement without treating missing telemetry as healthy |
| 4 | Homelab documentation audit | **IN PROGRESS — REMEDIATION** | **1–2 days** | Read-only audit completed in PR #182; reconcile current-looking stale architecture, migration, runbook, hardware and service docs while preserving dated evidence |
| 5 | Password manager | PLANNED / OPTIONAL | **1–2 days** | Select product/design deliberately; HTTPS/MFA, off-host backup, restore proof and emergency access required |
| 6 | Backup and disaster recovery | OUTSTANDING | **2–4 days** | Representative QEMU restore, application-consistent Nextcloud/PostgreSQL recovery, independent second copy and protected recovery identities |
| 7 | Komodo hardening | OUTSTANDING | **1–3 days** | HTTPS, low-risk update/rollback proof and only justified additional onboarding |
| 8 | Legacy infrastructure cleanup | REVIEW REQUIRED | **1–2 days** | Remove unreferenced pre-cluster rollback LVs only after explicit confidence review; reconcile superseded paths/docs; Jenkins already removed |
| 9 | Web analytics | OPTIONAL | **1–3 days** | Portfolio/Cloudflare/Umami/Grafana-Loki evidence-led analytics work |
| 10 | Cloudflare Tunnel | DEFERRED | **1–2 days if approved** | `edge-01` reserved; deploy `cloudflared` only for a real approved service requirement |

### Current sequence

1. Finish repository documentation reconciliation.
2. Return to remaining Project 3 host-intelligence quality work if still desired.
3. Continue backup/recovery depth and Komodo hardening according to priority.
4. Optional/deferred items are not automatic commitments.

## Delivery-step history

The original register repeatedly referred to a 20-step delivery plan, but the repository backlog itself contained named/evidenced entries only through Step 9. **Do not invent Step 11–20 names.** If an authoritative earlier checklist is recovered, reconcile it here before resuming numbered-step execution.

### Step 1/20 — Review management email — VERIFIED

Verified 23 September 2026: 15/15 host evidence, Greenbone and sensor evidence present, management email delivered. Closure notification sent.

### Step 2/20 — Verify reporting pipeline — VERIFIED

Collector/renderer/mailer and stale/missing-evidence handling verified. Closure email was blocked at the time; historical notification state is retained in prior Git history.

### Step 3/20 — Add AI-assisted interpretation — COMPLETE

OpenAI-assisted briefing added with bounded/sanitised evidence, `store=false`, timeout/factual fallback, isolated tests, live API test, systemd integration and production enablement. Closure notification sent.

### Step 4/20 — Separate factual evidence from AI interpretation — COMPLETE

Deterministic verified-evidence/provenance section implemented and production-tested; AI remains interpretation only. Closure notification sent.

### Step 5/20 — Validate end-to-end delivery and factual fallback — COMPLETE

Live service/SMTP/Gmail delivery and factual fallback were proven. Closure notification sent.

### Step 6/20 — Audit Suricata, Zeek, CrowdSec and Pi-hole — COMPLETE

Suricata/Zeek and DNS service evidence verified. CrowdSec confirmed absent across the active estate. Nginx Proxy Manager also absent/deferred. Closure notification sent.

### Step 7/20 — Zabbix and Loki evidence freshness — COMPLETE

Loki showed 15/15 expected hosts in recent windows. Zabbix item freshness was independently verified through read-only PostgreSQL evidence rather than widening report-token privileges. Closure notification sent.

### Step 8/20 — Add only missing actionable evidence — COMPLETE

Privacy-safe Pi-hole event-token ingestion through Alloy/Loki deployed on both DNS hosts. Synthetic privacy test and sampled production privacy checks passed. The carried-forward report integration was completed under Step 9. Closure notification subsequently reconciled/sent.

### Step 9/20 — Representative integration and regression tests — COMPLETE

PR #137 merged at `8b1db383066ccbe43d83a239a5aa2540c219eb42`. Collector/renderer regressions, production deployment, idempotence, live 24-hour Pi-hole evidence and scheduled/manual mail delivery were verified. Closure notification sent.

### Step 10/20 — Estate-wide Grafana overview — COMPLETE

Closure evidence is recorded in `docs/architecture/STEP-10-ESTATE-GRAFANA-CLOSURE-2026-10-05.md`.

Delivered/verified:

- Home/operations overview;
- Hosts dashboard;
- Patch & Reboot Status dashboard;
- Node Detail navigation;
- current `homelab_patch_*` metrics only;
- no retired patch metrics in the reconciled dashboards;
- live visual validation using `now-24h -> now`;
- patch telemetry `15 / 0 / 0 / 0 / 15 / 0`;
- production monitoring deployment succeeded;
- repeat Ansible run `changed=0`, `unreachable=0`, `failed=0`;
- PRs #179, #180 and #181 merged.

**Step 10 status: CLOSED.**

### Steps 11–20

**STATUS: NOT AUTHORITATIVELY ENUMERATED IN THIS REPOSITORY BACKLOG.**

The prior file referenced a 20-step programme but did not contain authoritative named entries for Steps 11–20. Recover/reconcile an authoritative prior checklist before using those numbers. Do not create substitute names merely to fill the sequence.

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
| CT105 / VM203 unattended backup evidence | Observed | CLOSED EVIDENCE GAP |
| CrowdSec | Not installed anywhere in active estate | ABSENT / DEFERRED; do not list as current telemetry |
| Authelia | Not deployed | ABSENT; Cloudflare remains intended MFA boundary for future public exposure |

## Documentation reconciliation — current work

The 5 October audit is merged as PR #182 and is the remediation baseline.

Phase A focuses on operator/authority documents:

- `CURRENT-STATE.md`;
- this backlog;
- `MIGRATION-TRACKER.md`;
- `TARGET-STATE.md`;
- `INSTALLED-SOLUTIONS-CATALOGUE.md`;
- repository/IaC READMEs;
- `runbooks/README.md` and `runbooks/registry.yml`.

Phase B will reconcile current hardware and production service runbooks. Dated historical audits should be preserved as evidence and clearly marked historical rather than rewritten into present tense.

## Completion-notification rule

Historical steps used one completion email per closed numbered step. For any future numbered plan, record whether notification was actually sent; do not claim delivery merely because a step was closed. A planning register does not itself send mail.

## Maintenance note

Current operational truth is `IaC/inventory/estate.json` plus `CURRENT-STATE.md`. This backlog describes intent/priorities and must not override those authorities.
