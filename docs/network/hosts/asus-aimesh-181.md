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
- Summary generated: `2026-10-15T00:20:55+01:00`
- MAC identity: `04:d4:c4:b8:52:28`
- Observed IP address(es): `192.168.2.181`
- Connections: **7,106**
- Traffic sent: **7.0 MiB**
- Traffic received: **518.6 KiB**
- Top services: `ssl` (5), `ntp` (4), `dhcp` (1)
- Top destination ports: `tcp/7788` (6523), `udp/9999` (573), `tcp/443` (5), `udp/123` (4), `udp/67` (1)

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

- Assessed: `2026-10-15T13:01:53+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:b8:52:28`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Identified as the documented ASUS AiMesh wireless mesh node at 192.168.2.181. It exposes Dropbear SSH and HTTPS-alt management services; the available OS fingerprint is inconsistent and does not support a precise OS identification.

### Confirmed facts

- Canonical estate identity is ASUS AiMesh node.
- Documented role is Wireless mesh node.
- Hostname and DHCP hostname are RT-AC86U-5228.
- Vendor is ASUSTek Computer.
- IP address is 192.168.2.181 and MAC address is 04:d4:c4:b8:52:28.
- TCP ports 22, 80, and 8443 are open.
- Port 22 is corroborated as Dropbear sshd, protocol 2.0.
- Port 8443 is corroborated as HTTPS-alt over TLS.
- The TLS certificate identifies RT-AC86U-5228 and includes ASUS router, repeater, and access-point names.
- Greenbone reports zero matching actionable findings for the current IP; this is not proof that the host is vulnerability-free.

### Inferences

- The device is consistent with embedded ASUS router or mesh-node firmware.
- The Nmap fingerprint suggests a Linux-family embedded implementation, but its Android/Linux alternatives are not sufficiently reliable to identify an exact OS.
- ASUS router-management services and certificate naming are consistent with the documented AiMesh role.

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
