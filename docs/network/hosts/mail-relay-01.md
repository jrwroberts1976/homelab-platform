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
- Summary generated: `2026-10-10T00:20:32+01:00`
- MAC identity: `bc:24:11:a5:cb:28`
- Observed IP address(es): `192.168.2.54`
- Connections: **28**
- Traffic sent: **304.9 KiB**
- Traffic received: **570.3 KiB**
- Top services: `ssl` (26), `smtp` (18), `http` (2)
- Top destination ports: `tcp/587` (18), `tcp/443` (8), `tcp/80` (2)

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

- Assessed: `2026-10-08T15:00:50+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:a5:cb:28`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC container CT102 running Debian GNU/Linux 13 as the internal Postfix SMTP relay. SSH and SMTP are corroborated open services; TCP/9100 is also open. No matching actionable Greenbone findings or pending security updates are reported.

### Confirmed facts

- The canonical estate identity is mail-relay-01, an LXC container managed by Ansible.
- The container is CT102 on PROXMOX.
- The authoritative OS inventory reports Debian GNU/Linux 13 (trixie) on x86_64 with kernel 7.0.14-20-pve.
- OpenSSH 10.0p2 Debian 7+deb13u4 is running on TCP/22.
- Postfix smtpd is running on TCP/25.
- TCP/9100 is open; its Nmap service label was omitted.
- The inventory vendor is Proxmox Server Solutions GmbH.
- Greenbone reports zero matching actionable findings for the current host IP.
- Patch telemetry reports zero available updates and no reboot required.

### Inferences

- The host is an internal mail-relay server based on its canonical role and corroborated Postfix SMTP service.
- The Debian userland is running within a Proxmox LXC environment.
- Observed SSH authentication failures and malformed SMTP command warnings merit operational review.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-09T22:46:20+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-08T07:03:09+01:00`
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
