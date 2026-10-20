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
- Summary generated: `2026-10-20T00:21:45+01:00`
- MAC identity: `5c:34:00:50:df:b3`
- Observed IP address(es): `192.168.2.234`
- Connections: **3,433**
- Traffic sent: **3.5 MiB**
- Traffic received: **3.3 MiB**
- Top services: `ssl` (269), `http` (49), `dns` (31), `ntp` (10), `dhcp` (7)
- Top destination ports: `udp/1900` (2589), `udp/443` (415), `tcp/443` (305), `tcp/80` (49), `udp/53` (31), `udp/123` (10)

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

- Assessed: `2026-10-15T13:01:53+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `5c:34:00:50:df:b3`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a Hisense VIDAA smart TV. Identity is well supported by the hostname, vendor attribution, and VIDAA-related DNS activity; no exact OS or firmware is established.

### Confirmed facts

- The device hostname is main-tv.jameshouse.
- The inventory and Nmap records identify the vendor as Hisense Electric.
- Observed DNS domains include multiple vidaahub.com endpoints.
- Nmap OS identification is incomplete, with no OS matches or port evidence.
- No actionable Greenbone findings matched the current IP at scan time.

### Inferences

- The device is likely a Hisense smart television using the VIDAA platform.
- The platform is best classified as embedded IoT firmware; the exact OS and firmware version are unknown.

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
