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

- Assessed: `2026-10-01T11:14:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:01:05`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

zabbix-01 is an online Debian 13 LXC container on PROXMOX (CT105), serving the Zabbix monitoring platform. SSH, Nginx on ports 80/8080, and port 9100 are open. Eight security updates are available and failed SSH authentication attempts were sampled in the last 24 hours.

### Confirmed facts

- The canonical estate identity is zabbix-01, a Zabbix monitoring platform in LXC container CT105 on PROXMOX.
- The container is hosted on PROXMOX node PROXMOX with VMID 105.
- Authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie) on x86_64.
- The host is online at 192.168.2.59.
- Open TCP ports include 22 with OpenSSH 10.0p2 Debian 7+deb13u4, 80 with Nginx, 8080 with Nginx, and 9100 with a tentative JetDirect service label.
- Zabbix Server, Agent 2, Nginx, PostgreSQL, and TimescaleDB are documented as active in the canonical estate record.
- Patching telemetry reports 8 security updates and 36 total updates available, with no reboot required.
- Greenbone reported zero matching actionable findings for the current IP; this does not establish that the host is vulnerability-free.

### Inferences

- The device is best classified as a managed Linux server workload rather than a physical network appliance.
- The port 9100 service may be related to a metrics or print-style protocol, but its function is not established by the supplied evidence.

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
