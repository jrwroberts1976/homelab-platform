# media-01

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `media-01` |
| Address | `192.168.2.195` |
| Type | physical |
| Role | Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target |
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
- MAC identity: `2c:cf:67:30:be:1f`
- Observed IP address(es): `192.168.2.195`
- Connections: **584**
- Traffic sent: **374.9 KiB**
- Traffic received: **1.8 MiB**
- Top services: `ssl` (257), `http` (96), `dns` (2), `dhcp` (1)
- Top destination ports: `tcp/443` (482), `tcp/80` (96), `udp/5353` (2), `udp/67` (1), `udp/3702` (1)

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
- MAC identity: `2c:cf:67:30:be:1f`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

media-01 is a confirmed Raspberry Pi physical host serving as the Kodi endpoint and primary Proxmox NFS backup target. SSH, Samba, and TCP/9100 are open. Linux-based operation is suggested, but no exact OS was identified. No actionable Greenbone findings matched this IP; 96 total updates are available, including 0 reported security updates.

### Confirmed facts

- The canonical estate record identifies media-01 as a physical Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target.
- The host is managed by Ansible and is online at 192.168.2.195.
- The inventory vendor is Raspberry Pi (Trading), and the MAC address is 2c:cf:67:30:be:1f.
- The hostname is media-01.jameshouse and the DHCP hostname is media-01.
- TCP port 22 is open and identified as OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP port 445 is open and identified as Samba smbd version 4.
- TCP port 9100 is open; Nmap labels the service jetdirect, but no product or version is provided.
- Nmap reported no OS matches and marked OS evidence as missing.
- Greenbone reported zero actionable findings matching 192.168.2.195; this does not establish that the host is vulnerability-free.
- Patch telemetry reports 96 updates available, 0 security updates available, and no reboot required.

### Inferences

- The host is likely running an embedded Linux-based Raspberry Pi environment, based on the Raspberry Pi identity and Nmap's Linux-related service metadata.
- The OpenSSH and Samba services are consistent with a managed Linux file/media host, but service presence alone does not prove the full host role or operating system.
- The TCP/9100 service may be printer-related, but its function is not confirmed by the supplied evidence.

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
