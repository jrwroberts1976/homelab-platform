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

- Assessed: `2026-10-08T14:00:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:26:25:d1`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Greenbone Community vulnerability scanner VM203 on Proxmox-2, running authoritative Debian 13 (trixie). SSH and HTTPS are exposed; no actionable Greenbone findings match 192.168.2.57, but feed-signature warnings require review.

### Confirmed facts

- Canonical estate identity is greenbone-01.
- The device is a VM, specifically a QEMU guest named greenbone-01 on Proxmox-2 with VMID 203.
- Its documented role is Greenbone Community vulnerability scanner.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 6.12.111+deb13-cloud-amd64.
- TCP ports 22, 443, and 9100 are open.
- Port 22 is corroborated as OpenSSH 10.0p2 Debian 7+deb13u4.
- Port 443 is corroborated as nginx 1.30.4 over TLS.
- Greenbone reports zero actionable findings matching 192.168.2.57.
- Patch telemetry reports zero available updates, zero security updates, and no reboot required.
- Recent Loki samples contain repeated Greenbone feed-signature warnings because /var/lib/openvas/plugins/sha256sums.asc is missing.

### Inferences

- The host is a Linux-based Debian virtual machine dedicated to vulnerability-scanning services, consistent with its documented estate role.
- The Proxmox vendor attribution reflects the virtualization platform rather than necessarily the guest operating-system vendor.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-08T14:21:51+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-08T06:32:41+01:00`
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
