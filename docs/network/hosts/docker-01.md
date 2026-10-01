# docker-01

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `docker-01` |
| Address | `192.168.2.220` |
| Type | physical |
| Role | Raspberry Pi 4 BirdNET-Go Docker host |
| Managed by Ansible | Yes |
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
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `d8:3a:dd:5a:51:44`
- Observed IP address(es): `192.168.2.220`
- Connections: **37**
- Traffic sent: **69.0 KiB**
- Traffic received: **2.6 MiB**
- Top services: `ssl` (33), `http` (2), `dhcp` (1), `dns` (1)
- Top destination ports: `tcp/443` (33), `tcp/80` (2), `udp/67` (1), `udp/5353` (1)

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

- Assessed: `2026-10-01T10:04:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `d8:3a:dd:5a:51:44`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Raspberry Pi 4 physical host running the BirdNET-Go Docker workload. Nmap identifies a Linux platform; exact distribution and version are not established. SSH, HTTP on 8080, RPC bind, and port 9100 are exposed. Patch telemetry reports 16 security updates and 131 total updates available; no matching actionable Greenbone findings were reported, which does not prove the host is secure.

### Confirmed facts

- The canonical estate record identifies this device as physical host docker-01 and assigns it the role “Raspberry Pi 4 BirdNET-Go Docker host”.
- The inventory vendor and Nmap vendor are Raspberry Pi Trading.
- The device hostname is docker-01.jameshouse, with DHCP hostname docker-01, at 192.168.2.220.
- Nmap completed OS detection and reported Linux matches, including Linux 4.15–5.19, with 96% accuracy.
- OpenSSH 10.0p2 Debian 7+deb13u4 is directly reported on TCP port 22.
- A Golang net/http server is reported on TCP port 8080.
- TCP ports 111, 9100, and 22 are reported open; port 9100 is tentatively labeled jetdirect by Nmap.
- Patch telemetry reports 16 security updates and 131 total updates available, with no reboot required.
- Greenbone reported zero matching actionable findings for this current IP.

### Inferences

- The host is a Linux-based Raspberry Pi system, consistent with the canonical Raspberry Pi 4 role and Nmap fingerprint.
- The exact operating-system distribution, release, and kernel version cannot be established from the supplied evidence.
- The exposed services are consistent with a managed infrastructure or Docker host, but service exposure alone does not establish the function of each port.

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
