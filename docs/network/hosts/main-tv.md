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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `5c:34:00:50:df:b3`
- Observed IP address(es): `192.168.2.234`
- Connections: **4,545**
- Traffic sent: **4.4 MiB**
- Traffic received: **3.2 GiB**
- Top services: `ssl` (412), `http` (145), `dns` (26), `dhcp` (6), `ntp` (6)
- Top destination ports: `udp/1900` (2830), `udp/10176` (679), `tcp/443` (431), `udp/5291` (344), `tcp/80` (85), `tcp/1765` (59)

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

- Assessed: `2026-10-08T12:04:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:34:00:50:df:b3`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely Hisense smart TV using VIDAA-related services. Exact operating system is unavailable; Nmap provided no OS evidence.

### Confirmed facts

- The inventory hostname is main-tv.jameshouse.
- The recorded vendor is Hisense Electric.
- DNS samples include multiple vidaahub.com domains, plus YouTube and Netflix domains.
- The device is currently online at 192.168.2.234.
- Nmap status is partial with no OS matches or port results.
- No actionable Greenbone findings currently match this IP; this is not proof that the host is vulnerability-free.

### Inferences

- The device is most likely a Hisense smart TV.
- The observed VIDAA-related DNS activity is consistent with embedded TV firmware, but does not establish an exact operating system or version.

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
