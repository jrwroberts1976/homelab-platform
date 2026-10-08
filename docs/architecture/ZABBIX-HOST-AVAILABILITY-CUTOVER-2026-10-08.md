# Zabbix host availability cutover — 8 October 2026

## Decision

Zabbix Agent 2 active checks are now the authoritative source for managed-host availability in the daily management report.

Prometheus/node-exporter remains in service for engineering telemetry, dashboards and metrics, but is no longer the human-facing source of truth for whether a managed host is reporting.

## Validation evidence

The `Homelab/Linux` Zabbix group contains the 15 managed Linux hosts.

A read-only API validation on 8 October 2026 confirmed all 15 hosts had a current `agent.ping` item with:

- `lastvalue = 1`
- item type `ACTIVE`
- item state `NORMAL`
- latest sample ages between 2 and 57 seconds

Validated hosts:

- PROXMOX
- Proxmox-2
- admin-01
- cloud-01
- dns-01
- dns-02
- docker-01
- edge-01
- greenbone-01
- komodo-01
- mail-relay-01
- media-01
- monitor-01
- sensor-01
- zabbix-01

## Interpretation

These hosts intentionally use active Zabbix Agent 2 checks and therefore do not require passive Agent interfaces in Zabbix. Interface availability is not used for this estate.

A managed host is considered available when its enabled `agent.ping` item is supported, its latest value is `1`, and the latest sample is fresh within the management-report threshold.

## Next steps

1. Update the management report to derive host availability from Zabbix `agent.ping` rather than Prometheus `up{job="node-exporter"}`.
2. Keep Prometheus/node-exporter metrics for dashboards and engineering telemetry.
3. Expand Zabbix use next for Problems and Inventory.
4. Add SNMP monitoring after the Problems/Inventory work is complete.
