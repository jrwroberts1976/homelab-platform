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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-29T16:03:23+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `2c:cf:67:30:be:1f`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

media-01 is a managed Raspberry Pi 5 running Debian GNU/Linux 13 (trixie), serving as the Kodi endpoint and primary Proxmox NFS backup target. Open services include SSH, HTTPS via nginx, and Samba; TCP/9100 is also open. No matching actionable Greenbone findings were reported.

### Confirmed facts

- The canonical device name is media-01.
- The device is a physical host managed by Ansible.
- The canonical role is Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target.
- The vendor is Raspberry Pi (Trading).
- Authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie), kernel 6.18.50+rpt-rpi-2712, and aarch64 architecture.
- TCP/22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP/443 is open and provides corroborated nginx over TLS.
- TCP/445 is open and provides corroborated Samba smbd version 4.
- TCP/9100 is open; its service label was omitted.
- Greenbone reported zero matching actionable findings for this host IP.
- Patch telemetry reports 31 available updates, zero security updates, and no reboot required.

### Inferences

- The device identity is consistent across the canonical estate record, hostname, vendor data, and authoritative host inventory.
- The host functions as a Linux-based network storage and media endpoint, consistent with its documented estate role and exposed services.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-29T23:28:17+00:00`
- Pending updates: **29**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-28T06:02:07+00:00`
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
