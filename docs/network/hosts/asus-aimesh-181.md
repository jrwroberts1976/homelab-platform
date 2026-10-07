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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-01T10:04:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:b8:52:28`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

ASUS RT-AC86U-class AiMesh wireless mesh node, identified from the canonical estate role, ASUS hostname, vendor data, and ASUS router TLS certificate. It exposes Dropbear SSH plus HTTP/HTTPS management services. Nmap suggests older Linux/Android fingerprints but does not establish the exact firmware or OS.

### Confirmed facts

- The canonical estate record identifies this device as an ASUS AiMesh node with role Wireless mesh node.
- The inventory and Nmap data identify the vendor as ASUSTek Computer.
- The DHCP and inventory hostnames are RT-AC86U-5228.
- The TLS certificate identifies RT-AC86U-5228 and includes ASUS router, repeater, access-point, and mesh-related DNS names.
- TCP ports 22, 80, and 8443 are open.
- Port 22 is identified as Dropbear sshd, protocol 2.0.
- No actionable Greenbone findings match IP 192.168.2.181.
- The host is currently online at 192.168.2.181.

### Inferences

- The device is likely an ASUS RT-AC86U-class unit operating as an AiMesh node.
- The platform is likely ASUS embedded firmware, probably Linux-based, but the supplied evidence does not establish an exact OS or firmware version.
- The Nmap Linux 3.x/4.x and Android fingerprints are tentative network fingerprints and are not sufficient to identify the exact OS.

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
