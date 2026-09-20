# Management Reporting Evidence — 20 September 2026

## Purpose

This record captures the additional live evidence established on 20 September 2026 while building the daily homelab management-reporting pipeline.

The evidence collector runs on `admin-01` and writes:

`/var/lib/homelab-management-report/evidence.json`

The estate boundary used by the collector is the 15-host canonical Linux estate. This matches the Zabbix `Homelab/Linux` group discovered during today's validation.

## Canonical estate coverage

The expected estate is:

- `PROXMOX`
- `Proxmox-2`
- `admin-01`
- `cloud-01`
- `dns-01`
- `dns-02`
- `docker-01`
- `edge-01`
- `greenbone-01`
- `komodo-01`
- `mail-relay-01`
- `media-01`
- `monitor-01`
- `sensor-01`
- `zabbix-01`

The collector now treats this as an explicit identity list rather than only trusting a host count. It records both missing and unexpected host identities.

## Prometheus evidence

Live validation on 20 September produced:

| Check | Result |
|---|---:|
| Expected hosts | 15 |
| Node Exporter reporting | 15 |
| Node Exporter up | 15 |
| Missing identities | 0 |
| Unexpected identities | 0 |
| Patch telemetry reporting | 15 |
| Patch evidence fresh | 15 |
| Patch freshness threshold | 90 minutes |
| Prometheus firing alerts | 0 |

The collector records the patch freshness threshold and current fresh-host count so a host that continues reporting but stops producing fresh patch evidence cannot be mistaken for a healthy patch-management state.

## Loki evidence

Loki was queried over a 24-hour evidence window.

Overall host presence:

- expected: 15
- reporting: 15
- missing: 0
- unexpected: 0

Current job/source distribution observed during validation:

| Loki job | Hosts |
|---|---|
| `systemd-journal` | `PROXMOX`, `Proxmox-2`, `admin-01`, `cloud-01`, `dns-01`, `dns-02`, `docker-01`, `edge-01`, `greenbone-01`, `komodo-01`, `mail-relay-01`, `media-01`, `monitor-01`, `zabbix-01` |
| `docker` | `greenbone-01`, `komodo-01` |
| `network-security` | `sensor-01` |
| `network-infrastructure` | `monitor-01` |

The absence of `sensor-01` from `systemd-journal` is not treated as a missing estate host because it is present through the dedicated `network-security` stream.

The collector therefore distinguishes overall Loki estate presence from individual job coverage.

## Alertmanager evidence

Alertmanager at `monitor-01`:

`http://192.168.2.52:9093`

returned HTTP 200 from `/api/v2/status`.

The active-alert endpoint returned an empty set:

- active alerts: 0

The collector now records both the active-alert count and the full Alertmanager alert objects when alerts exist.

Prometheus independently returned:

`ALERTS{alertstate="firing"} = []`

This gives the report two separate alert-state observations rather than relying on either source alone.

## Zabbix evidence established

Zabbix API:

`http://192.168.2.59:8080/api_jsonrpc.php`

reported:

`7.0.30`

The Zabbix database confirmed:

- host group `Homelab/Linux` has ID 22;
- that group contains exactly the same 15 canonical hosts;
- the only existing Zabbix users are `Admin` (Super admin role) and `guest` (Guest role);
- the existing roles are the four built-in User, Admin, Super admin and Guest roles;
- no dedicated management-report user/group currently exists;
- the Zabbix 7 token table is present.

Current unresolved Zabbix problems observed through the database were:

| Host | Severity | Problem |
|---|---|---|
| `zabbix-01` | Warning | Linux: Number of installed packages has been changed |
| `komodo-01` | Warning | Linux: Number of installed packages has been changed |
| `Zabbix server` | Warning | Linux: Number of installed packages has been changed |

The built-in `Zabbix server` object is separate from the 15-host `Homelab/Linux` estate and must not be counted as an additional canonical host.

### Zabbix reporting integration status

The Zabbix API endpoint and estate scope have been validated, but the dedicated read-only reporting identity has **not** yet been created.

The intended next step is a dedicated read-only reporting user/token restricted to the `Homelab/Linux` estate. Credentials must remain outside Git.

## Management-report collector implementation status

The collector on `admin-01` now provides deterministic evidence from:

1. Prometheus
2. Loki
3. Alertmanager

It records:

- canonical host identity;
- missing/unexpected host identities;
- Node Exporter reporting and up state;
- patch telemetry coverage;
- patch evidence freshness;
- Prometheus firing alerts;
- Loki overall host presence;
- Loki job/source coverage;
- Alertmanager active alerts.

The Ansible `management_report` role passed live deployment and subsequent check-mode idempotency with:

`changed=0`, `failed=0`

The collector completed successfully after deployment and produced the expected evidence JSON.

## Remaining work

The management-reporting programme is not yet complete.

Next evidence sources/work items are:

- provision and validate the dedicated read-only Zabbix API identity;
- add Zabbix evidence to the collector;
- add Greenbone/vulnerability evidence;
- complete network/security evidence correlation;
- build the report-generation/analysis layer;
- produce the management and engineering report outputs;
- wire scheduled delivery through the existing mail relay;
- perform an end-to-end scheduled-run test;
- document and validate failure/assurance-gap handling.

This record deliberately does not claim those remaining stages are complete.
