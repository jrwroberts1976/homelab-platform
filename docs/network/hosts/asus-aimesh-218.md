# ASUS AiMesh node — 192.168.2.218

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity
| Field | Value |
|---|---|
| Canonical name | `asus-aimesh-218` |
| Address | `192.168.2.218` |
| Type | network |
| Role | Wireless mesh node |
| Managed by Ansible | No |
| State | Active |

## Network identity
- MAC address:
- Vendor/OUI:
- Hostname / DHCP name:
- VLAN / network:

## Operating system and platform evidence
- Authoritative OS:
- OS evidence source:
- Firmware:
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
- Summary generated: `2026-10-06T00:24:03+01:00`
- MAC identity: `04:d4:c4:c1:62:38`
- Observed IP address(es): `192.168.2.218`
- Connections: **8,049**
- Traffic sent: **7.4 MiB**
- Traffic received: **536.2 KiB**
- Top services: `http` (86), `ntp` (5), `ssl` (5), `syslog` (1)
- Top destination ports: `tcp/7788` (7231), `udp/9999` (572), `udp/1900` (144), `tcp/2869` (89), `udp/123` (5), `tcp/443` (5)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->
| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity
Use bounded domain/service summaries only.

| Service / domain family | Example domains | Evidence source | Last observed | Interpretation |
|---|---|---|---|---|
| | | | | |

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-01T10:04:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:c1:62:38`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

ASUS AiMesh wireless mesh node identified as RT-AC86U-6238. Embedded router firmware is indicated, but the exact OS is unsupported by the available evidence. SSH, HTTP, and HTTPS-alt are exposed; no actionable Greenbone findings match the current IP.

### Confirmed facts

- The canonical estate record identifies this device as an ASUS AiMesh node with role Wireless mesh node.
- The vendor is ASUSTek Computer.
- The documented hostname and DHCP hostname are RT-AC86U-6238.
- The device is online at 192.168.2.218 with MAC address 04:d4:c4:c1:62:38.
- TCP ports 22, 80, and 8443 are open.
- Port 22 is identified as Dropbear sshd using SSH protocol 2.0.
- The TLS certificate identifies RT-AC86U-6238 and includes ASUS router, repeater, and access-point DNS names.
- Nmap completed OS identification but reported multiple Linux and Android candidate fingerprints rather than a single authoritative OS.
- Greenbone reported zero matching actionable findings for the current IP; this does not establish that the host is vulnerability-free.
- Patch telemetry is unavailable.

### Inferences

- The hostname, certificate, vendor, and canonical estate role are consistent with an ASUS RT-AC86U-based AiMesh node.
- The device likely runs ASUS embedded router firmware, but the exact firmware and underlying OS are not established.
- The Nmap Linux and Android matches are fingerprint candidates and are insufficient to identify Android or a specific Linux kernel.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

## Monitoring and security
- Grafana host dashboard:
- Monitoring:
- Alerting:
- Firewall/access policy:
- Accepted risks:

## Evidence history
| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| | | | |

## Notes
- 
