# asus-router

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `asus-router` |
| Address | `192.168.2.1` |
| Type | network |
| Role | ASUS RT-AC86U router, DHCP, AiMesh controller and OpenVPN remote-access endpoint |
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
- Summary generated: `2026-10-05T00:23:30+01:00`
- MAC identity: `24:4b:fe:5e:cc:c8`
- Observed IP address(es): `192.168.2.1`
- Connections: **1,605**
- Traffic sent: **7.1 MiB**
- Traffic received: **1020 B**
- Top services: `dhcp` (20), `http` (8)
- Top destination ports: `udp/9999` (574), `udp/5514` (331), `udp/7788` (275), `udp/1900` (240), `udp/51356` (144), `udp/68` (20)

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

- Assessed: `2026-10-01T10:03:30+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `24:4b:fe:5e:cc:c8`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

ASUS RT-AC86U network device at 192.168.2.1, serving as the documented router, DHCP server, AiMesh controller, and OpenVPN endpoint. Embedded firmware platform is likely, but the exact OS is not identified by the supplied evidence.

### Confirmed facts

- The canonical estate record identifies the device as an ASUS RT-AC86U named asus-router.
- Its documented kind is network, with the role of router, DHCP server, AiMesh controller, and OpenVPN remote-access endpoint.
- The device is online at 192.168.2.1 with hostname _gateway.
- The inventory vendor is ASUSTek Computer.
- TCP port 22 exposes Dropbear sshd protocol 2.0.
- TCP ports 53, 80, and 8443 are reported open; port 8443 has an HTTPS certificate for jrwroberts1976.asuscomm.com.
- Nmap OS identification is incomplete and reports os_evidence_missing.
- Greenbone reports zero actionable findings matching this current IP; this does not establish that the host is vulnerability-free or fully scanned.

### Inferences

- The device is consistent with an embedded router firmware platform.
- The Dropbear SSH service and web services are consistent with network-device firmware, but do not identify an exact OS or firmware version.

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
