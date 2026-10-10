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
- Summary generated: `2026-10-10T00:20:32+01:00`
- MAC identity: `f0:ef:86:35:bc:55`
- MAC-attributable originated connections: **none observed in this window**

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

- Assessed: `2026-10-08T13:03:48+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `f0:ef:86:35:bc:55`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely a Google Home Mini smart speaker. Identity is strongly supported by the DHCP hostname, Google vendor metadata, Google Home Nmap fingerprint, and a Chromecast/Google TLS certificate. The exact operating system is not established.

### Confirmed facts

- The device hostname is Google-Home-Mini / google-home-mini.jameshouse.
- The inventory and Nmap vendor fields identify Google.
- Nmap reports a Google Home device fingerprint.
- TCP ports 8008, 8009, and 8443 are open; Nmap service labels for these ports were omitted.
- TCP port 8443 has corroborated HTTPS-alt service evidence.
- A TLS certificate on port 8443 is issued by Google Inc. with issuer CN Chromecast ICA 7 (Audio Assist 2).
- The certificate subject identifies Google Inc. and the device-specific subject CN LQJ8EH FA8FCA6B2CFB.
- The exact OS is unavailable from authoritative inventory and no authoritative OS fact is present.

### Inferences

- The device is most consistent with a Google Home Mini or closely related Google smart-speaker platform.
- The platform is best classified broadly as embedded IoT firmware.
- Nmap Linux kernel matches are fingerprints and do not establish the exact underlying OS or kernel version.

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
