# Active Infrastructure Backlog

**Last reconciled:** 16 October 2026  
**Authority:** Planning register only. Validate implementation claims against `docs/architecture/CURRENT-STATE.md`, `IaC/inventory/estate.json` and live evidence.  
**Current documentation work:** 16 October patching/TLS/security reconciliation applied to the canonical current-state and installed-solutions documents.

**19 October updated risk decision:** Following the successful read-only media-01 firewall audit, the user ruled out changes to firewalls for accepted ICMP timestamp findings. The earlier firewall-pilot suggestion below is superseded. Keep existing accepted-risk entries intact, distinguish TCP sysctl hardening from ICMP timestamp handling, and prefer read-only scanner-perspective verification before further action. No live changes.

**19 October ICMP timestamp validation pending:** A one-target, scanner-perspective Ansible diagnostic on greenbone-01 is Git-staged (not run). It sends three type-13 requests only to media-01, validates matching type-14 responses, and reports an ordinary-ping baseline. Run offline tests plus syntax preflight before use. No host configuration, risk acceptance or managed Greenbone scan changes are proposed. Interpret absent replies cautiously.

**19 October accepted-risk validation update:** Read-only scanner-side `greenbone-icmp-timestamp-media01-readonly.yml` now executed successfully (`ok=5 changed=0 failed=0`); ping PASS, **3 ICMP timestamp probes sent and 3 matching replies received** on media-01. Its original Greenbone ICMP disclosure is reproducible and remains accepted, not remediated; user does not approve ICMP firewall changes. Other 13 accepted ICMP findings have not been re-probed, and BirdNET-Go `csrf` HttpOnly requires a separate decision. No full Greenbone rescan or host changes occurred.

**19 October user change — media-01 ICMP firewall pilot now authorised:** The earlier no-firewall choice was superseded after confirming no unicast ICMP timestamp sysctl in Pi Linux 6.18.50. Git-stage only one IPv4 type-13 drop in the **existing media-01 nftables role**, with independent scanner pre/post probes and separate rollback. Preserve ping, HTTPS-only qBittorrent, Kodi, SMB, SSH and Proxmox backup NFS. Validation and scoped deployment outstanding; don't remove accepted-risk policy entry before fresh completed Greenbone confirmation. All 13 other ICMP hosts and BirdNET cookie remain unchanged.

**19 October media-01 ICMP timestamp pilot verified live:** Existing nftables role deployed successfully `media-01 ok=18 changed=2 failed=0`; independent `greenbone-01 ok=8 changed=0 failed=0`. Before mitigation 3 of 3 timestamp replies were observed, whereas post-deployment `MEDIA01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED` and normal ping PASS. qBittorrent HTTPS/443 remains available, direct LAN HTTP/8081 remains blocked, internal backend still available. **Operational mitigation 1/14, pending authenticated Greenbone scan confirmation.** No accepted-risk entries removed; assess the remaining 13 ICMP hosts by their actual firewall owner and BirdNET-Go csrf HttpOnly separately. Earlier backlog comments against firewall work or stating pilot only staged are now historical/superseded.

**19 October docker-01 read-only audit completed:** `ok=2 changed=0 failed=0`, Debian 13, nftables service inactive, nft INPUT hooks 0, iptables-save readable and no timestamp rules. No firewall changes. Git-staged additional read-only backend/chain summary and scanner-side ICMP probe in `greenbone-icmp-timestamp-docker01-readonly.yml`, not run. Avoid installing/replacing nftables policy or disturbing Docker/BirdNET; identify effective packet owner before proposing remediation.

**19 October docker-01 remediation confirmed live:** `greenbone-icmp-timestamp-docker01-cutover.yml` completed `docker-01 ok=22 changed=3 failed=0`, `greenbone-01 ok=8 changed=0 failed=0`. Scanner-side timestamp replies suppressed and normal ping still works; Docker containers/DOCKER FORWARD chain invariants and trusted BirdNET HTTPS passed without a Docker restart. Dedicated host INPUT rule persisted by systemd unit (reboot not yet tested). **2 of 14 reported ICMP hosts operationally mitigated** (media-01, docker-01); 12 remaining and BirdNET csrf HttpOnly exception still open. No accepted-risk allowlist removals or fresh Greenbone scan yet. Older entries calling this Git-staged/pending are historical.

**19 October monitor-01 investigation pending:** A scoped, read-only `greenbone-accepted-icmp-firewall-readonly.yml` audit passed `monitor-01 ok=2 changed=0 failed=0`; nftables not readable, iptables ruleset readable, no timestamp-specific rules, no active firewall service detected. Neither iptables INPUT ownership nor ICMP timestamp reproducibility has yet been established. New Git-only `greenbone-icmp-timestamp-monitor01-readonly.yml` will investigate effective policies and probe from greenbone-01 without changing monitoring or firewall settings. Two operational ICMP mitigations remain confirmed (media-01 and docker-01); risk allowlist unchanged.

**19 October monitor-01 ICMP timestamp reproduced read-only:** `monitor-01 ok=3 changed=0 failed=0`, independent `greenbone-01 ok=5 changed=0 failed=0`; normal ping PASS, **3/3 matching timestamp replies**, confirming the accepted risk remains. No host changes. User's paste omitted first-play iptables/nftables backend and monitoring-service evidence. Run `greenbone-icmp-timestamp-monitor01-readonly.yml --limit monitor-01 --forks 1` to collect it without a new network probe; do not design firewall changes until that evidence is reviewed. Operational mitigations remain 2 of 14.

**19 October monitor-01 host-only ICMP type-13 mitigation staged (NOT LIVE):** Read-only evidence confirms iptables-nft INPUT ACCEPT/zero rules, FORWARD DROP, 4 custom chains and a prior 3/3 timestamp reply result. Services are Docker Compose-based; do not confuse native systemd not-active indicators with container status. Git-only dedicated `monitor_icmp_timestamp` role plus pre/post scanner playbook, Docker/Grafana health checks, exact rollback and offline validator are ready for syntax/source checks. No monitoring service or firewall change applied; 2/14 prior mitigations verified and risk allowlist unchanged.

**19 October monitor-01 ICMP timestamp fix deployed and verified:** `monitor-01 ok=25 changed=3 failed=0` and scanner `greenbone-01 ok=8 changed=0 failed=0`. Final result `MONITOR01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, normal ping PASS, host INPUT-only type-13 rule, Grafana HTTPS, monitoring containers and Docker FORWARD invariants preserved with no restarts. Persistent service installed, reboot not tested. Now **3/14 operationally mitigated; 11 ICMP hosts remain**, plus the separate BirdNET csrf HttpOnly acceptance. No Greenbone rescan or accepted-risk changes; historical earlier 'not deployed' notes superseded. Next one-host read-only audit candidate cloud-01.

**19 October remaining 11 audited; three-VM pilot Git-staged:** Authenticated, read-only Ansible sweep succeeded on all 11 hosts with zero changes/failures and confirmed 3 matching timestamp replies of 3 requests for every target. Firewall classes: five native nftables LXC, three iptables-nft VMs, mixed Komodo, physical admin Pi controller, Proxmox-2 cluster firewall. New role and serial cutover/rollback for sensor-01/cloud-01/greenbone-01 uses a single tagged host INPUT type-13 rule, preserving services, Docker forwarding, SSH and independent probe results; only `sensor-01` is first planned deployment. No live changes on remaining hosts, accepted-risk register or new Greenbone scan. Native LXC/Komodo/Proxmox/Controller further review pending.

**19 October sensor-01 ICMP timestamp mitigation verified:** Host INPUT-only tagged IPv4 type-13 DROP installed, systemd persistence enabled/active and both Suricata/Zeek remained active. Cutover returned `failed=1` on a false chain declaration comparison caused by live iptables packet counters, after rule installation. Independently from greenbone-01, repeated checks recorded normal ping PASS and 0/3 matching timestamp replies (`ok=4 changed=0 failed=0` each). Operational progress **4/14**, 10 remain. Source check corrected to ignore mutable counters; controller validation, rerun/idempotency, reboot proof, and fresh authenticated Greenbone scan are still pending. Do not deploy the next VM before these gates.\n\n## Working rules

**19 October ICMP timestamp programme expanded to remaining 11 hosts:** User authorised addressing the entire reported remainder (six LXC, three VM, admin-01 physical controller and Proxmox-2 cluster node). Git-only read-only `greenbone-icmp-timestamp-remaining11-readonly.yml` and safety validator are staged, not deployed; they collect firewall owner/capability and independently test every remaining target, using monitor-01 to probe the scanner itself. Grouped remediations will use per-host policy and rollback, no blanket firewall on LXCs or Proxmox, and protect DNS/SMTP/Nextcloud/monitoring/storage/cluster networking. Plan: `docs/security/GREENBONE-ICMP-REMAINING-ROLLOUT-2026-10-19.md`. Current live progress still **3 of 14**, 11 pending scanner/owner audit, accepted-risk register unchanged.


**19 October docker-01 host ICMP filtering staged (not deployed):** Read-only audit verified iptables-nft host INPUT ACCEPT/zero rules, Docker-managed FORWARD DROP/four chains, two running containers and 3/3 matching timestamp replies from scanner. New Git Ansible role adds only a tagged ICMP type-13 DROP on docker-01 host INPUT via iptables-nft, with independent systemd persistence and precise rollback; Docker's forwarding, NAT and published-port rules untouched. Offline validator and scanner pre/post tests staged; do not claim completed until user runs validated scoped playbook and confirms BirdNET/containers. Existing media-01 mitigation remains live and other accepted-risk dispositions remain unchanged.


**19 October Docker host verification complete, chain details pending:** Read-only scanner probe reproduced `docker-01`'s accepted ICMP timestamp disclosure (normal ping PASS; 3 requests, 3 matching replies; `docker-01 ok=3 changed=0`, `greenbone-01 ok=5 changed=0`). No network changes. User's excerpt lacks the first-play iptables backend, INPUT policy and Docker chain indicators. Obtain them via `greenbone-icmp-timestamp-docker01-readonly.yml --limit docker-01 --forks 1`, then design a minimal Docker-compatible change and rollback if appropriate. No new Greenbone scan or risk acceptance changes.


**19 October kernel-only mitigation assessed:** media-01's Raspberry Pi Linux 6.18.50 does **not** provide `net.ipv4.icmp_timestamp_ignore_all` (`TIMESTAMP_SYSCTL=NOT_PRESENT`). An upstream proposal is not a supported current kernel setting; a custom kernel patch would be a disproportionate maintenance/reboot burden for this low-impact LAN finding. User declined firewall changes, so keep the confirmed 3/3 ICMP finding accepted; no host changes. Distinguish prior TCP timestamp sysctl hardening. Greenbone scan verification of formerly actionable Medium findings remains pending.


**19 October — user-prioritised review of 15 accepted Greenbone risks:** Last report contains 14 ICMP timestamp replies and one BirdNET-Go csrf cookie missing HttpOnly; historical TCP timestamp acceptances are separate and should not be disabled based on these counts. ICMP mitigation is feasible by narrowly filtering IPv4 type-13 timestamp requests, but first audit firewall ownership for 14 hosts (particularly Proxmox-2/LXC/Docker), then test media-01 pilot with rollback. Preserve BirdNET's deliberate JavaScript-readable csrf token until compatibility of HttpOnly is demonstrated. New Git-only read-only playbook `greenbone-accepted-icmp-firewall-readonly.yml` and review `docs/security/GREENBONE-ACCEPTED-RISKS-2026-10-19.md`; no live changes, changed acceptances or new scan yet. Run audit before designing any remediation.


- Work in priority order unless James explicitly reprioritises.
- Update this file when a project closes, changes scope or is reprioritised.
- Verify live state before marking implementation complete.
- Keep accepted risks and deliberately deferred work out of the active implementation queue.
- Do not silently reopen completed work based on stale historical plans.
- Do not invent missing numbered roadmap steps or names.
- Historical audit/migration documents remain point-in-time evidence and are not rewritten to look current.

**19 October security update:** The media-01 qBittorrent LAN HTTPS-only cutover has passed live Ansible verification (`ok=19 changed=2 failed=0`, HTTPS HTTP 200, LAN 8081 BLOCKED, loopback 8081 AVAILABLE; no qBittorrent/Kodi/SMB/NFS restart). BirdNET's missing Secure cookie attribute was also corrected and verified. The two prior Greenbone actionable Mediums now require one new completed authenticated scan and validated evidence publication before closing; afterwards review the 14 accepted ICMP timestamp disclosures and one BirdNET CSRF `HttpOnly` exception. First check read-only scan state/evidence and GMP readiness; do not duplicate an active scan.

## Current position — 16 October 2026

The core homelab platform is built and operational. Current work is concentrated in final security validation, recovery proof, container lifecycle hardening and selected technical debt rather than missing foundational infrastructure.

### Completed today / now under control

- full controlled patch session across all 15 Ansible-managed Linux hosts;
- final patch state: **15 reachable, 0 pending updates, 0 reboot requirements**;
- unused Proxmox Ceph enterprise repository disabled through IaC;
- trusted browser-facing HTTPS deployed for Pi-hole, Greenbone, Grafana, Zabbix and both Proxmox nodes;
- all seven Let's Encrypt renewal/deploy-hook paths validated with Certbot dry-runs;
- Grafana port 3000 restricted to localhost behind nginx HTTPS;
- accepted-risk detail export/panel work landed on `main`;
- Raspberry Pi 4 TF-A speculative-execution mitigation on `docker-01` converted from a manual change to guarded, checksum-verified, idempotent IaC (`b3047742`).

### Current validation gate

The latest saved 16 October Greenbone managed evidence had **0 actionable findings and 30 accepted risks**, but it is now stale. After `Proxmox-2` returned on 18 October, the 16:18 BST managed-scan run **failed** because the GMP `gvmd.sock` connection was refused. Do not mark remediation closed until runtime readiness and a newer completed authenticated scan are validated.

Expected validation goals:

1. Critical remains 0.
2. High remains 0.
3. Confirm the prior Zabbix cleartext-management finding is absent after trusted HTTPS/reverse-proxy remediation.
4. Confirm the prior Raspberry Pi speculative-execution findings are absent or otherwise correctly reconciled after TF-A hardening.
5. Reconcile any remaining findings as either actionable remediation or explicit accepted risk.
6. Confirm the Grafana accepted-risk detail panel/report matches the authoritative Greenbone evidence.

## Programme snapshot

| View | Current status |
|---|---|
| Named/evidenced delivery steps 1–10 | **10/10 complete** |
| Core monitoring/security platform | **COMPLETE / operational** |
| Estate patching | **COMPLETE — refreshed 16 Oct 2026** |
| Trusted HTTPS / certificate lifecycle | **IMPLEMENTED + renewal-tested** |
| Vulnerability remediation | **FINAL SCAN VALIDATION PENDING** |
| Backup / DR depth | **OUTSTANDING** |
| Container image lifecycle | **PARTIAL** |
| Legacy cleanup | **REVIEW REQUIRED** |
| Optional/deferred capabilities | **UNCHANGED** |

Practical programme completion remains approximately **70–80%** when optional/deferred projects are excluded. The remaining percentage is dominated by recovery proof, estate-wide container lifecycle work and selected hardening/cleanup.

## Prioritised projects

| # | Project | Status | Remaining outcome |
|---|---|---|---|
| 1 | Greenbone and AI-assisted morning management report | **COMPLETE** | Normal operational maintenance only |
| 2 | Security and monitoring integration | **COMPLETE — 7 Oct 2026** | Individual detections/tuning are normal operations |
| 3 | Grafana dashboards and AI host intelligence | **COMPLETE — 10 Oct 2026** | Future enhancements are separate scope |
| 4 | Homelab documentation audit | **COMPLETE — 6 Oct 2026** | Current docs continue to be reconciled as architecture changes |
| 5 | Password manager | **OPTIONAL** | Select product/design only if deliberately prioritised; require HTTPS/MFA, backup, restore proof and emergency access |
| 6 | Backup and disaster recovery | **OUTSTANDING** | Representative QEMU restore, application-consistent Nextcloud/PostgreSQL recovery, independent second copy and protected recovery identities |
| 7 | Komodo hardening and Docker image lifecycle | **PARTIAL** | BirdNET canary complete; remaining estate-wide image inventory, release/dependency review, phased updates and rollback validation |
| 8 | Legacy infrastructure cleanup | **REVIEW REQUIRED** | Remove only clearly obsolete rollback/superseded state after confidence review |
| 9 | Web analytics | **OPTIONAL** | Start only if deliberately wanted |
| 10 | Cloudflare Tunnel | **DEFERRED** | `edge-01` reserved; deploy only for a real approved service requirement |
| 11 | Certificate and reverse proxy management | **IMPLEMENTATION COMPLETE — FINAL GREENBONE VALIDATION PENDING** | Trusted HTTPS and renewal paths are proven; close project after the post-remediation scan confirms the previous actionable cleartext finding is gone |

## Current sequence

1. **Diagnose Greenbone gvmd readiness after Proxmox-2 recovery, then validate a fresh completed scan.** The 18 October run failed while the latest saved evidence was from 16 October. This is the remaining gate on the current patching/vulnerability/TLS workstream.
2. **Next user-selected investigation: Raspberry Pi overclocking feasibility.** Start read-only: inventory Pi models, cooling, power supplies, current frequencies/thermal throttling and workload headroom before proposing any clock/voltage change.
3. **Encode the existing Proxmox GDS mitigation in IaC.** Live `gather_data_sampling=force` mitigation is proven but remains a manual GRUB/kernel-parameter configuration.
4. **Address the Certbot Cloudflare Python dependency warning.** Decide whether to pin the currently working 2.x dependency or deliberately migrate when compatibility with 3.x is established.
5. Resume **Project 7** estate-wide Docker image lifecycle work unless James reprioritises.
6. Default resilience priority remains **Project 6 Backup/DR**, followed by **Project 8 legacy cleanup**.

Projects 5, 9 and 10 remain optional/deferred and are not automatic commitments.

## Patching — COMPLETE 16 OCTOBER 2026

A full controlled patch session was completed across the 15-host Ansible baseline.

Validated final state:

```text
managed hosts:     15
reachable:         15
pending packages:  0
reboot required:   0
```

Both PVE nodes remained quorate with QDevice present. Pi-hole, Greenbone, Grafana/Prometheus, BirdNET, Kodi/SMB and other checked production services remained healthy. Known pre-existing failed helper/one-shot units are separate operational debt; no new patch regression was identified.

The Proxmox Ceph enterprise repository was found enabled even though Ceph is not configured or in use. IaC now explicitly disables that repository so normal package operations do not depend on the enterprise Ceph channel.

## Vulnerability management — FINAL VALIDATION PENDING

**19 October 2026 latest decision — HTTPS-only LAN cutover approved, Git-staged, not deployed:** User confirmed the qBittorrent HTTPS WebUI works and administrator password recovery succeeded, then explicitly requested closure of LAN HTTP/8081. The managed firewall defaults now select HTTPS/443=true, HTTP/8081=false, retaining Nginx→qBittorrent loopback, Kodi, SMB, SSH, NFS and monitoring traffic. A scoped HTTPS-only `qbittorrent-https-cutover.yml`, manual recovery `qbittorrent-https-http-rollback.yml`, and offline validators are staged. No production cutover performed yet. Next run offline/estate/syntax validation, deploy the scoped playbook from admin-01, verify HTTPS and loopback access plus refusal of new LAN 8081 connections, then run a completed authenticated Greenbone scan. Review 14 accepted ICMP timestamps and BirdNET CSRF missing HttpOnly next.

**19 October live verification and pending qBittorrent HTTPS deployment:** The targeted BirdNET Nginx playbook verified the `csrf` cookie has `Secure` on both tested paths (`ok=7 changed=0 failed=0`), without reload. qBittorrent HTTPS readiness on media-01 passed read-only (`ok=3 changed=0 failed=0`), confirming Nginx, Certbot, a certificate, a 443 listener and the desired DNS alias are absent. A Git-only `qbittorrent_https` role and `qbittorrent-https-stage.yml` now provide trusted DNS-01 certificate + Nginx proxy staging; a Pi-hole `media-01` alias is configured in Git for both resolvers, with offline source validator. **Controller validation passed 19 October:** qBittorrent HTTPS Jinja rendering and safety contracts, estate validation, DNS and TLS-stage playbook syntax. Managed DNS alias deployment is now **verified on both Pi-hole resolvers** (`ok=4 changed=0 failed=0` on each; both direct dig responses `192.168.2.195`). **qBittorrent trusted HTTPS staging passed live on 19 October:** `ok=33 changed=9 failed=0`, Nginx validation PASS and HTTPS HTTP 200; qBittorrent/Kodi/SMB/NFS not restarted. DNS name works on both resolvers. **LAN TCP/443 firewall allowance now deployed successfully** through scoped media_firewall Ansible playbook (`ok=16 changed=2 failed=0`), with both trusted HTTPS/443 and rollback HTTP/8081 returning HTTP 200 from admin-01 and Proxmox NFS rules preserved. User confirms the HTTPS browser endpoint works, but requires qBittorrent WebUI password recovery/reset before an authenticated login and WebUI functionality can be verified. New Git-only non-secret read-only `qbittorrent-webui-password-preflight.yml` can inspect whether a permanent password or current-session temporary password marker exists without restarts. Do not close 8081 yet. Port 8081 remains open; a later separately validated/approved cutover will block direct LAN HTTP after HTTPS login testing. An explicit Nginx proxy cookie regex (`~.*`) was staged in Git and requires offline revalidation. Next separately stage trusted HTTPS on media-01 without disabling 8081. **Next:** validate source, reconcile both DNS resolvers, stage trusted TLS, verify login and session handling, then cut over only the Web UI firewall to 443 and rescan. The accepted ICMP and HttpOnly issues remain subsequent work.

**19 October read-only host evidence and remediation staging:** `greenbone-two-medium-readonly.yml` passed on both hosts without changes. qBittorrent-nox listens on `*:8081`, Nginx inactive, no certificate on `media-01`; BirdNET-Go Nginx 1.26.3 sets a `csrf` cookie without `Secure` on its HTTPS 443 endpoint. A **not yet deployed** Nginx `proxy_cookie_flags csrf secure;` fix, a scoped BirdNET Nginx-only deploy/check playbook, and a qBittorrent HTTPS/Cerbot/DNS read-only readiness playbook have been staged in Git. Verify the new BirdNET cookie flags after isolated deployment, then review a trusted qBittorrent TLS name/certificate and DNS-01 route and remove direct HTTP exposure only after end-to-end validation. Do not blanket-enable HttpOnly on a CSRF cookie until JavaScript dependencies are understood. Preserve Kodi, SMB/NFS, BirdNET audio and qBittorrent downloads.

**19 October 2026 update — two actionable Medium findings remain:** A completed authenticated managed Greenbone scan report email arrived at 03:07 UTC (04:07 BST), report `6e75928d-f251-426f-809c-991ffcbf6603`: Critical 0, High 0, Medium 2, Low 0, informational 789, accepted 15. `media-01` (`192.168.2.195:8081`) is flagged for sensitive information transmitted over HTTP (score 4.8; OID `1.3.6.1.4.1.25623.1.0.108440`); `docker-01` (`192.168.2.220:443`) is flagged for missing Secure cookie attribute (score 5.0; OID `1.3.6.1.4.1.25623.1.0.902661`). Neither finding lists a CVE. Investigate service ownership and actual headers/configuration read-only through Ansible, then implement reviewed IaC remediation; do not presume fix or suppress findings. Acceptance count fell from 30 to 15; previous TCP timestamp findings are absent and require evidence-based reconciliation. Also confirm current report `managed.json` publication to `monitor-01` and dashboard freshness. The new emailed scan does not show the systemd boot-readiness guard is fixed; the guard remains staged/undeployed. **Leave final validation OPEN.**



The 14 October control-validation scan ended at:

```text
Critical:      0
High:          0
Medium:        1 actionable
Low:           0
Accepted risk: 30
```

That actionable Medium was the Zabbix cleartext HTTP management finding. The implementation response is now complete: Zabbix has trusted HTTPS/reverse-proxy management, and secure session-cookie handling is configured.

Separately, `docker-01` received and then codified a TF-A v2.15.0 mitigation for Cortex-A72 speculative-execution findings. Current live evidence is:

```text
Spectre v2: Mitigation: Branch predictor hardening, BHB
Speculative Store Bypass: Not affected
```

The accepted-risk reporting path now includes detail rather than only a count; related commits visible on `main` include the Greenbone accepted-risk detail publication, monitoring export and Grafana accepted-risk panel work.

Subsequent saved authenticated-managed evidence collected **16 October 2026 14:28 UTC** (report `35dc10c3-aac0-46fa-b6ce-7c1b31440d38`) was inspected via Ansible on 18 October: **0 actionable Critical/High/Medium/Low, 828 informational, 30 accepted risks**. The accepted entries comprise 14 ICMP timestamp, 15 TCP timestamp and one missing HttpOnly cookie findings. They are accepted classifications, not demonstrated fixes; recheck TCP timestamps after IaC hardening.

**New validation blocker (18 October):** `Proxmox-2` was restored and cluster quorum confirmed healthy with QDevice. A restart-associated Greenbone scan at 16:18 BST failed with `/run/gvmd/gvmd.sock` connection refused, leaving the 16 October evidence stale. Subsequent read-only Ansible inspection confirmed Docker and the `gvmd`/PostgreSQL containers healthy with a management socket present, and showed `gvmd` only became GMP-ready at 16:19:29 BST, **after** the failed scan. Greenbone rebuilt 190,103 vulnerability tests and finished feed synchronisation around 16:37 BST. The next `greenbone-gmp-preflight.yml` (runner `managed --check`, no scan) **timed out after 150 seconds (exit 124)** without output: authentication and task lookup remain unverified despite healthy containers. Read-only Ansible `greenbone-gmp-timeout-readonly.yml` subsequently confirmed orphan temporary root-owned GMP credentials remained (mode 0640), without a detected active scan lock owner/helper; gvmd and PostgreSQL were healthy. The fail-closed IaC playbook `greenbone-gmp-orphan-cleanup.yml` **succeeded live** on 18 October: `REMOVED_ORPHANED_GMP_CONFIG`, file absent, `ok=12 changed=1 failed=0`, without starting any services/scans. The read-only `greenbone-gmp-latency-readonly.yml` **passed live** on 18 October; Docker journal showed helper activity at 16:45:46–47 BST, but the source of the 150s timeout was not established; credentials stayed absent and host resources were adequate. **Instrumented scan runner deployed successfully and idempotently** through Ansible. The updated non-scanning preflight then **failed** (`rc=124`) at `GMP_CHECK_STAGE=querying_managed_task`; SIGTERM cleanup left no credentials, and Ansible's final readiness assertion failed as designed. The first live `greenbone-gmp-request-path-readonly.yml` diagnostic was interrupted at `docker compose exec -T gvmd`; the second attempt has no completion evidence. The playbook has been revised in Git to replace Docker exec with host-volume socket metadata inspection, still without any GMP request or scan; revised syntax/live validation is pending. A Docker exec/attach stall is possible but not proven. Direct Unix socket connect and unauthenticated GMP `get_version` **passed** (GMP 22.7, status 200), avoiding Docker Compose entirely. Direct authenticated GMP read-only Ansible check **passed** on 18 October (`ok=6 changed=0 failed=0`; auth 200; task query 200; exactly one matching authenticated task). A direct-socket change to the production runner/preflight is **staged in Git only**, controller-validated (Jinja/Python/mock GMP/Ansible syntax and estate all PASS) and **deployed through Ansible** to greenbone-01 on 18 October (`ok=3 changed=1 failed=0`; Python compilation passed). The deployed runner's **non-scanning preflight passed live** on 18 October (`ok=10 changed=0 failed=0`; GMP task lookup 0.1s; `CHECK=PASS`; legacy config absent). The old managed scan unit still has failed state. Safe systemd boot-readiness gating and fresh evidence remain the next blockers. Report retrieval/scan completion and boot-time startup readiness still require validation. A **bounded fail-closed scheduled-service readiness gate is now staged in Git only**, using `ExecStartPre` with the existing authenticated direct-socket `managed --check`, a 30-minute maximum wait and no timer/service activation by the scoped Ansible deploy playbook. Offline validator and controller syntax check are pending; the new unit/helper are not deployed. A fresh vulnerability scan and evidence publication remain pending. Validate a newly completed managed scan and evidence publication before closing this section.

## Certificate / trusted HTTPS work — IMPLEMENTED

Trusted browser-facing endpoints:

```text
https://dns-01.home.jrwroberts.co.uk/
https://dns-02.home.jrwroberts.co.uk/
https://greenbone.home.jrwroberts.co.uk/
https://grafana.home.jrwroberts.co.uk/
https://zabbix.home.jrwroberts.co.uk/
https://proxmox.home.jrwroberts.co.uk:8006/
https://proxmox-2.home.jrwroberts.co.uk:8006/
```

All seven renewal paths have been dry-run validated with their service deploy hooks. Post-hook service checks passed. Grafana is no longer directly exposed on LAN port 3000; Docker binds `127.0.0.1:3000` and nginx owns the trusted HTTPS endpoint.

Remaining certificate-lifecycle debt is limited to dependency hygiene around the Cloudflare Python 2.20.x compatibility warning observed during Certbot testing.

## Raspberry Pi TF-A hardening — COMPLETE

`docker-01` target identity:

```text
Raspberry Pi 4 Model B Rev 1.5
revision c03115
aarch64
Debian 13
```

The validated TF-A release artifact is vendored in the Ansible role with SHA-256, licence and provenance. The role verifies host identity and artifact integrity, safely owns the boot configuration, does not reboot automatically, and completed a second real reconciliation with `changed=0`, `failed=0`.

Commit on current `main`: `b3047742 feat(security): manage Raspberry Pi TF-A mitigation`.

## Project 7 — Docker container lifecycle

The BirdNET-Go controlled update/rollback pilot is complete and remains the reference implementation. Remaining scope:

- read-only inventory of running containers, Compose projects, image tags and digests across managed Docker hosts;
- identify floating tags, stale images, deliberate pins and dependency constraints;
- review upstream release notes before production changes;
- update in small risk-classified batches;
- validate health after each batch;
- retain known-good rollback images/tags/digests;
- keep human approval before desired-state changes/deployments;
- do not enable blanket unattended container upgrades.

## Project 6 — Backup and disaster recovery

Still outstanding:

- representative QEMU restore proof;
- application-consistent Nextcloud/PostgreSQL recovery;
- independent second backup copy/failure domain;
- protected recovery identities;
- deeper recovery proof where existing evidence is still incomplete.

## Project 8 — Legacy cleanup

Review only. Remove old rollback LVs or superseded paths only after explicit confidence that they are no longer required. Jenkins is already removed and must not be recreated as a cleanup task.

## Near-term Raspberry Pi overclocking investigation

This is an **investigation**, not an approved configuration change yet.

Before any overclock is proposed:

- identify every active Raspberry Pi model/revision and workload;
- capture stock CPU frequency/governor behaviour;
- capture idle and sustained-load temperatures;
- check `vcgencmd get_throttled`/equivalent undervoltage and thermal-throttle history where supported;
- identify cooling arrangement and power-supply capability;
- measure workload headroom/benefit, especially BirdNET-Go on `docker-01` and Kodi on `media-01`;
- preserve TF-A/security boot requirements on `docker-01`;
- define a reversible IaC-managed change and stability test before production use.

No Pi should be overclocked merely because spare thermal/CPU headroom appears available.

## Completed / accepted decisions

| Area | Decision | Backlog treatment |
|---|---|---|
| Router VPN | ASUS router-hosted OpenVPN operational and accepted | CLOSED; maintenance/recovery only |
| Proxmox storage / HA | Node-local guest storage + two-node cluster + QDevice; manual backup-based recovery accepted | Shared-storage/automatic HA out of scope unless reopened |
| `media-01` | Kodi/media + NFS backup target retained; Ethernet is normal path | NORMAL OPERATIONS |
| Home Assistant | `home-01` commissioned and operational | NORMAL OPERATIONS; explicit monitoring/recovery work only |
| Jenkins | Removed | CLOSED |
| Network discovery | Single-owner cutover to `monitor-01` complete | CLOSED MIGRATION |
| Security/monitoring integration | Closure validated | CLOSED |
| CrowdSec | Not installed | ABSENT / DEFERRED |
| Authelia | Not installed | ABSENT |

## Delivery-step history

Authoritative named/evidenced numbered delivery work in this repository exists through Steps 1–10 and those steps are complete. A historical 20-step programme was referenced, but authoritative names for Steps 11–20 are not present. Do not invent them.

Detailed completion evidence remains in the dated architecture/closure records and Git history. This file is intentionally kept focused on **what is still active now**.

## Maintenance note

Current operational truth is `IaC/inventory/estate.json` plus `CURRENT-STATE.md`. This backlog describes priorities and must not override those authorities.
