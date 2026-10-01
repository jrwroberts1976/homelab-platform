# edge-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `edge-01` |
| Address | `192.168.2.56` |
| Type | lxc |
| Role | Reserved edge LXC, CT103 on Proxmox-2; cloudflared not deployed |
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
- MAC identity: `bc:24:11:8d:1b:c1`
- Observed IP address(es): `192.168.2.56`
- Connections: **6**
- Traffic sent: **13.5 KiB**
- Traffic received: **27.9 KiB**
- Top services: `ssl` (6)
- Top destination ports: `tcp/443` (6)

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

- Assessed: `2026-10-01T11:14:34+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:8d:1b:c1`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC edge-01 (CT103) running authoritative Debian GNU/Linux 13 on x86_64. SSH is exposed on TCP 22 and TCP 9100 is open with an uncorroborated Nmap jetdirect label. No actionable Greenbone findings matched the current IP, and no updates are pending.

### Confirmed facts

- The canonical estate identity is edge-01, a reserved edge LXC, CT103 on Proxmox-2.
- The Proxmox cluster API identifies the guest as an LXC named edge-01 with VMID 103.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 7.0.14-17-pve.
- The hostname is edge-01.jameshouse and the current IP address is 192.168.2.56.
- The recorded vendor is Proxmox Server Solutions GmbH.
- TCP port 22 is open and provides OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 9100 is open; Nmap labels the service jetdirect but provides no product or version.
- Greenbone reported zero actionable findings matching the current IP; this does not establish that the host is vulnerability-free.
- Patch telemetry is fresh and reports zero available updates, zero security updates, and no reboot required.
- The bounded 24-hour log sample includes repeated SSH authentication failures and network-wait/protocol error messages.

### Inferences

- The host is a managed Debian-based infrastructure container rather than a physical Proxmox host.
- TCP 9100 may provide a print-style or raw TCP service, but its function is not confirmed by the supplied evidence.

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
