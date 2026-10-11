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

- Assessed: `2026-10-08T11:05:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:02:04`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Home Assistant OS 18.2**
- Manual review required: **No**

### Assessment summary

Home Assistant OS 18.2 virtual machine home-01, hosted as QEMU VM204 on PROXMOX. The host exposes a corroborated aiohttp HTTP service on TCP/80; TCP/111 is also open. No matching actionable Greenbone findings were reported, but this is not proof of full vulnerability coverage.

### Confirmed facts

- The canonical estate identifies home-01 as a Home Assistant OS 18.2 VM204 on PROXMOX.
- The Proxmox cluster API identifies the guest as a QEMU VM named home-01 with VMID 204 on node PROXMOX.
- The DHCP hostname and inventory hostname are homeassistant and home-01.jameshouse, respectively.
- The VM has IP address 192.168.2.60 and MAC address 02:00:00:00:02:04.
- TCP/80 is open and is identified with corroborated evidence as aiohttp 3.14.3 using Python 3.14.
- TCP/111 is open; its Nmap service label was omitted.
- Greenbone reported zero actionable findings matching the current IP in the supplied scan result.
- No authoritative OS record is available in the authoritative_os field.

### Inferences

- The device identity is consistent with a Home Assistant virtual appliance.
- The Nmap fingerprint is broadly consistent with a Linux-based platform, but does not establish a more precise kernel or operating-system version.
- The locally administered MAC address is consistent with a VM-assigned address.

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
