# zabbix-01

> Persistent private host record. Do not store passwords, API tokens, recovery keys, full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `zabbix-01` |
| Address | `192.168.2.59` |
| Type | lxc |
| Role | Zabbix monitoring platform, CT105 on PROXMOX |
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
- MAC identity: `02:00:00:00:01:05`
- Observed IP address(es): `192.168.2.59`
- Connections: **7**
- Traffic sent: **22.5 KiB**
- Traffic received: **33.7 KiB**
- Top services: `ssl` (7)
- Top destination ports: `tcp/443` (7)

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

- Assessed: `2026-10-01T10:02:06+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:01:05`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

zabbix-01 is the documented CT105 Zabbix monitoring container on PROXMOX. It exposes OpenSSH 10.0p2, nginx on ports 80 and 8080, and an unidentified service on port 9100. Evidence confirms a Linux-based environment, but does not support an exact OS identification. Eight security updates are available and unattended upgrades are disabled.

### Confirmed facts

- The canonical estate record identifies this host as zabbix-01, an LXC container CT105 on PROXMOX managed by Ansible.
- The documented role is a Zabbix monitoring platform with PostgreSQL, TimescaleDB, Zabbix Server, Agent 2, and Nginx active.
- The host is online at 192.168.2.59.
- Nmap OS fingerprinting identified Linux matches, primarily Linux 4.15–5.19, with 97% reported accuracy.
- OpenSSH 10.0p2 with Debian 7+deb13u4 is exposed on TCP port 22.
- Nginx is exposed on TCP ports 80 and 8080.
- TCP port 9100 is open and tentatively labelled jetdirect by Nmap, without product evidence.
- Greenbone reported zero actionable findings matching the current host IP; this is not proof that the host is vulnerability-free.
- Patch telemetry reports 8 security updates and 36 total updates available, with no reboot required and unattended upgrades disabled.

### Inferences

- The host is best classified as a Linux-based server container rather than a standalone physical or virtual appliance.
- The Debian-qualified OpenSSH package suggests a Debian-family userland, but the exact distribution and release are not established.
- The Nmap Linux kernel ranges are fingerprint matches and do not establish the running kernel version.

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
