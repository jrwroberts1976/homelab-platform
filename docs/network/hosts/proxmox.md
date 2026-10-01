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

- Assessed: `2026-10-01T11:33:08+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `80:e8:2c:1c:55:d2`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Proxmox VE / Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

PROXMOX is the managed physical Proxmox VE cluster node and cluster anchor at 192.168.2.70. Authoritative Zabbix inventory identifies Proxmox VE on Debian GNU/Linux 13 with kernel 7.0.14-17-pve. Open services include SSH, the Proxmox Virtual Environment REST API, and ports 111 and 9100 with Nmap labels omitted.

### Confirmed facts

- The canonical estate identifies this device as PROXMOX, a physical Proxmox VE cluster node 1 and cluster anchor.
- The device is managed by Ansible.
- The vendor is Hewlett Packard.
- The authoritative OS is Proxmox VE / Debian GNU/Linux 13 (trixie).
- The authoritative architecture is x86_64 and the kernel is 7.0.14-17-pve.
- TCP port 22 is open and provides OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 3128 is open and is identified as the Proxmox Virtual Environment REST API, version 3.0.
- TCP ports 111 and 9100 are open; their Nmap service labels were omitted.
- Greenbone reported zero actionable findings matching the current IP; this does not establish that the host is vulnerability-free or fully scanned.

### Inferences

- The host functions as a virtualization infrastructure server and likely provides Proxmox management services.
- Port 9100 may support monitoring or printing-related communication, but its service identity is not established by the supplied evidence.

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
