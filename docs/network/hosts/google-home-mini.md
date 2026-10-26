# google-home-mini

> Persistent private device record generated from the live network-detail audit on 29 September 2026. Keep secrets, raw packet captures and complete household browsing history out of Git.

## Identity

| Field | Value |
|---|---|
| Address | `192.168.2.249` |
| MAC | `f0:ef:86:35:bc:55` |
| DHCP / discovered hostname | `google-home-mini.jameshouse` |
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
- Summary generated: `2026-10-26T00:22:36+00:00`
- MAC identity: `f0:ef:86:35:bc:55`
- Observed IP address(es): `192.168.2.249`
- Connections: **10,193**
- Traffic sent: **12.2 MiB**
- Traffic received: **12.2 MiB**
- Top services: `dns` (3883), `ssl` (1202), `quic` (626), `ntp` (96), `http` (31), `dhcp` (7)
- Top destination ports: `udp/10101` (2803), `udp/53` (2621), `udp/5353` (1262), `udp/9478` (1171), `udp/9999` (946), `udp/443` (626)

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

- Assessed: `2026-10-22T15:00:05+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `f0:ef:86:35:bc:55`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

High-confidence Google Home Mini identity based on the documented DHCP hostname, Google vendor attribution, Nmap Google Home device match, and Chromecast/Google TLS certificate. Exact OS or firmware is not established.

### Confirmed facts

- The device is online at 192.168.2.249.
- The router documents the DHCP hostname as Google-Home-Mini.
- Inventory and Nmap identify the vendor as Google.
- Nmap includes a 98% match for Google Home device.
- TCP ports 8008, 8009, and 8443 are open according to Nmap.
- TCP 8443 is identified by service enrichment as HTTPS-alt and has a Google Chromecast ICA certificate.
- TCP 9000 is identified by service enrichment as cslistener over SSL.
- The TLS certificate subject and issuer identify Google and Chromecast-related certificate authorities.
- Greenbone reported zero actionable findings matching this current IP; this does not prove the host is vulnerability-free.
- No sampled warning or error entries were present in the bounded 24-hour Loki sample.

### Inferences

- The device is most likely a Google Home Mini smart speaker or closely related Google Home media device.
- The device likely uses embedded firmware with a Linux-based implementation, but the Nmap Linux kernel matches do not establish an exact OS or firmware version.
- The observed Google service domains are consistent with Google ecosystem connectivity but do not independently identify the device model.

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
