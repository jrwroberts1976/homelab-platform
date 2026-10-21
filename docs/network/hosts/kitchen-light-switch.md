# kitchen-light-switch

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.167` |
| MAC | `f8:17:2d:64:ca:04` |
| DHCP / discovered hostname | `kitchen-light-switch.jameshouse` |
| MAC vendor | Not yet known |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `baseline`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: vendor,OS,ports,DNS,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-21T00:24:48+01:00`
- MAC identity: `f8:17:2d:64:ca:04`
- Observed IP address(es): `192.168.2.167`
- Connections: **85**
- Traffic sent: **82.0 KiB**
- Traffic received: **64.2 KiB**
- Top services: `ssl` (62), `dhcp` (1)
- Top destination ports: `tcp/443` (71), `udp/6667` (8), `tcp/8886` (5), `udp/67` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity

| Signal / service family | Evidence | Interpretation |
|---|---|---|
| No bounded DNS signal recorded yet | automatic dual-Pi-hole evidence | Review with other evidence before identifying the device |

Use service/domain-family summaries here, not raw Pi-hole history. DNS resolution does not prove a person visited a website.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-15T13:01:53+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `f8:17:2d:64:ca:04`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online device at 192.168.2.167 identified primarily by its kitchen-light-switch hostname. The DHCP hostname is wlan0, creating an identity conflict; no OS, vendor, port, or service evidence is available.

### Confirmed facts

- The device is online at 192.168.2.167.
- Inventory and telemetry hostname are kitchen-light-switch.jameshouse and kitchen-light-switch, respectively.
- The router reports DHCP hostname wlan0 for this IP.
- No authoritative OS, inventory OS, or Nmap OS evidence is available.
- No TCP or UDP ports were reported by Nmap.
- No matching actionable Greenbone findings were reported for the current IP.

### Inferences

- The kitchen-light-switch hostname suggests this is a smart light-switch device.
- The device likely uses embedded IoT firmware, but the operating system is not identified.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

## Monitoring and security

- Grafana host dashboard:
- Expected services:
- Unexpected services:
- Alerts/findings:
- Firewall/access policy:
- Accepted risks:

## Ownership and administration

- Friendly/reviewed device name:
- Owner / responsible person:
- Physical location:
- Management method:
- Firmware / patching:
- Backup / recovery:
- Planned retirement / replacement:

## Evidence history

| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| 2026-09-29 | Initial persistent host record created from live inventory/detail audit | monitor-01 inventory + deep-profile + DNS state | pending review |

## Notes

- 
