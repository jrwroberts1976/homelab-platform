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
- Summary generated: `2026-10-03T00:22:04+01:00`
- MAC identity: `f0:ef:86:35:bc:55`
- Observed IP address(es): `192.168.2.249`
- Connections: **12,232**
- Traffic sent: **14.2 MiB**
- Traffic received: **18.2 MiB**
- Top services: `dns` (3877), `ssl` (1273), `quic` (658), `ntp` (94), `http` (35), `dhcp` (14)
- Top destination ports: `udp/10101` (2692), `udp/53` (2605), `udp/5353` (1272), `udp/9478` (1126), `udp/1111` (1057), `udp/9999` (963)

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
- MAC identity: `f0:ef:86:35:bc:55`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Google Home Mini identified with high confidence from DHCP hostname, Google vendor data, Nmap fingerprinting, and a Google Chromecast Audio Assist certificate. Exact OS is not supported by the evidence; Nmap Linux labels are tentative. No matching actionable Greenbone findings were reported for this IP.

### Confirmed facts

- The device hostname is google-home-mini.jameshouse and the DHCP hostname is Google-Home-Mini.
- The inventory and Nmap vendor fields identify Google.
- Nmap reported a Google Home device fingerprint with 98% accuracy.
- The device has open TCP ports 8008, 8009, and 8443; Nmap labeled them http, ajp13 over SSL, and https-alt respectively.
- The TLS certificate on port 8443 has issuer Chromecast ICA 7 (Audio Assist 2) and a Google Inc. organization.
- No actionable Greenbone findings matched 192.168.2.249 in the supplied report.
- Patch telemetry is unavailable and provides no update status.

### Inferences

- The device is most consistent with a Google Home Mini smart speaker or closely related Google Home/Chromecast Audio Assist hardware.
- It likely runs embedded firmware with a Linux-derived network implementation, but the exact operating system and version are unsupported.
- The Nmap Linux kernel matches are fingerprint-based estimates and should not be treated as authoritative OS identification.

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
