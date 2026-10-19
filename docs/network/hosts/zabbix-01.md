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

- Assessed: `2026-10-15T15:01:28+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:01:05`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC container CT105 running the Zabbix monitoring platform. Authoritative inventory identifies Debian 13 on x86_64. SSH and Nginx HTTP/HTTPS services are active; four security updates are pending and Greenbone reports a medium-severity cleartext HTTP finding on port 8080.

### Confirmed facts

- The canonical estate identity is zabbix-01, an LXC container managed by Ansible.
- The container is Zabbix monitoring platform CT105 on PROXMOX.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), x86_64, with kernel 7.0.14-23-pve.
- OpenSSH 10.0p2 Debian 7+deb13u4 is exposed on TCP port 22.
- Nginx HTTP service is exposed on TCP ports 80 and 8080.
- Nginx HTTPS service is exposed on TCP port 443.
- The TLS certificate for port 443 names zabbix.home.jrwroberts.co.uk.
- TCP port 9100 is open; its Nmap service label was omitted.
- Greenbone reports one matching medium-severity finding: Cleartext Transmission of Sensitive Information via HTTP on TCP port 8080.
- Four security updates are available, unattended upgrades are enabled, and no reboot is required.

### Inferences

- The host identity is well established as the Zabbix monitoring container because the canonical estate record, Proxmox inventory, hostname, authoritative agent inventory, and exposed services agree.
- The service set is consistent with a web-based Zabbix monitoring deployment, but port 9100's function is not inferred because its Nmap label was omitted.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-19T03:45:23+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-16T10:17:48+01:00`
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
