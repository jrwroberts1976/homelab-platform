# Four-column Trivy CVE visibility in Grafana — 26 October 2026

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** Git-only proposal on branch monitoring/trivy-four-column-cves-20261026. Not merged or deployed until independently verified and approved. This does **not** repair or reclassify a vulnerability.

## User requirement

The existing Grafana "Trivy — findings by image / severity" panel showed unreadable raw Prometheus labels (Time, __name__, image, instance, job, severity, target_name, Value) and one row per image/severity aggregate, with **no CVE or explanation**. The replacement **Trivy — vulnerabilities: CVE and details** table has exactly:

| Target name | Severity | CVE | Details |
| --- | --- | --- | --- |
| Verified Trivy scanner Docker host | Trivy severity | Trivy VulnerabilityID, clickable OSV advisory link | Bounded text containing affected running image, Trivy Title/Description summary, package names, and fixed versions (if scanner supplies them) |

**Never invent a CVE**. Advisory IDs other than CVEs are shown exactly as supplied by Trivy; missing VulnerabilityID rows remain in the severity summary counts, not this CVE table. Multiple affected images may legitimately produce the same CVE more than once because they are different remediation targets.

No raw Prometheus scrape timestamp, __name__, instance, job, image as separate column, or numeric gauge value is visible. Image context is intentionally retained inside Details. The new table uses the existing Trivy host selector, default All, and follows severity priority (Critical, High, Medium, Low, Unknown). Old redundant "images with critical findings" and "scan age by host" table panels are removed; the existing summary cards still show counts and scan age. The dashboard UID and Git file provisioner's 30-second poll interval remain unchanged.

## Trusted data and bounded cardinality

The existing all-host Trivy publisher used **homelab_container_estate_critical_cve** for critical-only advisory labels. Its source was insufficient to show individual High/Medium/Low CVEs. This PR adds **homelab_container_estate_cve_detail_score**, generated solely by parsing already-collected, validated per-image Trivy JSON. Existing count families and critical metric are **preserved** for compatibility. Each series has `image`, `severity`, `cve`, `details` labels, plus Node Exporter's target_name, with gauge value 5/4/3/2/1 for severity rank only (**NOT CVSS**). Rows are deduplicated within an image/severity/advisory, not across images. Details are capped at 420 characters, scanned titles/descriptions are shortened and normalised, and package/fix lists are bounded. The per-image advisory group safety cap prevents runaway metric series.

For each image, the publisher verifies the existing **summary completed/fresh**, **running Docker image immutable ID**, **report metadata image ID and restricted report path**, and the **actual counts for *every* severity** against the saved Trivy summary before emitting findings or CVE details. Invalid/stale/mismatched reports are fail-closed and marked image_valid=0, never clean. An empty table while coverage is incomplete means unknown, **not zero vulnerabilities**. This publisher does not trigger a new Trivy scan or any Docker operation besides read-only inspect.

## Rollout and explicit gates

1. Review PR and all CI checks; merge only after operator approval. On admin-01, pull main and run:
   - python3 scripts/validate-trivy-cve-dashboard.py
   - python3 scripts/validate-unified-vulnerability-cves.py
   - python3 scripts/validate-estate.py
   - cd IaC/ansible; ansible-playbook -i inventory/hosts.yml playbooks/trivy-critical-cve-exporter.yml --syntax-check
   - ansible-playbook -i inventory/hosts.yml playbooks/grafana-trivy-dashboard-update.yml --syntax-check
2. **Separate approval** to deploy exporter to cloud-01 canary, then to other four hosts. Reuse approved guarded, serial playbook `trivy-critical-cve-exporter.yml` (despite legacy name). Explicit flag `trivy_critical_cve_exporter_approved=true`. Its backup restores prior publisher; it reads existing Trivy reports and publishes Node Exporter textfile without new scans, restart or upgrade.
3. Read-only Prometheus verification on monitor-01 of coverage, freshness, new cve_detail_score label families and severity ranks for selected hosts. Never claim 0 CVEs from an empty result if metrics missing or scan incomplete.
4. Deploy **Greenbone HOST CVE metrics exporter** from merged PR #197 only if still outstanding, by separately approved `grafana-greenbone-cve-metrics-update.yml -e greenbone_cve_publisher_update_approved=true`. This is a different scanner/metric from the Trivy image table.
5. **Separate approval** to deploy one provisioned Grafana JSON file via `grafana-trivy-dashboard-update.yml -e grafana_trivy_dashboard_update_approved=true`. Backups and health checks are already built in. No Grafana or Docker restart; Grafana file provisioner refreshes approximately every 30 seconds.
6. Visually verify the correct dashboard **UID homelab-vulnerability-management** at https://grafana.home.jrwroberts.co.uk/d/homelab-vulnerability-management. Open several CVE links, check all four column headings, no raw labels or obsolete Trivy tables, and compare scanner target_name against Prometheus. Old "Trivy pilot" panels may live in a separately provisioned/dashboard UID: do not delete unrelated dashboards until their live identity is established.

## Existing operational evidence and limits

On 26 Oct at 15:29:14–15:31:51 GMT, the operator ran the existing Greenbone-host Trivy scanner manually after the feed refresh. The service returned success and local node-exporter textfile recorded RUNNING_IMAGES=16, VALID_IMAGES=16, SCAN_COMPLETE=1. This fixes prior Greenbone 9/16 image-ID drift **locally**; post-run central Prometheus confirmation and all-severity publisher rollout are still outstanding. The Greenbone Trivy scan schedule was separately moved to 19:00 UTC plus up to 30 minutes, with operator-verified timer-only backup and no scan started during timer change. The separate host-vulnerability exporter and new Grafana JSON deployment have not been confirmed.

## Rollback

Scoped Ansible playbooks use backup=true; retain actual publisher and dashboard backup paths in operator output. Restore via approved Ansible-only IaC after isolating failures. Do not weaken checks, manufacture clean findings, or delete panels in live Grafana manually.
