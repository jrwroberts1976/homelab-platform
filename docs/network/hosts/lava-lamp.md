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
- Summary generated: `2026-10-04T00:25:18+01:00`
- MAC identity: `68:ff:7b:1b:2d:07`
- Observed IP address(es): `192.168.2.233`
- Connections: **930**
- Traffic sent: **412.0 KiB**
- Traffic received: **44.8 KiB**
- Top services: `dns` (122), `ntp` (18), `ssl` (6), `dhcp` (1)
- Top destination ports: `udp/9999` (782), `udp/53` (122), `udp/123` (18), `tcp/443` (7), `udp/67` (1)

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

- Assessed: `2026-10-01T10:04:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `68:ff:7b:1b:2d:07`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link HS100 smart plug at 192.168.2.233. The device exposes TCP/9999; Nmap identified the service only tentatively as "abyss". Exact OS is unsupported by the available evidence.

### Confirmed facts

- The device is online at 192.168.2.233.
- The router DHCP hostname is HS100.
- Inventory and Nmap identify the vendor as TP-Link Technologies.
- MAC address is 68:ff:7b:1b:2d:07.
- TCP port 9999 is open.
- Nmap OS identification is incomplete and reports missing OS evidence.
- No actionable Greenbone findings matched the current IP.

### Inferences

- The HS100 hostname and TP-Link vendor are consistent with a TP-Link HS100 smart plug.
- The device likely runs embedded IoT firmware, but the exact operating system is unknown.
- The Nmap "abyss" service label is tentative and does not establish the device function.

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
