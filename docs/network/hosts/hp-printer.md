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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-29T13:02:13+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `c4:65:16:79:58:08`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

HP DeskJet 2600 series network printer, identified by corroborated service product data, HP hostnames, and printer-specific Nmap fingerprints. Exact firmware/OS is not established.

### Confirmed facts

- The device hostname is hp-printer.jameshouse and the DHCP hostname is HP795808.
- The inventory vendor is Hewlett Packard.
- Ports 80, 443, 631, 8080, and 9100 are open over TCP.
- Ports 80, 443, 631, and 8080 expose corroborated HP DeskJet 2600 series printer HTTP configuration services.
- The reported device serial is CN95O878PS06PX.
- The TLS certificate identifies HP795808 as both subject and issuer common name.
- No matching actionable Greenbone findings were reported for 192.168.2.123; this does not prove the device is vulnerability-free.
- DNS samples include HP printer-related domains such as xmpp009.hpeprint.com, chat.hpeprint.com, h10141.www1.hp.com, and ccc.hpeprint.com.

### Inferences

- The device is an HP DeskJet 2600 series network printer.
- The device likely uses embedded printer firmware; the exact operating system or firmware platform is not established.
- Nmap suggests VxWorks-related printer fingerprints, but this is treated as an unconfirmed inference rather than the exact OS.

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
