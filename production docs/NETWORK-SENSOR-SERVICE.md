# Homelab Network Sensor Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** Phase 1 deployed and validated; Phase 2 capture activation pending dedicated USB NIC and switch repatching  
**Host:** `sensor-01.jameshouse`  
**IPv4:** `192.168.2.55`  
**Placement:** VM 201 on `PROXMOX` / `192.168.2.70`  
**Last current-state review:** 12 September 2026

## Purpose

`sensor-01` is the dedicated passive network/security observation platform for the homelab.

It is deliberately separate from `monitor-01` so loss or maintenance of one Proxmox host does not remove both sensing and monitoring.

The design has two network roles:

1. **management NIC** — normal LAN connectivity for SSH, package updates and Prometheus scraping;
2. **capture NIC** — future dedicated USB Ethernet adapter passed directly through from `PROXMOX` and connected to the HP ProCurve SPAN destination.

The capture NIC must never have a normal IP address, gateway, DHCP client, DNS role or Proxmox bridge membership.

## Current phase state

### Phase 1 — COMPLETE

Validated 12 September 2026:

- Debian 13 VM is live at `192.168.2.55`;
- management networking works;
- only `lo` and the management `eth0` are present;
- no USB/capture NIC is attached;
- Suricata is installed and deliberately inactive/disabled;
- Zeek is installed and deliberately inactive;
- Node Exporter is active on TCP/9100;
- zero failed systemd units;
- Prometheus ICMP and Node Exporter targets are healthy.

### Phase 2 — PENDING

Phase 2 begins only when the dedicated USB capture NIC is available and the physical switch repatching is approved.

Do not start Suricata or Zeek merely because the software is installed.

## Current toolchain

| Tool | Validated state | Purpose |
|---|---|---|
| Suricata | 8.0.6, AF_PACKET support present | IDS/NSM detection engine |
| `suricata-update` | installed | Managed rules |
| Zeek | 8.0.10 under `/opt/zeek` | Passive metadata/protocol telemetry |
| Node Exporter | 1.9.0, active | VM OS/resource health |
| tcpdump | installed | Packet-arrival/SPAN validation |
| ethtool | installed | Capture-NIC/offload inspection |
| jq | installed | EVE JSON inspection |

The installed toolchain does not mean capture is operational. There is currently no dedicated capture interface.

## Why both Suricata and Zeek

Suricata primarily answers:

> Is this traffic suspicious or matching detection logic?

Zeek primarily answers:

> What hosts, connections, protocols and behaviours were observed?

They are complementary.

The target design uses a shared Community ID configuration so Suricata alerts can be correlated with Zeek connection records.

## Data paths after activation

### Suricata

Primary structured output:

```text
/var/log/suricata/eve.json
```

Expected event families may include alerts, anomalies, flows, DNS, HTTP, TLS, SSH and stats depending on the final configuration.

### Zeek

Primary logs:

```text
/opt/zeek/logs/current/
```

Useful logs include connection, DNS, TLS/SSL, HTTP, SSH, known-host/service, notice, weird, capture-loss and stats data.

## Capture design

Target physical path:

```text
selected LAN traffic
        |
        v
HP ProCurve 2510G-24
        |
        | configured mirror/SPAN session
        v
port 24 — future SPAN destination
        |
        v
dedicated USB Ethernet adapter
        |
        v
PROXMOX .70
USB passthrough
        |
        v
sensor-01 capture NIC
(no IP, no DHCP, no route)
        |
        +--> Suricata
        |
        +--> Zeek
```

## Important current switch reality

The 12 September switch audit proved:

- port mirroring is currently **disabled**;
- port 24 is currently **not** a SPAN destination;
- port 24 currently carries the primary ASUS router connection;
- physical patching is expected to change when the new USB capture adapter arrives.

Port 24 remains the **planned future SPAN destination**, but that is target state, not current state.

Do not configure mirroring until the repatching plan has been agreed and the router/uplink path has been safely moved.

## Capture-interface activation policy

When the USB capture NIC arrives:

1. record the adapter make/model, USB identity and MAC;
2. agree the final switch patching plan;
3. move the current port-24 router connection to its approved final port;
4. verify normal LAN/router connectivity after the move;
5. configure the HP ProCurve mirror/SPAN session with port 24 as destination;
6. pass the USB adapter directly through to `sensor-01`;
7. verify it is not part of a Proxmox bridge;
8. give the guest capture interface no IP configuration;
9. disable inappropriate packet-merging/offload features where required;
10. use `tcpdump` to prove mirrored traffic arrives;
11. inspect packet/drop counters;
12. enable Suricata through IaC;
13. enable Zeek through IaC;
14. validate both engines against the same mirrored traffic;
15. validate log volume, storage and CPU/RAM impact;
16. validate monitoring/log forwarding.

No switch mirror change should be considered complete until packet arrival is proven in the guest.

## Current switch evidence relevant to the sensor

Current evidence-backed switch mappings include:

```text
port 18 -> Proxmox-2 .71
port 20 -> admin-01 .48
port 21 -> PROXMOX .70
port 23 -> docker-01 .220
port 24 -> primary ASUS router .1
```

This is a dated snapshot and **not** the final repatching plan.

## Rules

Initial Suricata rule policy remains:

- use `suricata-update`;
- begin from the approved baseline feed;
- keep local suppressions/thresholds under Git;
- never silently suppress noisy signatures without recording why;
- validate the ruleset before reload.

## Monitoring integration

Current monitoring:

- ICMP probe from `monitor-01` — healthy;
- Node Exporter on TCP/9100 — healthy.

After capture activation, add monitoring for:

- engine service state;
- packet/drop counters;
- capture loss;
- rule-update health;
- log growth/disk capacity;
- CPU/memory impact;
- optional sensor-specific Prometheus export only after compatibility is proven.

## Logging direction

Do not assume Loki/Alloy exists centrally today.

When central logging is deliberately deployed, ingest useful Suricata/Zeek outputs with stable low-cardinality labels and preserve raw structured content for query-time analysis.

## IaC ownership

Current relevant paths include:

```text
IaC/terraform/proxmox/sensor-01/
IaC/ansible/playbooks/network-sensor.yml
IaC/ansible/playbooks/network-sensor-config.yml
IaC/ansible/roles/network_sensor/
IaC/ansible/roles/network_sensor_config/
IaC/scripts/deploy-sensor-01-vm.sh
IaC/scripts/deploy-network-sensor-toolchain.sh
IaC/scripts/configure-network-sensor-phase1.sh
```

Normal controller:

```text
admin-01
192.168.2.48
```

## Phase 1 definition of done

Phase 1 is complete because:

- VM identity/placement are correct;
- management networking works;
- Suricata is installed;
- Zeek is installed;
- packet engines are safely stopped without a capture NIC;
- Node Exporter is healthy;
- monitoring sees the host;
- zero failed units were observed.

## Phase 2 definition of done

Phase 2 is complete only when:

- dedicated USB capture NIC is installed and identified;
- switch repatching is complete and documented;
- port 24 is actually configured as SPAN destination;
- mirrored packets are proven at `sensor-01`;
- capture NIC has no management IP/route;
- Suricata runs and produces valid EVE data;
- Zeek runs and produces valid telemetry;
- capture loss/resource impact are acceptable;
- monitoring/logging is operational;
- final port map and recovery/runbook documentation are updated.
