# lava-lamp

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.233` |
| MAC | `68:ff:7b:1b:2d:07` |
| DHCP / discovered hostname | `lava-lamp.jameshouse` |
| MAC vendor | TP-Link Technologies |
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
- MAC identity: `68:ff:7b:1b:2d:07`
- Observed IP address(es): `192.168.2.233`
- Connections: **164**
- Traffic sent: **64.5 KiB**
- Traffic received: **234.6 KiB**
- Top services: `ntp` (79), `ssl` (50), `dhcp` (35)
- Top destination ports: `udp/123` (79), `tcp/443` (50), `udp/67` (35)

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

- Assessed: `2026-10-22T15:00:05+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `68:ff:7b:1b:2d:07`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link HS100 smart plug, identified from the DHCP hostname and TP-Link vendor evidence. OS/firmware is not identified; TCP port 9999 is open. No matching actionable Greenbone findings were reported.

### Confirmed facts

- The device is online at 192.168.2.233.
- The inventory hostname is lava-lamp.jameshouse and the telemetry hostname is lava-lamp.
- The DHCP hostname and router hostname are HS100.
- The recorded vendor is TP-Link Technologies.
- TCP port 9999 is open.
- Nmap OS identification is incomplete and returned no OS matches.
- No actionable Greenbone findings match the current IP.

### Inferences

- The device is likely a TP-Link HS100 smart plug, based on the HS100 DHCP hostname and TP-Link vendor evidence.
- The device likely runs embedded IoT firmware, but the exact OS and firmware version are unsupported by the supplied evidence.

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
