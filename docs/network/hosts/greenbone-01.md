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

- Assessed: `2026-10-15T15:01:28+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:26:25:d1`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Greenbone Community vulnerability scanner VM203 on Proxmox-2, running authoritative Debian GNU/Linux 13 (trixie). OpenSSH is available on TCP/22 and nginx HTTPS on TCP/443; three security updates are available and no matching actionable Greenbone findings were reported.

### Confirmed facts

- The canonical estate identity is greenbone-01.
- The device is classified as a VM and documented as the Greenbone Community vulnerability scanner, VM203 on Proxmox-2.
- Proxmox inventory identifies the guest type as QEMU.
- The authoritative OS is Debian GNU/Linux 13 (trixie), with x86_64 architecture and kernel 6.12.111+deb13-cloud-amd64.
- TCP/22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP/443 is open and provides corroborated nginx 1.30.4 over TLS.
- TCP/9100 is open; its Nmap service label was omitted.
- The Greenbone report has zero matching actionable findings for this host IP.
- Patch telemetry reports three security updates and seven total updates available; reboot is not required.

### Inferences

- The host identity is consistent with a managed Debian-based infrastructure VM running the Greenbone scanner role.
- The Proxmox vendor attribution describes the virtualization platform or guest inventory source rather than establishing the operating-system vendor.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-21T05:00:36+01:00`
- Pending updates: **1**
- Security updates pending: **0**
- Reboot required: **Yes**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-19T06:13:13+01:00`
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
