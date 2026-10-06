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

- Assessed: `2026-10-01T11:33:39+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:e9:49:60`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

cloud-01 is a managed QEMU VM on PROXMOX running authoritative Debian GNU/Linux 13 (trixie). It hosts production Nextcloud, PostgreSQL and Redis workloads, with OpenSSH on port 22, Apache HTTP on port 8080, and an additional open port 9100. A reboot is required and two non-security updates are available; no matching actionable Greenbone findings were reported.

### Confirmed facts

- The device hostname is cloud-01.jameshouse, with telemetry hostname cloud-01.
- The canonical estate identity is cloud-01, a VM managed by Ansible and hosted as VM200 on PROXMOX.
- The Proxmox cluster API identifies the guest type as QEMU.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 6.12.107+deb13-cloud-amd64.
- TCP port 22 is open and provides OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 8080 is open and provides Apache httpd 2.4.68 (Debian).
- TCP port 9100 is open; the Nmap service label was omitted.
- The host is online at 192.168.2.53.
- Greenbone reported zero matching actionable findings for the current host IP.
- Patch telemetry reports a required reboot, two updates available, and zero security updates available.

### Inferences

- The device is best classified as a Linux-based production application/server VM.
- The Proxmox vendor attribution describes the virtualization platform rather than the guest operating system.
- The open HTTP service on port 8080 is consistent with the documented production Nextcloud role, but the evidence does not establish the exact application bound to that port.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-06T04:42:22+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-05T19:55:38+01:00`
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
