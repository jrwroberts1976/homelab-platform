# PROXMOX

> Persistent private host record. Do not store passwords, API tokens, recovery keys, full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `PROXMOX` |
| Address | `192.168.2.70` |
| Type | physical |
| Role | Proxmox VE cluster node 1 and cluster anchor |
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
- Authoritative OS: Proxmox VE 9.2.21 / Debian GNU/Linux 13 (trixie)
- OS evidence source: live `pveversion`, `uname`, cluster and service validation on 5 October 2026
- Architecture: x86_64
- Kernel / firmware: `7.0.14-20-pve`
- Nmap fingerprint:
- Nmap evidence timestamp:
- Confidence / review status: High — live validated 5 October 2026

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

- Assessed: `2026-10-22T17:02:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `80:e8:2c:1c:55:d2`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Proxmox VE / Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

PROXMOX is a confirmed physical Proxmox VE cluster node and cluster anchor at 192.168.2.70. Authoritative Zabbix OS data identifies Proxmox VE on Debian 13 (trixie); OpenSSH and the Proxmox Virtual Environment REST API are exposed. No matching actionable Greenbone findings were reported, but patch telemetry is unavailable.

### Confirmed facts

- Canonical estate identifies the device as PROXMOX.
- The device is documented as physical, managed by Ansible, and serving as Proxmox VE cluster node 1 and cluster anchor.
- Authoritative Zabbix Agent 2 inventory identifies the OS as Proxmox VE / Debian GNU/Linux 13 (trixie) on x86_64 with kernel 7.0.14-23-pve.
- The inventory hostname is proxmox.jameshouse and the telemetry hostname is proxmox.
- The vendor is Hewlett Packard.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 3128 is open and provides the corroborated Proxmox Virtual Environment REST API, version 3.0.
- TCP ports 111 and 9100 are open; no service labels are supplied for these ports.
- Greenbone reported zero matching actionable findings for the current host IP.
- Patch telemetry is unavailable, and the bounded Loki sample contained zero sampled entries.

### Inferences

- The host is a physical virtualization infrastructure server based on its canonical Proxmox cluster-node role and physical classification.
- The exposed services are consistent with administration and Proxmox host management, with the service evidence directly confirming OpenSSH and the Proxmox REST API.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-26T18:05:35+00:00`
- Pending updates: **4**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-24T06:05:07+01:00`
- Patch state: **Healthy**

> Automatic reboot remains disabled by policy; reboot-required state is reported for controlled maintenance.
<!-- END AUTO:PATCHING -->

## Monitoring and security
- Grafana host dashboard: monitored through the homelab Linux estate dashboards
- Zabbix / Node Exporter / other monitoring: Zabbix Agent 2, Node Exporter, Grafana Alloy and homelab patch-status exporter
- Alerting: central monitoring on `monitor-01`
- Vulnerability findings: managed Greenbone evidence; no current actionable finding recorded in the latest retained assessment
- Firewall/access policy:
- Accepted risks:

## Ownership and administration
- Owner / responsible person: Homelab administrator
- Management method: Ansible from `admin-01`; Proxmox VE cluster management for hypervisor operations
- Configuration source: `homelab-platform/IaC/`
- Patching / maintenance: Debian security updates automated with `unattended-upgrades`; Proxmox platform/full upgrades performed as controlled maintenance; automatic reboot disabled
- Backup / recovery:
- Planned retirement / replacement:

## Evidence history
| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| 2026-10-05 | Full Proxmox/Debian upgrade completed; pve-manager 9.2.21 installed; node rebooted onto `7.0.14-20-pve`; cluster quorate with QDevice; guests healthy; automated security patching enrolled with 0 pending updates | Live Ansible validation / Prometheus patch status | James |

## Notes
- Proxmox package-stack upgrades remain controlled maintenance even though Debian security updates are automated.
- Automatic reboots are disabled by policy.
