# mail-relay-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `mail-relay-01` |
| Address | `192.168.2.54` |
| Type | lxc |
| Role | Internal Postfix SMTP relay, CT102 on PROXMOX |
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
- MAC identity: `bc:24:11:a5:cb:28`
- Observed IP address(es): `192.168.2.54`
- Connections: **49**
- Traffic sent: **443.1 KiB**
- Traffic received: **165.0 MiB**
- Top services: `ssl` (43), `smtp` (30), `http` (6)
- Top destination ports: `tcp/587` (30), `tcp/443` (13), `tcp/80` (6)

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

- Assessed: `2026-10-01T11:34:03+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:a5:cb:28`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC container CT102 providing the internal Postfix SMTP relay. Authoritative Zabbix inventory identifies Debian GNU/Linux 13 (trixie), x86_64. Open services include SSH on 22/tcp, Postfix SMTP on 25/tcp, and an unidentified open service on 9100/tcp.

### Confirmed facts

- Canonical estate identity is mail-relay-01, CT102, an LXC container on PROXMOX.
- The documented role is Internal Postfix SMTP relay.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), kernel 7.0.14-17-pve, and x86_64 architecture.
- OpenSSH 10.0p2 Debian 7+deb13u4 is open on 22/tcp.
- Postfix smtpd is open on 25/tcp.
- Port 9100/tcp is open; its Nmap service label was omitted.
- No actionable Greenbone findings match the current host IP.
- Patch telemetry reports zero available updates, zero security updates, and no reboot required.

### Inferences

- The host is a Debian-based mail-relay workload running inside a Proxmox LXC container.
- The Proxmox vendor attribution reflects the virtualization/container platform rather than the application workload vendor.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-06T08:55:30+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-05T19:57:15+01:00`
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
