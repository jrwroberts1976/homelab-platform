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
- Summary generated: `2026-10-04T00:25:18+01:00`
- MAC identity: `94:3a:91:cd:4c:51`
- Observed IP address(es): `192.168.2.8`
- Connections: **1,302**
- Traffic sent: **423.8 KiB**
- Traffic received: **3.3 KiB**
- Top services: `dns` (986)
- Top destination ports: `udp/5353` (948), `udp/53` (38), `udp/63004` (5), `udp/53836` (2), `udp/58077` (2), `udp/49670` (2)

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

- Assessed: `2026-10-01T10:02:06+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `94:3a:91:cd:4c:51`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

192.168.2.8 is an Amazon Technologies device with an Android/Android TV-like Nmap fingerprint and TCP port 8009 open. DNS inventory includes firetvcaptiveportal.com, which is consistent with an Amazon/Fire TV ecosystem, but the device identity and exact OS remain ambiguous.

### Confirmed facts

- The device is online at 192.168.2.8 with MAC address 94:3a:91:cd:4c:51.
- Inventory and Nmap identify the vendor as Amazon Technologies.
- Nmap reports TCP port 8009 as open and labels the service tcpwrapped.
- Nmap produced competing fingerprints for Android 5.0.1/Linux 3.10 and Android TV OS 11/Linux 4.19, among other Linux matches.
- The DNS server data lists firetvcaptiveportal.com among its top domains.
- No canonical estate role, hostname, authoritative OS fact, or direct service product/version is supplied.

### Inferences

- The device is likely an Android-based embedded media device, potentially associated with the Amazon/Fire TV ecosystem.
- The DNS domain signal supports, but does not prove, a Fire TV identity.
- The exact operating system cannot be established from the conflicting Nmap candidates.

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
