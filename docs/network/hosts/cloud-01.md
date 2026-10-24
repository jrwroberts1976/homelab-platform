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
- MAC identity: `bc:24:11:e9:49:60`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

cloud-01 is the managed QEMU VM cloud-01 on PROXMOX, running authoritative Debian GNU/Linux 13. It hosts documented production Nextcloud, PostgreSQL and Redis workloads; SSH and Apache HTTP services are exposed, with port 9100 also open. Greenbone reports two actionable medium-severity findings, while patch telemetry shows two updates available and a reboot required; both conditions merit review.

### Confirmed facts

- The canonical device name is cloud-01.
- The device is a VM with QEMU guest type and VMID 200 on PROXMOX.
- The documented estate role is Production Nextcloud, PostgreSQL and Redis.
- The authoritative OS is Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 6.12.111+deb13-cloud-amd64.
- Port 22/tcp is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- Port 8080/tcp is open and provides corroborated Apache httpd 2.4.68 (Debian).
- Port 9100/tcp is open; its service label is omitted.
- Greenbone reports two matching actionable medium-severity findings, including DSA-6572-1 and missing Linux kernel mitigations for Processor MMIO Stale Data vulnerabilities.
- Patch telemetry reports two updates available, zero security updates available, and a reboot required.

### Inferences

- The device is a managed Debian Linux server VM rather than a physical network appliance.
- The Proxmox vendor attribution identifies the virtualization platform or estate provider, not necessarily the guest OS vendor.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-24T17:28:52+01:00`
- Pending updates: **4**
- Security updates pending: **1**
- Reboot required: **Yes**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-22T06:56:09+01:00`
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
