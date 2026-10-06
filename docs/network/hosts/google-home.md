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
- Summary generated: `2026-10-06T00:24:03+01:00`
- MAC identity: `a4:77:33:5f:94:fe`
- Observed IP address(es): `192.168.2.17`
- Connections: **8,250**
- Traffic sent: **2.1 MiB**
- Traffic received: **196 B**
- Top services: `dns` (1832)
- Top destination ports: `udp/10101` (2836), `udp/5353` (1832), `udp/9478` (1293), `udp/1111` (1238), `udp/9999` (1041), `tcp/9999` (4)

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

- Assessed: `2026-10-01T10:04:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `a4:77:33:5f:94:fe`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Highly likely Google Home/Chromecast-family device. Identity is supported by the documented Google-Home hostname, Google vendor data, Nmap's Google Home device fingerprint, and a Chromecast Audio Assist TLS certificate. Exact OS is not established; Nmap Linux matches are fingerprint results only. No matching Greenbone findings were reported, which does not establish that the host is vulnerability-free.

### Confirmed facts

- The host is online at 192.168.2.17.
- The documented hostname is google-home.jameshouse, with DHCP hostname Google-Home.
- Inventory and Nmap identify the vendor as Google.
- Nmap reports a Google Home device fingerprint with 98% accuracy.
- The TLS certificate on TCP port 8443 has Google organization details and issuer common name Chromecast ICA 6 (Audio Assist).
- TCP ports 8008, 8009, and 8443 were observed open by Nmap; enrichment also reports services on 8443 and 9000.
- Greenbone reported zero actionable findings matching this current IP.
- Patch telemetry is unavailable.

### Inferences

- The device is most likely a Google Home or closely related Chromecast-family smart speaker/media device.
- The device likely uses embedded firmware with a Linux-derived networking environment, but the exact operating system and version are unsupported by the supplied evidence.

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
