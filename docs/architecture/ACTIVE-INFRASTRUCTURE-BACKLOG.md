# Active Infrastructure Backlog

**Last reconciled:** 2026-09-23  
**Authority:** This file records James's latest agreed project priorities, estimates, completed work and accepted risks. Check `docs/architecture/CURRENT-STATE.md` and `IaC/inventory/estate.json` before any implementation. This is a planning register, not evidence that an outstanding change has been deployed.

## Working rules

- Work in priority order unless James explicitly reprioritises.
- Update this file whenever James closes, adds, reprioritises or changes the scope of a project. Keep status, estimate and evidence links current.
- Verify live state before marking implementation complete; record the relevant PR, issue, test or run evidence.
- Keep accepted risks and deliberately deferred work out of the active implementation queue.
- Do not silently reopen completed work based on stale historical plans.
- Estimates below are **hands-on engineering effort**, excluding observation time and unexpected failures.

## Prioritised projects

| # | Project | Status | Estimated effort | Remaining outcome |
|---|---|---|---|---|
| 1 | Greenbone and morning management report | CURRENT FOCUS | **1–2 hours** | Verify latest completed Greenbone scan in 06:00 report, stale/missing evidence handling and unattended end-to-end delivery. Existing scanning, transfer and email are operational. See issue #127. |
| 2 | Security and monitoring integration | NEXT | **2–4 hours** | Audit existing Suricata, Zeek, CrowdSec, Pi-hole, Zabbix and Loki signals; connect only demonstrated missing actionable evidence to the management report; avoid duplicate collectors and noisy alerts. |
| 3 | Grafana dashboards and AI host intelligence | PLANNED | **4–7 days** | Estate overview and automatically provisioned node-specific pages; new discovered hosts appear automatically; show only relevant panels and available telemetry. Use all accessible inventory, discovery, network, DNS, router, switch, Proxmox, Komodo, Prometheus, Zabbix, Alloy/Loki, Suricata, Zeek, CrowdSec, Greenbone, backup, patch and service-health evidence. Produce evidence-linked AI descriptions distinguishing confirmed facts from inferred roles, with confidence and version history. Refresh existing hosts **weekly**; first analyse new hosts **one hour after identification**. Never treat unavailable telemetry as healthy or transmit secrets to AI. |
| 4 | Homelab documentation audit | PLANNED | **1–2 days (provisional)** | Read-only audit of the live estate against `IaC/inventory/estate.json`, `CURRENT-STATE.md`, service runbooks, target-state plans and monitoring/discovery evidence. Verify active host identities, VMIDs, addresses, roles, installed services, ports, backups, monitoring and retired assets; record discrepancies with evidence and update authoritative docs through reviewed changes. Do not silently change live infrastructure or reopen accepted risks. |\n| 5 | Password manager (Vaultwarden candidate) | PLANNED | **1–2 days** | Reconcile earlier Vaultwarden / dedicated `vault-01` plan with repository's older 'product not selected' wording before provisioning. HTTPS, MFA, protected off-host backups, tested restore and emergency access. |
| 6 | Backup and disaster recovery | OUTSTANDING | **2–4 days** | Application-consistent Nextcloud/PostgreSQL recovery, representative VM restore, independent second copy of important data and recovery secrets. Existing primary nightly backups are operational. No shared-storage or automatic HA project. |
| 7 | Komodo hardening | OUTSTANDING | **1–3 days** | HTTPS, remaining onboarding where actually needed, low-risk update/rollback proof, reconcile legacy Docker management. |
| 8 | Legacy infrastructure cleanup | REVIEW REQUIRED | **1–2 days** | Verify and safely remove unreferenced pre-cluster rollback LVs when appropriate; reconcile stale docs; review merged branches and superseded deployment paths. **Jenkins is already removed; do not create a Jenkins retirement task.** |
| 9 | Web analytics | OPTIONAL | **1–3 days** | Previously documented Cloudflare/Umami/Grafana-Loki analytics and portfolio website review (issue #125). |
| 10 | Cloudflare Tunnel | DEFERRED | **1–2 days** | `edge-01` is reserved, but do not deploy cloudflared until an approved service requires it. |

**Sequence:** Finish #1, then #2, then #3, then the new documentation audit #4, then Vaultwarden #5. Optional/deferred items are not automatic commitments.

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

## Dashboard / AI acceptance criteria

1. One estate overview and a navigable dedicated dashboard per monitored node, matching the node's actual services and available evidence.
2. A newly discovered device appears in the estate view automatically; its first AI analysis occurs one hour after identification. Discovery does not imply full telemetry is already available.
3. Existing hosts are reanalysed weekly, preserving previous descriptions and surfacing material behaviour changes.
4. Inventory-confirmed facts override AI hypotheses. Display evidence, confidence, last analysed time and data gaps; human-approved descriptions are not silently overwritten.
5. Dashboards and automation are Git-managed, rebuildable and use existing monitoring pipelines wherever possible.

## Maintenance note

Historical `README.md`, `TARGET-STATE.md` and `MIGRATION-TRACKER.md` may still mention work now completed or risk-accepted. Reconcile those separately against this latest user-approved register and the live current-state authority. This file does **not** itself prove a service change.
