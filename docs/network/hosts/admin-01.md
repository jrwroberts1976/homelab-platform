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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `b8:27:eb:e8:36:cd`
- Observed IP address(es): `192.168.2.48`
- Connections: **108**
- Traffic sent: **1.6 MiB**
- Traffic received: **3.5 MiB**
- Top services: `ssh` (50), `ntp` (42), `ssl` (12), `http` (4)
- Top destination ports: `tcp/22` (50), `udp/123` (42), `tcp/443` (12), `tcp/80` (4)

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

- Assessed: `2026-10-29T16:03:23+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `b8:27:eb:e8:36:cd`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

admin-01 is a managed Raspberry Pi 3 running Debian GNU/Linux 13 (trixie), serving as the administration, SSH jump, IaC controller, and Corosync QNetd host. Open TCP services include corroborated OpenSSH on port 22 and additional open ports 111 and 9100. No matching actionable Greenbone findings were reported; 11 non-security updates are available.

### Confirmed facts

- The documented hostname is admin-01, with FQDN admin-01.jameshouse and IP address 192.168.2.48.
- The canonical estate record identifies this as a physical Raspberry Pi 3 used for administration, SSH jump access, IaC control, and Corosync QNetd.
- The vendor is Raspberry Pi Foundation and the authoritative architecture is aarch64.
- Authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie) with kernel 6.18.50+rpt-rpi-v8.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP ports 111 and 9100 are open; their Nmap service labels were omitted.
- Greenbone reported zero matching actionable findings for this host IP.
- Patch telemetry reports zero security updates, 11 total updates available, unattended upgrades enabled, and no reboot required.

### Inferences

- The device is a Raspberry Pi-based Linux administration host rather than a general-purpose desktop system.
- The authoritative Debian and architecture facts provide high-confidence operating-system identification; Nmap OS identification was correctly skipped.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-31T04:49:13+00:00`
- Pending updates: **31**
- Security updates pending: **4**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-30T19:55:13+00:00`
- Patch state: **Attention required**

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
