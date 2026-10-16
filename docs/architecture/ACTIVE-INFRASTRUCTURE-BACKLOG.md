# Active Infrastructure Backlog

**Last reconciled:** 16 October 2026  
**Authority:** Planning register only. Validate implementation claims against `docs/architecture/CURRENT-STATE.md`, `IaC/inventory/estate.json` and live evidence.  
**Current documentation work:** 16 October patching/TLS/security reconciliation applied to the canonical current-state and installed-solutions documents.

## Working rules

- Work in priority order unless James explicitly reprioritises.
- Update this file when a project closes, changes scope or is reprioritised.
- Verify live state before marking implementation complete.
- Keep accepted risks and deliberately deferred work out of the active implementation queue.
- Do not silently reopen completed work based on stale historical plans.
- Do not invent missing numbered roadmap steps or names.
- Historical audit/migration documents remain point-in-time evidence and are not rewritten to look current.

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

A **final post-remediation Greenbone scan is running/pending completion**. Do not mark the vulnerability-remediation work fully closed until that report is reviewed.

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

1. **Wait for and review the final Greenbone post-remediation scan.** This is the only remaining gate on the current patching/vulnerability/TLS workstream.
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

**Do not close this section until the currently running Greenbone scan is reviewed.**

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
