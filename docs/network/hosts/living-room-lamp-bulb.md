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
- Summary generated: `2026-10-16T00:21:46+01:00`
- MAC identity: `68:ff:7b:1b:33:c0`
- Observed IP address(es): `192.168.2.91`
- Connections: **55**
- Traffic sent: **8.9 KiB**
- Traffic received: **55.8 KiB**
- Top services: `ntp` (46), `ssl` (8), `dhcp` (1)
- Top destination ports: `udp/123` (46), `tcp/443` (8), `udp/67` (1)

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

- Assessed: `2026-10-15T14:01:33+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `68:ff:7b:1b:33:c0`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online TP-Link smart-home endpoint at 192.168.2.91, identified by the hostname and DHCP name HS100. Exact firmware or operating system is not available. TCP port 9999 is open; no actionable Greenbone findings matched this IP.

### Confirmed facts

- The device is online at 192.168.2.91.
- The recorded hostname is living-room-lamp-bulb.jameshouse.
- The DHCP hostname is HS100.
- The MAC vendor is TP-Link Technologies.
- TCP port 9999 is open.
- No actionable Greenbone findings matched this current IP.
- No authoritative operating-system fact is available.

### Inferences

- The device is likely a TP-Link home-automation endpoint, potentially HS100-class based on the DHCP hostname.
- The device likely runs embedded IoT firmware, but the exact firmware and operating system are unknown.

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
