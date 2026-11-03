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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-11-03T16:04:24+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `94:3a:91:cd:4c:51`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Online Amazon Technologies device at 192.168.2.151. No hostname, services, Nmap fingerprints, DNS hints, or OS evidence are available, so the device identity and platform remain unresolved.

### Confirmed facts

- The device is online at 192.168.2.151.
- The MAC address is 94:3a:91:cd:4c:51.
- The recorded vendor is Amazon Technologies.
- No TCP or UDP ports are reported open by the baseline Nmap profile.
- No Nmap OS matches are reported.
- No hostname, inventory OS, role, or kind is recorded.
- No actionable Greenbone findings match this IP in the supplied scan results.

### Inferences

- The device may be an Amazon-manufactured or Amazon-branded networked device, but the specific product or function cannot be determined from the available evidence.

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
