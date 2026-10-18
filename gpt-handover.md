# GPT Handover — Homelab Platform

**Last updated:** 18 October 2026  
**Session focus:** Greenbone vulnerability validation and remediation  
**Current status:** Awaiting fresh *live* Greenbone scan evidence; no claim of a clean final scan  
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

**Current controller Git blocker (observed 18 October 2026):** On `admin-01`, `git pull --ff-only` fetched from GitHub but failed because local `main` and `origin/main` have **diverged**. The new `greenbone-scan-evidence-readonly.yml` was consequently absent from the local checkout and its syntax check failed with *playbook could not be found*. Two untracked paths (`IaC/ansible/metadata.tvshows.themoviedb.org.python` and `IaC/ansible/tvshows`) were also observed; preserve them. **Do not reset, clean, merge, rebase, pull or overwrite files until local-only commits are inspected.** Next action is **read-only local Git history comparison**, not Greenbone deployment. Local commit identities/content have not yet been supplied and should not be guessed.

From `admin-01` in `~/projects/homelab-platform` run (read-only):

```bash
git status -sb
git log --oneline --decorate origin/main..HEAD
git log --oneline --decorate HEAD..origin/main
git diff --stat origin/main...HEAD
git diff --name-status origin/main...HEAD
git log --graph --oneline --decorate --all -30
```

Inspect local-only patches, especially Greenbone, security and remediation work; agree a safe preservation/reconciliation plan **before** updating local `main`. A three-dot diff compares local changes since the merge base, unlike a two-dot diff between divergent tips.



### Next action — Ansible-only, read-only Greenbone inspection

**All host work is via Ansible from `admin-01`; all persistent changes are made in Git-managed IaC before deployment.** The standard reusable inspection playbook is:

`IaC/ansible/playbooks/greenbone-scan-evidence-readonly.yml`

**After local Git divergence is understood and safely reconciled**, syntax-check and run the read-only inspection. Do not run the following checkout update now while branches have diverged:

```bash
cd ~/projects/homelab-platform
git status --short
# Only after local commits are preserved and branch divergence reconciled:
git pull --ff-only
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-scan-evidence-readonly.yml --syntax-check
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-scan-evidence-readonly.yml
```

This playbook uses Ansible modules to query the scanner's systemd unit, timer, last 25 journal lines and machine-readable `managed.json` evidence, including the actionable and accepted-risk findings. It **does not** launch a scan, change configuration or install anything. **Repository code was committed, but there has not yet been a live controller syntax check or execution.** If a Git working tree has local edits, reconcile them before pulling.

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
- Greenbone playbooks: `IaC/ansible/playbooks/greenbone-scanning.yml`, `greenbone-scan-runner.yml`, `greenbone-authenticated-scan.yml`, **`greenbone-scan-evidence-readonly.yml`**
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
