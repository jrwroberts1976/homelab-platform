# Homelab Network Sensor Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** passive capture operational; Suricata and Zeek active  
**Host:** `sensor-01.jameshouse`  
**IPv4:** `192.168.2.55`  
**Placement:** VM 201 on `PROXMOX` / `192.168.2.70`  
**Last current-state review:** 14 September 2026

## Purpose

`sensor-01` is the dedicated passive network/security observation platform for the homelab.

It is deliberately separate from `monitor-01` so loss or maintenance of one Proxmox host does not remove both sensing and monitoring.

The design uses two network roles:

1. **management NIC** — normal LAN connectivity for SSH, package updates and Prometheus scraping;
2. **capture NIC** — dedicated USB Ethernet adapter passed through from `PROXMOX` and connected to the HP ProCurve mirror/SPAN destination.

The capture NIC is a passive observation interface and must not be repurposed as a normal routed management interface.

## Current operational state

The earlier Phase 1-only description is superseded.

Direct validation on 14 September 2026 showed:

```text
management interface: eth0
capture interface:    enx00249b63b38a
capture state:        UP, PROMISC, LOWER_UP
```

The capture activation gate exists at:

```text
/etc/homelab-network-sensor/capture-enabled
```

Current engine state:

| Tool | Version | Validated state |
|---|---|---|
| Suricata | 8.0.6 | active and enabled |
| `suricata-update` | installed | rules-management tool available |
| Zeek | 8.0.10 | `homelab-zeek.service` active and enabled; `zeekctl status` reports running |
| Alloy | 1.19.2 | active |
| Node Exporter | 1.9.0 | active |

The compact estate audit reported zero failed systemd units on `sensor-01`.

## Capture design

Current physical/logical path:

```text
LAN switch traffic
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
PROXMOX .70
USB passthrough
        |
        v
sensor-01
        |
        +--> eth0: management
        |
        +--> enx00249b63b38a: passive capture
                 |
                 +--> Suricata
                 |
                 +--> Zeek
```

The older documentation that described mirroring as disabled and port 24 as only a planned future destination is no longer current.

Current switch configuration evidence includes:

```text
mirror-port 24
interface 1-23
   monitor
```

`show monitor` confirms port 24 as the mirror destination and ports 1 through 23 as monitoring sources.

The previous dated physical port map must not be reused after this change without a fresh port-by-port validation.

## Why both Suricata and Zeek

Suricata primarily answers:

> Is this traffic suspicious or matching detection logic?

Zeek primarily answers:

> What hosts, connections, protocols and behaviours were observed?

They are complementary. The design uses shared identifiers/configuration where practical so Suricata detections can be correlated with Zeek connection metadata.

## Suricata

Primary structured output:

```text
/var/log/suricata/eve.json
```

Useful event families can include alerts, anomalies, flows, DNS, HTTP, TLS, SSH and stats depending on the deployed rules/configuration.

Current validation proved Suricata 8.0.6 active and enabled.

## Zeek

Primary logs:

```text
/opt/zeek/logs/current/
```

Useful outputs include connection, DNS, TLS/SSL, HTTP, SSH, known-host/service, notice, weird, capture-loss and stats data.

Direct validation on 14 September reported:

```text
Name  Type       Host       Status   Pid    Started
zeek  standalone localhost  running  25809  13 Sep 06:26:55
```

The exact PID/start time is observational evidence, not a desired-state value.

## Rules and policy

Suricata rule policy remains:

- use `suricata-update`;
- use the approved baseline feed;
- keep local suppressions/thresholds under Git;
- never silently suppress noisy signatures without recording why;
- validate the ruleset before reload.

Zeek policy/configuration should likewise remain Git-managed through the current IaC role rather than being hand-edited on the VM.

## Monitoring and logging

Current host/platform monitoring includes:

- ICMP reachability;
- Node Exporter;
- Alloy 1.19.2;
- zero failed-unit validation.

Alloy is now part of the deployed logging architecture. The older text that described central Loki/Alloy as future-only is superseded.

Sensor observability should continue to focus on useful signals such as:

- Suricata/Zeek service state;
- packet/drop counters;
- capture loss;
- rules/update health;
- log growth and disk capacity;
- CPU/memory impact;
- event/alert rates where actionable.

Avoid high-cardinality Loki labels such as arbitrary IPs, ports, usernames or full event text.

## IaC ownership

Relevant paths include:

```text
IaC/terraform/proxmox/sensor-01/
IaC/ansible/playbooks/proxmox-sensor-capture.yml
IaC/ansible/playbooks/network-sensor.yml
IaC/ansible/playbooks/network-sensor-config.yml
IaC/ansible/playbooks/network-sensor-zeek.yml
IaC/ansible/playbooks/network-sensor-alloy.yml
IaC/ansible/roles/proxmox_sensor_capture_usb/
IaC/ansible/roles/network_sensor/
IaC/ansible/roles/network_sensor_config/
IaC/ansible/roles/network_sensor_zeek/
IaC/ansible/roles/network_sensor_alloy/
```

Normal controller:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

## Operational safety gates

The capture design must continue to preserve these boundaries:

- `eth0` remains the management path;
- the capture adapter remains dedicated to passive observation;
- capture activation remains gated through IaC/state validation;
- switch mirror changes require deliberate validation;
- any future interface rename or USB replacement must be reconciled into IaC before engines are blindly restarted;
- after switch, hypervisor or USB changes, prove packet arrival and inspect capture/drop counters before declaring the sensor healthy.

## Definition of current operational state

The sensor is operational because:

- VM identity and placement are correct;
- management networking works;
- the dedicated capture interface is present, up and promiscuous;
- the capture gate exists;
- switch mirroring is configured with port 24 as destination and ports 1-23 as sources;
- Suricata is active/enabled;
- Zeek is active/enabled and reports its standalone process running;
- Node Exporter and Alloy are deployed;
- zero failed systemd units were observed during the 14 September compact audit.

## Remaining follow-up

- keep the physical switch port map current after SPAN changes;
- monitor capture loss and resource impact over time;
- tune Suricata/Zeek output only from observed operational needs;
- maintain low-cardinality Loki labels and useful dashboards;
- retain repeatable capture-path validation in the runbook/IaC workflow.
