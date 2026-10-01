# cloud-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `cloud-01` |
| Address | `192.168.2.53` |
| Type | vm |
| Role | Production Nextcloud, PostgreSQL and Redis, VM200 on PROXMOX |
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
- MAC identity: `bc:24:11:e9:49:60`
- Observed IP address(es): `192.168.2.53`
- Connections: **15**
- Traffic sent: **33.6 KiB**
- Traffic received: **48.8 MiB**
- Top services: `ssl` (15)
- Top destination ports: `tcp/443` (15)

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

- Assessed: `2026-10-01T11:14:23+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:e9:49:60`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

cloud-01 is a managed QEMU VM on PROXMOX running Debian GNU/Linux 13, hosting production Nextcloud, PostgreSQL and Redis services. OpenSSH, Apache httpd and TCP/9100 were detected. A reboot is required and two updates are available; no matching actionable Greenbone findings were reported.

### Confirmed facts

- The canonical estate identifies the device as cloud-01, a VM managed by Ansible.
- The VM is QEMU guest 200 on PROXMOX.
- The authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie), x86_64, with kernel 6.12.107+deb13-cloud-amd64.
- Open TCP ports are 22, 8080 and 9100.
- OpenSSH 10.0p2 Debian 7+deb13u4 is detected on TCP/22.
- Apache httpd 2.4.68 is detected on TCP/8080.
- Greenbone reports zero matching actionable findings for the current host IP.
- Patch telemetry reports two updates available, zero security updates available, and a reboot required.

### Inferences

- The host is a Linux-based production application and database VM consistent with its documented estate role.
- TCP/9100 is labeled jetdirect by scanning, but no product or version evidence confirms the service function.

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
