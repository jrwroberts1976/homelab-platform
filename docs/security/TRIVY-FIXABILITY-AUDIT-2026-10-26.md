# Trivy image fixability inventory — read-only remediation wave 0

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** Review/merge code before running. This is a bounded **read-only** Ansible scan-evidence audit and does NOT install patches, run vulnerability scans, query a remote registry or alter risk acceptance.

## Why this exists

On 26 October, five running Docker hosts had **30/30 fresh valid image reports** and **12,267 Trivy image/severity/advisory detail series**, comprising **94 CRITICAL** and **1,605 HIGH** references. They are NOT 12,267 unique CVEs or automatically remediable vulnerabilities: many occur in different images/packages, many have no listed fixed version, and Greenbone host/network scans measure different issues.

To decide what to patch, we need the **installed package version and Trivy-listed fixed version** alongside image tag and immutable identity, grouped per validated current image. Prometheus four-column dashboard Details intentionally omit InstalledVersion for readability, so we must read trusted original per-image reports.

## Safe scope

The script `IaC/ansible/playbooks/files/trivy-fixability-readonly.py` is invoked from `IaC/ansible/playbooks/trivy-fixability-readonly.yml` serially through Ansible, from admin-01, for **monitor-01, komodo-01, cloud-01, docker-01 and greenbone-01** only. It calls Docker **ps/image inspect read-only**, reads the existing `/var/lib/homelab-container-security/pilot-inventory-summary.json` and corresponding per-image Trivy JSON. It fails rather than reporting fixes if:

- Whole scan marked incomplete or older than 30 hours.
- A running image lacks a successful matching scan, or the saved immutable image ID mismatches Docker or report Metadata.
- The Trivy report path is outside the scanner directory (including symlink escapes), missing, malformed, or counts do not exactly match every saved severity.
- Host OS/identity/address differs from the canonical inventory.

Its output includes per-image CRITICAL/HIGH vulnerable **package rows**, unique CVE IDs per image and severity, and numbers of rows with/without a Trivy-listed `FixedVersion`. It prints at most the top 24 Critical/High fixed-version package *hints* and 12 no-fix Critical examples per host. A line is a scanner claim, **not confirmation an official compatible container image is released**. It prints no raw report JSON, environment, tokens, credentials, protected data or full host configuration; diagnostic output should still be handled as operational information. All `changed_when: false`. The Ansible script transport may use a temporary execution file but writes no persistent configuration and triggers no scanning or service restart.

## Operator steps

```bash
cd ~/projects/homelab-platform
git switch main
git pull --ff-only origin main
python3 scripts/validate-trivy-fixability-readonly.py
python3 scripts/validate-estate.py
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/trivy-fixability-readonly.yml --syntax-check

# Read-only evidence; intentionally no approval variable for an actual patch.
ansible-playbook -i inventory/hosts.yml -b --ask-become-pass \
  playbooks/trivy-fixability-readonly.yml
```

Capture/compare `IMAGE ... CRIT_ROWS/HIGH_ROWS/TRIVY_FIXED_ROWS` and `FIX_HINT` lines. Do not confuse unlisted fixed versions with proof no fix exists; cross-check upstream advisories and image release tags. Explicitly identify shared image references across hosts to avoid multiple independent patch tickets for the same underlying image.

## Actual remediation waves, separate from this audit

1. **Supported security patch:** Grafana 13.2.1 -> 13.2.4, from Git-managed PR #202. It has its own **disruptive**, approval-gated `grafana-security-patch-1324.yml` with protected SQLite backup, single-service recreation and API/other-service guards. Applying that PR must be separately authorised in a maintenance window.
2. **Trust-root update:** Komodo Core/Periphery 2.3.3 -> 2.3.4 is a real upstream release (22 October), but the extent to which it resolves Trivy package findings is **unknown**. Core data/storage and Periphery connectivity require different backups/checks. Do not indiscriminately recreate Core and all Periphery agents at once.
3. **Nextcloud residual Critical:** Nextcloud 35.0.2 has a partially mitigated OpenEXR image-codec route, plus libxml2 and linux-libc-dev vulnerability packages under separate investigation; Debian 13 Trixie and running host/kernel contexts differ. An unapproved container package change is not safe. See `NEXTCLOUD-REMAINING-CRITICAL-CVES-2026-10-26.md`.
4. **Greenbone host/network findings:** 7 Medium and 25 Low in the last full-LAN issue #187 baseline include RPC, cookie, certificates, TLS renegotiation and timestamps across mixed LXC, Docker and Proxmox devices. Firmware/config and actual network owners must be identified; do not blanket patch firewall or firmware or update all Greenbone containers without compatibility checks.
5. **Host apt upgrades:** Use existing host patching IaC/telemetry and current apt plan; 16 October 0-pending baseline is stale for 26 October. A controlled rolling apt deployment needs fresh per-host package lists, cluster/LXC safety, reboots individually where required, and service health gates.

## Closure

For each supported change: record immutable old/new image IDs and release, backup/recovery plan, one-service Ansible cutover, app health, authorised new Trivy scan, matching new immutable image identity, per-CVE result and central Prometheus freshness. Distinguish Fixed, Mitigated, Accepted and Pending. A lower dashboard count without image and version proof does **not** close a CVE.
