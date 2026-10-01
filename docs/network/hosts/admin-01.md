# admin-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `admin-01` |
| Address | `192.168.2.48` |
| Type | physical |
| Role | Raspberry Pi 3 administration, SSH jump, IaC controller and Corosync QNetd host |
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
- MAC identity: `b8:27:eb:e8:36:cd`
- Observed IP address(es): `192.168.2.48`
- Connections: **62**
- Traffic sent: **65.1 KiB**
- Traffic received: **2.5 MiB**
- Top services: `ntp` (42), `ssl` (9), `ssh` (7), `http` (2), `dns` (1), `dhcp` (1)
- Top destination ports: `udp/123` (42), `tcp/443` (9), `tcp/22` (7), `tcp/80` (2), `udp/5353` (1), `udp/67` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

Record reviewed, useful flow summaries rather than raw packet captures.

| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

### Expected flows

- 
- 

### Unexpected or investigated flows

- 

## Internet / DNS activity

Keep this section to **bounded domain/service summaries**. Do not commit a
complete household browsing history.

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

- Assessed: `2026-10-01T10:35:22+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `b8:27:eb:e8:36:cd`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

admin-01 is a managed physical Raspberry Pi 3 administration, SSH jump, IaC controller, and Corosync QNetd host running authoritative Debian GNU/Linux 13 (trixie) on aarch64. SSH and rpcbind are open; 19 security updates are available and no matching actionable Greenbone findings were reported.

### Confirmed facts

- The canonical device name is admin-01.
- The device is classified as physical and managed by Ansible.
- Its documented role is Raspberry Pi 3 administration, SSH jump, IaC controller, and Corosync QNetd host.
- The vendor is Raspberry Pi Foundation.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), kernel 6.18.39+rpt-rpi-v8, and architecture aarch64.
- Open TCP services include OpenSSH on port 22, rpcbind on port 111, and a service identified by Nmap as jetdirect on port 9100.
- Patching telemetry reports 19 security updates and 135 total updates available, with no reboot required.
- Greenbone reported zero matching actionable findings for the current host IP.

### Inferences

- The platform is Raspberry Pi hardware running Debian Linux.
- The host likely provides administration and infrastructure-management functions consistent with its documented estate role.
- The port 9100 service may be printer-protocol compatible, but its function is not confirmed by the supplied evidence.

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
