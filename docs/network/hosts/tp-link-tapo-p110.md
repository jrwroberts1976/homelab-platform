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
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `60:83:e7:f4:0b:2e`
- Observed IP address(es): `192.168.2.92`
- Connections: **4**
- Traffic sent: **192 B**
- Traffic received: **192 B**
- Top services: `ntp` (4)
- Top destination ports: `udp/123` (4)

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
