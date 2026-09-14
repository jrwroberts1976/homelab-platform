# Homelab Monitoring Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** operational metrics, alerting and logging platform  
**Primary host:** `monitor-01.jameshouse`  
**IPv4:** `192.168.2.52`  
**Placement:** VM 200 on `Proxmox-2` / `192.168.2.71`  
**Last current-state review:** 14 September 2026

## Purpose

`monitor-01` is the central monitoring and logging platform for the homelab.

Current core services:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter
- Loki
- Alloy
- rsyslog receiver for ASUS router logs

The earlier 12 September statement that Loki and Alloy were not deployed is superseded.

## VM state

Current VM:

```text
monitor-01.jameshouse
192.168.2.52
VM ID 200
Proxmox-2
Debian 13
```

The VM is intended to be reproducible through Git/IaC. Persistent monitoring data is useful, but configuration/dashboard authority should remain in Git wherever practical.

## Application versions

Direct validation on 14 September 2026 found:

| Service | Image/version |
|---|---|
| Grafana | `grafana/grafana:13.2.1` |
| Prometheus | `prom/prometheus:v3.14.0` |
| Alertmanager | `prom/alertmanager:v0.34.0` |
| Blackbox Exporter | `prom/blackbox-exporter:v0.28.0` |
| Loki | `grafana/loki:3.7.7` |
| Alloy | `1.19.2` native package/service |

Compose path:

```text
/opt/monitoring/docker-compose.yml
```

## Current health

Direct 14 September validation showed all five containers running:

```text
monitoring-loki-1
monitoring-grafana-1
monitoring-prometheus-1
monitoring-alertmanager-1
monitoring-blackbox-1
```

Listeners were present on:

```text
TCP/3000   Grafana
TCP/3100   Loki
TCP/9090   Prometheus
TCP/9093   Alertmanager
TCP/9115   Blackbox Exporter
TCP/12345  Alloy local UI/API on loopback
```

Local health checks returned HTTP 200 for:

```text
http://127.0.0.1:9090/-/healthy
http://127.0.0.1:3000/api/health
http://127.0.0.1:9093/-/healthy
http://127.0.0.1:3100/ready
```

The compact audit also reported zero failed systemd units on `monitor-01`.

## Metrics coverage

Prometheus remains the authority for host/service metrics and Blackbox probes.

Validated target families include:

- DNS TCP probes;
- ICMP probes;
- Proxmox HTTPS probes;
- Node Exporter across the managed estate;
- service-specific metrics where deliberately added.

The exact target count is operational data and may change as the estate evolves. Do not preserve an old target count in documentation as if it were a design constraint.

## Logging architecture

Loki is now part of the monitoring Compose stack and Alloy provides the host/log forwarding layer.

Current high-level path:

```text
managed hosts / service logs
        |
        v
Alloy
        |
        v
Loki on monitor-01
        |
        v
Grafana
```

Alloy 1.19.2 is deployed across the current managed baseline, including both Proxmox nodes, DNS resolvers, cloud, mail relay, media, BirdNET, edge and administration hosts.

`admin-01` was reconciled during the 14 September audit after being identified as the one baseline host without Alloy.

## Router syslog relationship

`monitor-01` receives ASUS router remote syslog on UDP/5514 through rsyslog and stores the dedicated local file at:

```text
/var/log/homelab/router/rt-ac86u.log
```

Alloy now ships that file to the local Loki service at:

```text
http://127.0.0.1:3100/loki/api/v1/push
```

Local file retention/rotation remains useful resilience and is not replaced by Loki.

See `ROUTER-SYSLOG-SERVICE.md` for the receiver and log-path details.

## Failure-domain placement

Monitoring runs on `Proxmox-2` so loss of the primary `PROXMOX` node does not also remove central visibility.

`Proxmox-2` remains a standalone Proxmox node by design.

## IaC ownership

Current ownership model:

- Terraform/OpenTofu: monitoring VM definition;
- Ansible: Debian baseline, Docker/Compose, Alloy, service files, persistent directories and health checks;
- Compose: Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki;
- Prometheus configuration: Git-managed scrape/probe targets;
- Grafana provisioning: Git-managed datasource/dashboards where practical;
- Loki configuration: Git-managed;
- Alloy configuration: Git-managed through the relevant host/service roles;
- Alertmanager configuration: Git-managed routing with protected secrets outside Git.

Primary paths include:

```text
IaC/terraform/proxmox/monitor-01/
IaC/ansible/playbooks/monitoring.yml
IaC/ansible/playbooks/monitor-router-alloy.yml
IaC/ansible/roles/monitoring_stack/
IaC/ansible/roles/monitor_router_alloy/
IaC/scripts/deploy-monitoring-platform.sh
```

Manual GUI edits are not authoritative unless reconciled back into Git.

## Controller

Normal deployment/reconciliation is launched from:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired `TestServer` identity at `.220` must not be used as the controller. `.220` is `docker-01`.

## Alerting policy

Alerting should remain actionable rather than comprehensive for its own sake.

New rules should be introduced only when:

- the underlying metric/log signal is stable;
- the alert has a clear operator action;
- planned maintenance/outages are considered;
- noisy duplicates are avoided.

Log ingestion does not imply that every log message should generate an alert.

## Current follow-up work

Useful next work includes:

- continue enriched Network Hosts dashboards and device-detail views;
- build the planned Web Platform / Analytics dashboard combining Cloudflare, Umami and origin health;
- add service-specific metrics/log views only where operationally useful;
- continue backup/recovery work for persistent monitoring state where justified;
- periodically validate Loki ingestion and label cardinality.

## Definition of current operational state

The monitoring platform is operational because:

- `monitor-01` exists at the intended address/placement;
- Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki are running;
- Prometheus, Grafana, Alertmanager and Loki health endpoints returned HTTP 200 during the 14 September validation;
- Alloy is active on `monitor-01` and across the managed baseline;
- router syslog has a local rsyslog path and an active Alloy/Loki ingestion path;
- zero failed systemd units were observed on `monitor-01` during the compact audit.
