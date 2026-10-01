# Proxmox-2

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `Proxmox-2` |
| Address | `192.168.2.71` |
| Type | physical |
| Role | Proxmox VE cluster node 2; former network-discovery source retained for rollback/history |
| Managed by Ansible | Yes |
| State | Active |

## Network identity
- MAC address:
- Vendor/OUI:
- Hostname / DHCP name:
- VLAN / network:
- Physical location:

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
- MAC identity: `00:1a:9f:0c:30:3b`
- Observed IP address(es): `192.168.2.71`
- Connections: **361**
- Traffic sent: **38.7 KiB**
- Traffic received: **1.2 MiB**
- Top services: `ntp` (343), `ssl` (10), `http` (5)
- Top destination ports: `udp/123` (343), `tcp/443` (10), `tcp/80` (5), `tcp/111` (2), `tcp/2049` (1)

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

- Assessed: `2026-10-01T10:02:06+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:1a:9f:0c:30:3b`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Proxmox-2 is a managed physical Proxmox VE cluster node. Evidence supports a Linux-based host with OpenSSH and a Proxmox REST API service; the exact OS and version are not established. No matching Greenbone findings were reported, which does not prove the host is vulnerability-free.

### Confirmed facts

- The canonical estate record identifies the device as Proxmox-2, a physical Proxmox VE cluster node 2.
- The host is online at 192.168.2.71 and has hostname proxmox-2.jameshouse.
- The host exposes OpenSSH 10.0p2 Debian 7+deb13u4 on TCP port 22.
- Nmap reports Linux as the operating-system family with 97% accuracy for Linux 4.15–5.19.
- Nmap reports a Proxmox Virtual Environment REST API service on TCP port 3128, identified as version 3.0.
- TCP ports 111 and 9100 were reported open; their service identities are not fully corroborated.
- Greenbone reported zero actionable findings matching the current IP.
- Inventory reports the MAC vendor as A-Link.

### Inferences

- The host is likely a Linux-based Proxmox virtualization server.
- The Debian package suffix in the OpenSSH banner is consistent with a Debian-family userspace, but it does not establish the complete operating system or Proxmox version.

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
