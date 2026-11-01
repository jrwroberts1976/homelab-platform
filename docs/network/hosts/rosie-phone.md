# rosie-phone

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.224` |
| MAC | `92:ff:53:0a:16:e9` |
| DHCP / discovered hostname | `rosie-phone.jameshouse` |
| MAC vendor | Not attributable by OUI (locally administered MAC) |
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
- MAC identity: `92:ff:53:0a:16:e9`
- Observed IP address(es): `192.168.2.224`
- Connections: **5,794**
- Traffic sent: **93.2 MiB**
- Traffic received: **1.2 GiB**
- Top services: `ssl` (4659), `quic` (1622), `dns` (221), `http` (144), `ayiya` (13), `dhcp` (11)
- Top destination ports: `tcp/443` (3355), `udp/443` (1689), `udp/5353` (213), `tcp/5222` (179), `tcp/80` (144), `tcp/5228` (41)

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
- MAC identity: `92:ff:53:0a:16:e9`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

POCO-C75 appears to be a POCO smartphone based on its DHCP and telemetry hostname. No authoritative OS, Nmap OS match, service data, or vendor-identifying MAC information is available.

### Confirmed facts

- The device hostname is POCO-C75 in inventory, telemetry, DHCP, and Nmap data.
- The device is online at 192.168.2.179 with MAC address 92:ff:53:0a:16:e9.
- The MAC address has no vendor information in the supplied evidence.
- Nmap OS identification is incomplete because OS evidence is missing.
- No TCP or UDP ports were reported by the bounded Nmap result.
- No matching actionable Greenbone findings were reported for the current IP.

### Inferences

- The model-like POCO-C75 hostname is consistent with a POCO smartphone.
- The platform is likely mobile-device firmware, but Android or another exact operating system is not established.

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
