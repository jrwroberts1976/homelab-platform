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
- Summary generated: `2026-10-21T00:24:48+01:00`
- MAC identity: `04:d4:c4:c1:62:38`
- Observed IP address(es): `192.168.2.218`
- Connections: **21,544**
- Traffic sent: **6.9 MiB**
- Traffic received: **483.7 KiB**
- Top services: `ssl` (5), `ntp` (1)
- Top destination ports: `udp/7788` (15293), `tcp/7788` (5908), `udp/9999` (330), `tcp/443` (5), `udp/123` (1)

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

- Assessed: `2026-10-15T13:01:53+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:c1:62:38`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

ASUS AiMesh wireless mesh node identified as an RT-AC86U-family device. It exposes Dropbear SSH and web management services; the exact firmware/OS is not established.

### Confirmed facts

- The canonical estate role is ASUS AiMesh node / Wireless mesh node.
- The DHCP and inventory hostname is RT-AC86U-6238.
- The recorded vendor is ASUSTek Computer.
- TCP/22 is open and provides corroborated Dropbear SSH service, protocol 2.0.
- TCP/80 is open; its Nmap service label was omitted.
- TCP/8443 is open and is corroborated as HTTPS-alt.
- The TLS certificate subject identifies RT-AC86U-6238 and includes ASUS router/repeater management DNS names.
- Greenbone reported zero actionable findings matching the current host IP; this is not proof that the host is vulnerability-free.

### Inferences

- The device is very likely an ASUS RT-AC86U-family AiMesh node, supported by the hostname, canonical role, vendor, and TLS certificate.
- The platform is likely embedded ASUS router firmware built on a Linux-derived stack; Nmap OS matches are not sufficient to establish an exact OS or firmware version.

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
