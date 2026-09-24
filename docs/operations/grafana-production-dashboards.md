# Grafana Production Dashboards migration

Grafana 13.2.1: move reviewed **Home** (`homelab-operations`) and **Hosts** (`homelab-linux-estate`) into **Homelab / Production Dashboards**. Keep the eight unreviewed dashboards in Homelab. Dashboard UIDs and URLs are unchanged.

Parent folder UID: `dfy4vfvi07rpca`. Stable child UID: `homelab-production`.

## Deployment order

The child folder **must exist before the production file provider starts**. Grafana's file provider can create a root-level folder when the specified UID is missing; do not deploy the provider before creating and verifying the nested folder.

1. Fetch the feature branch on `admin-01` and copy `scripts/grafana/ensure-production-folder.py` to `monitor-01:/tmp/`.
2. On `monitor-01`, back up `/opt/monitoring/grafana/provisioning/dashboards` and the Grafana database before modifying the provider. Do not print `/opt/monitoring/.env`.
3. Run `sudo python3 /tmp/ensure-production-folder.py` on `monitor-01`. This uses the protected local Grafana admin password and the Grafana folder API. It is idempotent and verifies the folder parent.
4. Deploy the updated Ansible role **or** reconcile the equivalent Komodo files. The Ansible role installs the new production provider, copies the two reviewed JSON files to `/opt/monitoring/grafana/provisioning/dashboards/production/`, removes their old copies from `homelab/`, and restarts Grafana when provisioning changes.
5. Verify both dashboard UIDs via `/api/dashboards/uid/<uid>` and confirm `meta.folderUid == "homelab-production"`. Confirm the other eight still have `meta.folderUid == "dfy4vfvi07rpca"`. Check the Home and Hosts browser URLs.
6. Only merge this branch after successful live verification.

## Safety

Do not leave copies of the same UID under both providers. Never use `docker compose down -v`. If folder creation fails, stop before changing providers. If verification fails, restore the dashboard provider and dashboard JSON files from backup and restart Grafana; leave the new folder in place until the restored dashboards are confirmed.

For future dashboard reviews, move each newly approved JSON into the `production/` directory in **both** the Ansible and Komodo trees, and move its filename from `monitoring_grafana_dashboard_files` to `monitoring_grafana_production_dashboard_files` in the Ansible defaults.
