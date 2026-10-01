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

- Assessed: `2026-10-01T10:02:06+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:26:25:d1`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

Proxmox QEMU VM203 identified as the Greenbone Community vulnerability scanner. It exposes SSH, HTTPS/nginx, and TCP/9100; evidence supports a Linux guest, but not a precise OS or kernel. Greenbone reports no actionable findings for this IP, while feed-signature warnings and a required reboot merit review.

### Confirmed facts

- Canonical estate record identifies greenbone-01 as a managed VM and Greenbone Community vulnerability scanner on Proxmox-2.
- Proxmox inventory reports a QEMU guest named greenbone-01 with VMID 203.
- The host is online at 192.168.2.57 and has hostname greenbone-01.jameshouse.
- TCP ports 22, 443, and 9100 are open.
- Port 22 reports OpenSSH 10.0p2 Debian 7+deb13u4 with SSH protocol 2.0.
- Port 443 reports nginx 1.30.4 over TLS.
- Nmap OS detection completed and reports Linux matches, including Linux 4.15–5.19 and other less-specific alternatives.
- Greenbone reports zero actionable findings matching the current IP.
- Patch telemetry reports six total updates available, zero security updates available, and a reboot required.
- Loki samples include repeated Greenbone feed-signature warnings because sha256sums.asc was missing.

### Inferences

- The guest is most consistent with a Linux-based server VM running Greenbone services.
- The Debian build string on OpenSSH suggests a Debian-family userland, but it does not establish the guest OS or version.
- The TCP/9100 service is identified tentatively as jetdirect; its host function is not established from that label alone.

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
