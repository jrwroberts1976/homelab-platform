# Greenbone feed versus Trivy scheduling — 26 October 2026

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** Git-only proposed timer correction. Not merged or deployed. No scan started by this change.

## Confirmed incident and cause

Read-only operator diagnostics on greenbone-01 established a complete recent Trivy summary but only 9/16 current running Docker image IDs validated. These SEVEN Greenbone feed/data images were replaced after the Trivy run:

- cert-bund-data
- data-objects
- dfn-cert-data
- notus-data
- report-formats
- scap-data
- vulnerability-tests

For every one, SCANNED image SHA differed from TAG NOW and RUNNING, while TAG NOW equalled RUNNING. This is **real running image replacement**, not tag-only drift. The current publisher must reject all seven old scan records, report SCAN_COMPLETE=FALSE, and withhold their CVE findings; it must not report false zero vulnerabilities.

Live systemd times (26 Oct 2026 UTC):
- Greenbone managed network scan: 02:00:04 to 04:19:50, success.
- Trivy Docker image scan: 09:29:04 to 09:32:20, success.
- Greenbone feed refresh: 10:00:04 to 10:20:57, success.
- Previous Sunday full-LAN Greenbone scan: 25 Oct 12:00:05 to 15:23:57, success.
- Feed updater status JSON: FEED_CONTAINERS_UPDATED_IMPORT_PENDING at 10:20:57 UTC. It establishes container replacement completed but NOT completion of Greenbone's asynchronous database feed import.
- At inspection the services were inactive. 5.0 GiB RAM available (no swap), and 51 GiB disk free.

**Cause:** The daily Trivy scan ran BEFORE the feed refresh that subsequently recreated seven containers. Trivy's correctly captured image IDs were obsolete by the time the refreshed exporter examined the running images.

## IaC correction, proposed only

The existing Trivy greenbone-01 systemd timer currently schedules 09:00 UTC with 30 minutes randomized delay. Change **only the timer** to 19:00 UTC with the same 30-minute delay, keeping Persistent=false. The chosen window is after the 10:00 local Greenbone feed updater (3-hour systemd time limit) and Sunday's 12:00 local full-LAN Greenbone scan (6-hour scan timeout plus 15-minute systemd margin). In winter the theoretical full-LAN maximum ends at 18:15 UTC, leaving at least 45 minutes to 19:00 UTC. Summer local-time jobs start one hour earlier in UTC.

This scheduled separation prevents the OBSERVED normal-order race but is not an absolute guarantee if systemd jobs run late or images are modified manually; the image-ID fail-closed checks and freshness monitoring remain essential. It does not modify Greenbone feed refresh, full-LAN/managed scans, Docker, any image, the Trivy scanner executable, cache, report data, approved empty-result allowlist or scanner resource caps (MemoryMax=2G, CPUQuota=50%, TimeoutStartSec=180min).

Files:
- IaC/ansible/roles/container_vulnerability_pilot/files/homelab-trivy-greenbone.timer
- IaC/ansible/playbooks/trivy-greenbone-after-feed-timer.yml (new)
- scripts/validate-greenbone-trivy-schedule.py (new)
- .github/workflows/validate-greenbone-trivy-timer-order.yml (new)

The new narrow playbook checks exact greenbone-01 inventory and observed host identity, existing timer/scanner units, known current timer contents, Trivy scanner INACTIVE and timer ACTIVE before any modification. It copies only the reviewed timer with backup=true, daemon-reloads and **restarts the timer unit only** to activate the new schedule. Afterward it asserts Trivy scanner remains INACTIVE and prints the next scheduled trigger. Since Persistent=false, it does not make up a missed scan when restarted. No image scan is started by the playbook.

## Approval-gated operator stages

1. Review and merge PR only after GitHub validations pass.
2. From admin-01, after merging, synchronize Git and validate:

       cd ~/projects/homelab-platform
       git pull --ff-only origin main
       python3 scripts/validate-greenbone-trivy-schedule.py
       python3 scripts/validate-estate.py
       cd IaC/ansible
       ansible-playbook -i inventory/hosts.yml playbooks/trivy-greenbone-after-feed-timer.yml --syntax-check

3. Only with separate explicit timer-rollout approval, execute:

       ansible-playbook -i inventory/hosts.yml -b --ask-become-pass \
         playbooks/trivy-greenbone-after-feed-timer.yml \
         -e greenbone_trivy_timer_change_approved=true

4. Check the timer's next activation is in the **19:00–19:30 UTC window** and scanner was not started by the timer deployment. Record Ansible's backup path.
5. After the next successful scheduled Trivy run or a separately approved scanner-only on-demand run, use read-only Ansible to compare current image IDs to Trivy evidence and central Prometheus metrics. Require RUNNING_IMAGES=16, VALID_IMAGES=16, SCAN_COMPLETE=TRUE and valid scan freshness before declaring coverage restored. If any image changes again, the exporter must go fail-closed. Trivy report validity does not imply vulnerability remediation.
6. Only when scan evidence is reconciled should the independent approval gates for the Greenbone host CVE exporter and Grafana provisioned JSON from merged PR #197 proceed. The current live Grafana dashboard is not changed by this PR.

## Rollback

The playbook creates a timestamped Ansible backup of the old timer. Revert via a separately approved Git-managed Ansible timer-only rollback using the original 09:00 timer definition/backup, daemon-reload and timer-only restart; verify the next trigger. Reversion also reintroduces the earlier freshness problem until alternative ordering is in place.

## Tracking

Security issue #187 and root handover file. Do not classify absent CVEs as zero findings. A feed-container update does not establish the asynchronous Greenbone import is finished; verify it separately if needed.
