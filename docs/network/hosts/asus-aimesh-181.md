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

- Assessed: `2026-10-22T14:00:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:b8:52:28`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Identified as the ASUS AiMesh wireless mesh node documented as asus-aimesh-181, using the model-like hostname RT-AC86U-5228. It exposes Dropbear SSH and web services; the exact firmware/OS is not established. No actionable Greenbone findings matched the current IP.

### Confirmed facts

- The canonical estate role is ASUS AiMesh node / Wireless mesh node.
- The documented hostname is RT-AC86U-5228, with IP address 192.168.2.181.
- The inventory vendor and Nmap vendor are ASUSTek Computer.
- TCP ports 22, 80, and 8443 are open.
- Port 22 provides corroborated Dropbear SSH service, protocol 2.0.
- A TLS certificate on port 8443 identifies RT-AC86U-5228 and includes ASUS router, repeater, access-point, ZenWiFi, and ExpertWiFi names.
- DNS observations include routerahs.asus.com and fwupdate.asuswrt-merlin.net.
- No actionable Greenbone findings matched 192.168.2.181 in the supplied report.

### Inferences

- The hostname, certificate identity, vendor, and canonical role strongly support an ASUS RT-AC86U-class AiMesh device.
- The device likely runs embedded ASUS router firmware, potentially in the ASUSWRT family, but the exact firmware and OS are unsupported by the evidence.
- Nmap Linux/Android matches are fingerprinting alternatives and do not establish Android or a precise Linux version.
- The open web services are consistent with router administration, but the omitted Nmap label for port 80 is not interpreted.

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
