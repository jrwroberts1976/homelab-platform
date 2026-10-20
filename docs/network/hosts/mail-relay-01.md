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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-15T16:04:13+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:a5:cb:28`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Authoritative inventory identifies 192.168.2.54 as mail-relay-01, CT102 on PROXMOX, running Debian GNU/Linux 13 in an LXC container. Corroborated services are OpenSSH 10.0p2 and Postfix SMTP on ports 22 and 25; port 9100 is open with no service label supplied. One Greenbone finding for CVE-2022-40982 and current patch status with no pending updates both merit review.

### Confirmed facts

- Canonical estate identity is mail-relay-01.
- The host is an internal Postfix SMTP relay, CT102 on PROXMOX.
- The guest type is LXC and it is managed by Ansible.
- The host IP is 192.168.2.54 and it is currently online.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), kernel 7.0.14-23-pve, and x86_64 architecture.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 25 is open and provides corroborated Postfix smtpd.
- TCP port 9100 is open; its Nmap service label was omitted.
- Greenbone reports one matching actionable finding: CVE-2022-40982, rated Medium, concerning missing Linux kernel mitigations for GDS/Downfall.
- Patch telemetry reports zero available updates, zero security updates, successful recent patch telemetry, and no reboot required.
- Unattended upgrades are enabled.

### Inferences

- The device identity is resolved with high confidence because the canonical estate record, Proxmox inventory, hostname, and authoritative agent inventory agree.
- The platform is best represented as Debian Linux operating within a Proxmox LXC guest rather than as a standalone physical host.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-20T04:06:34+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-16T10:17:45+01:00`
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
