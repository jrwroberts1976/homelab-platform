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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `f0:ef:86:35:bc:55`
- Observed IP address(es): `192.168.2.249`
- Connections: **10,654**
- Traffic sent: **13.5 MiB**
- Traffic received: **14.0 MiB**
- Top services: `dns` (4412), `ssl` (1276), `quic` (643), `ntp` (96), `http` (29), `dhcp` (7)
- Top destination ports: `udp/53` (2853), `udp/10101` (2640), `udp/5353` (1559), `udp/9478` (1153), `udp/9999` (970), `tcp/443` (660)

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

- Assessed: `2026-10-29T15:01:29+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `f0:ef:86:35:bc:55`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Identified as a Google Home Mini smart speaker. The exact firmware/OS is not established; Nmap reports a tentative Google Home device fingerprint and three open TCP ports.

### Confirmed facts

- The inventory and DHCP hostname are Google-Home-Mini.
- The inventory and Nmap vendor are Google.
- Nmap identifies the device as a Google Home device with 98% fingerprint accuracy.
- TCP ports 8008, 8009, and 8443 are open.
- Observed DNS domains include Google services such as homeplatformmesh-pa.googleapis.com and connectivitycheck.gstatic.com.
- Greenbone reports zero matching actionable findings for the current IP; this does not establish that the device is vulnerability-free.

### Inferences

- The device is most likely a Google Home Mini smart speaker.
- The platform is best classified broadly as embedded IoT firmware.
- Nmap Linux kernel matches are tentative and do not establish the exact OS or firmware.

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
