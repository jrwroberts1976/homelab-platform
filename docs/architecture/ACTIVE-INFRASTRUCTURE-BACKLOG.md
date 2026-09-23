# Active Infrastructure Backlog

**Last reconciled:** 2026-09-23  
**Authority:** This file records James's latest agreed project priorities, estimates, completed work and accepted risks. Check `docs/architecture/CURRENT-STATE.md` and `IaC/inventory/estate.json` before any implementation. This is a planning register, not evidence that an outstanding change has been deployed.

## Working rules

- Work in priority order unless James explicitly reprioritises.
- Update this file whenever James closes, adds, reprioritises or changes the scope of a project. Keep status, estimate and evidence links current.
- Verify live state before marking implementation complete; record the relevant PR, issue, test or run evidence.
- **Completion-email rule (2026-09-23):** After each individual step in the agreed 20-step delivery plan is verified and closed, email James a short completion notice using the established homelab reporting address or his confirmed email destination. Include the step number/name, outcome, evidence/test results, relevant GitHub link, outstanding caveats, **the complete remaining task/step checklist with current statuses and estimates**, and the next step. Mark the just-closed step completed, preserve priority order and distinguish blocked, planned, optional and deferred work. Record email delivery status in the closure note; if sending fails, keep the email action outstanding and report the failure rather than claiming notification succeeded. This is an event-driven workflow when steps are closed, not a daily digest. Do not send an email merely because a checklist item was discussed or planned.
- Keep accepted risks and deliberately deferred work out of the active implementation queue.
- Do not silently reopen completed work based on stale historical plans.
- Estimates below are **hands-on engineering effort**, excluding observation time and unexpected failures.

## Prioritised projects

| # | Project | Status | Estimated effort | Remaining outcome |
|---|---|---|---|---|
| 1 | Greenbone and AI-assisted morning management report | CURRENT FOCUS | **1–2 hours for existing verification; AI addition to be estimated after reviewing current report code** | Verify latest completed Greenbone scan in 06:00 report, stale/missing evidence handling and unattended end-to-end delivery. Add AI-assisted interpretation of the collected security, monitoring, patch and backup evidence to produce a concise management summary with priorities, overnight changes and recommended follow-up. Keep all numeric results deterministic and source-linked; distinguish confirmed facts from AI interpretation, flag missing/stale evidence, minimise sensitive inputs and fall back to the existing factual report if AI is unavailable. Existing scanning, transfer and email are operational. See issue #127. |
| 2 | Security and monitoring integration | NEXT | **2–4 hours** | Audit existing Suricata, Zeek, CrowdSec, Pi-hole, Zabbix and Loki signals; connect only demonstrated missing actionable evidence to the management report; avoid duplicate collectors and noisy alerts. |
| 3 | Grafana dashboards and AI host intelligence | PLANNED | **4–7 days** | Estate overview and automatically provisioned node-specific pages; new discovered hosts appear automatically; show only relevant panels and available telemetry. Use all accessible inventory, discovery, network, DNS, router, switch, Proxmox, Komodo, Prometheus, Zabbix, Alloy/Loki, Suricata, Zeek, CrowdSec, Greenbone, backup, patch and service-health evidence. Produce evidence-linked AI descriptions distinguishing confirmed facts from inferred roles, with confidence and version history. Refresh existing hosts **weekly**; first analyse new hosts **one hour after identification**. Never treat unavailable telemetry as healthy or transmit secrets to AI. |
| 4 | Homelab documentation audit | PLANNED | **1–2 days (provisional)** | Read-only audit of the live estate against `IaC/inventory/estate.json`, `CURRENT-STATE.md`, service runbooks, target-state plans and monitoring/discovery evidence. Verify active host identities, VMIDs, addresses, roles, installed services, ports, backups, monitoring and retired assets; record discrepancies with evidence and update authoritative docs through reviewed changes. Do not silently change live infrastructure or reopen accepted risks. |\n| 5 | Password manager (Vaultwarden candidate) | PLANNED | **1–2 days** | Reconcile earlier Vaultwarden / dedicated `vault-01` plan with repository's older 'product not selected' wording before provisioning. HTTPS, MFA, protected off-host backups, tested restore and emergency access. |
| 6 | Backup and disaster recovery | OUTSTANDING | **2–4 days** | Application-consistent Nextcloud/PostgreSQL recovery, representative VM restore, independent second copy of important data and recovery secrets. Existing primary nightly backups are operational. No shared-storage or automatic HA project. |
| 7 | Komodo hardening | OUTSTANDING | **1–3 days** | HTTPS, remaining onboarding where actually needed, low-risk update/rollback proof, reconcile legacy Docker management. |
| 8 | Legacy infrastructure cleanup | REVIEW REQUIRED | **1–2 days** | Verify and safely remove unreferenced pre-cluster rollback LVs when appropriate; reconcile stale docs; review merged branches and superseded deployment paths. **Jenkins is already removed; do not create a Jenkins retirement task.** |
| 9 | Web analytics | OPTIONAL | **1–3 days** | Previously documented Cloudflare/Umami/Grafana-Loki analytics and portfolio website review (issue #125). |
| 10 | Cloudflare Tunnel | DEFERRED | **1–2 days** | `edge-01` is reserved, but do not deploy cloudflared until an approved service requires it. |

**Sequence:** Finish #1, then #2, then #3, then the new documentation audit #4, then Vaultwarden #5. Optional/deferred items are not automatic commitments.


## Delivery step progress

- **Step 1/20 — Review 2026-09-23 06:00 management email: VERIFIED.** Delivered at 06:00 BST; 15/15 hosts and patch evidence current, zero active infrastructure alerts, zero actionable Greenbone vulnerabilities, 10 informational findings. Greenbone evidence timestamp 2026-09-23 02:44:57 UTC matches latest completed scan report (report ID `b0be6d8e-8420-4010-b09f-524254daa374`). Suricata/Zeek evidence marked current and coverage complete. Evidence: [management email](https://mail.google.com/mail/u/?authuser=jrwroberts1976%40gmail.com#all/1a0cca2c0b180d5c), [Greenbone scan email](https://mail.google.com/mail/u/?authuser=jrwroberts1976%40gmail.com#all/1a0cc27071b87607). **Closure email: SENT** to `jrwroberts1976@gmail.com` (Gmail message `1a0cca52de0cc637`), including remaining 20-step checklist and later backlog.
- **Step 2/20 — Verify reporting pipeline: VERIFIED.** 2026-09-23 06:00:11 BST timer run: collector, generator and mailer each exited `0/SUCCESS`; journal confirms report output and SMTP handoff through `mail-relay-01:25`; receipt independently confirmed. Actual Greenbone evidence: `/var/lib/homelab-management-report/evidence-sources/greenbone-01/incoming/managed.json` (modified 03:44:58 BST, owner `evidence-greenbone`, mode `640`). Code inspection confirmed 30-hour Greenbone and 45-minute sensor freshness thresholds, missing/invalid/stale statuses, and report summary suppresses misleading zero-vulnerability claim when evidence unavailable. User-executed isolated temporary-file tests: **MISSING PASS, STALE PASS, OK PASS (3/3)**; production evidence untouched, no test email sent. Evidence transfer succeeded for this run; source-side transfer logs and end-to-end SMTP failure injection were not separately tested. **Closure email: NOT SENT — Gmail send action was blocked; retry only when permitted.**
- **Step 3/20 — Add AI-assisted interpretation: IN PROGRESS (implementation staged, NOT deployed).** OpenAI API selected. Initial optional briefing script and isolated unittest suite committed at `IaC/monitoring/management-report/` (commits `6b08137`, `d0e7954`). Script allowlists aggregate evidence, uses Responses API with `store=false` and strict timeout, writes a fresh factual-only fallback before optional briefing, and never edits the factual source or sends email. On `admin-01`, all seven isolated unit tests **PASSED** on 2026-09-23 (`Ran 7 tests in 0.025s`, `OK`): success, sanitisation, timeout, missing evidence, omitted-source `not_assessed`, stale prior briefing and API request settings. User supplied complete unittest summary. Live synthetic OpenAI API test on `admin-01` returned `AI_BRIEFING=OK`, preserved the factual report, and correctly described omitted Zabbix, Alertmanager, Loki and network-sensor sources as **not assessed** (not outages). Root-owned key file on `admin-01` confirmed non-empty, mode `0600`; no key content recorded. Ansible integration now staged on `main`: role installs AI generator and root-only credential directory; service conditionally invokes AI with systemd `ExecStart=-` before the mailer; mailer includes AI only when output is newer than the factual report and embeds its exact factual contents. **`management_report_ai_enabled: false` by default; not deployed or integration-tested.** On `admin-01`, Ansible 2.19.11 and Jinja2 available; clean working tree; seven unit tests pass and packaged AI script compiles. User-executed isolated Jinja2-rendered service/mailer integration test **PASSED**: `SERVICE_AI_OFF`, `FACTUAL_FALLBACK_AI_OFF`, `SERVICE_AI_ON`, `FACTUAL_FALLBACK_AI_ON`, `AI_SUCCESS_SELECTION`, `STALE_AI_REJECTED`, `LOCAL_TEMPLATE_INTEGRATION` all PASS; SMTP mocked, no email sent. This validates template logic, not Ansible deployment or real systemd execution. Live `monitor-01` read-only evidence schema check **PASSED**: all six sections (`prometheus`, `zabbix`, `alertmanager`, `loki`, `greenbone`, `network_sensor`) are dictionaries; all allowlisted count fields are integers, statuses/timestamps strings and severity counts a dictionary. Only types, not values or secrets, were printed. Still needed: secure key on `monitor-01`, Ansible deployment check and isolated host-side success/failure tests, then enable only after approval. Current 06:00 service remains unchanged. Current 06:00 service remains unchanged.

## Completed and accepted decisions

| Area | Decision | Backlog treatment |
|---|---|---|
| Router VPN | ASUS router-hosted OpenVPN operational and accepted. | CLOSED. Routine router/DDNS/client recovery documentation only. |
| Proxmox storage / HA | Keep node-local guest storage, two-node cluster and QDevice; no sufficiently fast shared disk available. Accept manual backup-based recovery and longer recovery time after node failure. | SHARED STORAGE / AUTOMATIC HA OUT OF SCOPE. Do not re-propose. |
| Legacy HP ProCurve switch | Keep existing hardware; Telnet-only management and current SNMP limitations acknowledged and risk-accepted for now. | HARDENING / REPLACEMENT CLOSED by risk acceptance. |
| `media-01` | Kodi/media work complete. Its existing NFS backup-target role continues. | CLOSED. |
| Home Assistant | Operational; standard Home Assistant backup accepted as sufficient. | CLOSED. Do not add extra whole-VM restore/monitoring work without new request. |
| Jenkins | Already removed. | CLOSED. |
| CT104 / VM204 unattended backups | Successful 2026-09-23 PROXMOX scheduled backup email included both. | Do not list first unattended proof as pending. |

## Step closure and email notification

Each of the 20 agreed delivery steps requires: (1) implementation or verification evidence, (2) a GitHub closure/update with a reference, and (3) an individual completion email to James. **Every completion email must include the full up-to-date remaining checklist, not just the immediate next step**, grouped by project, with step number, status and current estimate where available. Include the rest of the prioritised backlog after the first 20 steps, clearly marking optional/deferred work. Send one email per closed step, even when multiple steps close in one session. Confirm the recipient address from the established reporting setup before the first send. If a step closes outside a session with ChatGPT, automatic notification requires a separately implemented GitHub/event-driven workflow; this register alone does not send mail.

## Daily management email: AI acceptance criteria

1. Build the existing factual report from authoritative Greenbone, Suricata/Zeek, CrowdSec, Pi-hole, Zabbix/Prometheus, Loki, patch and backup evidence where available. Do not fabricate a missing feed.
2. Give AI only a bounded, sanitised evidence summary to draft the executive overview, meaningful overnight changes, priority issues and suggested follow-up. Preserve exact source-derived counts, timestamps, freshness and statuses outside AI control.
3. Clearly distinguish verified observations from interpretation; never declare an unverified event, cause or fix as fact. Include references or timestamps for the underlying evidence and disclose gaps.
4. If the AI service times out or fails, send the original factual 06:00 email rather than skipping delivery. Record AI generation status and test this fallback.
5. Validate the next unattended delivery and revise the effort estimate after reviewing the existing report generator. Do not treat this specification as deployed.

## Dashboard / AI acceptance criteria

1. One estate overview and a navigable dedicated dashboard per monitored node, matching the node's actual services and available evidence.
2. A newly discovered device appears in the estate view automatically; its first AI analysis occurs one hour after identification. Discovery does not imply full telemetry is already available.
3. Existing hosts are reanalysed weekly, preserving previous descriptions and surfacing material behaviour changes.
4. Inventory-confirmed facts override AI hypotheses. Display evidence, confidence, last analysed time and data gaps; human-approved descriptions are not silently overwritten.
5. Dashboards and automation are Git-managed, rebuildable and use existing monitoring pipelines wherever possible.

## Maintenance note

Historical `README.md`, `TARGET-STATE.md` and `MIGRATION-TRACKER.md` may still mention work now completed or risk-accepted. Reconcile those separately against this latest user-approved register and the live current-state authority. This file does **not** itself prove a service change.
