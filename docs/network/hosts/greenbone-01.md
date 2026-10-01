# greenbone-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `greenbone-01` |
| Address | `192.168.2.57` |
| Type | vm |
| Role | Greenbone Community vulnerability scanner, VM203 on Proxmox-2 |
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
- MAC identity: `bc:24:11:26:25:d1`
- Observed IP address(es): `192.168.2.57`
- Connections: **44**
- Traffic sent: **39.8 KiB**
- Traffic received: **1.7 MiB**
- Top services: `dns` (33), `ssl` (11)
- Top destination ports: `udp/5355` (33), `tcp/443` (11)

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

- Assessed: `2026-10-01T11:13:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:26:25:d1`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

greenbone-01 is a managed Greenbone Community vulnerability scanner VM203 on Proxmox-2, running authoritative Debian 13 (trixie) x86_64. SSH, HTTPS/nginx, and TCP/9100 are open. No matching actionable Greenbone findings were reported, but feed-signature warnings and a required reboot merit review.

### Confirmed facts

- Hostname is greenbone-01.jameshouse and IP address is 192.168.2.57.
- The canonical estate role is Greenbone Community vulnerability scanner, VM203 on Proxmox-2.
- The guest is a QEMU VM managed by Ansible on Proxmox-2.
- Authoritative Zabbix Agent 2 facts identify Debian GNU/Linux 13 (trixie), kernel 6.12.107+deb13-cloud-amd64, architecture x86_64.
- TCP ports 22, 443, and 9100 are open.
- OpenSSH 10.0p2 Debian 7+deb13u4 is exposed on TCP/22.
- nginx 1.30.4 is exposed over TLS on TCP/443.
- Greenbone reported zero matching actionable findings for the current IP.
- Six updates are available, zero security updates are reported, and a reboot is required.
- Sampled logs contain repeated Greenbone feed-signature warnings for a missing /var/lib/openvas/plugins/sha256sums.asc file.

### Inferences

- This is a Linux-based server VM hosting Greenbone/OpenVAS-related services.
- TCP/9100 is identified as jetdirect by Nmap, but no product or function is confirmed for that service.

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
