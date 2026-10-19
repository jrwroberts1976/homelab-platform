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

- Assessed: `2026-10-15T15:01:28+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:01:04`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

komodo-01 is the documented Komodo container-management control-plane LXC (CT104) on PROXMOX, running authoritative Debian GNU/Linux 13. SSH is exposed on TCP/22 and TCP/9100 is open. Three security updates are available; no matching actionable Greenbone findings were reported.

### Confirmed facts

- The device hostname is komodo-01.jameshouse and its IP address is 192.168.2.58.
- The canonical estate identity is komodo-01, an LXC container with VMID/CT104 on PROXMOX.
- The documented role is Komodo container-management control-plane host.
- The authoritative OS is Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 7.0.14-23-pve.
- TCP/22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP/9100 is open; its Nmap service label was omitted.
- Three security updates and seven total updates are available; unattended upgrades are enabled and no reboot is required.
- Greenbone reported zero matching actionable findings for this host IP in the supplied report.

### Inferences

- The host is a managed infrastructure system rather than an unidentified consumer or IoT device, based on its authoritative estate record and Proxmox inventory.
- The documented Komodo, Docker, MongoDB, and backup-related services indicate a container-management control-plane workload.
- Pending updates and sampled SSH authentication failures merit operational review; the supplied evidence does not establish a specific vulnerability or compromise.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-19T22:16:41+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-16T10:18:19+01:00`
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
