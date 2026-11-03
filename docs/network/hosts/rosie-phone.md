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

- Assessed: `2026-11-03T16:04:24+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `92:ff:53:0a:16:e9`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online host with no hostname, vendor, service, DNS, or OS identification evidence. Device identity remains unresolved and requires review.

### Confirmed facts

- The host is currently online at 192.168.2.179.
- The observed MAC address is 92:ff:53:0a:16:e9.
- No authoritative OS fact is available.
- No inventory hostname, kind, role, vendor, kernel, or OS is recorded.
- Nmap completed a baseline scan with no TCP or UDP ports reported and no OS matches.
- No bounded DNS policy matches were recorded in the last hour.
- Greenbone reported zero actionable findings matching this IP; this does not prove the host is vulnerability-free or fully scanned.
- Loki telemetry is unavailable and patching status is unavailable.

### Inferences

- The MAC address does not provide a reliable vendor identity from the supplied evidence.
- The device type and platform cannot be determined from the available evidence.

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
