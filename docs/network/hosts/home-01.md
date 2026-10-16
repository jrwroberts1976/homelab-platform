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
- Summary generated: `2026-10-16T00:21:46+01:00`
- MAC identity: `02:00:00:00:02:04`
- Observed IP address(es): `192.168.2.60`
- Connections: **8,826**
- Traffic sent: **9.0 MiB**
- Traffic received: **121.9 MiB**
- Top services: `http` (6042), `ssl` (2353), `ntp` (72), `dns` (28), `dhcp` (1)
- Top destination ports: `tcp/43425` (5899), `tcp/853` (1536), `tcp/443` (858), `udp/1900` (288), `tcp/80` (143), `udp/123` (72)

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

- Assessed: `2026-10-15T12:02:16+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:02:04`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Home Assistant OS 18.2**
- Manual review required: **No**

### Assessment summary

Home Assistant OS 18.2 running as QEMU VM204 on PROXMOX, identified as home-01/homeassistant at 192.168.2.60. Port 80 serves corroborated aiohttp/Python 3.14.3; port 111 is open. No matching actionable Greenbone findings were reported, which does not establish that the host is vulnerability-free.

### Confirmed facts

- Canonical estate identifies home-01 as a VM running Home Assistant OS 18.2, Home Assistant Core 2026.9.2, on PROXMOX as VM204.
- Proxmox inventory identifies the guest type as QEMU and the VM name as home-01.
- The host is online at 192.168.2.60 with MAC address 02:00:00:00:02:04.
- DHCP and router records identify the hostname as homeassistant.
- TCP port 80 is open and provides corroborated HTTP service evidence for aiohttp, Python 3.14.3.
- TCP port 111 is open; its Nmap service label was omitted.
- Nmap reported Linux fingerprint matches, including Linux 4.15–5.19, but these are fingerprint results rather than authoritative OS facts.
- Greenbone reported zero actionable findings matching the current host IP in the supplied scan.

### Inferences

- The device identity is consistent with the documented Home Assistant virtual appliance.
- The Nmap Linux results are consistent with the Linux-based Home Assistant OS platform but do not establish a more precise kernel or distribution version.

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
