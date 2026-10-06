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
- Summary generated: `2026-10-06T00:24:03+01:00`
- MAC identity: `bc:24:11:26:25:d1`
- Observed IP address(es): `192.168.2.57`
- Connections: **55**
- Traffic sent: **57.1 KiB**
- Traffic received: **246.2 MiB**
- Top services: `dns` (33), `ssl` (21)
- Top destination ports: `udp/5355` (25), `tcp/443` (21), `udp/53` (8), `icmp/3` (1)

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

- Assessed: `2026-10-01T11:32:39+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:26:25:d1`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

greenbone-01 is a managed Debian 13 VM on Proxmox-2, documented as the Greenbone Community vulnerability scanner. SSH, HTTPS/nginx, and TCP/9100 are open. Reboot is required and six updates are available; no matching actionable Greenbone findings were supplied.

### Confirmed facts

- The canonical estate record identifies greenbone-01 as VM203 on Proxmox-2 and as a Greenbone Community vulnerability scanner.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), on x86_64 with kernel 6.12.107+deb13-cloud-amd64.
- The Proxmox enrichment identifies the guest type as QEMU and the vendor as Proxmox Server Solutions GmbH.
- TCP port 22 is open with corroborated OpenSSH 10.0p2 Debian 7+deb13u4 evidence.
- TCP port 443 is open with corroborated nginx 1.30.4 over TLS evidence.
- TCP port 9100 is open; its Nmap service label was omitted.
- The current Greenbone data contains zero matching actionable findings for this host IP.
- Patch telemetry reports six updates available, zero security updates available, and a reboot required.
- The host is online at 192.168.2.57 and is managed by Ansible.

### Inferences

- The host is likely an application server dedicated to Greenbone scanning based on its documented estate role and observed OpenVAS/Greenbone-related logs.
- The HTTPS service likely provides the scanner's web interface, but the supplied evidence does not directly identify the application behind nginx.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-06T06:57:21+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-05T20:16:54+01:00`
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
