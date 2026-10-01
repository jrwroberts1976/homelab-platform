# PROXMOX

> Persistent private host record. Do not store passwords, API tokens, recovery keys, full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `PROXMOX` |
| Address | `192.168.2.70` |
| Type | physical |
| Role | Proxmox VE cluster node 1 and cluster anchor |
| Managed by Ansible | Yes |
| State | Active |

## Network identity
- MAC address:
- Vendor/OUI:
- Hostname / DHCP name:
- VLAN / network:
- Physical location or hypervisor:
- Stable device identifier:

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
- MAC identity: `80:e8:2c:1c:55:d2`
- Observed IP address(es): `192.168.2.70`
- Connections: **351**
- Traffic sent: **38.1 KiB**
- Traffic received: **828.2 KiB**
- Top services: `ntp` (333), `ssl` (10), `http` (5)
- Top destination ports: `udp/123` (333), `tcp/443` (10), `tcp/80` (5), `tcp/111` (2), `tcp/2049` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->
| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

### Expected flows
- 

### Unexpected or investigated flows
- 

## Internet / DNS activity
Keep only bounded domain/service summaries, not complete browsing history.

| Service / domain family | Example domains | Evidence source | Last observed | Interpretation |
|---|---|---|---|---|
| | | | | |

### Known cloud/service dependencies
- 

### Browsing / application observations
- 

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-01T10:06:08+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `80:e8:2c:1c:55:d2`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

PROXMOX is a Hewlett Packard physical Proxmox VE cluster node and cluster anchor. Linux is strongly indicated, with Debian-packaged OpenSSH observed; the exact host OS and version are not established by the available evidence.

### Confirmed facts

- The canonical estate identifies PROXMOX as a physical Proxmox VE cluster node 1 and cluster anchor.
- The host is managed by Ansible.
- The inventory hostname is proxmox.jameshouse and the vendor is Hewlett Packard.
- Nmap OS detection completed and matched Linux 4.15–5.19 with 97% accuracy.
- OpenSSH 10.0p2 Debian 7+deb13u4 is exposed on TCP port 22.
- TCP port 3128 was identified by Nmap as the Proxmox Virtual Environment REST API, version 3.0.
- TCP ports 111 and 9100 were open; Nmap labeled them rpcbind and jetdirect respectively.
- Greenbone reported zero matching actionable findings for the current IP; this does not prove the host is vulnerability-free or fully scanned.

### Inferences

- The host is likely a Debian-based Proxmox VE system.
- The Nmap Linux result and Debian-packaged OpenSSH support a Linux platform classification.
- The port 9100 label alone is insufficient to infer that this host functions as a printer.

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
