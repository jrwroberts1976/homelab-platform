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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-22T14:00:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:c1:62:38`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

ASUS AiMesh wireless mesh node identified as an RT-AC86U-class device. It exposes Dropbear SSH and web management services; exact firmware and OS version are not established.

### Confirmed facts

- The canonical estate record identifies this device as an ASUS AiMesh node with the role Wireless mesh node.
- The vendor is ASUSTek Computer.
- The DHCP and inventory hostname is RT-AC86U-6238.
- TCP port 22 is open and provides corroborated Dropbear SSH service, protocol 2.0.
- TCP ports 80 and 8443 are open.
- The TLS certificate identifies RT-AC86U-6238 and includes ASUS router, repeater, and access-point domains.
- Nmap reported a Linux 3.X–4.X fingerprint, but no authoritative OS fact is available.
- Greenbone reported zero actionable findings matching this host IP; this does not prove the host is vulnerability-free.

### Inferences

- The hostname, certificate identity, ASUS-related DNS domains, and canonical role strongly support an ASUS RT-AC86U-class AiMesh node.
- The device likely runs embedded Linux-based router firmware, but the exact firmware and OS version cannot be determined from the supplied evidence.

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
