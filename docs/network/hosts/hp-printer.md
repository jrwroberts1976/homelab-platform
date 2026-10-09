# hp-printer

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.123` |
| MAC | `c4:65:16:79:58:08` |
| DHCP / discovered hostname | `hp-printer.jameshouse` |
| MAC vendor | Hewlett Packard |
| Online at audit | False |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `complete`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 10 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: OS,DNS,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `c4:65:16:79:58:08`
- MAC-attributable originated connections: **none observed in this window**

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

- Assessed: `2026-10-08T11:05:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `c4:65:16:79:58:08`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

HP DeskJet 2600 series printer identified at 192.168.2.123, with corroborated printer web configuration services and HP scan gateway evidence. Exact operating system is not supported by the available data.

### Confirmed facts

- The device hostname is hp-printer.jameshouse and its DHCP hostname is HP795808.
- The inventory and Nmap vendor are Hewlett Packard.
- Nmap and service enrichment identify an HP DeskJet 2600 series printer configuration service on ports 80, 443, 631, and 8080.
- The identified printer serial is CN95O878PS06PX.
- HP Generic Scan Gateway version 1.0 is exposed on TCP port 9220.
- TCP ports 3910, 3911, 5355, 9100, and 53048 are open; their Nmap labels were omitted.
- DNS observations include HPE printer-related domains such as chat.hpeprint.com, xmpp009.hpeprint.com, and ccc.hpeprint.com.
- No matching actionable Greenbone findings were reported for the current IP; this does not establish that the device is vulnerability-free.
- No authoritative operating-system fact is available.

### Inferences

- The device is a networked HP DeskJet 2600 series printer, with high identity confidence based on corroborated product and service evidence.
- The platform is best represented broadly as embedded IoT firmware; the exact operating system cannot be determined from the supplied evidence.
- Manual review is appropriate if an exact firmware or operating-system identity is required.

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
