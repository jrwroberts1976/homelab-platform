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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `00:9c:02:45:39:00`
- Observed IP address(es): `192.168.2.16`
- Connections: **1**
- Traffic sent: **300 B**
- Traffic received: **300 B**
- Top services: `dhcp` (1)
- Top destination ports: `udp/67` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
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

- Assessed: `2026-10-08T11:05:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:9c:02:45:39:00`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

HP ProCurve 2510G-24 managed switch at 192.168.2.16. Corroborated HTTP evidence identifies the model and HP switch software; TCP 23 and 80 are open. Exact OS is not established.

### Confirmed facts

- The canonical estate record identifies the device as an HP ProCurve 2510G-24 and assigns it the role of core managed switch and SPAN source.
- The device is online at 192.168.2.16 with hostname hp-switch.jameshouse.
- The vendor is recorded as Hewlett Packard.
- TCP port 23 is open; the Nmap service label is omitted.
- TCP port 80 is open and has corroborated HTTP evidence: eHTTP 2.0 with extra information identifying an HP ProCurve Switch 2510G-24 HTTP configuration service.
- Greenbone reported zero actionable findings matching this current IP; this is not proof that the host is vulnerability-free or fully scanned.

### Inferences

- The device is an embedded network-switch platform rather than a general-purpose host.
- Nmap produced a VxWorks match and several alternative embedded-device matches, but these are not sufficient to establish the exact operating system.
- Manual review is required because the platform and exact OS remain ambiguous.

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
