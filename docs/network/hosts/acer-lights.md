# acer-lights

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.95` |
| MAC | `60:83:e7:f3:c1:92` |
| DHCP / discovered hostname | `acer-lights.jameshouse` |
| MAC vendor | TP-Link PTE. |
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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `60:83:e7:f3:c1:92`
- Observed IP address(es): `192.168.2.95`
- Connections: **5**
- Traffic sent: **500 B**
- Traffic received: **492 B**
- Top services: `ntp` (4), `dhcp` (1)
- Top destination ports: `udp/123` (4), `udp/67` (1)

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

- Assessed: `2026-10-29T16:03:23+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `60:83:e7:f3:c1:92`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a TP-Link Tapo P110 smart plug. The device advertises TP-Link/Tapo cloud endpoints and exposes TCP port 80. Nmap identified lwIP, which is a TCP/IP stack rather than a complete operating system.

### Confirmed facts

- The device hostname is P110.
- The recorded vendor is TP-Link PTE.
- DNS activity includes TP-Link cloud/Tapo endpoints.
- Nmap reports a lwIP 1.4.1–2.0.3 fingerprint.
- TCP port 80 is open.
- No actionable Greenbone findings match the current IP 192.168.2.112.

### Inferences

- The hostname P110 together with TP-Link vendor data and Tapo cloud DNS strongly indicates a TP-Link Tapo P110 smart plug.
- The device likely runs embedded IoT firmware using the lwIP networking stack.

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
