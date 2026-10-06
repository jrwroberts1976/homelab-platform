<!-- estate-authority: IaC/inventory/estate.json -->
# Grafana Production Dashboards

**Status:** OPERATIONAL / GIT-PROVISIONED  
**Grafana:** 13.2.1  
**Host:** `monitor-01` (`192.168.2.52`)  
**Current-state review:** 6 October 2026

## Production folder

Production dashboards are provisioned under:

```text
Homelab / Production Dashboards
folder UID: homelab-production
```

The parent Homelab folder remains available for non-production/unreviewed dashboards.

## Current production dashboard set

Core reviewed navigation includes:

| Dashboard | UID | Purpose |
|---|---|---|
| Homelab — Home / Operations | `homelab-operations` | estate operational landing page |
| Homelab — Hosts | `homelab-linux-estate` | dynamic managed-Linux host overview |
| Homelab — Patch & Reboot Status | `homelab-patching` | patch/reboot/policy coverage across 15 Linux hosts |
| Homelab — Node Detail | `homelab-node-detail` | selected-host operational detail |
| Homelab — Network Hosts | existing network-host UID | discovered-device inventory and evidence views |

Generated MAC/device dashboards are managed separately by the network-host generation workflow and are not manually promoted one by one through this folder procedure.

## Step 10 acceptance

The estate-wide dashboard work is complete.

Final deployment evidence:

```text
first production deployment:
  monitor-01 ok=85 changed=3 unreachable=0 failed=0

repeat idempotence run:
  monitor-01 ok=84 changed=0 unreachable=0 failed=0
```

Final patch telemetry at acceptance:

```text
reporting hosts:             15
pending updates:             0
security updates pending:    0
reboots required:            0
unattended-upgrades present: 15
automatic reboots enabled:   0
```

Visual acceptance of `Homelab — Hosts` was completed using a relative `now-24h -> now` time range. Absolute future-ended time ranges can legitimately produce `No data` and should not be mistaken for exporter failure.

## Provisioning ownership

The dashboard provider is Git/Ansible managed. Production JSON files live under the monitoring role's production dashboard directory and are copied into Grafana provisioning on `monitor-01`.

Current provider behaviour includes:

- stable UIDs;
- provisioned production folder;
- periodic provider refresh;
- UI edits not treated as authoritative.

Do not keep duplicate copies of the same UID under multiple providers.

## Deployment workflow

Normal reconciliation:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook \
  -i inventory/hosts.yml \
  playbooks/monitoring.yml \
  --limit monitor-01
```

After an intentional dashboard/provisioning change, run the playbook again and expect stable state to converge to `changed=0` unless a clearly understood dynamic task requires otherwise.

## Validation

Validate:

1. Grafana health;
2. provisioned dashboard existence by UID;
3. correct production folder assignment;
4. Prometheus datasource health;
5. representative host/dashboard data at `now-24h -> now`;
6. patch dashboard values and missing-data semantics;
7. dashboard links between Home, Hosts, Node Detail and Patching;
8. repeat Ansible idempotence.

Missing telemetry must not silently render as healthy zero unless the query semantics explicitly prove that zero.

## Safety / rollback

- never use `docker compose down -v` as a dashboard deployment step;
- back up provisioning/database state before risky Grafana structural changes;
- preserve stable dashboard UIDs;
- if provisioning fails, restore the last known-good provider/JSON set and restart/revalidate Grafana;
- do not solve provisioning drift with unreconciled GUI-only edits.

## Future dashboard reviews

New dashboards should enter the production provider only after they have a clear operator purpose, stable datasource/query semantics, useful no-data behaviour and a validated Git-managed deployment path.
