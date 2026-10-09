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
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `16:c1:05:ad:4b:8a`
- Observed IP address(es): `192.168.2.206`
- Connections: **9,177**
- Traffic sent: **34.6 MiB**
- Traffic received: **371.9 MiB**
- Top services: `dns` (5312), `ssl` (2968), `quic` (661), `ntp` (37), `http` (25), `dhcp` (3)
- Top destination ports: `udp/53` (4984), `tcp/443` (2729), `udp/443` (714), `udp/5353` (327), `tcp/853` (72), `tcp/5228` (39)

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

- Assessed: `2026-10-08T12:04:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `16:c1:05:ad:4b:8a`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely James's mobile phone, identified from the inventory and DHCP hostnames. No vendor, OS, open-port, or service evidence is available; manual review is required for platform identification.

### Confirmed facts

- The device is online at 192.168.2.206.
- The inventory hostname is james-phone.jameshouse and the telemetry hostname is james-phone.
- The DHCP hostname is james-s-A13.
- Nmap completed with baseline status but found no TCP or UDP ports and no OS matches.
- No authoritative OS information is available.
- No matching actionable Greenbone findings were reported for this IP; this does not establish that the host is vulnerability-free.
- No sampled Loki entries or recent high-risk DNS policy matches were present.

### Inferences

- The host is likely a smartphone or other mobile phone.
- The DHCP hostname may indicate a device model or user-assigned naming convention, but it is not sufficient to identify the vendor or exact model.
- The operating system and exact platform cannot be determined from the supplied evidence.

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
