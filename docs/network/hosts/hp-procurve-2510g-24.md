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
- Summary generated: `2026-10-27T00:23:49+00:00`
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

- Assessed: `2026-10-29T13:02:13+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:9c:02:45:39:00`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

HP ProCurve 2510G-24 switch identified from the hostname, Hewlett Packard vendor data, and corroborated HTTP service evidence. Exact firmware/OS is not established; no actionable Greenbone findings match this IP.

### Confirmed facts

- The device IP is 192.168.2.134.
- The reported hostname is hp-switch.jameshouse.
- Inventory and Nmap vendor data identify Hewlett Packard.
- TCP port 80 is open and has corroborated service evidence for an HP ProCurve Switch 2510G-24 HTTP configuration interface.
- TCP port 23 is open; no service label is provided for this port.
- Greenbone reports zero actionable findings matching this current IP.

### Inferences

- The device is an HP ProCurve 2510G-24 network switch.
- The device likely uses embedded switch firmware, but the exact firmware or operating system is unsupported by the supplied evidence.
- The Nmap VxWorks result is a tentative fingerprint and is not sufficient to establish the exact OS.

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
