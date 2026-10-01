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

- Assessed: `2026-10-01T10:06:08+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:e9:49:60`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

cloud-01 is the documented production Nextcloud/PostgreSQL/Redis VM200 guest on Proxmox. Linux is strongly supported by Nmap and the Debian-built OpenSSH banner; the exact distribution and kernel are not established. Apache HTTP is exposed on TCP/8080, SSH on TCP/22, and TCP/9100 has a tentative JetDirect service label. Two updates are available and a reboot is required; Greenbone reported no matching actionable findings, which does not prove the host is vulnerability-free.

### Confirmed facts

- The canonical estate record identifies cloud-01 as a managed VM, VM200 on PROXMOX, with the role Production Nextcloud, PostgreSQL and Redis.
- Proxmox enrichment identifies the guest type as QEMU and the Proxmox node as PROXMOX.
- Nmap identified Linux matches with up to 96% accuracy and classified the SSH service as Linux.
- TCP/22 is open and exposes OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP/8080 is open and exposes Apache httpd 2.4.68 with Debian information.
- TCP/9100 is open and has the Nmap service label jetdirect without product or version evidence.
- Patch telemetry reports two updates available, zero security updates available, unattended upgrades enabled, and a reboot required.
- Greenbone completed successfully with zero matching actionable findings for this host IP.

### Inferences

- The host is most consistent with a Linux-based server VM supporting the documented production application stack.
- The Debian-specific OpenSSH build suggests a Debian-family userspace, but the exact distribution and kernel are not established.
- The TCP/9100 JetDirect label alone is insufficient to infer printer-related host functionality.

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
