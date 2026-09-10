# Homelab Network Sensor Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** VM deployed; sensor/capture implementation in progress
**Host:** `sensor-01.jameshouse` / `192.168.2.55`
**Placement:** VM201 on `PROXMOX` / `192.168.2.70`
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`

## Purpose

`sensor-01` is the dedicated passive network/security observation platform for the homelab.

It is deliberately separate from `monitor-01` so the monitoring platform and packet-analysis workload are split across the two Proxmox failure domains.

## Current state

The VM now exists and is running on `PROXMOX` with the approved management identity at `192.168.2.55`.

Phase-1 sizing is approximately:

- 3 GiB RAM;
- 80 GiB disk;
- Debian 13 VM;
- management network on the normal LAN.

The full Suricata + Zeek mirrored-traffic workload is **not considered complete** merely because the VM is running. Capture hardware/path, engine activation and loss/drop validation remain implementation gates.

## Network roles

The sensor design has two distinct paths:

1. **management NIC** — normal LAN connectivity for SSH, updates and Prometheus scraping;
2. **capture NIC** — dedicated mirrored-traffic path from HP ProCurve port 24, with no normal IP address, default route, DHCP or DNS role.

The capture NIC must never be used for management traffic.

## Capture architecture

```text
selected LAN traffic
       |
       v
HP ProCurve 2510G-24
mirror/SPAN destination port 24
       |
       v
dedicated capture adapter/path
       |
       v
PROXMOX .70
       |
       v
sensor-01 VM201
capture interface: no L3 configuration
       |
       +--> Suricata
       |
       +--> Zeek
```

## Tooling target

Approved sensor tooling includes:

- Suricata for IDS/NSM detection;
- `suricata-update` with Emerging Threats Open baseline initially;
- Zeek LTS for connection/protocol metadata;
- Node Exporter for VM health;
- `tcpdump`, `ethtool`, `jq`, `iproute2` and hardware-identification tooling for capture validation.

Suricata and Zeek are complementary. Community ID should use the same seed in both engines so an alert can be correlated with the matching Zeek connection metadata.

## Data produced

Suricata primary structured output:

```text
/var/log/suricata/eve.json
```

Useful Zeek logs include connection, DNS, TLS, HTTP, SSH, notices, weird traffic, capture-loss and statistics data.

Do not enable continuous full-PCAP retention by default; storage requirements must be understood first.

## Capture-interface validation

Before declaring the packet path operational:

1. identify the dedicated capture adapter by stable hardware identity;
2. ensure it is not part of a Proxmox bridge used for management;
3. pass/attach it only as designed;
4. ensure the guest capture interface has no IP address/route/DHCP configuration;
5. disable packet-merging offloads where supported and appropriate;
6. verify promiscuous receive;
7. use `tcpdump` to prove mirrored traffic arrives;
8. inspect packet/drop counters;
9. start Suricata and validate EVE output/rules;
10. start Zeek and validate expected logs;
11. prove both engines observe the same test flow.

No switch mirror change is complete until traffic arrival is proven inside `sensor-01`.

## Rules and tuning

Initial Suricata policy:

- manage feeds with `suricata-update`;
- begin with ET Open;
- keep local suppressions/thresholds in Git;
- record why a signature is suppressed;
- validate rules before reload.

Do not turn noisy signatures off silently.

## Monitoring

`monitor-01` (`192.168.2.52`) is the monitoring authority.

Initial sensor monitoring should include:

- VM reachability;
- Node Exporter;
- Suricata process/rules/capture state after activation;
- Zeek process/telemetry after activation;
- capture-loss/drop counters;
- disk/log capacity.

## Central logging

The old TestServer/ids-01 logging path is not the target design.

After fresh Loki/Alloy central logging is operational on `monitor-01`, ship selected Suricata EVE and Zeek data centrally with controlled retention and low-cardinality labels.

See `CENTRAL-LOGGING-SERVICE.md`.

## IaC ownership

- Terraform/OpenTofu: VM compute/storage/management network and any later passthrough declaration;
- Ansible: OS baseline, toolchain, Suricata/Zeek configuration, capture-interface policy, services and validation;
- Git: desired configuration except secrets/generated runtime data;
- Proxmox GUI/manual guest edits are not authoritative unless reconciled back into Git.

Relevant paths include:

```text
IaC/terraform/proxmox/sensor-01/
IaC/ansible/playbooks/network-sensor.yml
IaC/ansible/playbooks/network-sensor-config.yml
IaC/ansible/roles/network_sensor/
IaC/ansible/roles/network_sensor_config/
```

## Capacity

`PROXMOX` remains the chosen sensor host because of its six physical CPU cores, large VM SSD datastore and separation from `monitor-01`, but it has materially less spare RAM than `Proxmox-2`.

The sensor must therefore stay within validated resource limits. Re-run host CPU/RAM/storage checks before increasing VM memory or enabling a significantly heavier capture workload.

## Phase gates

### Phase 1 — VM/toolchain

- VM exists and management access works;
- required packages/configuration deployed;
- Node Exporter/host monitoring works;
- packet engines remain disabled until the capture path is ready.

### Phase 2 — capture path

- dedicated capture hardware/path attached;
- capture interface has no L3 configuration;
- offload/promiscuous policy validated;
- real mirrored packets proven inside the VM.

### Phase 3 — engines

- Suricata enabled with valid rules/EVE data;
- Zeek enabled with expected logs;
- Community ID aligned;
- capture-loss/drop behaviour measured and acceptable.

### Phase 4 — ingestion

- fresh Loki/Alloy platform operational;
- selected Suricata/Zeek logs shipped centrally;
- retention and dashboards/queries validated.

## Definition of done

The sensor platform is complete only when infrastructure/configuration is reproducible, management and capture paths are separated, mirrored packets are proven at the guest, Suricata and Zeek both produce valid data, loss/drop metrics are understood, `monitor-01` receives health telemetry and central logging is integrated according to the approved policy.
