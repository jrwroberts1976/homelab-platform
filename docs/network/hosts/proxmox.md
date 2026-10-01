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

- Assessed: `2026-10-01T11:19:21+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `80:e8:2c:1c:55:d2`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Proxmox VE / Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

PROXMOX is a managed physical Proxmox VE cluster node at 192.168.2.70, running authoritative Debian 13 (trixie) OS facts. SSH, rpcbind, the Proxmox REST API, and a JetDirect-labeled TCP service are exposed; no matching actionable Greenbone findings were reported.

### Confirmed facts

- Canonical estate identifies the device as PROXMOX, a physical Proxmox VE cluster node 1 and cluster anchor.
- The device is managed by Ansible.
- The hostname is proxmox.jameshouse and the telemetry hostname is proxmox.
- The vendor is Hewlett Packard.
- The authoritative OS is Proxmox VE / Debian GNU/Linux 13 (trixie) on x86_64, with kernel 7.0.14-17-pve.
- The device is online at 192.168.2.70.
- TCP ports 22, 111, 3128, and 9100 are open.
- OpenSSH 10.0p2 Debian 7+deb13u4 is identified on TCP port 22.
- The Proxmox Virtual Environment REST API, version 3.0, is identified on TCP port 3128.
- TCP port 111 is labeled rpcbind and TCP port 9100 is labeled jetdirect.
- Greenbone reported zero matching actionable findings for the current IP; this does not prove the host is vulnerability-free.
- Patch telemetry is unavailable.

### Inferences

- The host functions as a Proxmox virtualization server and cluster anchor based on the canonical estate role and authoritative identity.
- The JetDirect label on TCP 9100 does not by itself establish that the host is a printer or print server.
- The exposed rpcbind service may indicate RPC-related functionality, but its specific host function is not established by the supplied evidence.

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
