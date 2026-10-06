<!-- estate-authority: IaC/inventory/estate.json -->
# Homelab Network Sensor Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** OPERATIONAL PASSIVE SENSOR  
**Host:** `sensor-01.jameshouse`  
**IPv4:** `192.168.2.55`  
**Placement:** VM201 on `PROXMOX`  
**Last current-state review:** 6 October 2026

## Purpose

`sensor-01` is the dedicated passive network/security observation platform. It is deliberately separate from the active Greenbone scanner and from the central monitoring VM.

Two network roles are maintained:

1. `eth0` — normal management path;
2. `enx00249b63b38a` — dedicated passive capture interface.

The capture interface must not be repurposed as routed management or Corosync networking.

## Current operational state

```text
management interface: eth0
capture interface:    enx00249b63b38a
capture state:        UP / PROMISC
Suricata:             active
Zeek:                 active via homelab-zeek.service
```

The capture activation gate is retained under `/etc/homelab-network-sensor/` and remains part of the IaC safety model.

Latest 5 October maintenance evidence:

| Component | Current observation |
|---|---|
| Suricata | 8.0.7, active |
| Zeek | 8.0.10, active under IaC-managed service |
| Grafana Alloy | 1.20.1, active |
| Zabbix Agent 2 | 7.0.31, active |
| failed systemd units | 0 |

Version observations are dated evidence, not permanent pins unless IaC explicitly pins them.

## Capture path

```text
LAN traffic
   |
   v
HP ProCurve 2510G-24
   |
   | mirror sources: ports 1-23
   v
port 24 mirror destination
   |
   v
dedicated USB Ethernet adapter
   |
   v
PROXMOX USB passthrough
   |
   v
sensor-01 capture NIC
   +--> Suricata
   +--> Zeek
```

Port 24 is the current SPAN destination. Older port maps that show it as a normal uplink are historical pre-repatch evidence.

## Suricata

Primary structured output:

```text
/var/log/suricata/eve.json
```

Rules are managed through the approved Git/IaC workflow and `suricata-update`. Suppressions/thresholds require an explicit reason and validation before reload.

## Zeek

Primary logs:

```text
/opt/zeek/logs/current/
```

The authoritative service is `homelab-zeek.service`; checks against a non-existent generic `zeek.service` must not be interpreted as a Zeek outage.

Useful current evidence includes connection, DNS, HTTP/TLS and other protocol metadata according to enabled policy.

## Evidence pipeline

The sensor produces schema-version-2 network-security evidence on a scheduled collector interval.

Current flow:

```text
sensor-01 local evidence
   |
   | restricted SFTP with pinned host key
   v
monitor-01 evidence store
   |
   v
management-report collector/renderer
```

The evidence uses a bounded window and freshness validation. Missing/stale evidence is surfaced as an assurance gap rather than treated as zero events.

The end-to-end transfer and management-report consumption were proven in September and remain the production architecture.

## Monitoring and logging

Current baseline includes:

- Node Exporter;
- Grafana Alloy;
- Zabbix Agent 2;
- centralized Loki ingestion;
- service-state/capture evidence checks.

Operationally useful monitoring should focus on:

- Suricata/Zeek service state;
- packet/drop and capture-loss indicators;
- rules/update health;
- log growth/disk capacity;
- CPU/memory impact;
- actionable alert/event trends.

Avoid high-cardinality Loki labels for arbitrary IPs, ports, usernames or raw event text.

## IaC ownership

Relevant automation includes:

```text
IaC/terraform/proxmox/sensor-01/
IaC/ansible/playbooks/proxmox-sensor-capture.yml
IaC/ansible/playbooks/network-sensor.yml
IaC/ansible/playbooks/network-sensor-config.yml
IaC/ansible/playbooks/network-sensor-zeek.yml
IaC/ansible/roles/network_sensor*/
```

Normal orchestration runs from `admin-01`.

## Operational safety gates

- keep `eth0` as management;
- keep the capture adapter passive/dedicated;
- preserve IaC capture activation checks;
- validate switch mirroring after cabling/switch changes;
- reconcile interface/USB identity changes before restarting capture blindly;
- after switch/hypervisor/USB changes, prove packet arrival and review capture/drop counters.

## Definition of operational state

The sensor is operational when VM identity/placement are correct, management connectivity works, the dedicated capture NIC is present/promiscuous, switch SPAN is active, Suricata and Zeek are healthy, telemetry/evidence pipelines are current and no failed systemd units are present.

## Remaining follow-up

- keep the physical switch map current;
- monitor capture loss/resource impact;
- tune rules/output only from observed needs;
- keep evidence freshness and reporting low-noise;
- retain repeatable capture-path validation in IaC/runbooks.
