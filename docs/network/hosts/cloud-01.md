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

- Assessed: `2026-10-15T16:04:13+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:e9:49:60`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

cloud-01 is the managed QEMU VM cloud-01 on Proxmox VM200, running Debian GNU/Linux 13 (trixie). It provides corroborated OpenSSH 10.0p2 and Apache httpd 2.4.68 services, with TCP ports 22, 8080, and 9100 open. Greenbone reports two medium-severity kernel-mitigation findings; patch telemetry currently shows no pending updates or reboot requirement.

### Confirmed facts

- The canonical estate identity is cloud-01, documented as a VM managed by Ansible.
- The VM is QEMU guest cloud-01, VMID 200, hosted on PROXMOX.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 6.12.111+deb13-cloud-amd64.
- The documented estate role is Production Nextcloud, PostgreSQL and Redis, VM200 on PROXMOX.
- TCP port 22 is open and serves corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 8080 is open and serves corroborated Apache httpd 2.4.68 (Debian).
- TCP port 9100 is open; its Nmap service label was omitted.
- Greenbone reports two matching medium-severity kernel-mitigation findings involving MDS and SSB speculative-execution vulnerabilities.
- Patch telemetry is fresh, reports zero available security updates and zero total updates, and indicates no reboot is required.

### Inferences

- The host is a production Linux application/server VM based on its documented estate role and exposed services.
- The authoritative OS facts supersede Nmap OS or DNS inference.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-19T08:53:52+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **Yes**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-18T06:19:31+01:00`
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
