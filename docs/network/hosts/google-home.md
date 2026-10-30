# google-home

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.17` |
| MAC | `a4:77:33:5f:94:fe` |
| DHCP / discovered hostname | `google-home.jameshouse` |
| MAC vendor | Google |
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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `a4:77:33:5f:94:fe`
- Observed IP address(es): `192.168.2.17`
- Connections: **7,287**
- Traffic sent: **10.0 MiB**
- Traffic received: **9.3 MiB**
- Top services: `dns` (3981), `ssl` (966), `quic` (467), `ntp` (96), `http` (24), `dhcp` (1)
- Top destination ports: `udp/53` (2448), `udp/5353` (1533), `udp/9478` (1184), `udp/9999` (981), `tcp/443` (522), `udp/443` (467)

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

- Assessed: `2026-10-29T14:02:32+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `a4:77:33:5f:94:fe`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely Google Home smart speaker/media device. The hostname, Google vendor attribution, and Nmap device classification align; exact firmware/OS is not supported by the evidence. TCP ports 8008, 8009, and 8443 are open. No matching actionable Greenbone findings were reported for 192.168.2.125.

### Confirmed facts

- The device hostname is Google-Home.
- The inventory and Nmap vendor fields identify Google.
- Nmap reports a Google Home device classification.
- TCP ports 8008, 8009, and 8443 are open.
- The device is online at 192.168.2.125.
- Greenbone reported zero matching actionable findings for 192.168.2.125.
- The router data contains a Google-Home record at 192.168.2.17.

### Inferences

- The device is most likely a Google Home smart speaker or related Google media device.
- It likely uses embedded IoT firmware, possibly Linux-based, but the exact OS and firmware version cannot be determined.
- The separate router IP record may reflect a stale or separate DHCP observation and does not by itself establish a second device.

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
