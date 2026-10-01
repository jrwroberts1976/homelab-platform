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

- Assessed: `2026-10-01T11:19:27+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:1a:9f:0c:30:3b`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Proxmox VE / Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Proxmox-2 is a managed physical Proxmox VE cluster node at 192.168.2.71. Authoritative Zabbix Agent 2 facts identify Proxmox VE on Debian GNU/Linux 13; SSH, rpcbind, the Proxmox REST API, and JetDirect-labeled TCP services are open. No matching actionable Greenbone findings were reported.

### Confirmed facts

- Canonical estate identifies the device as Proxmox-2, a physical Proxmox VE cluster node 2.
- The device is managed by Ansible.
- Authoritative OS inventory reports Proxmox VE / Debian GNU/Linux 13 (trixie), x86_64, with kernel 7.0.14-17-pve.
- The device is online at 192.168.2.71 with MAC address 00:1a:9f:0c:30:3b.
- TCP ports 22, 111, 3128, and 9100 are open.
- Port 22 provides OpenSSH 10.0p2 Debian 7+deb13u4.
- Port 3128 is identified as the Proxmox Virtual Environment REST API, version 3.0.
- Greenbone reported zero actionable findings matching the current IP; this does not establish that the host is vulnerability-free.
- Patch telemetry is unavailable.

### Inferences

- The device functions as a Proxmox VE virtualization cluster node and likely hosts or manages virtual machines and containers, based on its canonical role and Proxmox service evidence.
- The A-Link vendor value may describe the detected network hardware rather than the complete system vendor.

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
