# main-tv

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.234` |
| MAC | `5c:34:00:50:df:b3` |
| DHCP / discovered hostname | `main-tv.jameshouse` |
| MAC vendor | Hisense Electric |
| Online at audit | False |
| Stable identity key | MAC |

## Profiling and platform evidence

- Deep-profile status: `partial`
- Nmap OS evidence: 0 Nmap match(es), needs_os=True
- Observed TCP-port summary: 0 open TCP port(s)
- Automatic device hint: None yet
- Details still to investigate: OS,ports,DNS,device-type

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

- Assessed: `2026-10-29T14:02:32+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:34:00:50:df:b3`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a Hisense smart TV using VIDAA-related services. Exact operating system or firmware is not identified by the supplied evidence.

### Confirmed facts

- The device hostname is main-tv.jameshouse.
- The inventory vendor is Hisense Electric.
- The device MAC address is 5c:34:00:50:df:b3.
- The device IP address is 192.168.2.234.
- DNS activity includes multiple vidaahub.com domains.
- No Nmap TCP or UDP ports, services, or OS matches were recorded.
- No matching actionable Greenbone findings were reported for this IP; this does not establish that the device is vulnerability-free.
- The router currently reports the device as online, while inventory marks it offline.

### Inferences

- The device is most likely a Hisense smart TV.
- The vidaahub.com DNS domains are consistent with a VIDAA-based smart-TV platform.
- The underlying OS or firmware version cannot be determined from the supplied evidence.

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
