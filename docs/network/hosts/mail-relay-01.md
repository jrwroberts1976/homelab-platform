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

- Assessed: `2026-10-22T17:02:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:a5:cb:28`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

mail-relay-01 is CT102, an Ansible-managed Proxmox LXC running Debian GNU/Linux 13 (trixie) as the internal Postfix SMTP relay. SSH and SMTP are corroborated open services; three security updates are available, with no matching actionable Greenbone findings.

### Confirmed facts

- The device hostname is mail-relay-01.jameshouse and its IP address is 192.168.2.54.
- The canonical estate identity is mail-relay-01, an LXC with role Internal Postfix SMTP relay, CT102 on PROXMOX.
- Proxmox inventory identifies the guest as LXC mail-relay-01 with VMID 102.
- Authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie), x86_64, kernel 7.0.14-23-pve.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 25 is open and provides corroborated Postfix smtpd.
- TCP port 9100 is open; its Nmap service label was omitted.
- Greenbone reports zero matching actionable findings for the current host IP.
- Patching reports three security updates and five total updates available; unattended upgrades are enabled and no reboot is required.

### Inferences

- The device is a Debian-based mail-relay workload hosted as a Proxmox LXC container.
- The documented role and corroborated Postfix SMTP service indicate that this host functions as an internal SMTP relay.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-25T03:12:00+00:00`
- Pending updates: **4**
- Security updates pending: **1**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-23T07:03:34+01:00`
- Patch state: **Attention required**

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
