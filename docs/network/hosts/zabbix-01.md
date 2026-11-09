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

- Assessed: `2026-11-03T18:04:04+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:01:05`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC container CT105 hosting the Zabbix monitoring platform. The estate record identifies PostgreSQL, TimescaleDB, Zabbix Server, Agent 2, Nginx and nightly backups. A high-severity Debian security advisory finding is present; patch telemetry reports no currently available updates, so both conditions merit review.

### Confirmed facts

- The canonical estate identifies this host as zabbix-01, an LXC container named CT105 on Proxmox.
- The canonical role is a Zabbix monitoring platform with PostgreSQL, TimescaleDB, Zabbix Server, Agent 2 and Nginx active.
- The host is online at 192.168.2.59 and is managed by Ansible.
- The host has one matching actionable Greenbone finding: Debian Security Advisory DSA-6600-1, severity High, score 8.8, associated with package remediation.
- Patch telemetry is fresh, reports zero available updates, and indicates that a reboot is not required.
- The bounded Loki sample includes systemd, apt, SSH authentication, and network-connectivity messages.
- Nmap reported no TCP or UDP ports and no OS matches in the supplied baseline.

### Inferences

- The host is likely running a Debian-family Linux userspace inside an LXC container, based on the Debian advisory and systemd/apt evidence.
- The exact operating system and version are not established by the supplied evidence.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-11-09T23:01:37+00:00`
- Pending updates: **1**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-11-09T06:54:26+00:00`
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
