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

- Assessed: `2026-10-01T11:32:24+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `2c:cf:67:30:be:1f`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

media-01 is a managed physical Raspberry Pi 5 running authoritative Debian GNU/Linux 13 (trixie) on aarch64. It serves SSH, Samba, and an open port 9100. No matching actionable Greenbone findings were reported; 96 general updates are available and failed SSH authentication samples were observed.

### Confirmed facts

- The canonical estate identity is media-01, a physical device managed by Ansible.
- The canonical role is Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target.
- The vendor is Raspberry Pi (Trading), with MAC address 2c:cf:67:30:be:1f.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), aarch64, with kernel 6.18.39+rpt-rpi-2712.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 445 is open and provides corroborated Samba smbd version 4.
- TCP port 9100 is open; its Nmap service label was omitted.
- No actionable Greenbone findings currently match this host IP.
- Patch telemetry reports 96 updates available, 0 security updates available, and no reboot required.
- The bounded Loki sample contains failed SSH authentication events, including attempts involving unknown users and root.

### Inferences

- The device is a Raspberry Pi 5 running a Debian-based Linux system used for media playback and network backup duties, consistent with its canonical estate role.
- Samba and SSH indicate file-sharing and remote-administration capabilities; the open port 9100 may support printing or another raw TCP service, but the supplied evidence does not identify its function.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-08T09:24:30+01:00`
- Pending updates: **0**
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
