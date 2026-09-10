# Homelab Network Sensor Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** implementation branch / not yet deployed  
**Target host:** `sensor-01.jameshouse`  
**Target IPv4:** `192.168.2.55` (must pass unused-address preflight before creation)  
**Placement:** VM on `PROXMOX` / `192.168.2.70`

## Purpose

`sensor-01` is the dedicated passive network/security observation platform for the homelab.

It is deliberately separate from `monitor-01` so loss or maintenance of one Proxmox host does not remove both sensing and monitoring.

The sensor has two distinct network roles:

1. **management NIC** — normal LAN connectivity for SSH, package updates and Prometheus scraping;
2. **capture NIC** — future USB NIC passed directly through from PROXMOX and connected only to HP ProCurve mirror/SPAN destination port 24.

The capture NIC must never have a normal IP address, gateway, DHCP client, DNS role or bridge membership.

## Toolchain

### Required baseline

| Tool | Purpose | Deployment policy |
|---|---|---|
| Suricata 8.0.x | IDS/NSM detection engine | Debian 13 backports; installed now, capture service disabled until dedicated NIC exists |
| suricata-update | Managed Suricata rules | Debian 13 backports; ET Open baseline initially |
| Zeek 8.0.x LTS | Passive network metadata and protocol telemetry | Official Zeek Debian 13 repository; installed now, runtime disabled until dedicated NIC exists |
| Prometheus Node Exporter | VM OS/resource health | Debian package, managed by existing `node_exporter` role |
| tcpdump | Packet-arrival and SPAN validation | Debian package |
| ethtool | Capture-NIC features/statistics/offload control | Debian package |
| jq | EVE JSON inspection and validation | Debian package |
| iproute2 | Interface/link/address inspection | Debian package |
| usbutils | USB passthrough identification | Debian package |
| pciutils | Hardware/driver inspection | Debian package |
| curl + ca-certificates + gnupg | Repository/bootstrap/health tooling | Debian packages |
| logrotate | Local log retention control | Debian package |

### Deliberately not baseline

- **Security Onion** — too much overlapping platform/storage/UI for this design.
- **Arkime** — full-session/PCAP indexing is deferred until storage requirements are understood.
- **EveBox** — UI/storage overlap; Grafana/Loki direction is already established.
- **Elasticsearch/OpenSearch** — not required for the first sensor phase.
- **tshark/Wireshark inside the VM** — `tcpdump` is sufficient for server-side proof; packet files can be analysed on an admin workstation when needed.
- **continuous full packet capture** — deferred; the first design stores Suricata/Zeek metadata, not every packet.

## Why both Suricata and Zeek

Suricata answers primarily:

> Is this traffic suspicious or matching known detection logic?

Zeek answers primarily:

> What hosts, connections, protocols and behaviours were observed?

They are complementary rather than competing engines.

Both engines will use **Community ID with the same seed** so a Suricata alert can later be correlated with the matching Zeek connection record.

## Data produced

### Suricata

Primary structured output:

```text
/var/log/suricata/eve.json
```

Initial EVE event classes should include:

- alert
- anomaly
- flow
- DNS
- HTTP
- TLS
- SSH
- DHCP where supported
- stats

Ethernet metadata must be enabled so MAC addresses are retained when available.

### Zeek

Primary logs:

```text
/opt/zeek/logs/current/
```

Useful initial logs include:

- `conn.log`
- `dns.log`
- `dhcp.log`
- `ssl.log`
- `http.log`
- `ssh.log`
- `known_hosts.log`
- `known_services.log`
- `notice.log`
- `weird.log`
- `capture_loss.log`
- `stats.log`

Zeek's native telemetry framework will be used for Prometheus health/performance metrics once the engine is activated. No third-party Zeek exporter is required.

## Suricata Prometheus metrics

Suricata does not provide a native Prometheus exposition endpoint.

The Corelight `suricata_exporter` remains a **candidate**, not a baseline dependency. It reads counters from the Suricata Unix command socket, but its compatibility must be proved against the exact Suricata 8 package before production adoption.

Until that gate passes:

- Node Exporter reports host health;
- Suricata EVE stats provide sensor/capture counters;
- Prometheus-specific Suricata export is deferred rather than introducing an unproven dependency.

## Capture design

Target physical path:

```text
selected LAN switch traffic
          |
          v
HP ProCurve 2510G-24
mirror/SPAN destination port 24
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

The management NIC remains separate and attached to `vmbr0`.

## Capture-interface policy

When the USB capture NIC arrives:

1. identify it by stable USB vendor/product/device identity;
2. pass it directly to `sensor-01`;
3. verify it is not part of a Proxmox bridge;
4. give the guest capture interface no IP configuration;
5. disable GRO/LRO/GSO/TSO and other packet-merging offloads where supported;
6. verify promiscuous receive;
7. use `tcpdump` to prove mirrored traffic arrives;
8. measure packet/drop counters before starting analyzers;
9. enable Suricata;
10. enable Zeek;
11. validate both tools against the same mirrored traffic.

No switch mirror change should be considered complete until packet arrival is proven at the guest.

## Rules

Initial Suricata rule policy:

- use `suricata-update`;
- begin with the default Emerging Threats Open feed;
- keep local suppressions/thresholds under Git;
- never silently suppress a noisy signature without recording why;
- schedule updates through IaC-managed systemd units;
- validate the ruleset before reload.

## Correlation

Community ID is enabled in both engines using the same seed.

This allows future pivots such as:

```text
Suricata alert
   -> community_id
   -> Zeek conn.log
   -> DNS/TLS/HTTP context
   -> device inventory
```

## Monitoring integration

`monitor-01` remains the monitoring authority.

Initial sensor monitoring:

- ICMP availability;
- Node Exporter on TCP/9100;
- Suricata process/rules/capture status after activation;
- Zeek native telemetry after activation;
- capture loss/drop counters;
- disk/log capacity.

Dashboards are intentionally deferred until the collector/sensor estate is complete.

Loki/Alloy integration is also deferred. Structured logs remain local and rotation-controlled until the logging platform is ready.

## IaC ownership

- Terraform: `sensor-01` VM compute/storage/management network and, later, USB passthrough.
- Ansible: OS baseline, sensor toolchain, repositories, Suricata/Zeek configuration, capture NIC policy, services, rules and validation.
- Git: all desired configuration except secrets and generated runtime data.
- Proxmox GUI/manual guest edits: not authoritative.

## Resource sizing

Live preflight on 10 September 2026 showed PROXMOX has 7.6 GiB total RAM with
about 4.0 GiB available before sensor creation. The original 6 GiB sensor
proposal was therefore rejected.

Phase 1 uses **3 GiB RAM** and an **80 GiB disk on `vm-ssd`**. Suricata and
Zeek remain disabled, so this phase is for installation, configuration
validation and monitoring only.

Before both packet engines are activated, rerun CPU/RAM/storage capacity
checks. The final sensor memory allocation is evidence-driven; the current
8 GiB hypervisor is not assumed to have enough physical headroom for both
engines under mirrored production traffic.

## Phase gates

### Phase 1 — toolchain

Can be completed before the USB adapter arrives:

- build `sensor-01` with the phase-1 3 GiB allocation;
- install the complete toolchain;
- prove exact Suricata/Zeek versions;
- validate binaries/configuration;
- keep packet engines disabled;
- expose Node Exporter;
- prove `monitor-01` can scrape the host.

### Phase 2 — capture hardware

After the USB adapter arrives:

- add USB passthrough in Terraform;
- configure the capture interface through Ansible;
- confirm no IP/route;
- apply offload policy;
- connect switch port 24;
- prove packet arrival.

### Phase 3 — engines

- pass the final PROXMOX capacity gate and adjust VM RAM through Terraform if required;
- activate Suricata;
- update/validate rules;
- activate Zeek;
- enable matching Community ID;
- validate EVE and Zeek logs;
- validate capture-loss/drop metrics.

### Phase 4 — ingestion

After Loki is deployed:

- ship selected Suricata EVE and Zeek logs;
- retain only useful event classes centrally;
- establish retention;
- correlate sensor events with device inventory.

## Definition of done

The sensor platform is complete when:

- VM infrastructure is reproducible from Git;
- all packages/configuration are reproducible through Ansible;
- management and capture networks are physically/logically separate;
- the capture interface has no L3 configuration;
- mirrored packets are proven at `sensor-01`;
- Suricata produces valid EVE data with rules loaded and no capture loss beyond an agreed threshold;
- Zeek produces expected connection/protocol logs;
- Community ID correlates the same flow between both engines;
- `monitor-01` receives health/telemetry data;
- runtime data survives normal service restarts;
- a second IaC apply is idempotent;
- no production monitoring collector depends on TestServer `.220`.
