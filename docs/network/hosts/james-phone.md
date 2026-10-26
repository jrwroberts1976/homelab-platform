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
- Summary generated: `2026-10-26T00:22:36+00:00`
- MAC identity: `16:c1:05:ad:4b:8a`
- Observed IP address(es): `192.168.2.206`
- Connections: **2,449**
- Traffic sent: **26.7 MiB**
- Traffic received: **447.1 MiB**
- Top services: `ssl` (1693), `quic` (570), `dns` (111), `ntp` (17), `http` (16), `ayiya` (4)
- Top destination ports: `tcp/443` (1375), `udp/443` (697), `udp/5353` (107), `udp/1900` (65), `udp/123` (17), `tcp/5228` (15)

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

- Assessed: `2026-10-22T14:00:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `16:c1:05:ad:4b:8a`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely James's smartphone, identified from the recorded hostnames. The DHCP name may reference an A13 model, but the exact manufacturer, model, and OS are unconfirmed. No ports or service data were collected.

### Confirmed facts

- The device is associated with IP address 192.168.2.206.
- The recorded inventory hostname is james-phone.jameshouse.
- The router reports DHCP hostname james-s-A13 for this IP.
- The MAC address is 16:c1:05:ad:4b:8a.
- The router currently reports the device as online, while inventory marks it offline.
- Nmap has no port or OS results; the TCP scan ended with a host-matching error.
- No authoritative OS, vendor, DNS hint, service, or Greenbone finding is available.

### Inferences

- The hostnames indicate this is likely a smartphone associated with James.
- The DHCP hostname may refer to an A13 device model, but this is not sufficient to establish a manufacturer or exact model.
- The operating system and firmware cannot be determined from the supplied evidence.

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
