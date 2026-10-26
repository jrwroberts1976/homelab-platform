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
- Summary generated: `2026-10-26T00:22:36+00:00`
- MAC identity: `5c:34:00:50:df:b3`
- Observed IP address(es): `192.168.2.234`
- Connections: **4,227**
- Traffic sent: **3.9 MiB**
- Traffic received: **6.5 MiB**
- Top services: `ssl` (202), `dns` (29), `http` (27), `dhcp` (2), `ntp` (2)
- Top destination ports: `udp/1900` (3243), `udp/443` (637), `tcp/443` (251), `tcp/80` (32), `udp/53` (29), `tcp/1883` (28)

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

- Assessed: `2026-10-22T14:00:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:34:00:50:df:b3`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Identified as a Hisense smart TV, likely using VIDAA services. Exact operating system or firmware is unavailable; no open ports or Nmap OS matches were observed. No actionable Greenbone findings matched the current IP.

### Confirmed facts

- The device hostname is main-tv.jameshouse and telemetry hostname is main-tv.
- The recorded vendor is Hisense Electric.
- The device IP is 192.168.2.234 and MAC address is 5c:34:00:50:df:b3.
- DNS samples include multiple vidaahub.com domains and Netflix service domains, along with www.youtube.com.
- Nmap collection was partial with no TCP or UDP ports and no OS matches.
- No actionable Greenbone findings matched this current IP.
- Authoritative OS information is unavailable.

### Inferences

- The device identity is consistent with a Hisense smart TV.
- The vidaahub.com DNS activity is consistent with VIDAA platform services.
- The exact operating system and firmware version cannot be determined from the supplied evidence.

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
