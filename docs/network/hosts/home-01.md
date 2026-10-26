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

- Assessed: `2026-10-22T13:00:41+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:02:04`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Home Assistant OS 18.2**
- Manual review required: **No**

### Assessment summary

Home Assistant OS 18.2 virtual machine home-01, running as QEMU VM204 on PROXMOX. It exposes a corroborated aiohttp HTTP service on TCP/80; no actionable Greenbone findings matched the current IP.

### Confirmed facts

- The canonical estate identifies home-01 as a Home Assistant OS 18.2 VM, VM204 on PROXMOX.
- The Proxmox enrichment identifies the guest type as QEMU and the VM name as home-01.
- The device is online at 192.168.2.60 with hostname home-01.jameshouse and DHCP hostname homeassistant.
- TCP port 80 is open and is identified with corroborated evidence as aiohttp, Python 3.14.3.
- TCP port 111 is open; its Nmap service label was omitted.
- Greenbone reported zero actionable findings matching the current IP in the supplied scan.

### Inferences

- The device identity is consistent with a Home Assistant virtual appliance.
- Nmap fingerprinting is broadly consistent with a Linux-based platform, but does not establish an exact kernel or operating-system version.
- The fixed locally administered MAC address is consistent with a virtual-machine network interface.

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
