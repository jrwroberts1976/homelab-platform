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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `68:ff:7b:1b:33:c0`
- Observed IP address(es): `192.168.2.91`
- Connections: **54**
- Traffic sent: **7.6 KiB**
- Traffic received: **48.9 KiB**
- Top services: `ntp` (47), `ssl` (7)
- Top destination ports: `udp/123` (47), `tcp/443` (7)

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
- MAC identity: `68:ff:7b:1b:33:c0`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Online TP-Link smart-home device identified by hostname and DHCP model-like name HS100. Nmap found TCP/9999 open, but no supported OS fingerprint or exact firmware evidence is available.

### Confirmed facts

- The device is online at 192.168.2.91.
- The inventory hostname is living-room-lamp-bulb.jameshouse.
- The DHCP hostname is HS100.
- The recorded vendor is TP-Link Technologies.
- TCP port 9999 is open.
- Nmap OS identification is incomplete and returned no OS matches.
- No actionable Greenbone findings matched this IP in the supplied scan results.

### Inferences

- The device is likely an HS100-class TP-Link smart-home device, consistent with the DHCP hostname.
- The device likely runs embedded IoT firmware, but the specific operating system and firmware version are unknown.

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
