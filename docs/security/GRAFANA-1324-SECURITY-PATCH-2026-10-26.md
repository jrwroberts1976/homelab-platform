# Grafana 13.2.4 — supported same-minor security update

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** Reviewed Git-only remediation change, not yet deployed to monitor-01. Requires an independently approved service interruption and Ansible execution from admin-01. Do not silently upgrade every monitoring container.

## Verified source and target

- The canonical Ansible monitoring defaults currently pin `grafana/grafana:13.2.1` and the additional Git-managed Komodo monitoring Compose file has the same pin. The active monitor-01 stack uses `/opt/monitoring/docker-compose.yml` with a loopback-only Grafana backend `127.0.0.1:3000` and trusted HTTPS reverse proxy. The alternatives are kept version-aligned; the auxiliary Komodo Compose file is **not** deployed by this patch.
- The upstream **Grafana v13.2.4** release published 13 October 2026 is a supported security patch on the same `13.2` minor branch. Its release notes state fixes for **CVE-2026-15577, CVE-2026-33374, CVE-2026-93294, CVE-2026-95502** in addition to security fixes made in 13.2.2 and 13.2.3. Source: https://github.com/grafana/grafana/releases/tag/v13.2.4 . Security advisories are version-level vendor evidence, **not proof that each CVE was present in the current container**.
- Grafana 13.2.1 was specifically within the range named in the September 2026 government vulnerability alert: https://www.cyber.gc.ca/en/alerts-advisories/grafana-security-advisory-av26-936 . This is a solid priority despite there being other high-count containers.
- This update will NOT clear Nextcloud, Komodo, Greenbone, Redis or PostgreSQL CVEs. Existing Grafana plugin state and provisioned dashboard data are not modified by source changes alone.

## Targeted one-time cutover

Playbook: `IaC/ansible/playbooks/grafana-security-patch-1324.yml`. Expected host only: `monitor-01` / `192.168.2.52` / Debian 13. Approval variable: `grafana_security_patch_approved=true`. Intentionally fails closed if the live Grafana image is no longer exactly `grafana/grafana:13.2.1` or the live Compose line differs; do not loosen the safeguards simply to make a rerun succeed. Record a new change/verification if the image is already upgraded.

**Before running**, confirm operator access to `admin-01`, a maintenance opportunity for several minutes of Grafana downtime, the Proxmox VM's recoverability, healthy Prometheus/Loki/Alertmanager/Blackbox and free backup storage. This is a Grafana-container restart/recreate, unlike the earlier JSON-only dashboard deployments. A Grafana SQLite data backup is an additional safety guard, but does not replace a tested VM/workload recovery plan where needed.

The playbook:
1. Checks exact host, OS, repo pin, old running image, existing Compose/environment/provisioning files, and a persistent Grafana SQLite DB. Requires Grafana `/api/health` to say 13.2.1 and four other monitoring services to be present.
2. Creates a protected root-only directory `/var/backups/homelab-security/grafana/` and a consistent online SQLite `backup()` verified with `PRAGMA quick_check`. No DB or secret contents are printed.
3. Pulls **only** `grafana/grafana:13.2.4`, replaces exactly its image reference in the existing Compose file using Ansible's timestamped backup; validates Compose without logging expanded environment secrets.
4. Executes `docker compose --project-directory /opt/monitoring up -d --no-deps --no-build --force-recreate grafana` (single service). It will temporarily interrupt Grafana UI and may trigger internal DB migrations; no other monitoring service should be recreated.
5. Verifies the local Grafana health API identifies 13.2.4, and verifies Prometheus, Loki, Alertmanager and Blackbox container IDs did not change. Reports the Compose rollback backup and the SQLite backup path.

## Offline validation and operator-run live command

```bash
cd ~/projects/homelab-platform
git switch main
git pull --ff-only origin main
python3 scripts/validate-grafana-security-patch-1324.py
python3 scripts/validate-estate.py
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/grafana-security-patch-1324.yml --syntax-check
```

If the reviewed PR is merged and the operator explicitly approves the Grafana-only maintenance:

```bash
ansible-playbook -i inventory/hosts.yml -b --ask-become-pass \
  playbooks/grafana-security-patch-1324.yml \
  -e grafana_security_patch_approved=true
```

**Do not run full** `playbooks/monitoring.yml` as a shortcut: that playbook applies the entire monitoring role and reconciles every monitoring container.

## Verification and rollback boundary

Post-change independently verify:

- `https://grafana.home.jrwroberts.co.uk/` login and the existing `homelab-vulnerability-management` dashboard are reachable; dashboards/datasources and alerting still function.
- Current Grafana container is `grafana/grafana:13.2.4`; the original immutable image ID and backup Compose path remain recoverable.
- Original Prometheus, Loki, Blackbox and Alertmanager containers, metrics, logs, alert evaluations and known credentials still work.
- **Fresh Trivy evidence is essential**: changing the Grafana container image makes that image's previous scan invalid by design. Only after validating service health, separately approve/perform the existing monitor-01 scanner service (verify its actual name with read-only Ansible first), and query central `running_images`, `valid_images`, `scan_complete` and actual CVE list. Never claim four vendor fixes removed every vulnerability in the image.

**Rollback:** Stop and investigate if the Graphana API/metrics or dashboard fails, record current status and the backup paths. Restore the previous Compose image line using a *separately approved and reviewed* IaC change and recreate only Grafana. Restore the protected pre-upgrade SQLite database **only if required and verified safe**, using an offline/quiesced DB restore and avoiding downgrading an already-migrated DB in place. Do not invent a rollback command or assume a database schema downgrade is safe. A protected VM-level snapshot/backup is recommended as an additional recovery option. Preserve logs, secrets and backups; do not publish raw Grafana SQLite.

## Other services

Komodo 2.3.4 and other image/OS patches require their **own** change plans and canary checks. The latest published Komodo release updates a trust-root package; it is not evidence that the large Perl/OpenSSH CVE counts are resolved. Greenbone feed/data container image changes require scan scheduling and feed import safety, and cannot be indiscriminately replaced along with monitoring.
