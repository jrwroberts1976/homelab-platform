# Homelab Monitoring Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** operational core metrics platform; Loki/Alloy not deployed on `monitor-01`  
**Primary host:** `monitor-01.jameshouse`  
**IPv4:** `192.168.2.52`  
**Placement:** VM 200 on `Proxmox-2` / `192.168.2.71`  
**Last current-state review:** 12 September 2026

## Purpose

`monitor-01` is the central metrics/probe/alerting platform for the homelab.

Current core services:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter

Loki and Alloy are **not deployed on `monitor-01`**. Router syslog is collected locally by rsyslog as a separate current service and can be integrated into Loki later if the central logging design is approved.

## VM state

Current VM:

```text
monitor-01.jameshouse
192.168.2.52
VM ID 200
Proxmox-2
4 vCPU
6144 MiB RAM
80 GiB disk
Debian 13
```

The VM is intended to be reproducible through Git/IaC. Persistent Prometheus/Grafana data is useful but configuration/dashboard authority should remain in Git wherever practical.

## Application versions

Validated current Compose images:

| Service | Version |
|---|---|
| Grafana | 13.2.1 |
| Prometheus | 3.14.0 |
| Alertmanager | 0.34.0 |
| Blackbox Exporter | 0.28.0 |

Compose path:

```text
/opt/monitoring/docker-compose.yml
```

## Current health

The 12 September 2026 direct audit found:

```text
Prometheus:       healthy
Grafana:          healthy
Alertmanager:     healthy
Blackbox Exporter healthy
active targets:   23
healthy targets:  23
active alerts:    0
failed systemd:   0
```

Grafana's database/health endpoint was healthy during the audit.

## Current target coverage

Observed target coverage includes:

### DNS

- DNS TCP probe: `192.168.2.50:53`
- DNS TCP probe: `192.168.2.51:53`
- Node Exporter on both resolvers

### ICMP

Observed ICMP probe targets include:

- ASUS router `.1`
- `dns-02 .50`
- `dns-01 .51`
- `monitor-01 .52`
- `sensor-01 .55`
- `PROXMOX .70`
- `Proxmox-2 .71`
- `media-01 .195`
- `docker-01 .220`

### Proxmox HTTPS

- `https://192.168.2.70:8006`
- `https://192.168.2.71:8006`

### Node Exporter

Current validated Node Exporter targets include:

```text
dns-01       192.168.2.51:9100
dns-02       192.168.2.50:9100
monitor-01   192.168.2.52:9100
sensor-01    192.168.2.55:9100
PROXMOX      192.168.2.70:9100
Proxmox-2    192.168.2.71:9100
media-01     192.168.2.195:9100
docker-01    192.168.2.220:9100
```

`mail-relay-01` does not currently run Node Exporter and is not a Prometheus target.

## Failure-domain placement

Monitoring runs on `Proxmox-2` so loss of the primary `PROXMOX` host does not also remove monitoring.

This gives useful visibility into workloads on the other host including:

- `dns-02`
- `mail-relay-01`
- `cloud-01`
- `sensor-01`
- the `PROXMOX` node itself.

The two hypervisors remain standalone by design.

## IaC ownership

- Terraform/OpenTofu: monitoring VM definition
- Ansible: Debian baseline, Docker/Compose, service files, persistent directories and health checks
- Compose: Prometheus, Grafana, Alertmanager and Blackbox Exporter
- Prometheus configuration: Git-managed scrape/probe targets
- Grafana provisioning: Git-managed datasource/dashboards where practical
- Alertmanager configuration: Git-managed routing with protected secrets outside Git
- managed DNS: `monitor-01.jameshouse -> 192.168.2.52`

Manual GUI edits are not authoritative unless reconciled back into Git.

Primary paths:

```text
IaC/terraform/proxmox/monitor-01/
IaC/ansible/playbooks/monitoring.yml
IaC/ansible/roles/monitoring_stack/
IaC/scripts/deploy-monitoring-platform.sh
IaC/scripts/preflight-monitoring.sh
```

## Controller

Normal deployment/reconciliation is launched from:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired `TestServer` identity at `.220` must not be used as the normal monitoring controller. `.220` is now `docker-01`.

## Ports

LAN management/application ports:

- Grafana: TCP/3000
- Prometheus: TCP/9090
- Alertmanager: TCP/9093
- Blackbox Exporter: TCP/9115

The 12 September audit found no Loki TCP/3100 listener and no Alloy TCP/12345 listener on `monitor-01`.

## Router syslog relationship

`monitor-01` also receives the ASUS router's remote syslog through rsyslog on UDP/5514 and stores it locally at:

```text
/var/log/homelab/router/rt-ac86u.log
```

That local receiver is operational and documented separately in `ROUTER-SYSLOG-SERVICE.md`.

This is **not** evidence that Loki/Alloy central logging exists.

## Alerting policy

Alerting should remain actionable rather than comprehensive for its own sake.

Current audit state:

```text
active Prometheus alerts: 0
```

New rules should be introduced only when:

- the underlying metric/probe is stable;
- the alert has a clear operator action;
- planned maintenance/outages are considered;
- noisy duplicates are avoided.

## Planned observability work

Future work includes:

- central Loki/Alloy design if still required;
- router syslog ingestion into that pipeline;
- service-specific metrics where useful;
- enriched Network Hosts data gatherer/dashboard;
- Web Platform / Analytics dashboard combining Cloudflare edge/security data, Umami analytics and origin/application health;
- additional service monitoring where it provides actionable value.

Do not treat planned dashboards/logging as already deployed.

## Validation

Useful current checks from `admin-01` include controller-side HTTP/API checks against the four services and inspection of Prometheus targets/alerts.

A healthy monitoring service should show:

- Prometheus API responsive;
- Grafana health responsive;
- Alertmanager responsive;
- Blackbox Exporter responsive;
- configured targets healthy or with understood failures;
- no unexplained active alerts;
- zero unexpected failed units on `monitor-01`.

## Definition of current operational state

The core monitoring platform is operational because:

- `monitor-01` exists at the intended address/placement;
- all four core services are healthy;
- current target discovery works;
- 23/23 active targets were healthy during the latest audit;
- Node Exporter covers the current core host set;
- DNS/ICMP/Proxmox HTTPS probes are live;
- Grafana is connected to Prometheus;
- no active Prometheus alerts were present during the audit.

Loki/Alloy deployment remains a future workstream, not a condition for calling the current metrics platform operational.
