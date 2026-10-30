# komodo-01

> Persistent private host record. Do not store passwords, API tokens, recovery keys, full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `komodo-01` |
| Address | `192.168.2.58` |
| Type | lxc |
| Role | Komodo container-management control-plane host, CT104 on PROXMOX; Docker, MongoDB and Komodo Core commissioned; application backup and isolated restore validated |
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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-29T16:03:23+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:01:04`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

komodo-01 is CT104, a Proxmox LXC container running Debian GNU/Linux 13 (trixie). It serves as the Komodo container-management control-plane host, with Docker, MongoDB and Komodo Core commissioned. OpenSSH 10.0p2 is exposed on TCP/22 and TCP/9100 is open. No actionable Greenbone findings match the current IP; nine updates are available, including zero security updates.

### Confirmed facts

- The canonical device name is komodo-01.
- The device is an LXC guest, CT104, hosted on PROXMOX.
- The documented role is Komodo container-management control-plane host.
- Authoritative Zabbix Agent 2 evidence identifies the OS as Debian GNU/Linux 13 (trixie) on x86_64.
- Docker, MongoDB and Komodo Core are documented as commissioned.
- TCP/22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4 with protocol 2.0.
- TCP/9100 is open; its Nmap service label is omitted.
- Greenbone reports zero actionable findings matching 192.168.2.58.
- Patch telemetry reports nine updates available, zero security updates available, and no reboot required.
- The bounded Loki sample contains network-connectivity wait-online error and timeout messages.

### Inferences

- The host is a managed application/control-plane server rather than a general-purpose end-user device.
- Its platform is a Debian-based Linux environment running inside Proxmox LXC.
- The device identity is corroborated by canonical estate data, Proxmox inventory, hostname, and authoritative OS telemetry.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-30T16:35:08+00:00`
- Pending updates: **9**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-24T07:18:14+01:00`
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
