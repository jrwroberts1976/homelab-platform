# Proxmox-2

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `Proxmox-2` |
| Address | `192.168.2.71` |
| Type | physical |
| Role | Proxmox VE cluster node 2; former network-discovery source retained for rollback/history |
| Managed by Ansible | Yes |
| State | Active |

## Network identity
- MAC address:
- Vendor/OUI:
- Hostname / DHCP name:
- VLAN / network:
- Physical location:

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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-06T00:24:03+01:00`
- MAC identity: `00:1a:9f:0c:30:3b`
- Observed IP address(es): `192.168.2.71`
- Connections: **622**
- Traffic sent: **70.5 KiB**
- Traffic received: **406.0 MiB**
- Top services: `ntp` (592), `ssl` (16), `http` (14)
- Top destination ports: `udp/123` (592), `tcp/443` (16), `tcp/80` (14)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->
| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity
Use bounded domain/service summaries only.

| Service / domain family | Example domains | Evidence source | Last observed | Interpretation |
|---|---|---|---|---|
| | | | | |

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-01T11:33:02+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `00:1a:9f:0c:30:3b`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Proxmox VE / Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Proxmox-2 is a confirmed physical Proxmox VE cluster node running the authoritative Zabbix-reported Proxmox VE / Debian GNU/Linux 13 (trixie) operating system. SSH and the Proxmox Virtual Environment REST API are identified; ports 111 and 9100 are open without retained service labels.

### Confirmed facts

- The canonical estate identifies this host as Proxmox-2, a physical Proxmox VE cluster node 2.
- The host is online at 192.168.2.71 and has hostname proxmox-2.jameshouse.
- Authoritative Zabbix Agent 2 facts report Proxmox VE / Debian GNU/Linux 13 (trixie), kernel 7.0.14-17-pve, and x86_64 architecture.
- TCP port 22 is open and provides OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 3128 is open and is identified as the Proxmox Virtual Environment REST API version 3.0.
- TCP ports 111 and 9100 are open; their Nmap service labels were omitted.
- Greenbone reports zero matching actionable findings for this host IP in the supplied scan result.

### Inferences

- The host is managed infrastructure rather than a general-purpose endpoint, consistent with its canonical Proxmox cluster-node role.
- The A-Link vendor value is an inventory/MAC-vendor attribution and does not establish the physical system manufacturer.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-06T07:47:37+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-05T18:14:49+01:00`
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
