# james-lt

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.183` |
| MAC | `24:b2:b9:30:f8:55` |
| DHCP / discovered hostname | `james-lt.jameshouse` |
| MAC vendor | Not yet known |
| Online at audit | True |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `baseline`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: vendor,OS,ports,DNS,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-10T00:20:32+01:00`
- MAC identity: `24:b2:b9:30:f8:55`
- Observed IP address(es): `192.168.2.183`
- Connections: **13,085**
- Traffic sent: **87.2 MiB**
- Traffic received: **1008.8 MiB**
- Top services: `dns` (8822), `ssl` (3037), `quic` (991), `http` (359), `ssh` (5), `dtls` (4)
- Top destination ports: `udp/53` (4776), `tcp/53` (3735), `tcp/443` (2255), `udp/443` (1002), `udp/5353` (243), `tcp/80` (148)

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

- Assessed: `2026-10-08T12:04:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `24:b2:b9:30:f8:55`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

James-LT is an online network endpoint at 192.168.2.183. Its hostname is consistently reported by DHCP, the router, inventory, and Nmap, but no vendor, OS, port, or service evidence is available. Manual review is required to determine the device type and platform.

### Confirmed facts

- The device is online at 192.168.2.183.
- The router DHCP hostname and hostname are both James-LT.
- Inventory reports hostname james-lt.jameshouse and telemetry hostname james-lt.
- The MAC address is 24:b2:b9:30:f8:55.
- Nmap collection is partial and reports no OS matches or ports; the TCP scan also reported an error.
- No authoritative OS information is available.
- Greenbone reported zero matching actionable findings; this does not prove the host is vulnerability-free or fully scanned.
- No sampled Loki entries or recent high-risk DNS policy matches were reported.

### Inferences

- The consistent James-LT naming supports identifying this host as the James-LT endpoint.
- The available evidence is insufficient to determine whether this is a laptop, desktop, or another client device.
- The operating system and platform family cannot be identified from the supplied evidence.

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
