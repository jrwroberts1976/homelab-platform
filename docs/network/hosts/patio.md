# patio

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.30` |
| MAC | `c4:82:e1:f2:f9:9f` |
| DHCP / discovered hostname | `patio.jameshouse` |
| MAC vendor | Tuya Smart |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `baseline`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: OS,ports,DNS,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-02T00:22:09+01:00`
- MAC identity: `c4:82:e1:f2:f9:9f`
- Observed IP address(es): `192.168.2.30`
- Connections: **71**
- Traffic sent: **52.9 KiB**
- Traffic received: **46.7 KiB**
- Top services: `ssl` (67), `dhcp` (1)
- Top destination ports: `tcp/443` (70), `udp/67` (1)

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

- Assessed: `2026-10-01T10:04:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `c4:82:e1:f2:f9:9f`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a Tuya Smart embedded IoT device at 192.168.2.30. No exposed services, Nmap OS match, DNS identity signal, or OS telemetry were collected; exact device type and OS require manual review.

### Confirmed facts

- The device is online at 192.168.2.30.
- The recorded hostname is patio.jameshouse and the telemetry hostname is patio.
- The DHCP/router hostname is wlan0.
- The recorded vendor is Tuya Smart.
- The MAC address is c4:82:e1:f2:f9:9f.
- Nmap OS identification is incomplete because OS evidence is missing; no TCP or UDP ports were reported.
- No Zeek connections or top services were reported in the supplied sample.
- No matching actionable Greenbone findings were reported for this IP; this does not establish that the host is vulnerability-free.

### Inferences

- The Tuya Smart vendor attribution supports classifying the device as an embedded IoT device.
- The supplied evidence does not support identifying a specific Tuya product, function, operating system, or OS version.

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
