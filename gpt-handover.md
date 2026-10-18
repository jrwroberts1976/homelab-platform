# GPT Handover — Homelab Platform

**Last updated:** 18 October 2026

**Session focus:** Greenbone vulnerability validation and remediation

**Current status:** Proxmox-2/VM203 and both PVE nodes confirmed accessible/quorate; Greenbone Docker, gvmd and PostgreSQL now healthy. 18 October reboot triggered a scan before gvmd was ready: scan failed at 16:18:01 BST and gvmd only accepted GMP at 16:19:29. VT database rebuild/feed synchronisation completed approximately 16:37 BST. **Fresh GMP preflight and post-remediation scan remain unverified**; last saved evidence is 16 October (0 actionable / 30 accepted).

**Owner:** User-led, ChatGPT-assisted infrastructure work

## Read this first in every new chat

1. Read this file **before** proposing new work.
2. Read `IaC/inventory/estate.json`, `docs/architecture/CURRENT-STATE.md`, `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md`, and the relevant Ansible configuration. These remain the source of truth; this handover is a **working pointer**, not an independent authority.
3. Read `AGENTS.md` and follow its preflight and validation rules.
4. Check Git status and the latest commits before editing; do not overwrite work from another session or blindly trust this handover if it is older than current changes.
5. Distinguish **implemented/committed**, **validated live**, **pending validation**, and **accepted risk**. Never interpret missing or stale evidence as zero vulnerabilities.
6. **Every user/assistant-driven change** to the repository, IaC, operational configuration, architecture, runbooks, security findings or project priorities requires a contemporaneous update to this file, preferably in the **same commit/PR**. Update the current status, evidence/commands, decision, next action and change log. Update canonical docs too if architecture or backlog status changed. Routine automated telemetry-only commits do not by themselves change the handover unless they alter a decision or status.
7. **Use Ansible for every host-level operation**, including inspection and read-only checks, from `admin-01` using the Git-managed inventory. **All persistent changes go into Git-managed IaC first**, validated and applied by Ansible; do not propose direct SSH/manual edits except an explicitly approved emergency exception subsequently reconciled into IaC.
8. Do not store passwords, keys, API tokens or raw confidential scan evidence here. Do not claim that local-only commands, tests, deployment or live verification ran unless they actually did.

## Current task — finish the Greenbone remediation gate

As of the repository review on **18 October 2026**, the last documented Greenbone managed scan is **14 October 2026**:

| Finding type | Last documented count |
| --- | ---: |
| Critical | 0 |
| High | 0 |
| Medium actionable | 1 |
| Low | 0 |
| Accepted risks | 30 |

The Medium finding was **cleartext Zabbix management HTTP**. Trusted HTTPS/reverse-proxy and secure cookie remediation is recorded as implemented, but **the final scan has not yet been reviewed**. Do not close it prematurely.

Other remediation already recorded:
- `docker-01`: Raspberry Pi 4 Trusted Firmware-A v2.15.0 speculative-execution hardening, codified and validated idempotently with Ansible; commit `b3047742`. Confirm scan findings after remediation.
- Grafana: port 3000 bound to localhost behind nginx HTTPS; seven public certificate renewal/deploy paths dry-run tested on 16 October.
- 16 October: new `tcp_timestamp_hardening` Ansible playbook/role to disable `net.ipv4.tcp_timestamps` across the 15 Greenbone-flagged Linux hosts; commit `e27b864f4d`. **Git commit confirmed; live rollout/Greenbone clearance not independently checked in this 18 October review.**
- 16 October: automated Suricata threat-rule refresh with validation and rollback; commit `827e7c9e85`. This is separate preventative security work, not proof that Greenbone findings cleared.
- Accepted-risk details are integrated with management reporting and Grafana; verify their consistency against Greenbone evidence.

**Decision:** Finish vulnerability validation before changing priority to Raspberry Pi overclocking, Docker lifecycle, or disaster recovery.

**Outage update — 18 October 2026:** The user reports **`Proxmox-2` is down**; on `admin-01`, Ansible's `greenbone-scan-evidence-readonly.yml` failed at the first remote command with `ssh: connect to host 192.168.2.57 port 22: Connection timed out`. The initial `assert` ran locally (it did **not** establish SSH connectivity). This **does not** mean there are zero vulnerabilities. Greenbone VM203, monitoring VM202, `dns-01` CT101, and `edge-01` CT103 are assigned to `Proxmox-2`; guest disks are node-local, and these workloads may be unavailable while their host is down. Actual Proxmox-2 power/cluster health has not been independently verified, nor has `PROXMOX` quorum been checked after the outage. Restore/repair is **not** approved by this note; avoid rebooting/migrating guests without evidence and authorisation.

**Greenbone stack live health evidence — 18 October 2026 (approx. 16:38 BST):** The user executed `greenbone-stack-health-readonly.yml` after fetching the repository update. Ansible syntax check PASSED; recap `greenbone-01 ok=7 changed=0 unreachable=0 failed=0`. Docker `ActiveState=active`; `gvmd` and `pg-gvm` containers are `Up ... (healthy)`; `docker compose exec ... gvmd` confirmed `gvmd-socket-present`; historical managed scan service still `failed` from the earlier launch. Logs give a clear **startup race**: Docker active and managed scan launched at **16:17:47 BST**, scan failed at **16:18:01 BST**, gvmd recorded `ready to accept GMP connections` only at **16:19:29 BST**. A scanner/database VT hash mismatch triggered a rebuild; logs show **190,103 VTs updated at 16:36:50 BST** and `SecInfo feed sync finished` at approximately **16:37:11 BST**. PostgreSQL emitted repeated `checkpoints are occurring too frequently` / `max_wal_size` hints during the import (separate performance observation; no unreviewed DB tuning). `gvmd` also logged a missing `data-objects/gvmd` feed subdirectory during startup; its impact is not established.

The existing `homelab-greenbone-managed-scan.timer` uses `Persistent=true`, and its service only orders `After=docker.service network-online.target`, which does **not** guarantee GMP readiness. This explains the attempt during startup; a durable Ansible-managed GMP readiness gate is a candidate fix but has **not** been deployed or yet designed/validated. Before starting another scan, use `greenbone-gmp-preflight.yml` to run the existing scan runner's `managed --check` (authenticated GMP task lookup **without scanning**). This uses a temporary, cleaned-up GMP config and ephemeral Docker helper; not a completely side-effect-free operation. The dedicated preflight is committed but **not yet syntax-checked or executed live**.

**Live Ansible results — 18 October 2026, approximately 16:27–16:29 BST:** Controller probes show TCP/22 connected to `PROXMOX`, `Proxmox-2` and `greenbone-01`. QNetd service is active. `pvecm status` returned `Quorate: Yes`, `Total votes: 3`, `Flags: Quorate Qdevice`. Proxmox reports both nodes online and all documented active guests on Proxmox-2 (`dns-01` CT101, `edge-01` CT103, `monitor-01` VM202 and `greenbone-01` VM203) running. The diagnostic and scan inspection playbooks both completed with `changed=0` and no unreachable/failed hosts.

**Vulnerability evidence and failure — 18 October 2026:** Live Ansible read `/var/lib/homelab-greenbone-scanning/managed.json`: collection `2026-10-16T14:28:39.034610+00:00` (15:28 BST); authenticated managed report `35dc10c3-aac0-46fa-b6ce-7c1b31440d38`; Critical=0, High=0, Medium=0, Low=0 actionable; Log=828; `actionable_count=0`; `accepted_risk_count=30`. This is **historical saved evidence**, not a fresh result. Its 30 accepted findings comprise 14 ICMP timestamp replies (CVE-1999-0524), 15 TCP timestamp disclosures and one missing HttpOnly cookie for the BirdNET-Go listener on `docker-01` TCP/8080. Some accepted TCP timestamp observations may predate the Ansible hardening; re-scan before claiming removal.

The 16 October 06:50 scan reported successful evidence publication at 08:43 with 0 actionable / 30 accepted (772 informational), and a later 16 October 17:14 scan was launched without a completion record in the last 25 unit journal lines. A restart-associated scan at **18 October 16:17:47 BST** failed at **16:18:01 BST**, `ExecMainStatus=1`: `Could not connect to socket /run/gvmd/gvmd.sock. Error was [Errno 111] Connection refused`. The scheduled timer remained configured for 19 October 02:00 BST. Container startup/readiness immediately after boot is a **plausible hypothesis**, not confirmed root cause. No new scan should start until current `gvmd`/PostgreSQL state is checked; do not interpret a failed scan as clean.

**Next diagnostic IaC:** `IaC/ansible/playbooks/greenbone-stack-health-readonly.yml` checks Docker service, all Compose containers, `gvmd` socket presence and bounded `gvmd`/`pg-gvm` logs without restarting anything. Created alongside this handover update; syntax and live execution **not yet verified**.

**Recovery update — 18 October 2026:** User reports `Proxmox-2` has returned. This is **user-reported**, not verified live. First check PVE node status/quorum/QDevice and Greenbone TCP/22 through the Ansible connectivity playbook. If VM203 is accessible, run the separate read-only Greenbone evidence playbook. Do not start/restart a scan, guest or service just on the basis of this report.

**IaC diagnostic created:** `IaC/ansible/playbooks/greenbone-connectivity-readonly.yml` was initially committed at `1220e052`, then revised at `1ff5ed8d` (and probe-result display corrected at `4329652183`) to run read-only probes on `admin-01` and gather `pvecm status` and cluster resource views from surviving `PROXMOX` rather than SSHing into offline `Proxmox-2`. This connectivity diagnostic **passed Ansible syntax check and live execution** on 18 October 2026, with both PVE nodes/quorum and Greenbone TCP/22 healthy.



**Controller Git merge resolved — 18 October 2026:** `admin-01` successfully reconciled local-only `f752562f` (qBittorrent and Kodi DLNA firewall IaC) with GitHub `origin/main`. The user created protective branch `backup/media-before-sync-20261018`, retained remote `docs/architecture/MEDIA-01.md` when resolving the only merge conflict, and committed merge `9dbbacc9`. User-supplied terminal output confirmed `git push origin main` succeeded (`36f9fd20..9dbbacc9`), `python3 scripts/validate-estate.py` passed (20 active assets), `git diff --cached --check` had no warnings, and `ansible-playbook -i inventory/hosts.yml playbooks/greenbone-scan-evidence-readonly.yml --syntax-check` passed. **The actual Greenbone read-only inspection has NOT yet run.** The untracked Kodi-related paths `IaC/ansible/metadata.tvshows.themoviedb.org.python` and `IaC/ansible/tvshows` remain intentionally untouched. No change to host configuration was made during the merge.

### Next action — verify authenticated GMP readiness without scanning

After Proxmox-2 recovered, the read-only Docker/pg-gvm/gvmd diagnostic showed healthy containers and completed VT rebuild. The failed 16:18 scan was launched before gvmd's 16:19 GMP-ready event. Use **Ansible** to run the existing scan runner's **`--check` mode**, which validates GMP authentication and task lookup without starting a scan. The IaC preflight `IaC/ansible/playbooks/greenbone-gmp-preflight.yml` refuses to run concurrently with an active managed scan service, additionally uses the runner's shared `flock` lock to avoid collisions with other scan modes, and bounds the check to 150 seconds. It uses a disposable helper container and temporarily writes/cleans up a protected runtime credential config, so it is non-scanning, not literally side-effect-free.

```bash
cd ~/projects/homelab-platform
git status -sb
git pull --ff-only || exit 1
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-gmp-preflight.yml --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-gmp-preflight.yml
```

**If CHECK=PASS**, evaluate a permanent startup/readiness gate in `greenbone_scanning` IaC before deliberately initiating a fresh managed scan. **If it fails**, inspect the failure; no blind restarting or starting scans. Do not mark previous findings cleared until a newly completed scan report/evidence publication and coverage are verified.

**Do not** start an additional scan while one is running. The runner is `/usr/local/sbin/homelab-greenbone-scan` and the evidence path is `/var/lib/homelab-greenbone-scanning/managed.json`. The managed scan systemd service is `homelab-greenbone-managed-scan.service`; the timer is `homelab-greenbone-managed-scan.timer`. Source: `IaC/ansible/roles/greenbone_scanning/`.

After seeing the live result:
1. Verify freshness, report ID, mode and completed scan status (a recent JSON file alone does not prove target coverage).
2. Compare actionable and accepted-risk findings with the documented 14 October baseline, by host and NVT/OID as available.
3. Explicitly verify the Zabbix cleartext HTTP finding, Raspberry Pi speculative-execution findings, and TCP timestamp findings.
4. Resolve any remaining actionable items; formally reconcile intentional risks without treating them as fixed.
5. Verify that evidence transfer to `monitor-01` and the Grafana accepted-risk display match the authoritative report.
6. Update this file **and** `CURRENT-STATE.md` / backlog when the scan is genuinely reviewed and closure justified.

### Known locations

- Estate inventory: `IaC/inventory/estate.json`
- Ansible inventory: `IaC/ansible/inventory/hosts.yml`
- Greenbone playbooks: `IaC/ansible/playbooks/greenbone-scanning.yml`, `greenbone-scan-runner.yml`, `greenbone-authenticated-scan.yml`, **`greenbone-scan-evidence-readonly.yml`**, **`greenbone-connectivity-readonly.yml`**
- Greenbone implementation: `IaC/ansible/roles/greenbone_scanning/`
- Greenbone host: `greenbone-01` = `192.168.2.57`
- Evidence publisher destination: `monitor-01` via the managed reporting evidence pipeline; compare timestamp and report ID
- Current architecture: `docs/architecture/CURRENT-STATE.md`
- Remaining work: `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md`

## Programme context after the Greenbone gate

The core 15-host Ansible Linux baseline was patched on **16 October 2026**: **15 reachable, 0 pending package updates, 0 required reboots**. Core monitoring and security integration are operational; seven trusted HTTPS renewal paths were dry-run tested. The backlog estimated about **70–80%** practical overall completion, excluding optional/deferred capabilities.

Pending after vulnerability review (unless reprioritised):
1. Raspberry Pi overclocking **feasibility only**, read-only inventory/thermal/power checks before any proposed change.
2. Encode already-live Proxmox GDS `gather_data_sampling=force` in IaC.
3. Review the Certbot Cloudflare Python dependency compatibility warning.
4. Project 7: controlled estate-wide Docker image lifecycle review (BirdNET canary already complete).
5. Project 6: QEMU restore proof, application-consistent Nextcloud/PostgreSQL recovery, independent backup copy.
6. Project 8: deliberate legacy cleanup review. Optional password manager/web analytics and deferred Tunnel are not automatic tasks.

## Latest session log

| Date | Change / observation | Evidence and validation | Next step |
| --- | --- | --- | --- |
| 2026-10-18 | Greenbone stack health verified post-reboot; confirmed managed-scan/GMP startup race and completed VT rebuild. Added non-scanning GMP preflight IaC. | User Ansible output: Docker active, gvmd/pg-gvm healthy, socket present; scan failed 16:18:01 BST before gvmd ready 16:19:29; 190103 VTs rebuilt and feed sync complete around 16:37 BST. New preflight **untested**. | Syntax-check and run `greenbone-gmp-preflight.yml`; if authenticated lookup succeeds, design/apply reviewed startup guard and validate a fresh scan. |
| 2026-10-18 | Verified Proxmox-2/cluster recovery, obtained old Greenbone evidence and found new scan startup failure; added read-only Docker/gvmd diagnostic Ansible playbook. | User-pasted controller output: both PVE nodes online, quorum 3/3 with QDevice, Greenbone reachable; 16 Oct 14:28Z JSON report `35dc10c3` 0 actionable/30 accepted; 18 Oct 16:18 BST scan failed with gvmd socket connection refused. New diagnostic **not executed**. | Pull and syntax-check/run `greenbone-stack-health-readonly.yml`; investigate startup readiness before any repairs/re-scan. |
| 2026-10-18 | User reports `Proxmox-2` is back online after the outage. | **Reported by user only**; cluster quorum/VM203 and Greenbone SSH health not yet verified by Ansible; no scan evidence read. | Run existing Ansible connectivity diagnostics; if healthy, inspect Greenbone evidence read-only; reconcile findings. |
| 2026-10-18 | User reported `Proxmox-2` down after Greenbone read-only playbook failed to reach VM203 on TCP/22. Added/revised read-only Ansible connectivity/cluster diagnostic. | User-provided Ansible output: `greenbone-01` SSH timeout, `unreachable=1` (host assertion passed locally only); diagnostic IaC commits `1220e052`, `1ff5ed8d`, `4329652183`; **new diagnostic not yet executed**. | Verify surviving PVE quorum/node/guest state via the new Ansible playbook; defer Greenbone findings review until VM203 access returns. |
| 2026-10-18 | Confirmed clean controller merge/push and Ansible syntax test; updated handover after merge. | Merge `9dbbacc9` on `main` verified via GitHub; controller's user-pasted syntax check PASS, estate validation PASS; **Greenbone live evidence still pending**. | From `admin-01`, fast-forward local checkout and run `greenbone-scan-evidence-readonly.yml`; assess findings and update handover. |
| 2026-10-18 | Resolved `MEDIA-01.md` conflict retaining remote documentation, preserved local qBittorrent IaC and completed merge `9dbbacc9`; push succeeded. | Controller output: estate validation PASS (20 assets), no whitespace errors, Greenbone inspection playbook Ansible syntax PASS; no live scan inspection performed. | Pull latest handover fast-forward and run Ansible read-only Greenbone inspection. |
| 2026-10-18 | Controller history confirms exactly one local-only commit: `f752562f` (qBittorrent and Kodi DLNA firewall / `media-01`), with 7 remote-only commits at the time of the user's last fetch; the remote has since advanced. | User-supplied `git log` and `git diff --stat`; remote `788d8330` also changes `docs/architecture/MEDIA-01.md`, so conflict is possible; **full local patch not yet inspected**. | Preserve local commit with a backup branch, refresh origin, review/merge without dropping it, then run Ansible Greenbone evidence inspection. |
| 2026-10-18 | Local `admin-01` checkout reported divergent `main` and `origin/main`; fast-forward pull failed, so the new Greenbone playbook is not local. Untracked Kodi-related directories exist. | User-supplied controller output; **local-only commits and content not yet inspected; no Ansible run or live scan verified**. Preserve all local work, run read-only Git history/diff commands before choosing merge/rebase. | Inspect local commits and identify security/vulnerability progress; reconcile safely before attempting the Greenbone playbook. |
| 2026-10-18 | Confirmed Ansible-only host operations and Git-managed IaC for persistent changes; added reusable, read-only Greenbone Ansible inspection playbook. | `AGENTS.md` rule commit `98d2615269`; new `IaC/ansible/playbooks/greenbone-scan-evidence-readonly.yml` commit `4d688144a6`. **No live scanner or controller access; syntax check and playbook execution still required.** | On `admin-01`, sync the repo, syntax-check and run the playbook; return its results. |
| 2026-10-18 | Created cross-chat handover, then updated `AGENTS.md` to require handover updates for user/agent changes. | Handover commit `c0dbfedf0232`; AGENTS commit `cba755914606`. GitHub files read back successfully; **local `validate-estate.py` and GitHub Actions result not yet verified**, and **no live scanner access / new scan result verified**. | Obtain live managed scan status and evidence; reconcile findings. |
| 2026-10-17 | Latest existing repository work documented `media-01` service/UPnP port state. | Commits `788d8330d5` / `aecfd02d68`. | No change to Greenbone validation gate shown. |
| 2026-10-16 | TCP timestamp hardening and Suricata updater committed. | Commits `e27b864f4d` / `827e7c9e85`; repo changes inspected on 18 October. | Verify live rollout / scan findings as appropriate. |

## Session update checklist

For **every** change we make:
- [ ] Check current Git/repository state and read the authoritative inventory/docs first.
- [ ] Use Ansible for host-level inspection and deployment; encode any persistent host change in reviewed, Git-managed IaC before applying it.
- [ ] State exactly what changed (including path and commit/ref) and why.
- [ ] Record what was **tested live**, what was **tested syntactically**, and what is **not tested**.
- [ ] Update status and next actionable step here; update canonical docs/backlog if impacted.
- [ ] Validate with `python3 scripts/validate-estate.py` and applicable tests/workflows where execution is available.
- [ ] Commit/push changes and this handover together when possible; verify the new repository state.
