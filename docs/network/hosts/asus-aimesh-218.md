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

- Assessed: `2026-10-08T12:04:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:c1:62:38`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

ASUS RT-AC86U-class wireless mesh node, identified by the canonical estate role, ASUS vendor data, DHCP hostname, and matching TLS certificate. It exposes Dropbear SSH plus web management ports; the exact embedded OS/firmware is not established.

### Confirmed facts

- The canonical estate identifies this host as an ASUS AiMesh node with the role Wireless mesh node.
- The inventory and Nmap data identify the vendor as ASUSTek Computer.
- The DHCP and inventory hostname is RT-AC86U-6238.
- The TLS certificate identifies the device as RT-AC86U-6238 and includes ASUS router, repeater, and access-point domains.
- TCP port 22 is open and runs Dropbear sshd, protocol 2.0.
- TCP ports 80 and 8443 are open.
- The 8443 service is identified as HTTPS-alt over TLS.
- No authoritative OS fact is available.

### Inferences

- The device is an ASUS RT-AC86U-class router or mesh node operating embedded firmware.
- The available evidence is consistent with a Linux-based embedded platform, but Nmap fingerprint alternatives do not establish an exact kernel or operating system.
- DNS activity involving routerahs.asus.com and fwupdate.asuswrt-merlin.net is consistent with an ASUS router firmware ecosystem, but does not prove a specific firmware build.

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
