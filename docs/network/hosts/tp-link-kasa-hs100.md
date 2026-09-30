# TP-Link Kasa HS100 — 192.168.2.76

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.76` |
| MAC | `68:ff:7b:1b:1e:ab` |
| DHCP / discovered hostname | `HS100` (ASUS router DHCP evidence) |
| MAC vendor | TP-Link Technologies |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `partial`
- Nmap OS evidence: no reliable OS match; `needs_os_identification=true`
- Observed TCP-port summary: TCP/9999 open
- Reviewed device identity: TP-Link Kasa HS100 Smart Wi-Fi Plug
- Identity confidence: High
- OS/platform: embedded IoT firmware; exact OS remains unresolved
- Identity evidence: ASUS DHCP hostname `HS100`, TP-Link MAC vendor, TCP/9999

The targeted profile completed but did not yield a reliable OS fingerprint. Device identity is strong; exact embedded OS remains an AI/manual identification candidate.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-09-30T00:24:50+01:00`
- MAC identity: `68:ff:7b:1b:1e:ab`
- Observed IP address(es): `192.168.2.76`
- Connections: **51**
- Traffic sent: **4.1 KiB**
- Traffic received: **13.3 KiB**
- Top services: `ntp` (48), `ssl` (2), `dhcp` (1)
- Top destination ports: `udp/123` (48), `tcp/443` (2), `udp/67` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity

| Signal / service family | Evidence | Interpretation |
|---|---|---|
| No bounded DNS signal recorded yet | automatic dual-Pi-hole evidence | Device identity is supported by router hostname, vendor and TCP/9999 rather than DNS |

Use service/domain-family summaries here, not raw Pi-hole history. DNS resolution does not prove a person visited a website.

## Monitoring and security

- Grafana host dashboard:
- Expected services:
- Unexpected services:
- Alerts/findings:
- Firewall/access policy:
- Accepted risks:

## Ownership and administration

- Friendly/reviewed device name: TP-Link Kasa HS100
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
| 2026-09-29 | Identified as TP-Link Kasa HS100 from ASUS DHCP hostname, TP-Link vendor and TCP/9999 evidence; exact OS remains unresolved | ASUS inventory + targeted Nmap | reviewed |

## Notes

- 
