# living-room-lamp-bulb

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.91` |
| MAC | `68:ff:7b:1b:33:c0` |
| DHCP / discovered hostname | `living-room-lamp-bulb.jameshouse` |
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
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `68:ff:7b:1b:33:c0`
- Observed IP address(es): `192.168.2.91`
- Connections: **1,119**
- Traffic sent: **187.3 KiB**
- Traffic received: **133.8 KiB**
- Top services: `dns` (64), `ntp` (47), `ssl` (23), `dhcp` (12)
- Top destination ports: `udp/9999` (958), `udp/53` (64), `udp/123` (47), `tcp/443` (37), `udp/67` (12), `udp/43459` (1)

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

- Assessed: `2026-10-08T13:03:48+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `68:ff:7b:1b:33:c0`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link HS100 smart-home device based on its DHCP hostname and vendor data. The host exposes TCP port 9999, but no service label or operating-system evidence is available. No actionable Greenbone findings matched this IP.

### Confirmed facts

- The device is online at 192.168.2.91.
- The documented inventory hostname is living-room-lamp-bulb.jameshouse, with telemetry hostname living-room-lamp-bulb.
- The DHCP hostname is HS100.
- The reported vendor is TP-Link Technologies.
- The MAC address is 68:ff:7b:1b:33:c0.
- TCP port 9999 is open.
- Nmap provided no OS matches and reported missing OS evidence.
- No actionable Greenbone findings matched this current IP.
- No recent locally blocked high-risk DNS policy matches were recorded.

### Inferences

- The DHCP hostname HS100 and TP-Link vendor strongly suggest a TP-Link HS100 smart-home device, commonly a smart plug.
- The device likely uses embedded IoT firmware, but the operating system and firmware version are unsupported by the supplied evidence.

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
