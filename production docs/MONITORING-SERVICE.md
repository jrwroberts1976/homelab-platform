<!-- estate-authority: IaC/inventory/estate.json -->
# Homelab Monitoring Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** OPERATIONAL  
**Primary host:** `monitor-01.jameshouse`  
**IPv4:** `192.168.2.52`  
**Placement:** VM202 on `Proxmox-2` (`192.168.2.71`)  
**Last current-state review:** 6 October 2026

## Purpose

`monitor-01` is the central monitoring, logging, management-report and active network-discovery platform.

Current core services:

- Prometheus;
- Grafana;
- Alertmanager;
- Blackbox Exporter;
- Loki;
- native Grafana Alloy;
- rsyslog receiver for ASUS router logs;
- Network Hosts discovery/enrichment/OS-evidence/guest-refresh workflows;
- management-report evidence collection/rendering/AI-assisted summary/mail workflow.

## VM state

```text
monitor-01.jameshouse
192.168.2.52
VM ID 202
host: Proxmox-2
OS: Debian 13
```

VM200 references are obsolete; VM200 is `cloud-01` on `PROXMOX`.

## Core application versions

Current production monitoring stack versions documented during Step 10 validation:

| Service | Version |
|---|---|
| Grafana | 13.2.1 |
| Prometheus | 3.14.0 |
| Alertmanager | 0.34.0 |
| Blackbox Exporter | 0.28.0 |
| Loki | 3.7.7 |

Alloy was updated to 1.20.1 on `monitor-01` during the 5 October maintenance cycle. Version observations are dated operational evidence, not permanent policy pins unless the associated IaC explicitly pins them.

Compose path:

```text
/opt/monitoring/docker-compose.yml
```

## Current health

The production monitoring stack is live and was revalidated during the Step 10 deployment/acceptance work.

Expected listeners include:

```text
TCP/3000   Grafana
TCP/3100   Loki
TCP/9090   Prometheus
TCP/9093   Alertmanager
TCP/9115   Blackbox Exporter
TCP/12345  Alloy local UI/API
UDP/5514   ASUS router syslog receiver
```

Health/readiness checks are included in the Ansible monitoring role. The final Step 10 deployment completed with zero failures, and the repeat deployment was idempotent:

```text
changed=0
unreachable=0
failed=0
```

## Monitoring coverage

The normal managed Linux baseline contains 15 reporting systems.

Prometheus/Blackbox coverage includes host metrics and approved service/network probes. Zabbix Agent 2 provides the second host/service monitoring plane across the same 15 managed Linux systems.

Missing telemetry must not be interpreted as healthy state. Dashboards and reports should distinguish `no data` from a verified zero/healthy value.

## Grafana production dashboards

Step 10 estate-wide Grafana work is complete. Current navigation includes:

- Homelab Home / operations overview;
- Homelab Hosts;
- Homelab Patch & Reboot Status;
- Node Detail;
- Network Hosts and generated per-device dashboards.

Grafana production dashboards are provisioned from Git and are not intended to be authoritative through ad-hoc UI edits.

## Patch telemetry

Final validated estate state after the 5 October controlled maintenance cycle:

```text
reporting hosts:             15
pending updates:             0
security updates pending:    0
reboots required:            0
unattended-upgrades present: 15
automatic reboots enabled:   0
```

The current exporter/dashboard metric namespace is `homelab_patch_*`.

## Logging architecture

High-level path:

```text
managed hosts / service logs
        |
        v
Grafana Alloy
        |
        v
Loki on monitor-01
        |
        v
Grafana / management evidence
```

Alloy is deployed across the managed estate according to inventory scope. Dedicated pipelines include router syslog, network-security evidence/logs and privacy-filtered Pi-hole event logging where configured.

## Router syslog

ASUS router remote syslog is received on UDP/5514 and retained locally at:

```text
/var/log/homelab/router/rt-ac86u.log
```

Alloy forwards the approved stream to Loki. Local retention remains useful as a first-receipt/recovery layer.

## Network discovery ownership

Since the 27 September 2026 cutover, `monitor-01` is the **sole production owner** of active network discovery/identification.

Current responsibilities include:

- collector;
- selective enricher;
- OS-evidence publisher;
- trusted Proxmox guest refresh;
- targeted deep profiling;
- first-seen notifier;
- dashboard/host-page publication;
- bounded DNS evidence correlation.

`Proxmox-2` retains source rollback/history evidence with its discovery timers disabled/inactive.

## Failure-domain placement

`monitor-01` runs on `Proxmox-2`, one member of the `jameshouse-pve` cluster. The hypervisor is **not standalone**.

Monitoring placement on node 2 reduces coupling with workloads on `PROXMOX`, but node-local VM storage still means cluster membership alone does not provide automatic monitoring VM storage HA.

## IaC ownership

Primary ownership includes:

```text
IaC/terraform/proxmox/monitor-01/
IaC/ansible/playbooks/monitoring.yml
IaC/ansible/roles/monitoring_stack/
IaC/monitoring/
```

Normal reconciliation is launched from `admin-01`. Manual Grafana/service changes are not authoritative until reconciled into Git.

## Alerting policy

Alerts should be introduced only when the signal is stable, operator action is clear, planned maintenance is considered and duplicate/noisy alerts are avoided.

Log ingestion does not imply that every event should alert.

## Backup / recovery

`monitor-01` VM202 is included in the `Proxmox-2` nightly backup selection and unattended backup evidence has been observed.

Configuration/dashboard authority remains in Git wherever practical. A representative QEMU restore remains part of the wider recovery-depth backlog.

## Current follow-up work

- cluster/QDevice/link-health telemetry where it adds actionable value;
- `home-01` external availability monitoring;
- useful service-specific coverage without duplicating existing signals;
- ongoing Loki label/cardinality/privacy review;
- recovery-depth testing as part of the wider backup programme.

## Definition of operational state

The service is considered operational because the monitoring/logging stack is healthy, 15/15 managed Linux hosts report, patch/dashboard telemetry is current, network discovery is owned by `monitor-01`, router/Loki pipelines are active, and the Git-managed deployment is idempotent.
