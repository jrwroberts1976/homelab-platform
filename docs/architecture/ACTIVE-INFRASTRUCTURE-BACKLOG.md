# Active Infrastructure Backlog

**Last reconciled:** 2026-10-12
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

## Programme progress snapshot

As of 10 October 2026:

| View | Progress | Meaning |
|---|---:|---|
| Authoritative delivery steps 1–10 | **10/10 complete — 100%** | All named/evidenced delivery steps currently recoverable from the repository are closed |
| Prioritised project areas fully closed | **4/10 — 40%** | Projects 1, 2, 3 and 4 are fully complete |
| Prioritised project areas with baseline/foundation complete | **4/10 — 40%** | Projects 1–4 have either closed or reached baseline/foundation-complete state |
| Optional/deferred projects | **3/10** | Projects 5, 9 and 10 are not automatic commitments |
| Genuine outstanding/review projects | **3/10** | Projects 6, 7 and 8 contain substantive remaining engineering work |

**Practical programme estimate:** approximately **70–80% complete** when optional/deferred work is excluded and partially completed foundations are recognised. This is a planning estimate, not a formal weighted burn-down metric.

The core platform is largely built. Remaining work is now concentrated in recovery proof, hardening, refinement and technical-debt cleanup rather than major missing infrastructure.

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
| 2 | Security and monitoring integration | **COMPLETE — 7 OCTOBER 2026** | — | Monitoring core, Zabbix, Suricata/Zeek passive sensor and evidence integration closure-validated; CrowdSec remains absent/deferred and is not a current source |
| 3 | Grafana dashboards and AI host intelligence | **COMPLETE — 10 OCTOBER 2026** | — | Production host-intelligence evidence semantics, scheduled AI resolver, bounded assessment history, conditional Grafana presentation and estate-wide regression closure proven |
| 4 | Homelab documentation audit | **COMPLETE — 6 OCTOBER 2026** | — | Audit baseline PR #182; remediation PRs #183, #184 and #185 completed and guard-validated |
| 5 | Password manager | PLANNED / OPTIONAL | **1–2 days** | Select product/design deliberately; HTTPS/MFA, off-host backup, restore proof and emergency access required |
| 6 | Backup and disaster recovery | OUTSTANDING | **2–4 days** | Representative QEMU restore, application-consistent Nextcloud/PostgreSQL recovery, independent second copy and protected recovery identities |
| 7 | Komodo hardening and Docker image lifecycle | **PARTIAL — HTTPS/WSS COMPLETE; BIRDNET CANARY COMPLETE 12 OCTOBER 2026** | **1–2 days remaining** | Strict Core HTTPS and CA-validated Periphery WSS complete; BirdNET controlled image/update/rollback canary proven; remaining work is the estate-wide Docker image/update audit, release-note and dependency review, phased container updates, and only justified additional Periphery onboarding |
| 8 | Legacy infrastructure cleanup | REVIEW REQUIRED | **1–2 days** | Remove unreferenced pre-cluster rollback LVs only after explicit confidence review; reconcile superseded paths where still justified; Jenkins already removed |
| 9 | Web analytics | OPTIONAL | **1–3 days** | Portfolio/Cloudflare/Umami/Grafana-Loki evidence-led analytics work |
| 10 | Cloudflare Tunnel | DEFERRED | **1–2 days if approved** | `edge-01` reserved; deploy `cloudflared` only for a real approved service requirement |

## Choose what to do next

The remaining non-optional work has different goals. Choose according to the outcome you want rather than treating the list as a mandatory sequence.

| Choice | Project | Why choose it next | Effort | What completion buys |
|---|---|---|---:|---|
| **A — strongest resilience gain** | **#6 Backup and disaster recovery** | Biggest remaining operational-risk reduction | **2–4 days** | Proven QEMU restore, application-consistent Nextcloud/PostgreSQL recovery, independent second copy and stronger recovery confidence |
| **C — harden container operations** | **#7 Komodo hardening and Docker image lifecycle** | Reduces control-plane and container-update risk across the managed Docker estate | **1–2 days** | HTTPS/WSS plus a current image inventory, deliberate version decisions, phased updates and proven low-risk rollback behaviour |
| **D — reduce technical debt** | **#8 Legacy infrastructure cleanup** | Removes old rollback/superseded state after confidence review | **1–2 days** | Cleaner estate and less ambiguity, without changing active architecture |

### Decision shortcuts

- If the priority is **resilience and recovery confidence**, choose **Project 6**.
- If the priority is **container-management security and rollback confidence**, choose **Project 7**.
- If the priority is **reducing legacy clutter and technical debt**, choose **Project 8**.
- Projects **5, 9 and 10 remain optional/deferred** and should only be started because you specifically want the capability.

### Current sequence

1. **Current user-selected priority: investigate Greenbone vulnerability-detection coverage before performing further production container upgrades.**
2. Determine whether the current Greenbone feed contains detection coverage for known relevant vulnerabilities such as `CVE-2026-15815`, whether affected product/version evidence is being discovered, and whether scan configuration/authentication/QoD prevents applicable findings from being reported.
3. Correct any Greenbone feed, scanner, credential, target, VT-selection or product/version-detection problem found and prove the fix with a controlled validation scan.
4. Do not perform further production Docker image upgrades until the Greenbone investigation and validation scan are complete.
5. After Greenbone detection confidence is restored, resume Project 7's estate-wide image review and phased container updates using the completed BirdNET-Go lifecycle canary as the reference process.
6. After Project 7 closes, default engineering priority returns to **Project 6 (Backup/DR)**, then **Project 8 (legacy cleanup)** unless James reprioritises.
7. Project 3 is closed; future host-intelligence changes require a separately reviewed scope.
8. Optional/deferred items are not automatic commitments.

### Project 7 — Docker container lifecycle extension — IN PROGRESS 12 OCTOBER 2026

**Current gate:** further production image upgrades are paused pending the
Greenbone vulnerability-detection investigation and a successful validation
scan. The purpose is to avoid applying known fixes before understanding why the
existing vulnerability-management control did not surface them.

Requested scope:

- produce a read-only inventory of running containers, Compose projects, image tags and digests across `docker-01`, `monitor-01`, `cloud-01`, `greenbone-01` and the Komodo management stack on `komodo-01`;
- identify floating tags, stale images, deliberate pins and application/version dependencies;
- check current upstream releases and release notes before changing production images;
- classify updates by operational risk, with stateful services such as Nextcloud/PostgreSQL/Redis, Greenbone and Komodo/Mongo requiring explicit backup/compatibility checks;
- update in small batches rather than blanket-pulling the estate;
- validate service health after each batch and retain a clear rollback path to the previously proven image/tag/digest;
- codify a repeatable Docker image-lifecycle process using automatic update detection and visibility, human approval before changing Git desired state or deploying, scoped Komodo ResourceSync, post-change health validation and retained rollback images; do not enable blanket unattended container upgrades;
- use the completed BirdNET-Go canary as the reference implementation for that lifecycle process across the remaining managed estate;
- do not add extra Periphery hosts unless there is a demonstrated management benefit.

### BirdNET-Go controlled lifecycle canary — COMPLETE 12 OCTOBER 2026

Closure evidence is recorded in
`docs/architecture/PROJECT-7-BIRDNET-LIFECYCLE-PILOT-2026-10-12.md`.

Validated outcome:

- upgraded BirdNET-Go from `20260823` to `20261010`;
- captured the previous image digest and retained the previous image for rollback;
- validated persistent `/config` and `/data` mounts before the update;
- validated the replacement container as healthy with failing streak `0`;
- updated the Git-backed Komodo declaration to `20261010`;
- refreshed ResourceSync and observed exactly one intended Deployment update;
- verified `pending_deploys=0` before applying the desired-state change;
- scoped `RunSync` specifically to the `birdnet-go` Deployment;
- proved Git, Komodo desired state, host Compose configuration and running
  container all converged on `20261010`;
- left automatic update disabled and update polling enabled;
- retained `20260823` locally as the proven rollback image.

The low-risk Komodo update/rollback proof is therefore complete. Project 7
remains open for the remaining estate-wide image review and phased updates.

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

### Security and monitoring integration — COMPLETE

Completed 7 October 2026 and recorded in `docs/architecture/SECURITY-MONITORING-INTEGRATION-CLOSURE-2026-10-07.md`.

Closure validation demonstrated:

- Prometheus, Alertmanager, Loki, Grafana and Blackbox Exporter healthy on `monitor-01`;
- every active Prometheus target reported `up`, with no non-healthy targets returned;
- Zabbix core services active on `zabbix-01` with no failed units or matching recent server errors;
- Suricata, Alloy, node exporter and managed `homelab-zeek.service` active on `sensor-01`;
- `zeekctl status` reported the standalone worker running and live protocol logs were current;
- Zeek capture loss was 0.0% with zero gaps;
- Suricata kernel-drop percentage was approximately 0.0002%, far below the configured 0.1% warning level;
- sensor evidence reported capture health `healthy`, both 24-hour coverage windows `complete`, and zero assurance gaps;
- bounded Suricata and Zeek evidence reached the management-report evidence path;
- the current monitoring/security/reporting pipeline contains no CrowdSec dependency.

Individual Suricata/Zeek detections remain normal security-operations inputs. They may justify investigation or tuning, but they do not keep the integration project open.

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

### Project 3 — host-intelligence quality refinement — COMPLETE

Closed 10 October 2026.

Closure-validated outcomes:

- managed-host OS, architecture and kernel evidence comes from fresh Zabbix Agent 2 facts;
- authoritative managed OS evidence overrides weaker Nmap inference;
- bounded AI assessment change history is retained;
- the AI resolver timer is enabled and active on `monitor-01`;
- managed Zabbix OS source state is explicit as `fresh`, `stale`, `missing` or `not_expected`;
- Zabbix OS last-observed time is published as a numeric Prometheus gauge;
- live validation found 15 managed hosts fresh, 0 stale, 0 missing, all 15 authoritative;
- exactly 15 Zabbix OS timestamp series were present;
- all 50 generated host dashboards parsed successfully;
- panel 26 appeared on exactly the 15 devices with timestamp evidence;
- repeat deployment completed with `changed=0`, `unreachable=0`, `failed=0`;
- the full monitoring regression suite passed 143 tests;
- the 26-panel host template had no duplicate IDs and no required Project 3 panels missing.

Key implementation commits include `26409916`, `027b319a`, `712126b2`,
`6330dd9a`, with the reconciled feature reaching `main` through `96b6a2ff`.

Future host-intelligence improvements are separate enhancements and do not keep
Project 3 open.

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
| Security and monitoring integration | Monitoring core, Zabbix and passive Suricata/Zeek evidence path closure-validated on 7 October 2026 | CLOSED — individual detections/tuning are normal operations; new tooling requires separate scope |
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
