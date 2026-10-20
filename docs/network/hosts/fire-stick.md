# fire-stick

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.149` |
| MAC | `ac:17:02:07:0d:5d` |
| DHCP / discovered hostname | `fire-stick.jameshouse` |
| MAC vendor | Fibar Group sp. z o.o. |
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
- Summary generated: `2026-10-20T00:21:45+01:00`
- MAC identity: `ac:17:02:07:0d:5d`
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

- Assessed: `2026-10-15T12:02:16+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `ac:17:02:07:0d:5d`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely an Amazon Fire TV device at 192.168.2.149. Hostname, Nmap fingerprint, and DNS activity support the identification, but the inventory/MAC vendor is recorded as Fibar Group and the exact OS is unavailable.

### Confirmed facts

- The device hostname is fire-stick.jameshouse and its telemetry hostname is fire-stick.
- The device IP is 192.168.2.149 and MAC address is ac:17:02:07:0d:5d.
- Nmap identified an Amazon Fire TV or Kindle Paperwhite fingerprint with 99% accuracy and classified it as an embedded media device.
- TCP port 8009 is open.
- DNS signals include Amazon Fire TV, Amazon Video, and Alexa endpoints, as well as NordVPN endpoints.
- The inventory vendor is recorded as Fibar Group sp. z o.o.
- No authoritative OS information is available.
- No actionable Greenbone findings match the current IP.
- Patch telemetry is unavailable.

### Inferences

- The device is most likely an Amazon Fire TV or closely related Amazon media device; the hostname and DNS signals favor Fire TV over Kindle Paperwhite.
- The platform is best described conservatively as embedded media-device firmware; no exact OS or version is supported.
- The conflicting Fibar Group vendor attribution warrants manual review.

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
