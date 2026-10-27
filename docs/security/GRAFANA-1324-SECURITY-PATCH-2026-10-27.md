# Grafana 13.2.1 → 13.2.4: security patch plan

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** Git-only targeted playbook and pinned image update; **not deployed to monitor-01**. One-service image recreation causes a brief **Grafana UI interruption** but must preserve Prometheus, Loki, Alertmanager, Blackbox and the existing SQLite data.

## Evidence and source validation

The Git-managed monitoring role and separate Komodo reference Compose both pin `grafana/grafana:13.2.1`. Grafana's official v13.2.4 release (published 13 October 2026) includes security fixes for `CVE-2026-15577`, `CVE-2026-33374`, `CVE-2026-93294` and `CVE-2026-95502`; the intervening 13.2.2/13.2.3 releases also included fixes. Reference: https://github.com/grafana/grafana/releases/tag/v13.2.4. This makes a **supported, patch-level upstream upgrade candidate**, not a claim that every Trivy image finding will disappear or any exact CVE is currently exploitable.

The canonical source `IaC/ansible/roles/monitoring_stack/defaults/main.yml` now pins `grafana/grafana:13.2.4` and the secondary `IaC/komodo/stacks/monitoring/compose.yml` reference matches. **Do not use the full monitoring role or reconcile the secondary Compose** to apply this targeted change: doing so could unnecessarily touch other running workloads or diverge from the established HTTPS runtime.

## Preflight, guarded deployment and verification

One new playbook: `IaC/ansible/playbooks/grafana-security-patch-1324.yml`, must be executed only after separate explicit approval to briefly restart **Grafana only**. It guards:

- Exact Debian 13 `monitor-01` IP/identity, explicit `grafana_security_patch_approved=true`, and source target pin; existing currently running Grafana **13.2.1**, live API `/api/health` reporting that version, existing approved Compose line and persistent `/var/lib/grafana` volume.
- Existing protected `/opt/monitoring/.env` and dashboard provisioning; prior Compose validation and nonempty SQLite database.
- Protected, consistent SQLite online backup to `/var/backups/homelab-security/grafana/` using Python `sqlite3.Connection.backup` and `PRAGMA quick_check`; root-only file mode 0600 and separate timestamped Compose rollback backup.
- Pull **only** `grafana/grafana:13.2.4`, change exactly one existing line in the existing Compose, validate it, recreate **only** the Grafana service with `up -d --no-deps --no-build --force-recreate grafana`. No unrelated container updates, system packages or scanner runs.
- Require upgraded local API to report 13.2.4 and check unrelated monitoring container IDs unchanged. Version or service-health failure stops automatic progress; **no automatic SQLite downgrade/restore** because an upgrade may have applied migrations.

**Offline validation after merge:**

```sh
cd ~/projects/homelab-platform
git switch main
git pull --ff-only origin main
python3 scripts/validate-grafana-security-patch-1324.py
python3 scripts/validate-estate.py
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/grafana-security-patch-1324.yml --syntax-check
```

**Separate operator-approved deployment, not yet run:**

```sh
ansible-playbook -i inventory/hosts.yml -b --ask-become-pass \
  playbooks/grafana-security-patch-1324.yml \
  -e grafana_security_patch_approved=true
```

**After live application:** verify trusted Grafana HTTPS, login, Prometheus panels, four-column CVE table, alerting, and Loki ingestion. Then separately authorize a fresh Trivy scan for `monitor-01` to compare specific `grafana/grafana` CVE findings against a new validated immutable image ID. Aggregate CVE count reductions alone are insufficient.

**Rollback:** Record actual original image digest and Compose backup before change. A 13.2.4 → 13.2.1 downgrade may be unsafe due to database migration; do **not** automatically restore old SQLite data into a running container. Use the protected pre-upgrade SQLite backup **only** as part of a separately approved recovery procedure after evaluating persistence/migrations and pausing Grafana. This work does not modify either Prometheus or Grafana alert rules.

## Remaining security scope

Do not treat this patch as closing issue #187. `Komodo Core/Periphery 2.3.3` has a distinct upstream 2.3.4 update (22 October 2026) with root-store changes. Nextcloud 35.0.2 still has documented residual critical CVEs, two with EXR path mitigation only, not patched library versions; see `docs/security/NEXTCLOUD-REMAINING-CRITICAL-CVES-2026-10-26.md`. Greenbone scanner appliance/feed stacks and low-severity host findings need separate compatibility and root-cause reviews. **Never replace all 30 running images with latest versions in one operation.**
