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
- Summary generated: `2026-10-05T00:23:30+01:00`
- MAC identity: `92:ff:53:0a:16:e9`
- Observed IP address(es): `192.168.2.224`
- Connections: **4,018**
- Traffic sent: **16.5 MiB**
- Traffic received: **430.4 MiB**
- Top services: `dns` (2178), `ssl` (1494), `quic` (465), `http` (34), `ntp` (6), `dhcp` (2)
- Top destination ports: `udp/53` (1924), `tcp/443` (1155), `udp/443` (487), `udp/5353` (254), `tcp/5222` (54), `tcp/80` (44)

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

- Assessed: `2026-10-01T10:03:30+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `92:ff:53:0a:16:e9`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely a POCO C75 mobile device identified from its DHCP hostname. No MAC vendor, service, Nmap OS, or exact-OS evidence is available; router telemetry currently reports it online while inventory reports it offline.

### Confirmed facts

- The router reports DHCP hostname POCO-C75 for 192.168.2.224.
- The device MAC address is 92:ff:53:0a:16:e9.
- Nmap collection is partial and has no TCP/UDP ports or OS matches; OS identification is pending.
- No actionable Greenbone findings matched the current IP.
- No high-risk DNS policy matches were recorded in the recent one-hour window.
- Patch telemetry is unavailable.

### Inferences

- The DHCP hostname likely identifies the device as a POCO C75.
- The device is likely a smartphone, and may use Android-based mobile firmware.
- The locally administered MAC address provides no reliable vendor identification.

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
