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
- Summary generated: `2026-10-15T00:20:55+01:00`
- MAC identity: `f0:ef:86:35:bc:55`
- Observed IP address(es): `192.168.2.249`
- Connections: **10,416**
- Traffic sent: **13.6 MiB**
- Traffic received: **13.2 MiB**
- Top services: `dns` (4040), `ssl` (1216), `quic` (644), `ntp` (93), `http` (33), `dhcp` (8)
- Top destination ports: `udp/10101` (2769), `udp/53` (2630), `udp/5353` (1410), `udp/9478` (1177), `udp/9999` (1016), `udp/443` (644)

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

- Assessed: `2026-10-15T14:01:33+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `f0:ef:86:35:bc:55`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Identified as a Google Home Mini smart speaker/media device at 192.168.2.249. Google-specific hostname, vendor data, Nmap fingerprint, and Chromecast certificate corroborate the identity; exact OS is not established.

### Confirmed facts

- The device is online at 192.168.2.249.
- The DHCP hostname is Google-Home-Mini.
- Inventory and Nmap vendor fields identify Google.
- Nmap identifies the host as a Google Home device with 99% fingerprint accuracy.
- TCP ports 8008, 8009, and 8443 are open.
- Port 8443 provides HTTPS-related service evidence and presents a certificate issued by Google Inc. with a Chromecast ICA issuer.
- The enrichment data reports TCP port 9000 with the cslistener service over SSL.
- No matching actionable Greenbone findings were reported for the current IP; this is not proof that the host is vulnerability-free.

### Inferences

- The device is most likely a Google Home Mini smart speaker or closely related Google media device.
- It uses embedded IoT firmware, but the exact operating system and firmware version are unsupported by the supplied evidence.

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
