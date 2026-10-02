# home-01

> Persistent private host record. Do not store passwords, API tokens, recovery keys, full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `home-01` |
| Address | `192.168.2.60` |
| Type | vm |
| Role | Home Assistant OS 18.2, VM204 on PROXMOX |
| Managed by Ansible | No |
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
- Summary generated: `2026-10-03T00:22:04+01:00`
- MAC identity: `02:00:00:00:02:04`
- Observed IP address(es): `192.168.2.60`
- Connections: **9,061**
- Traffic sent: **9.0 MiB**
- Traffic received: **12.7 MiB**
- Top services: `http` (6023), `ssl` (2305), `ntp` (69), `dns` (66), `dhcp` (1)
- Top destination ports: `tcp/35580` (3765), `tcp/57992` (2062), `tcp/853` (1490), `tcp/443` (865), `udp/1900` (288), `tcp/33657` (177)

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
- MAC identity: `02:00:00:00:02:04`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Home Assistant OS 18.2**
- Manual review required: **No**

### Assessment summary

Confirmed Home Assistant OS 18.2 VM204 on Proxmox, observed at 192.168.2.60. HTTP/aiohttp and rpcbind are open; Nmap identifies a Linux-family stack. Greenbone has no matching actionable findings, while patch telemetry is unavailable and should be reviewed.

### Confirmed facts

- The canonical estate record identifies this device as home-01, a VM running Home Assistant OS 18.2, Home Assistant Core 2026.9.2, VM204 on PROXMOX.
- The Proxmox enrichment identifies guest type qemu, name home-01, and VMID 204.
- The device is online at 192.168.2.60 with MAC address 02:00:00:00:02:04.
- The router reports DHCP hostname homeassistant; inventory and Nmap report home-01.jameshouse.
- TCP port 80 is open and directly identified as aiohttp 3.14.3 with Python 3.14.
- TCP port 111 is open and identified as rpcbind.
- Nmap reports Linux OS matches, primarily Linux 4.15–5.19, with an OpenWrt 22.03 match at lower confidence.
- Greenbone reports zero matching actionable findings for the current IP; this is not proof that the host is vulnerability-free.
- Patch telemetry is unavailable, with no update or reboot status reported.

### Inferences

- The host is likely a Home Assistant appliance workload rather than a general-purpose server, based on the authoritative estate role and Home Assistant-specific DNS activity.
- The Nmap Linux results are consistent with the documented Home Assistant OS VM but do not establish an exact kernel version.

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
