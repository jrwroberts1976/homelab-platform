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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `24:b2:b9:30:f8:55`
- Observed IP address(es): `192.168.2.183`
- Connections: **6,631**
- Traffic sent: **138.8 MiB**
- Traffic received: **890.8 MiB**
- Top services: `ssl` (4995), `quic` (2327), `dns` (447), `http` (138), `ayiya` (6), `dhcp` (1)
- Top destination ports: `tcp/443` (3252), `udp/443` (2335), `udp/5353` (426), `tcp/80` (139), `udp/3702` (71), `udp/138` (54)

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
- MAC identity: `24:b2:b9:30:f8:55`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

James-LT is an online network client identified by its documented hostname. The hostname suggests a laptop, but no vendor, service, or operating-system evidence is available; the Nmap scan is incomplete.

### Confirmed facts

- The documented hostname is James-LT.
- The host is online at 192.168.2.186 with MAC address 24:b2:b9:30:f8:55.
- The inventory and telemetry hostname are both James-LT.
- Nmap status is partial and reports missing OS evidence; no TCP or UDP ports were recorded.
- No actionable Greenbone findings matched the current IP.

### Inferences

- The hostname suffix LT cautiously suggests a laptop or portable computer.
- The exact operating system and hardware vendor cannot be determined from the supplied evidence.
- The router also reports James-LT at 192.168.2.183, which may reflect a stale or separate DHCP observation.

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
