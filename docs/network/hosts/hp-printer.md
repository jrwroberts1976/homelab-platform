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
- Summary generated: `2026-10-07T00:21:27+01:00`
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

- Assessed: `2026-10-01T10:02:06+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `c4:65:16:79:58:08`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

HP DeskJet 2600 series network printer identified at 192.168.2.123. Embedded firmware is indicated, but no exact operating system is supported by the evidence. No matching actionable Greenbone findings were reported; this does not establish that the host is vulnerability-free.

### Confirmed facts

- Inventory identifies vendor Hewlett Packard and hostname hp-printer.jameshouse.
- DHCP/router hostname is HP795808.
- Nmap identifies the device type as printer and reports HP DeskJet 2600 series printer HTTP configuration services on ports 80, 443, 631, and 8080.
- The device exposes JetDirect on TCP port 9100 and HP Generic Scan Gateway 1.0 on TCP port 9220.
- The observed serial is CN95O878PS06PX.
- No Nmap OS matches or inventory OS evidence are present.
- Greenbone reported zero matching actionable findings for the current IP.

### Inferences

- The device is very likely an HP DeskJet 2600 series printer using embedded printer firmware.
- The TLS certificate naming HP795808 is consistent with the documented DHCP hostname.

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
