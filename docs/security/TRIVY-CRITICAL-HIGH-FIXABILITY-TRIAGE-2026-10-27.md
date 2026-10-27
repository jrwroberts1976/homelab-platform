# Critical / High Trivy findings — fixability evidence before patching

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** Read-only Git/Ansible investigation prepared, not executed on the user's hosts in this turn. Do not equate per-package vulnerabilities with verified exploitable CVEs or confirmed available patched container images.

## Verified existing state
The latest user-run five-host Prometheus verification from 26 October returned 30/30 valid current running image references, with Critical CVE/advisory row counts monitor-01=4, komodo-01=5, cloud-01=9, docker-01=12, greenbone-01=64; High rows 144, 66, 230, 173, 992 respectively. This data is timestamped, changes after image recreation, and counts image/severity/advisory records, not unique root causes or patched candidates.

**Separate confirmed package/image context:**
- Grafana `grafana/grafana:13.2.1` currently pinned in Git for monitor-01. Official v13.2.4 (13 Oct 2026) includes four security advisory fixes. The guarded Grafana-only 13.2.4 playbook and version pins are separately tracked under `docs/security/GRAFANA-1324-SECURITY-PATCH-2026-10-27.md`; code in main is not evidence of live rollout.
- Komodo Core and Periphery are pinned to `ghcr.io/moghtech/komodo-*:2.3.3`, with upstream v2.3.4 dated 22 Oct 2026 and a webpki-roots trust store change. Compatibility across one central core and four Periphery hosts, protected Mongo and TLS/onboarding state must be verified before changing their image references.
- Nextcloud is already on `nextcloud:35.0.2-apache`. The current critical libopenexr package entries have a documented partial ImageMagick EXR coder mitigation only, not a patched image. The separate libxml2 and linux-libc-dev findings have documented reachability/host-kernel assessments and no immediately confirmed safe Debian 13 fix. Do not force package upgrades or remove libraries to falsify Trivy counts.
- Greenbone scanner and seven data/feed images have tightly coupled version/feed lifecycle; an automated 10:00 feed-image replacement previously invalidated seven scans. A later successful Trivy scan restored local 16/16 and the timer now scans after feed refresh. Avoid blind image pulls or feed updates.

## New read-only Ansible root-cause inventory

`IaC/ansible/playbooks/security-container-triage-readonly.yml` executes **serially** against only five canonical Trivy Docker hosts. It requires exact Debian/host/IP identity; checks existing saved scan JSON is complete and within 30 hours; discovers the *current* image tags/immutable IDs with read-only Docker inspect; requires report path constrained to Trivy evidence directory, matching immutable scan report IDs, and correct counts for all severity levels. It prints only bounded per-image C/H package counts, the number of C/H rows with a `FixedVersion` and a **maximum 25** image+severity+advisory+package+version examples per host, not all raw vulnerabilities or protected evidence. It changes no host state, starts no scan, executes no update and prints no credentials.

**Source verification, from `admin-01` after PR review/merge:**

```sh
cd ~/projects/homelab-platform
git switch main && git pull --ff-only origin main
python3 scripts/validate-security-container-triage-readonly.py
python3 scripts/validate-estate.py
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/security-container-triage-readonly.yml --syntax-check
```

**Read-only operator execution:**

```sh
ansible-playbook -i inventory/hosts.yml -b --ask-become-pass \
  playbooks/security-container-triage-readonly.yml
```

Note: Ansible may mark a command task changed by default; this playbook sets `changed_when: false` and does no writes.

## Remediation decisions after collecting evidence

1. Deduplicate identical `(immutable image ID, severity, advisory, package)` groups, prioritising currently internet-reachable services and any actively exploited security advisories. A Trivy `FixedVersion` is *package metadata*, not proof an updated compatible upstream Docker image exists; verify release image digest and vendor guidance.
2. Schedule one compatible patch at a time (Grafana first likely low-blast-radius; Komodo TLS/Periphery across hosts second; Nextcloud/Greenbone only after database/feed and backup assessment). Protect image/digest rollback and persistent data, and test a canary where practical.
3. After each approved image change, verify service health, running image ID and successful *new* Trivy scan under the correct identity. Compare **exact prior CVE+package** with fresh validated report rather than inferring fixes from an aggregate drop.
4. For non-fixable entries, record exploit path, mitigations, owner and review date without silently accepting or deleting CVEs. Greenbone LAN RPC/cookie/certificate/TLS and ICMP timestamp findings require separate host/device policy validation, not Docker image updates.

No unattended bulk upgrade has been authorized or run by this report.
