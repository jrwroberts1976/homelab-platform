# Grafana Trivy dashboard — findings and scan freshness clarification (26 October 2026)

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** Proposed IaC dashboard change. Not yet deployed to monitor-01; approval-gated update only. Review PR and merge before production execution.

**Canonical dashboard:** `IaC/ansible/roles/monitoring_stack/files/grafana/dashboards/production/homelab-vulnerability-management.json` (UID `homelab-vulnerability-management`, title *Homelab — Vulnerability Management*).
**Grafana URL:** https://grafana.home.jrwroberts.co.uk/d/homelab-vulnerability-management

## What the user observed

- At **2026-10-26 11:52:46** the Grafana Trivy finding table showed `ghcr.io/moghtech/komodo-periphery:2.3.3` on `cloud-01` with **13 CRITICAL / 152 HIGH**, alongside PostgreSQL and Redis. The separate scan-validity panel included `nextcloud:35.0.2-apache` on cloud-01 with image_valid=1.
- This **Time** is a Prometheus sample/scrape timestamp, *not* the underlying scan completion timestamp. It proves Prometheus recently read published metrics, not that Trivy just ran.
- The existing raw Grafana table query `homelab_container_estate_findings` had **no filter excluding Nextcloud**; Nextcloud's absence from the pasted visible rows does not establish a missing metric or exporter bug. Validate the complete dataset / panel pagination and query Prometheus directly.
- Independent read-only Trivy JSON evidence on 26 Oct 08:53:20 UTC: Nextcloud `35.0.2-apache` was scanned and contributed **4 CRITICAL / 231 HIGH** on cloud-01. These are *package-level* findings and do not decrement for ImageMagick EXR coder mitigation.
- Independent Komodo investigation on cloud-01 confirmed the running container `ghcr.io/moghtech/komodo-periphery:2.3.3` with installed Perl packages `libperl5.40`, `perl`, `perl-base`, `perl-modules-5.40` all `5.40.1-6`, and `openssh-client 1:10.0p1-7+deb13u4`. The **13 CRITICAL package rows are still a valid finding baseline** for that unmodified image; 12 Perl rows list fixed Trixie version `5.40.1-6+deb13u1`, one SSH client row has no fix listed in the report. The `apt-cache policy` candidate shown inside the container remained the old installed version because the image's local package metadata is not evidence of current repository availability. Do not `apt upgrade` a running container.

## Change to the dashboard (display only)

- Preserve `refresh: 30s`, all existing panel IDs, datasource references and source metrics. No vulnerability scanner or exporter changes.
- Make the general Trivy findings panel aggregate by `target_name,image,severity`, retaining all severities and showing readable **Host / Image / Severity / Findings** columns. Suppress noisy scrape timestamp from the visual presentation; a dedicated panel reports actual scan age.
- Add **Nextcloud findings by severity** restricted to `target_name="cloud-01",image=~"nextcloud:.*"`. Missing data remains **No data**, never implicitly treated as 0 findings.
- Add separate **scan age (hours) by host**, **scan-complete status by host** and **CRITICAL package findings by host** tables, with explicit explanation that an old textfile metric can remain `scan_complete=1`. Treat scan age **over 30 hours** as stale.
- Grafana dashboards are file-provisioned in `/opt/monitoring/grafana/provisioning/dashboards/production/` from the Ansible role, Grafana provider checks files every **30 seconds**. No Grafana restart is needed for this JSON-only update.

## Controlled deployment on monitor-01

After PR review/merge and local `git pull --ff-only origin main` on admin-01:

```bash
cd ~/projects/homelab-platform/IaC/ansible

python3 -m json.tool roles/monitoring_stack/files/grafana/dashboards/production/homelab-vulnerability-management.json >/dev/null
ansible-playbook -i inventory/hosts.yml playbooks/grafana-trivy-dashboard-update.yml --syntax-check

# Explicitly approved deploy, limited to one Grafana JSON file only:
ansible-playbook -i inventory/hosts.yml -b --ask-become-pass \
  playbooks/grafana-trivy-dashboard-update.yml \
  -e grafana_trivy_dashboard_update_approved=true
```

The Ansible playbook:
1. requires explicit approval; validates Debian 13 `monitor-01` identity `192.168.2.52`;
2. confirms the production dashboard file already exists and Grafana is healthy;
3. copies the version-controlled dashboard only, with `backup: true` and JSON syntax validation;
4. checks panel identity and health afterwards, reporting the backup path;
5. **does not run `monitoring.yml`, reconcile Docker, pull images, restart Grafana, modify Prometheus or trigger Trivy scans**.

Grafana should automatically reload the provisioned file on its next polling cycle (~30 seconds). Inspect the Grafana URL to confirm the panels appear. File-level acceptance does not establish that Prometheus contains every expected series: query actual metrics below.

## Read-only Prometheus truth checks

On `monitor-01`, Prometheus API listens at `127.0.0.1:9090`. Query via Prometheus Explore or `curl --get --data-urlencode 'query=...'` from the host:

```promql
# Nextcloud per-severity current reported image findings
homelab_container_estate_findings{target_name="cloud-01",image=~"nextcloud:.*"}

# Cloud-01 last completed scan age in hours (actual age, not sample Time)
(time() - homelab_container_estate_last_scan_timestamp_seconds{target_name="cloud-01"}) / 3600

# Cloud-01 scan completeness and coverage, separately
homelab_container_estate_scan_complete{target_name="cloud-01"}
homelab_container_estate_running_images{target_name="cloud-01"}
homelab_container_estate_valid_images{target_name="cloud-01"}

# Absence/presence of textfile scrape errors
node_textfile_scrape_error{instance="192.168.2.53:9100"}

# Observed cloud-01 CRITICAL package rows in last exported evidence
sum(homelab_container_estate_findings{severity="CRITICAL",target_name="cloud-01"})
```

For a complete and current four-image cloud-01 scan following the Nextcloud upgrade, expected **historical** values are running=4, valid=4, scan_complete=1, image Nextcloud CRITICAL=4, HIGH=231 and cloud-01 CRITICAL total=18. These figures can change legitimately after scans and patch updates; do not hard-code them into dashboard panels.

**If scan age is over 30 hours, exporter data incomplete, or specific image findings absent:** inspect the scan summary, image identity and systemd service/timer before rerunning the scanner. Do not overwrite metrics with invented counts or restart healthy services to make dashboard numbers change.

## Rollback

The targeted Ansible copy task preserves the previous dashboard file with a timestamped `backup_file` reported by Ansible if changed. If review finds a presentation regression, restore that exact backup via an approved and auditable Ansible change, or revert the relevant Git commit and rerun the targeted playbook. Grafana provider reloads the restored JSON; no Docker restart is required.

## Security-triage separation

- EXR codec policy mitigation **does not** patch OpenEXR libraries or change Trivy image findings.
- The no-NFS-server observation affects runtime exposure assessment, **not** the image `linux-libc-dev` package finding.
- Komodo Perl 12 fixable package rows remain until a vendor-approved image containing fixed packages is deployed through IaC and a new Trivy scan confirms the running image digest and package versions.
- Reference issue #187 for security remediation; this dashboard-only PR is not a CVE remediation.
