# HP ProCurve 2510G-24

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity
| Field | Value |
|---|---|
| Canonical name | `hp-procurve-2510g-24` |
| Address | `192.168.2.16` |
| Type | network |
| Role | Core managed switch and SPAN source |
| Managed by Ansible | No |
| State | Active |

## Network identity
- MAC address:
- Vendor/OUI:
- Firmware: Y.11.52
- VLAN/network: VLAN 1 untagged
- SPAN: ports 1–23 mirrored to port 24

## Operating system and platform evidence
- Platform: HP ProCurve 2510G-24 (J9279A)
- Management evidence:
- Nmap fingerprint:
- Confidence / review status:

## Open ports and services
| Port | Protocol | Service | Product/version | Evidence time | Expected? |
|---:|---|---|---|---|---|
| | | | | | |

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
A switch should normally have little or no direct Internet/DNS activity. Record only reviewed summaries.

| Service / domain family | Example domains | Evidence source | Last observed | Interpretation |
|---|---|---|---|---|
| | | | | |

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-22T13:00:41+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:9c:02:45:39:00`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

HP ProCurve 2510G-24 managed switch and SPAN source at 192.168.2.16. HTTP configuration service is exposed on TCP/80; TCP/23 is open. No matching actionable Greenbone findings were reported.

### Confirmed facts

- The canonical estate identity is HP ProCurve 2510G-24.
- The documented estate role is core managed switch and SPAN source.
- The device vendor is Hewlett Packard.
- The device is online at 192.168.2.16 with hostname hp-switch.jameshouse.
- TCP/23 and TCP/80 are open.
- TCP/80 provides a corroborated eHTTP 2.0 service identified as HP ProCurve Switch 2510G-24 HTTP configuration.
- Greenbone reported zero matching actionable findings for the current host IP.

### Inferences

- The device uses embedded network-switch firmware rather than a general-purpose host operating system.
- Nmap produced a 100% VxWorks fingerprint match, but this is not sufficient to establish the exact operating system or firmware.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

## Monitoring and security
- Grafana host dashboard:
- Monitoring:
- Legacy management exposure: Telnet
- SPAN security purpose: feeds passive sensor capture
- Accepted risks:

## Evidence history
| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| | | | |

## Notes
- 
