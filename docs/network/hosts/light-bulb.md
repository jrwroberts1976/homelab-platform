# light-bulb

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.252` |
| MAC | `40:ed:00:7c:7b:80` |
| DHCP / discovered hostname | `light-bulb.jameshouse` |
| MAC vendor | TP-Link Limited |
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
- MAC identity: `40:ed:00:7c:7b:80`
- Observed IP address(es): `192.168.2.252`
- Connections: **5**
- Traffic sent: **2.0 KiB**
- Traffic received: **930.4 KiB**
- Top services: `ssl` (2), `http` (1), `dhcp` (1), `ntp` (1)
- Top destination ports: `tcp/443` (2), `tcp/80` (1), `udp/67` (1), `udp/123` (1)

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

- Assessed: `2026-10-29T14:02:32+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `40:ed:00:7c:7b:80`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a TP-Link L510-series IoT device, probably a smart bulb. The hostname and vendor are consistent, but DHCP/router evidence associates L510 with a different IP address, so address identity should be reviewed.

### Confirmed facts

- The observed hostname is L510.
- The inventory and Nmap vendor are TP-Link Limited.
- The observed IP address is 192.168.2.174 with MAC address 40:ed:00:7c:7b:80.
- The device is currently reported online.
- Nmap has no recorded TCP or UDP ports and no OS matches.
- The router reports hostname L510 at 192.168.2.252, creating an address-association discrepancy.

### Inferences

- L510 is likely a TP-Link L510-series IoT device, commonly associated with a smart-bulb product line.
- The device likely runs embedded IoT firmware, but no exact operating system or firmware version is supported.

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
