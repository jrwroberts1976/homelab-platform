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

- Assessed: `2026-10-01T11:13:34+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `2c:cf:67:30:be:1f`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

media-01 is a Raspberry Pi 5 running authoritative Debian GNU/Linux 13 (trixie). It serves as a Kodi endpoint and primary Proxmox NFS backup target, with SSH, Samba, and TCP/9100 exposed. No matching actionable Greenbone findings were reported; 96 non-security updates are available.

### Confirmed facts

- The canonical device name is media-01.
- The device is documented as physical and managed by Ansible.
- The canonical role is Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target.
- The vendor is Raspberry Pi (Trading).
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture aarch64, with kernel 6.18.39+rpt-rpi-2712.
- TCP port 22 is open and identified as OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 445 is open and identified as Samba smbd 4.
- TCP port 9100 is open; Nmap labels the service jetdirect without product or version details.
- Greenbone reported zero matching actionable findings for the current IP.
- Patch telemetry reports zero security updates, 96 total updates, and no reboot required.

### Inferences

- The platform is consistent with a Raspberry Pi running Debian Linux.
- The exposed Samba service is consistent with network file-sharing duties, but the scan alone does not establish its exact use.

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
