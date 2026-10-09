# Amazon Fire TV / Fire TV Stick — 192.168.2.8

> Persistent private device record. Identification is evidence-qualified; keep raw DNS history out of Git.

## Identity
| Field | Value |
|---|---|
| Address | `192.168.2.8` |
| MAC | `94:3a:91:cd:4c:51` |
| MAC vendor | Amazon Technologies |
| Device type | Amazon Fire TV / Fire TV Stick |
| Confidence | corroborated |
| Identity key | MAC |

## Operating system and platform evidence
- Nmap OS: Android 9–10 (Linux 4.9–4.14)
- Evidence source: `inferred_nmap`
- Nmap-reported accuracy: 100%
- Nmap family/generation: Android / 10.X
- Nmap vendor/device type: Google / phone
- Nmap CPE: `cpe:/o:google:android:10`
- Nmap profile completion: 2026-09-16 18:19 UTC

## Open ports and services
| Port | Protocol | Service | Product/version | Evidence | Expected? |
|---:|---|---|---|---|---|
| 38364 | TCP | tcpwrapped | — | Nmap | Review |
| 4070 | TCP | nagios-nsca | Nagios NSCA guess | Nmap | Review |
| 44994 | TCP | http | Amazon FireTV Stick | Nmap | Strong identity evidence |
| 55442 | TCP | nagios-nsca | Nagios NSCA guess | Nmap | Review |
| 55443 | TCP | unknown | — | Nmap | Review |

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `94:3a:91:cd:4c:51`
- Observed IP address(es): `192.168.2.8`
- Connections: **1,489**
- Traffic sent: **676.8 KiB**
- Traffic received: **83.6 KiB**
- Top services: `dns` (876), `http` (6)
- Top destination ports: `udp/5353` (876), `udp/14600` (303), `udp/39400` (223), `tcp/1879` (36), `udp/45280` (26), `udp/1900` (14)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->
| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity
Only bounded application/service evidence is retained here.

| Service / domain family | Example domains | Evidence source | Interpretation |
|---|---|---|---|
| Amazon Fire TV / Video | `ftvpes-eu.amazon.com`, `*.api.amazonvideo.com` | dns-01 + dns-02 | Supports Fire TV identity |
| Alexa | `avs-alexa-18-eu.amazon.com` | dns-01 + dns-02 | Amazon voice/service dependency |
| Fire TV release services | `firereleasenotes-eu.amazon.com` | dns-01 | Fire TV platform activity |
| NordVPN | `pdp.nordvpn.com`, `nc-mqtt.nordvpn.com` | dns-01 | NordVPN application/service activity observed |

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-08T11:05:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `94:3a:91:cd:4c:51`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely Amazon Fire TV or Fire TV Stick at 192.168.2.8. Amazon/Fire TV DNS activity and an Amazon media-device Nmap fingerprint support the identity, but the exact OS and model are not established.

### Confirmed facts

- The device is online at 192.168.2.8.
- The recorded vendor is Amazon Technologies.
- Nmap reports a 99% match for Amazon Fire TV or Kindle Paperwhite and classifies it as an Amazon embedded media device.
- TCP port 8009 is open.
- DNS evidence includes Amazon Fire TV, Amazon Video, and Alexa endpoints, with a corroborated Fire TV device hint.
- No matching actionable Greenbone findings were reported for the current IP; this does not establish that the host is vulnerability-free.

### Inferences

- The device is more likely an Amazon Fire TV or Fire TV Stick than a Kindle Paperwhite because the bounded DNS activity specifically indicates Fire TV, Amazon Video, and Alexa services.
- The platform is best classified cautiously as embedded IoT firmware; the supplied Nmap alternatives do not establish an exact OS.
- NordVPN-related DNS activity may indicate VPN-related software or traffic, but it does not establish a specific installed function or user intent.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

## Monitoring and security
- Grafana dashboard UID: `net-host-f81780db642f`
- Identity correlation: DNS + Amazon MAC vendor + Nmap Amazon FireTV service
- DNS confidence: corroborated
- Review unexpected ports/services separately; service guesses are not authoritative.

## Evidence history
| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| 2026-09-29 | Automatic Fire TV identity corroborated | dual Pi-hole + MAC + Nmap | automated/reviewed |

## Notes
- 
