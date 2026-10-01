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
- Summary generated: `2026-10-02T00:22:09+01:00`
- MAC identity: `00:9c:02:45:39:00`
- MAC-attributable originated connections: **none observed in this window**

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

- Assessed: `2026-10-01T10:03:30+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:9c:02:45:39:00`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Identified as the HP ProCurve 2510G-24 core managed switch and SPAN source at 192.168.2.16. Telnet and the HP ProCurve web configuration service are exposed. Exact firmware OS is not established; Nmap suggests VxWorks but the fingerprint is not definitive.

### Confirmed facts

- The canonical estate record identifies the device as an HP ProCurve 2510G-24 network device named hp-procurve-2510g-24.
- The documented estate role is core managed switch and SPAN source.
- The inventory vendor is Hewlett Packard.
- TCP/23 is open and identified as Telnet.
- TCP/80 is open and identified as eHTTP 2.0 with HP ProCurve Switch 2510G-24 HTTP configuration metadata.
- Nmap completed OS identification and reported no need for additional OS identification.
- Greenbone reported zero actionable findings matching 192.168.2.16 in the supplied scan results.

### Inferences

- The device is an embedded network-switch platform rather than a general-purpose host.
- VxWorks is a leading Nmap fingerprint, but it is not sufficiently corroborated to establish the exact operating system.
- The exposed Telnet service may warrant security review.

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
