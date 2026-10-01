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

- Assessed: `2026-10-01T11:14:47+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `d8:3a:dd:5a:51:44`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

docker-01 is a Raspberry Pi 4 physical host running authoritative Debian GNU/Linux 13 (trixie) with Docker-host role. SSH, HTTP on 8080, rpcbind, and JetDirect-labeled TCP/9100 are open. Sixteen security updates are pending; no matching actionable Greenbone findings were reported.

### Confirmed facts

- The canonical estate identity is docker-01, a physical host managed by Ansible.
- Its documented role is Raspberry Pi 4 BirdNET-Go Docker host.
- The vendor is Raspberry Pi Trading and the architecture is aarch64.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie) with kernel 6.18.39+rpt-rpi-v8.
- TCP ports 22, 111, 8080, and 9100 are open.
- OpenSSH 10.0p2 Debian 7+deb13u4 is identified on TCP/22.
- A Golang net/http server is identified on TCP/8080.
- Sixteen security updates and 131 total updates are available; no reboot is required.
- Greenbone reported zero matching actionable findings for the current IP.

### Inferences

- The host is serving as a Linux-based Raspberry Pi infrastructure and container host consistent with its documented estate role.
- The TCP/9100 service is only tentatively labeled JetDirect because no product or version was supplied.
- The sampled container-log errors merit operational review, but the bounded sample does not establish overall host health.

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
