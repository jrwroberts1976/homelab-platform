# james-phone

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.206` |
| MAC | `16:c1:05:ad:4b:8a` |
| DHCP / discovered hostname | `james-phone.jameshouse` |
| MAC vendor | Not attributable by OUI (locally administered MAC) |
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
- Summary generated: `2026-10-20T00:21:45+01:00`
- MAC identity: `16:c1:05:ad:4b:8a`
- Observed IP address(es): `192.168.2.206`
- Connections: **6,337**
- Traffic sent: **36.5 MiB**
- Traffic received: **328.9 MiB**
- Top services: `ssl` (4048), `quic` (1065), `dns` (540), `ntp` (50), `http` (31), `ayiya` (2)
- Top destination ports: `tcp/443` (3950), `udp/443` (1115), `udp/5353` (534), `tcp/5228` (76), `tcp/5222` (56), `udp/123` (50)

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
- MAC identity: `16:c1:05:ad:4b:8a`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely James's smartphone, identified from the inventory hostname and DHCP hostname `james-s-A13`. Exact OS and vendor are not established. No actionable Greenbone findings were reported for 192.168.2.206.

### Confirmed facts

- The device is associated with IP address 192.168.2.206.
- The inventory hostname is `james-phone.jameshouse`, with telemetry hostname `james-phone`.
- The router reports DHCP hostname `james-s-A13`.
- Authoritative OS data is unavailable.
- Nmap did not obtain an OS match or port data; the scan reported an expected-single-host error.
- No actionable Greenbone findings matched this IP.
- No Zeek connections or top ports/services were recorded in the supplied data.

### Inferences

- The host is likely a smartphone.
- The `A13` suffix may be a model-related DHCP hostname component, but the exact manufacturer and model are unconfirmed.
- The platform is likely mobile embedded firmware, but Android or another specific OS is not established.

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
