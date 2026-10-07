# Management Report Network Inventory v1 Closure — 7 October 2026

**Status:** COMPLETE  
**Implementation commit:** `abb5c90` — `Add factual network inventory to management report`  
**Production owner:** `monitor-01`  
**Scope:** factual network-inventory section in the daily management report

## Outcome

The daily management report now includes a bounded factual network-inventory section sourced from the active network-discovery owner on `monitor-01`.

The v1 section reports only facts directly supported by the existing collector metrics:

- retained network inventory total;
- hosts currently considered online by the network collector;
- hosts first observed in the preceding 24 hours;
- source timestamp / evidence age;
- freshness status.

The implementation deliberately does **not** claim operating-system changes, port changes, device-identity changes or other inferred changes. It has no `enrichment.json` dependency.

## Authoritative source

The management-report collector is explicitly pinned to:

```text
Prometheus target_name="monitor-01"
textfile="/var/lib/prometheus/node-exporter/homelab_network_hosts.prom"
```

This explicit owner binding is required because Prometheus still exposes retained historical textfile metrics from the former discovery source on `Proxmox-2` and an older file on `PROXMOX`.

During implementation an unscoped query demonstrated why this guard is necessary:

```text
max(homelab_network_host_inventory_total) = 51
sum(homelab_network_host_up)             = 82
```

The online total was invalid because it combined current and retained historical publishers. The final queries therefore scope every network-inventory metric to `target_name="monitor-01"`.

## Production queries

The factual v1 uses the equivalent of:

```promql
max(homelab_network_host_inventory_total{target_name="monitor-01"})
```

```promql
sum(homelab_network_host_up{target_name="monitor-01"}) or vector(0)
```

```promql
count(homelab_network_host_first_seen_seconds{target_name="monitor-01"} > time() - 86400) or vector(0)
```

Freshness is derived from the actual textfile modification timestamp rather than from Prometheus scrape time:

```promql
max(node_textfile_mtime_seconds{target_name="monitor-01",file="/var/lib/prometheus/node-exporter/homelab_network_hosts.prom"})
```

## Freshness and evidence safety

The network collector runs every 5 minutes. Management-report network evidence uses a conservative 15-minute freshness threshold.

The renderer presents counts only when evidence status is `ok`.

If required evidence is missing, stale or invalid, the report shows the evidence problem and suppresses the counts rather than presenting them as current facts.

Additional validity guards include:

- source timestamp must be valid and not unexpectedly in the future;
- counts must be non-negative integers;
- `currently_online` cannot exceed `inventory_total`;
- `first_seen_24h` cannot exceed `inventory_total`.

The `currently_online > inventory_total` guard specifically protects against the duplicate-publisher condition discovered during implementation.

## Production validation

A manual production run on `monitor-01` completed successfully with:

```json
{
  "currently_online": 40,
  "first_seen_24h": 0,
  "freshness_threshold_seconds": 900,
  "inventory_total": 51,
  "source": "Prometheus target_name=\"monitor-01\" textfile=\"/var/lib/prometheus/node-exporter/homelab_network_hosts.prom\"",
  "source_age_seconds": 64,
  "status": "ok"
}
```

The corresponding factual report section rendered as:

```text
Network Inventory
-----------------
Status: Evidence current
Last evidence: 2026-10-06T12:52:20+00:00
Inventory devices: 51
Currently online: 40
First observed in last 24h: 0
Evidence age: 64 seconds
```

The changing online count is expected operational behaviour; it is a live presence metric, not a fixed inventory property.

## Provenance validation

The live report records deterministic provenance:

```text
Network inventory status: OK
Network inventory evidence: Prometheus target_name="monitor-01" textfile="/var/lib/prometheus/node-exporter/homelab_network_hosts.prom"
Network inventory timestamp: 2026-10-06T12:52:20+00:00
```

A final forbidden-claim/source check returned no matches for:

```text
Proxmox-2
enrichment.json
OS change
port change
ports changed
operating system changed
```

This confirms the delivered v1 stayed within the agreed factual boundary.

## Regression and deployment validation

The management-report role has dedicated network-inventory regression coverage for:

- authoritative `monitor-01` query scoping;
- fresh evidence rendering verified counts;
- stale evidence suppressing counts;
- impossible online count being rejected;
- missing required metric being reported unavailable.

Final validation:

```text
management-report tests: 9 passed
Ansible syntax check:     passed
initial production deploy: changed=2, failed=0
repeat production deploy: changed=0, failed=0
```

The repeat `changed=0` run proves role idempotence after deployment.

## Files delivered

The implementation is contained in:

```text
IaC/ansible/roles/management_report/defaults/main.yml
IaC/ansible/roles/management_report/templates/management-report-collector.py.j2
IaC/ansible/roles/management_report/templates/management-report-renderer.py.j2
IaC/ansible/roles/management_report/test_network_inventory_report.py
```

## Boundary for future versions

This closure applies only to factual network-inventory v1.

Any future addition of OS change detection, port change detection, identity-change claims or enrichment-derived conclusions requires a separately reviewed evidence model and regression coverage. Those capabilities must not be inferred from this v1 completion.