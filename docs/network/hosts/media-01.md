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
- Summary generated: `2026-10-26T00:22:36+00:00`
- MAC identity: `2c:cf:67:30:be:1f`
- MAC-attributable originated connections: **none observed in this window**

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

- Assessed: `2026-10-22T16:05:03+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `2c:cf:67:30:be:1f`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

media-01 is a managed Raspberry Pi 5 running authoritative Debian GNU/Linux 13 (trixie) on aarch64. It serves as a Kodi endpoint and primary Proxmox NFS backup target, with SSH, HTTPS/nginx, Samba, and an additional open TCP port 9100. No actionable Greenbone findings matched the current IP; sampled logs contain media-device, audio, and authentication errors.

### Confirmed facts

- The canonical device name is media-01 and it is a physical host.
- The documented role is Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target.
- The vendor is Raspberry Pi (Trading).
- The authoritative OS is Debian GNU/Linux 13 (trixie), with aarch64 architecture and kernel 6.18.50+rpt-rpi-2712.
- The host is managed by Ansible.
- TCP ports 22, 443, 445, and 9100 are open.
- TCP 22 provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP 443 provides corroborated nginx over TLS.
- TCP 445 provides corroborated Samba smbd version 4.
- No actionable Greenbone findings matched 192.168.2.195 in the supplied report.
- The bounded 24-hour Loki sample contains media-device, audio, HTTP parsing, and authentication-related warning or error samples.

### Inferences

- The host is suitable for the documented media-playback and backup roles based on its canonical estate record and observed services.
- The host was recently reachable through DHCP/router telemetry, although inventory telemetry reports it as offline.
- The sampled log messages merit operational review, but the bounded sample does not establish an incident or overall host health.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-22T05:35:26+01:00`
- Pending updates: **22**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-21T06:54:11+01:00`
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
