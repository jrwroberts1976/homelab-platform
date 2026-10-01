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
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `bc:24:11:a5:cb:28`
- Observed IP address(es): `192.168.2.54`
- Connections: **17**
- Traffic sent: **180.6 KiB**
- Traffic received: **70.6 KiB**
- Top services: `ssl` (17), `smtp` (11)
- Top destination ports: `tcp/587` (11), `tcp/443` (6)

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

- Assessed: `2026-10-01T11:14:41+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:a5:cb:28`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Authoritative inventory identifies this host as the Proxmox CT102 internal Postfix SMTP relay. It runs Debian GNU/Linux 13 (trixie) and exposes SSH, SMTP, and TCP/9100; no matching actionable Greenbone findings were reported.

### Confirmed facts

- Canonical estate identity is mail-relay-01, role Internal Postfix SMTP relay, CT102 on PROXMOX.
- The host is an LXC guest managed through Proxmox, VMID 102.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), x86_64, with kernel 7.0.14-17-pve.
- Open services include OpenSSH 10.0p2 on TCP/22 and Postfix smtpd on TCP/25.
- TCP/9100 is open and has the Nmap service label jetdirect, without product or version evidence.
- Greenbone reported zero matching actionable findings for the current host IP.
- Patch telemetry reports zero available updates and no reboot required at collection time.

### Inferences

- The platform is a Debian-based Linux system running inside a Proxmox LXC container.
- The host function is an internal SMTP relay, supported by the canonical role and Postfix service evidence.
- The TCP/9100 service identity and purpose remain unconfirmed because no product or version was supplied.

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
