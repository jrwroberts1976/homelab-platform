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

- Assessed: `2026-10-01T08:31:05+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `b8:27:eb:e8:36:cd`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

admin-01 is a Raspberry Pi 3 physical administration host running Linux, with SSH and RPC services exposed. OpenSSH reports a Debian build; the exact OS release and kernel are not established. 19 security updates and 135 total updates are available.

### Confirmed facts

- The canonical estate identifies admin-01 as a physical Raspberry Pi 3 administration, SSH jump, IaC controller, and Corosync QNetd host.
- The inventory and router identify the hostname as admin-01 / admin-01.jameshouse at 192.168.2.48.
- The recorded vendor is Raspberry Pi Foundation.
- Nmap identified Linux operating-system matches with 95–97% fingerprint accuracy.
- OpenSSH 10.0p2 Debian 7+deb13u4 is exposed on TCP port 22.
- TCP ports 111 (rpcbind) and 9100 (jetdirect) are open.
- Patch telemetry reports 19 security updates and 135 total updates available, with no reboot required.
- Greenbone completed successfully with zero actionable findings matching this current IP.

### Inferences

- The host is likely running a Debian-based Linux installation on Raspberry Pi hardware, based on the Debian OpenSSH build and Linux fingerprint.
- The exact distribution release and kernel version cannot be determined from the supplied evidence.
- The TCP 9100 service may provide raw printing functionality, but the evidence does not establish the attached device or its purpose.

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
