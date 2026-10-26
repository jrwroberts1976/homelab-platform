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
- Summary generated: `2026-10-26T00:22:36+00:00`
- MAC identity: `b8:27:eb:e8:36:cd`
- Observed IP address(es): `192.168.2.48`
- Connections: **74**
- Traffic sent: **45.4 KiB**
- Traffic received: **384.0 MiB**
- Top services: `ntp` (42), `ssl` (18), `http` (9), `dns` (2), `dhcp` (1)
- Top destination ports: `udp/123` (42), `tcp/443` (18), `tcp/80` (9), `udp/5353` (2), `tcp/22` (2), `udp/67` (1)

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

- Assessed: `2026-10-22T16:05:03+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `b8:27:eb:e8:36:cd`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

admin-01 is a managed Raspberry Pi 3 administration and SSH jump host running authoritative Debian GNU/Linux 13 (trixie). OpenSSH is exposed on TCP/22; TCP/111 and TCP/9100 are also open. Three security updates and one matching medium-severity Debian advisory require review.

### Confirmed facts

- The documented device name is admin-01.
- The device is a physical host managed by Ansible.
- Its canonical role is Raspberry Pi 3 administration, SSH jump, IaC controller, and Corosync QNetd host.
- The vendor is Raspberry Pi Foundation.
- The authoritative OS is Debian GNU/Linux 13 (trixie), with aarch64 architecture and kernel 6.18.50+rpt-rpi-v8.
- TCP/22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP/111 and TCP/9100 are open; their Nmap service labels were omitted.
- Greenbone reports one matching actionable medium-severity Debian security advisory, DSA-6572-1.
- Patch telemetry reports three security updates available, 29 total updates available, and no reboot required.

### Inferences

- The host is likely used as a Linux-based infrastructure administration server consistent with its documented estate role.
- The authoritative OS and service evidence indicate a Raspberry Pi running Debian rather than an embedded IoT firmware platform.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-26T09:46:27+00:00`
- Pending updates: **1**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-25T17:05:29+00:00`
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
