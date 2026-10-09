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
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `2c:cf:67:30:be:1f`
- Observed IP address(es): `192.168.2.195`
- Connections: **693**
- Traffic sent: **724.8 KiB**
- Traffic received: **3.9 MiB**
- Top services: `ssl` (257), `http` (99), `dhcp` (1)
- Top destination ports: `tcp/443` (496), `tcp/80` (99), `udp/1900` (97), `udp/67` (1)

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

- Assessed: `2026-10-08T14:00:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `2c:cf:67:30:be:1f`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

media-01 is a managed physical Raspberry Pi 5 running authoritative Debian GNU/Linux 13 (trixie). It serves SSH and Samba, and is documented as the Kodi endpoint and primary Proxmox NFS backup target. No actionable Greenbone findings or pending updates are reported.

### Confirmed facts

- The device hostname is media-01 and its IP address is 192.168.2.195.
- The device is a physical host managed by Ansible.
- The canonical device role is Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target.
- The vendor is Raspberry Pi (Trading).
- The authoritative operating system is Debian GNU/Linux 13 (trixie), with aarch64 architecture and kernel 6.18.50+rpt-rpi-2712.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 445 is open and provides corroborated Samba smbd version 4.
- TCP port 9100 is open; its Nmap service label was omitted.
- Greenbone reports zero matching actionable findings for the current host IP.
- Patch telemetry reports zero available updates and no reboot required.

### Inferences

- The host functions as both a media endpoint and network file-service target, consistent with its documented estate role and exposed SSH/Samba services.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-09T21:57:24+01:00`
- Pending updates: **3**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-08T06:40:27+01:00`
- Patch state: **Healthy**

> Automatic reboot remains disabled by policy; reboot-required state is reported for controlled maintenance.
<!-- END AUTO:PATCHING -->

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
