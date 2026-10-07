# admin-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `admin-01` |
| Address | `192.168.2.48` |
| Type | physical |
| Role | Raspberry Pi 3 administration, SSH jump, IaC controller and Corosync QNetd host |
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

- Assessed: `2026-10-01T11:33:16+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `b8:27:eb:e8:36:cd`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Raspberry Pi 3 administration host running authoritative Debian GNU/Linux 13 (trixie) on aarch64. It serves as an SSH jump/IaC controller and Corosync QNetd host. OpenSSH is exposed on TCP/22; TCP/111 and TCP/9100 are also open. Patch telemetry reports 19 security updates and 135 total updates available, with no reboot required.

### Confirmed facts

- Canonical estate identity is admin-01, a physical host managed by Ansible.
- The documented role is Raspberry Pi 3 administration, SSH jump, IaC controller, and Corosync QNetd host.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), kernel 6.18.39+rpt-rpi-v8, and architecture aarch64.
- The vendor is Raspberry Pi Foundation, and the MAC address is b8:27:eb:e8:36:cd.
- TCP/22 is open and provides OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP/111 and TCP/9100 are open; no service labels are asserted for these ports.
- Greenbone reports zero matching actionable findings for the current IP.
- Patch telemetry reports 19 security updates and 135 total updates available; unattended upgrades are disabled and a reboot is not required.

### Inferences

- The host is best classified as a Raspberry Pi-based Debian administration/server node rather than a general-purpose workstation.
- The open SSH service is consistent with its documented SSH jump and infrastructure-management role.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-07T16:54:00+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-06T06:22:57+01:00`
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
