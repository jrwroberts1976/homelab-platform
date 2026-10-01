# fire-stick

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.149` |
| MAC | `ac:17:02:07:0d:5d` |
| DHCP / discovered hostname | `fire-stick.jameshouse` |
| MAC vendor | Fibar Group sp. z o.o. |
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
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `ac:17:02:07:0d:5d`
- Observed IP address(es): `192.168.2.149`
- Connections: **209**
- Traffic sent: **8.1 MiB**
- Traffic received: **60.0 MiB**
- Top services: `dns` (199)
- Top destination ports: `udp/5353` (199), `udp/1232` (10)

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

- Assessed: `2026-10-01T10:03:30+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `ac:17:02:07:0d:5d`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely an Amazon Fire TV/Fire Stick streaming device based on its documented hostname and Amazon Fire TV/Video DNS activity. Nmap reports conflicting Android/Linux fingerprints, so the exact OS is not established. The recorded Fibar vendor and conflicting online-state fields merit review.

### Confirmed facts

- The inventory hostname is fire-stick.jameshouse and the telemetry hostname is fire-stick.
- The inventory vendor is recorded as Fibar Group sp. z o.o.
- DNS activity includes Amazon Fire TV, Amazon Video, Alexa, and NordVPN-related domains.
- Nmap completed OS detection and identified TCP port 8009 as open with a tcpwrapped service label.
- Nmap produced multiple Android and Linux OS matches, including Android 4.1–6.0, Android 9–10, and Linux kernel ranges.
- Greenbone reported zero matching actionable findings for 192.168.2.149; this is not proof that the host is vulnerability-free.
- Router telemetry reports the host online, while inventory telemetry reports it offline.

### Inferences

- The device is likely an Amazon Fire TV/Fire Stick or closely related Amazon streaming endpoint.
- The platform is likely embedded Android/Linux-based firmware, but the supplied evidence does not support a precise OS or version.
- The Nmap service label alone does not establish the host function.

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
