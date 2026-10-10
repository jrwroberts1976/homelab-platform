# asus-aimesh-181

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `asus-aimesh-181` |
| Address | `192.168.2.181` |
| Type | network |
| Role | ASUS AiMesh node |
| Managed by Ansible | No |
| State | Active |

## Network identity
- MAC address:
- Vendor/OUI:
- Hostname / DHCP name:
- VLAN / network:
- Physical location or hypervisor:

## Operating system and platform evidence
- Authoritative OS:
- OS evidence source:
- Architecture:
- Kernel / firmware:
- Nmap fingerprint:
- Nmap evidence timestamp:
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
- Summary generated: `2026-10-10T00:20:32+01:00`
- MAC identity: `04:d4:c4:b8:52:28`
- Observed IP address(es): `192.168.2.181`
- Connections: **7,858**
- Traffic sent: **8.0 MiB**
- Traffic received: **527.3 KiB**
- Top services: `ssl` (5), `ntp` (1), `dhcp` (1)
- Top destination ports: `tcp/7788` (7277), `udp/9999` (574), `tcp/443` (5), `udp/123` (1), `udp/67` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->
| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity
Use bounded domain/service summaries only; do not commit a complete household browsing history.

| Service / domain family | Example domains | Evidence source | Last observed | Interpretation |
|---|---|---|---|---|
| | | | | |

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-08T12:04:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:b8:52:28`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

ASUS AiMesh wireless mesh node identified as RT-AC86U-5228 at 192.168.2.181. It exposes Dropbear SSH and web management services; the exact firmware/OS is not established by the available evidence.

### Confirmed facts

- The canonical estate record identifies this device as an ASUS AiMesh node and wireless mesh node.
- The device hostname and DHCP hostname are RT-AC86U-5228.
- The inventory and Nmap vendor are ASUSTek Computer.
- TCP ports 22, 80, and 8443 are open.
- Port 22 provides corroborated Dropbear SSH service using protocol 2.0.
- Port 8443 provides a corroborated TLS-wrapped HTTPS-alt service.
- The TLS certificate identifies RT-AC86U-5228 and includes ASUS router, repeater, access-point, and mesh-related DNS names.
- Greenbone reports zero matching actionable findings for the current IP; this does not establish that the device is vulnerability-free or fully scanned.

### Inferences

- The device is likely an ASUS RT-AC86U-based embedded router/repeater platform used as an AiMesh node.
- The firmware is likely within the ASUS router/repeater firmware family, but no precise firmware version or operating system is supported.
- Nmap Linux and Android matches are fingerprints only and do not establish the device OS.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

## Monitoring and security
- Grafana host dashboard:
- Zabbix / Node Exporter / other monitoring:
- Alerting:
- Vulnerability findings:
- Firewall/access policy:
- Accepted risks:

## Ownership and administration
- Owner / responsible person:
- Management method:
- Configuration source:
- Patching / maintenance:
- Backup / recovery:
- Planned retirement / replacement:

## Evidence history
| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| | | | |

## Notes
- 
