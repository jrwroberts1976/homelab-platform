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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `02:00:00:00:01:04`
- Observed IP address(es): `192.168.2.58`
- Connections: **54**
- Traffic sent: **76.2 KiB**
- Traffic received: **355.1 KiB**
- Top services: `ssl` (54)
- Top destination ports: `tcp/443` (54)

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
- MAC identity: `02:00:00:00:01:04`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

komodo-01 is the documented Komodo control-plane LXC container CT104 on PROXMOX. It presents a Linux network stack with SSH/OpenSSH 10.0p2 on Debian-packaged builds and an additional open TCP port 9100 with an unverified JetDirect label. Eight security updates and 36 total updates are available; unattended upgrades are disabled. No matching actionable Greenbone findings were reported, which does not establish vulnerability-free status.

### Confirmed facts

- The canonical estate record identifies this device as komodo-01, an LXC container managed by Ansible.
- The documented role is the Komodo container-management control-plane host, CT104 on PROXMOX.
- The Proxmox cluster API identifies guest type lxc, name komodo-01, node PROXMOX, and VMID 104.
- The host is online at 192.168.2.58 and has hostname komodo-01.jameshouse.
- TCP port 22 is open and directly identified as OpenSSH 10.0p2, protocol 2.0, with version text Debian 7+deb13u4.
- TCP port 9100 is open; Nmap labels the service jetdirect, but provides no product or version.
- Nmap OS fingerprinting reports Linux matches, primarily Linux kernel ranges 4.15–5.19, with additional lower-confidence alternatives.
- No matching actionable Greenbone findings were reported for 192.168.2.58.
- Patch telemetry reports 8 security updates and 36 total updates available, with unattended upgrades disabled and no reboot required.

### Inferences

- The host is best classified as a Linux-based containerized server rather than a physical appliance or consumer IoT device.
- The Debian text in the OpenSSH package version is consistent with Debian-based userland, but the exact operating system and version are not established.
- The Nmap JetDirect label on port 9100 is tentative and does not establish that this host provides printer functionality.

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
