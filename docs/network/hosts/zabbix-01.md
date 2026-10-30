# zabbix-01

> Persistent private host record. Do not store passwords, API tokens, recovery keys, full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `zabbix-01` |
| Address | `192.168.2.59` |
| Type | lxc |
| Role | Zabbix monitoring platform, CT105 on PROXMOX |
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
- MAC identity: `02:00:00:00:01:05`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

zabbix-01 is CT105, an Ansible-managed Proxmox LXC running the Zabbix monitoring platform on Debian GNU/Linux 13. Zabbix services, PostgreSQL/TimescaleDB, Nginx, SSH, and a Prometheus-compatible metrics endpoint are present. No actionable Greenbone findings matched the current IP; seven updates are available, including security updates reported as zero.

### Confirmed facts

- The canonical estate identifies the device as zabbix-01, a Zabbix monitoring platform in CT105 on PROXMOX.
- Proxmox identifies the guest as an LXC container named zabbix-01 with VMID 105.
- Authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie), x86_64, with kernel 7.0.14-23-pve.
- OpenSSH 10.0p2 on Debian is exposed on TCP port 22.
- Nginx is exposed on TCP ports 80 and 443, with TLS on port 443.
- TCP port 9100 is open; its Nmap service label was omitted.
- The TLS certificate for port 443 is for zabbix.home.jrwroberts.co.uk.
- Greenbone reports zero actionable findings matching this current IP.
- Patch telemetry reports seven updates available, zero security updates available, and no reboot required.

### Inferences

- The device is a managed Linux server container dedicated to monitoring infrastructure.
- The HTTPS service is likely associated with the Zabbix web interface based on the canonical role and certificate hostname.
- Port 9100 is consistent with an exposed metrics endpoint, but the supplied evidence does not provide its service label.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-30T14:02:06+00:00`
- Pending updates: **7**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-24T07:51:04+01:00`
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
