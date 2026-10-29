<!-- estate-authority: IaC/inventory/estate.json -->

# Security remediation programme — Greenbone and Trivy

**Opened:** 20 October 2026  
**Status:** ACTIVE — dated evidence framework, reconciled 29 October; no live changes authorised  
**Tracking issue:** [#187 — Security remediation programme](https://github.com/jrwroberts1976/homelab-platform/issues/187)  
**Owner:** Homelab operator (approve disruptive changes individually)  
**Sources of authority:** `IaC/inventory/estate.json`, `docs/architecture/CURRENT-STATE.md`, Git-managed IaC, completed scan reports and validated live state  
**Related work:** Project 7 (Docker lifecycle), existing Greenbone/ICMP accepted-risk work, `CONTAINER-VULNERABILITY-STATUS.md`, `CONTAINER-VULNERABILITY-REMEDIATION-RUNBOOK.md`

> **29 October 2026 reconciliation:** This document preserves the **20 October** scan baselines and explains the remediation workflow; it is not a current vulnerability scan. The home gateway has since migrated to the Raspberry Pi **router-01 at 192.168.2.1**. Historical Greenbone findings naming the **ASUS router at .2.1** must NOT be attributed to the new Pi without a new identity-matched scan. The live Pi now provides dnsmasq DHCP on `192.168.2.100–199`; `media-01` (historically `.195`) is offline and ASUS AiMesh `.181` has not been reverified. Separate read-only DHCP exclusion preflight was merged in [PR #214](https://github.com/jrwroberts1976/homelab-platform/pull/214); **no DHCP exclusion has been deployed**. The October 26 Trivy and Greenbone updates may supersede the counts below; check `CURRENT-STATE.md`, the latest scanner run and issue #187 before any action. No part of this documentation grants permission for a deployment or scan.

## Goal and non-goals

Reduce meaningful vulnerabilities and unsafe service exposure across the existing estate while retaining DNS, routing/AiMesh, Proxmox quorum, SSH, Nextcloud, monitoring, Greenbone and BirdNET functionality. Track every finding through evidence → ownership → assessed risk → supported mitigation/fix → approved deployment → independent recheck → closure, instead of chasing raw severity totals.

**Not authorised:** unattended upgrades, unreviewed firmware changes, mass firewall changes, disruptive scans, blanket dismissals, removal of current risk acceptances, or restarting Greenbone while a scan is active. Backup/DR is a separate, currently deferred priority; workload-specific data-safe rollback remains mandatory for an individual approved security change.

Do not expose credentials, full `docker inspect` environment data, secrets from container command arguments, or private detailed vulnerability artifacts in GitHub issues or commits.

## Evidence snapshot — 20 October 2026

| Source | Scope | Observed results | Important qualification |
| --- | --- | --- | --- |
| Greenbone **Full LAN — Weekly** email, report `ffced3ba-fc6d-4d60-b949-277b8b70de89` | Wider LAN (reported 20 Oct) | **0 Critical, 0 High, 7 Medium, 25 Low**, 1,132 Log, 0 Accepted | Scan scope/policy differs from authenticated managed daily. Seven Medium entries are the active network triage queue. |
| Greenbone **Managed Infrastructure — Authenticated Daily** email, report `680f0ee6-fbd1-421a-ada2-27250d0d2f3a` | Managed targets (reported 20 Oct) | **0 Critical, 0 High, 0 Medium, 0 Low**, 864 Log, 0 Accepted; no actionable items | Does not negate findings on other LAN devices or establish that all endpoints were authenticated. |
| Trivy full running-image baseline, `CONTAINER-VULNERABILITY-STATUS.md` | Five Docker hosts, 32 running containers, 30 host-local running image references | **30/30** image references valid in manual batches; **191 Critical package-finding rows** | Repeated package/advisory occurrences are not 191 unique CVEs, nor proof of reachability. First unattended daily scans scheduled for 21 Oct; confirm execution. |

All of these are **dated snapshots**, not live current-state assertions. Before any decision, verify report timestamps, host inventory, image IDs and any later reports.

### Greenbone Medium triage register (historical 20 October scanner targets)

| ID | Recorded endpoint / device | Finding | First action | State |
| --- | --- | --- | --- | --- |
| G-M01 | `192.168.2.183:135/tcp` — ownership not verified | DCE/RPC / MSRPC service enumeration (5.0) | Identify endpoint and whether RPC is expected or unnecessarily exposed; check host firewall/service dependencies | **Investigate** |
| G-M02 | `192.168.2.16:80/tcp` — **HP ProCurve 2510G-24** in estate | Cookie without `HttpOnly` (5.0) | Read-only header/session validation; check firmware and management access restrictions before judging compatibility | **Investigate** |
| G-M03 | `192.168.2.17:8443,10001/tcp` — ownership not verified | Certificate signed using weak signature algorithm (two 4.0 findings) | Identify exact device, cert chain/signature/management role, vendor firmware and safe certificate replacement path | **Investigate** |
| G-M04 | `192.168.2.1`, `.181`, `.218` on `8443/tcp` — **historical ASUS/AiMesh-attributed scan targets; ownership changed or may have changed after router migration** | TLS renegotiation DoS indicator (three 5.0 findings) | Reidentify each device against current topology; the 20 Oct ASUS finding at .2.1 does **not** imply a finding on today's Pi gateway. Then assess exposure, firmware and vendor support without disrupting mesh/routing | **Investigate** |

**Seven Medium findings in the 20 October report, grouped into four root-cause investigations.** Current device ownership and scan state require revalidation. Neither a scanner detection nor a missing security header proves exploitation. Do not disable an administrative endpoint or change certificates before proving safe access and rollback. Unknown `.17` and `.183` are not in the canonical estate inventory; use monitoring discovery or approved local investigation to identify them rather than inventing device identities.

### Greenbone Low and accepted-risk reconciliation

The historical 20 October weekly LAN email reports **13 ICMP timestamp-reply disclosures** and **12 TCP timestamp disclosures** (25 Low). Treat these as a *newer, broader-scope finding set*, not an automatic continuation of the earlier 14 managed-host ICMP findings. Compare exact device identity, scanner target, NVT OID, report ID and mitigation status before claiming a regression or reopening an accepted risk.

Prior separately documented ICMP programme: media-01, docker-01 and monitor-01 were scanner-perspective validated as blocked; sensor-01 subsequently had an independently reproduced no-reply post-change result, with controller/playbook validation caveats. The older accepted-risk allowlist was not automatically cleared. See `GREENBONE-ACCEPTED-RISKS-2026-10-19.md` and `GREENBONE-ICMP-REMAINING-ROLLOUT-2026-10-19.md`. Never use the old 14-host denominator to describe the new weekly LAN scan.

For unmanaged/consumer devices, check whether a safe fix exists. Where not, consider restricting administration exposure, support/firmware lifecycle and explicit risk acceptance with a review date. Do not indiscriminately disable TCP timestamps or modify Proxmox/Docker/LXC packet filtering. Keep the separate BirdNET-Go JavaScript-readable `csrf` / `HttpOnly` exception open pending compatibility evidence.

### Trivy image findings

Start from the existing per-image JSON reports at `/var/lib/homelab-container-security/` on the affected host and central `homelab_container_estate_*` metrics; **do not rerun or recreate the already installed scanning stack** just to plan changes.

1. Require `scan_complete=1`, current timestamp and `valid_images=running_images` on each host; verify scan report `Metadata.ImageID` against running image. Missing/stale scans mean **unknown**, never clean.
2. Group detections by **image ID/digest + advisory/CVE + package** so repeated Komodo Periphery instances or duplicate package rows do not generate redundant remediation tickets.
3. Rank confirmed exploitable/reachable or exposed authentication/remote execution issues first, then vendor-fixable Critical/High, then mitigations/no-fix findings. Record upstream advice, tested image tag/digest and compatibility; do not treat `FixedVersion` as proof a compatible upstream image exists.
4. Limit first production image change to one workload/canary. Preserve dependencies and stateful rollback; validate application health, rescan the exact *new* image ID, and prove the specific CVE has cleared.
5. Keep the already completed Blackbox Exporter upgrade `v0.28.0` → `v0.29.0` as a reference pattern (17/17 probes remained healthy). Do not repeat it unless fresh evidence identifies a new problem. Other images have not been remediated merely because Trivy monitoring is deployed.

## Work packages and verification gates

| Phase | Work and evidence | Exit gate |
| --- | --- | --- |
| **S0 — Evidence assurance (start here)** | Verify latest Greenbone scopes and reports, Trivy 5/5 age/identity/coverage, first unattended 21 Oct timer runs, and CI documentation guard status; identify unowned LAN endpoints | Exact reports, timestamps, owners, and outstanding validation gaps recorded |
| **S1 — Critical image triage** | Deduplicate the 191 Critical package occurrences; assess each root cause by reachability, severity, exploit status, patch availability, and impact; create scoped change items | High-risk root causes ordered with a defensible fix/mitigation/acceptance decision |
| **S2 — Seven Medium Greenbone findings** | Four investigations G-M01–G-M04; verify ownership/firmware/management policy and propose safe targeted fixes | Each finding has a decision, reviewed change or accepted-risk reason |
| **S3 — Low-risk / exceptions** | Reconcile 13 ICMP + 12 TCP detections and older managed ICMP/CSRF exceptions without resetting their decisions | Dated accepted/mitigated register, no duplicated or misattributed findings |
| **S4 — Change and verify** | Git-backed IaC, per-change approval, preflight, backup/rollback, one-service cutover, functional checks, new targeted scan evidence | Specific issue cleared or transparently marked mitigated/accepted; services healthy |
| **S5 — Keep it working** | Dashboards show host-separated and fresh findings; age/coverage alerts checked; secrets-handling hygiene assessed without outputting secrets; successful next unattended runs documented | Repeatable evidence and a sustainable review cadence established |

Security-sensitive observations, including unsafe exposure of process arguments or runtime credentials, must be assessed **privately first**; any rotation requires a coordinated change plan and application validation. Do not print credentials during inspection.

## Per-finding tracking contract

For each independently actionable **root cause**, link a GitHub issue/change record containing:

- Stable finding ID and source (report ID/date, NVT OID or CVE/advisory; avoid secret-bearing raw artifacts).
- Affected device identity/service or exact running image ID and affected hosts; confidence in owner mapping.
- Exposure/reachability and verified impact; upstream vendor/version/fix evidence.
- Disposition: `Investigating`, `Planned`, `Mitigated`, `Fixed`, `Accepted`, or `Blocked`, including reason, reviewer and review date.
- Scoped Git change, pre/post operational checks, and independent scanner proof; rollback and service dependency notes.

**Do not close on a version number, Git commit or `rc=0` alone.** Closure requires a new report tied to the affected identity/CVE and a successful service/functional check. If risk is intentionally accepted, record compensating controls and re-review date instead of claiming fixed.

## First safe action

Use **read-only evidence review**, not another deployment: confirm the **latest** completed Trivy timer runs, image-ID match and freshness on all five hosts, then extract and deduplicate *currently present* Critical root causes from the existing JSON reports. The 21 October timer gate described in this historical plan is no longer future work. In parallel, identify the two unowned weekly LAN Medium endpoints via already collected monitoring inventory. Propose the first specific fix only after ownership, supported upstream remediation and rollback are established.

**No live changes, active scan disruptions, or permission to bulk-remediate are implied by adoption of this project.**
