# TP-Link Tapo P110 — 192.168.2.92

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.92` |
| MAC | `60:83:e7:f4:0b:2e` |
| DHCP / discovered hostname | `P110` (ASUS router DHCP evidence) |
| MAC vendor | TP-Link PTE. |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `complete`
- Nmap OS evidence: `lwIP 1.4.1 - 2.0.3` (100% Nmap match)
- Observed TCP-port summary: TCP/80 open
- Reviewed device identity: TP-Link Tapo P110 Smart Plug
- Identity confidence: High
- Platform: embedded IoT firmware using the lwIP TCP/IP stack
- Exact OS: Unknown; lwIP is a network stack, not a complete operating system
- Identity evidence: ASUS DHCP hostname `P110`, TP-Link vendor, Nmap lwIP fingerprint, TP-Link/Tapo cloud DNS

The targeted profile provides strong embedded-platform evidence. The lwIP fingerprint identifies the TCP/IP stack, not a specific operating system.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-04T00:25:18+01:00`
- MAC identity: `60:83:e7:f4:0b:2e`
- Observed IP address(es): `192.168.2.92`
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
| TP-Link/Tapo cloud | `security.iot.i.tplinknbu.com`, `euw1-device-cloudgateway.iot.i.tplinknbu.com` | Supports Tapo device identity; does not identify a complete OS |

Use service/domain-family summaries here, not raw Pi-hole history. DNS resolution does not prove a person visited a website.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-01T10:07:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `60:83:e7:f4:0b:2e`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link Tapo P110 smart plug at 192.168.2.92. The host uses TP-Link/Tapo cloud endpoints and exposes HTTP; Nmap reports a tentative lwIP fingerprint, which does not establish a complete operating system.

### Confirmed facts

- The device hostname is P110.
- The inventory and Nmap vendor are reported as TP-Link PTE.
- The device is online at 192.168.2.92.
- Bounded DNS evidence includes TP-Link cloud/Tapo endpoints, including security.iot.i.tplinknbu.com and euw1-device-cloudgateway.iot.i.tplinknbu.com.
- TCP port 80 is open and Nmap labels the service as HTTP.
- Nmap reports a lwIP 1.4.1–2.0.3 fingerprint with 100% match accuracy.
- Greenbone has zero actionable findings matching the current IP; this is not proof that the host is vulnerability-free or fully scanned.
- Patch telemetry is unavailable.

### Inferences

- The P110 hostname together with TP-Link/Tapo cloud DNS strongly suggests a TP-Link Tapo P110 smart plug.
- The device likely runs embedded IoT firmware using the lwIP TCP/IP stack.
- The exact operating system and firmware version cannot be established from the supplied evidence.

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

- Friendly/reviewed device name: TP-Link Tapo P110
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
| 2026-09-29 | Identified as TP-Link Tapo P110; Nmap reports lwIP stack and DNS shows TP-Link/Tapo cloud activity | ASUS inventory + targeted Nmap + dual-Pi-hole DNS | reviewed |

## Notes

- 
