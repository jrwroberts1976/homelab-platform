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
- Summary generated: `2026-10-04T00:25:18+01:00`
- MAC identity: `60:83:e7:f3:c1:92`
- Observed IP address(es): `192.168.2.95`
- Connections: **4**
- Traffic sent: **120 B**
- Traffic received: **376 B**
- Top services: `dns` (4)
- Top destination ports: `udp/53` (4)

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

- Assessed: `2026-10-01T10:07:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `60:83:e7:f3:c1:92`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo P110 IoT device, probably a smart plug. It exposes HTTP and was fingerprinted only as lwIP; no supported exact OS is established.

### Confirmed facts

- The device is online at 192.168.2.95.
- The documented hostname is acer-lights.jameshouse, with telemetry hostname acer-lights.
- The DHCP hostname is P110.
- The recorded vendor is TP-Link PTE.
- DNS activity includes TP-Link cloud/Tapo endpoints, including security.iot.i.tplinknbu.com and euw1-device-cloudgateway.iot.i.tplinknbu.com.
- TCP port 80 is open and identified by Nmap as HTTP.
- Nmap matched lwIP 1.4.1–2.0.3 with a 100% match accuracy.
- Greenbone reported zero matching actionable findings for the current IP; this is not proof that the host is vulnerability-free or fully scanned.

### Inferences

- The DHCP hostname P110 and Tapo-related DNS signals indicate a likely TP-Link Tapo P110 device.
- The likely device function is a smart plug based on the P110 model association, but this function is not directly confirmed by the supplied evidence.
- lwIP is treated as a TCP/IP stack, not as a complete operating-system identification.

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
