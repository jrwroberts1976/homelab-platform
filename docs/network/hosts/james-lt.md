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
- Summary generated: `2026-10-21T00:24:48+01:00`
- MAC identity: `24:b2:b9:30:f8:55`
- Observed IP address(es): `192.168.2.183`
- Connections: **7,035**
- Traffic sent: **116.2 MiB**
- Traffic received: **2.5 GiB**
- Top services: `ssl` (3691), `quic` (1460), `dns` (1025), `http` (951), `ayiya` (3), `dhcp` (2)
- Top destination ports: `tcp/443` (3034), `udp/443` (1470), `udp/5353` (932), `tcp/80` (632), `tcp/35435` (330), `udp/5355` (88)

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

- Assessed: `2026-10-15T13:01:53+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `24:b2:b9:30:f8:55`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online host 192.168.2.183 is identified as James-LT from DHCP and inventory hostnames. The laptop classification is inferred from the hostname; no OS, vendor, port, or service evidence is available.

### Confirmed facts

- The host is online at 192.168.2.183.
- The router reports the DHCP hostname James-LT.
- Inventory records the hostname james-lt.jameshouse and telemetry hostname james-lt.
- The MAC address is 24:b2:b9:30:f8:55.
- No authoritative OS fact is available.
- Nmap did not obtain OS, TCP-port, or UDP-port evidence.
- No matching actionable Greenbone findings are reported for this IP; this does not establish that the host is vulnerability-free.

### Inferences

- The hostname suffix LT suggests this is likely a laptop or other endpoint computer.
- The operating system and hardware vendor cannot be determined from the supplied evidence.

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
