# rosie-laptop

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.6` |
| MAC | `58:02:05:fd:e1:8b` |
| DHCP / discovered hostname | `rosie-laptop.jameshouse` |
| MAC vendor | Not yet known |
| Online at audit | False |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `complete`
- Nmap OS evidence: 0 Nmap match(es), needs_os=None
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: vendor,OS,ports,device-type

A `baseline` profile means the controlled seven-day backlog has not yet supplied the targeted profile for this device. Zero ports in this summary is therefore not proof that no ports are open.

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-06T00:24:03+01:00`
- MAC identity: `58:02:05:fd:e1:8b`
- MAC-attributable originated connections: **none observed in this window**

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity

| Signal / service family | Evidence | Interpretation |
|---|---|---|
| windows_update | automatic dual-Pi-hole evidence | Microsoft/Windows delivery activity observed; supporting clue only |

Use service/domain-family summaries here, not raw Pi-hole history. DNS resolution does not prove a person visited a website.

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-01T10:03:30+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `58:02:05:fd:e1:8b`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Likely the Rosie laptop at 192.168.2.6. DHCP identifies it as LAPTOP-SRR7CFCE, while inventory and Nmap use rosie-laptop.jameshouse. Microsoft Windows Update-related DNS signals support a cautious Windows-like endpoint classification, but no exact OS is confirmed. Manual review is recommended.

### Confirmed facts

- The device IP is 192.168.2.6.
- The MAC address is 58:02:05:fd:e1:8b.
- Inventory hostname and Nmap hostname are rosie-laptop.jameshouse.
- The router reports DHCP hostname LAPTOP-SRR7CFCE and currently reports the host online.
- Nmap completed without an error and reported no TCP ports or OS matches.
- Nmap reported UDP ports 53, 67, 68, 69, 123, 137, 138, 161, 500, 514, 1900, 4500, 5353, and 5683 as open|filtered with tentative service labels.
- DNS evidence includes Windows Update / Microsoft delivery endpoint signals.
- No matching actionable Greenbone findings were present for this IP.
- Patch telemetry is unavailable.

### Inferences

- The hostname strongly suggests this is a laptop associated with Rosie.
- The Microsoft Update-related DNS signals are consistent with a Windows-associated endpoint.
- The platform remains ambiguous because no authoritative OS, product/version, MAC vendor, or Nmap OS match is supplied.

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
