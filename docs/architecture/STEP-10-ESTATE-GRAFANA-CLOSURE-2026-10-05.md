# Step 10 — Estate-wide Grafana overview closure

**Closed:** 2026-10-05  
**Scope:** Delivery plan Step 10 — estate-wide Grafana overview

## Outcome

Step 10 is complete and live on `monitor-01`.

The Grafana estate overview is Git/IaC managed and provides:

- production Home/operations overview;
- single-host `Homelab — Hosts` dashboard;
- `Homelab — Node Detail` dashboard;
- estate-wide `Homelab — Patch & Reboot Status` dashboard;
- network-host overview and generated per-device dashboards;
- 30-second Grafana refresh on the Step 10 dashboards;
- navigation between Home, Hosts, Node Detail and Patching views;
- current patch telemetry based on the `homelab_patch_*` exporter metrics rather than retired metric names.

## Patch dashboard evidence

PR #179 added the production `homelab-patching` dashboard and updated the Home dashboard to current patch telemetry.

Live Prometheus validation after the controlled estate patch cycle returned:

```text
count(homelab_patch_status_timestamp_seconds)             15
sum(homelab_patch_pending_updates)                         0
sum(homelab_patch_security_updates_pending)                0
sum(homelab_patch_reboot_required)                         0
count(homelab_patch_unattended_upgrades_installed == 1)   15
sum(homelab_patch_automatic_reboot)                        0
```

This confirms all 15 managed Linux hosts were reporting current patch state, with zero pending packages, zero pending security updates, zero reboot requirements, unattended-upgrades installed on all 15 hosts and automatic reboot disabled estate-wide.

The final pending package found during validation was `wf-panel-pi` on `admin-01`; after upgrade, the local exporter reported zero pending updates and Prometheus converged to the estate-wide zero state above.

## Legacy metric cleanup

PR #180 replaced remaining retired patch metric references in:

- `IaC/ansible/roles/monitoring_stack/files/grafana/dashboards/production/homelab-linux-estate.json`
- `IaC/ansible/roles/monitoring_stack/files/grafana/dashboards/homelab-node-detail.json`

The cleanup migrated panels to:

- `homelab_patch_pending_updates`
- `homelab_patch_security_updates_pending`
- `homelab_patch_reboot_required`
- `homelab_patch_status_timestamp_seconds`
- `homelab_patch_unattended_upgrades_installed`
- `homelab_patch_automatic_reboot`

Repository validation found no remaining retired patch metric names in the Grafana dashboard tree.

## Deployment and idempotence

The post-merge production deployment to `monitor-01` completed successfully:

```text
monitor-01 : ok=85 changed=3 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0
```

The three changes were expected from dashboard provisioning updates and Grafana restart.

The immediate repeat deployment was fully idempotent:

```text
monitor-01 : ok=84 changed=0 unreachable=0 failed=0 skipped=2 rescued=0 ignored=0
```

This is the final Step 10 acceptance gate.

## Closure decision

Step 10 is **COMPLETE**.

No further infrastructure change is required to close this step. Broader Project #3 work — richer AI host intelligence, automatic relevance filtering and longer-term host-description/version-history features — remains separate planned work and should not be conflated with this completed estate-overview foundation.
