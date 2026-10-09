# sensor-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `sensor-01` |
| Address | `192.168.2.55` |
| Type | vm |
| Role | Suricata and Zeek passive network sensor, VM201 on PROXMOX |
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
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `bc:24:11:3b:b9:e4`
- Observed IP address(es): `192.168.2.55`
- Connections: **55**
- Traffic sent: **28.9 KiB**
- Traffic received: **2.2 MiB**
- Top services: `ntp` (42), `ssl` (12)
- Top destination ports: `udp/123` (42), `tcp/443` (12), `tcp/5355` (1)

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

- Assessed: `2026-10-08T14:00:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:3b:b9:e4`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

sensor-01 is an online QEMU VM (VMID 201) on PROXMOX, managed by Ansible as a Suricata and Zeek passive network sensor. It runs authoritative Debian GNU/Linux 13 (trixie) on x86_64 with kernel 6.12.107+deb13-amd64. SSH is exposed on TCP 22; TCP 9100 is also open. No actionable Greenbone findings or pending updates were reported.

### Confirmed facts

- The canonical estate name is sensor-01 and its role is a Suricata and Zeek passive network sensor.
- The device is a VM, specifically a QEMU guest with VMID 201 on PROXMOX.
- The VM is managed by Ansible and is currently online at 192.168.2.55.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture x86_64, kernel 6.12.107+deb13-amd64.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP port 9100 is open; its Nmap service label was omitted.
- Greenbone reported zero actionable findings matching this current IP.
- Patch telemetry reports zero available updates, zero security updates, no reboot required, and enabled unattended upgrades.
- The bounded 24-hour Loki sample contains 1,263 entries from the network-security job.

### Inferences

- The platform is a managed Debian-based network-monitoring VM consistent with its documented Suricata and Zeek sensor role.
- The Proxmox vendor and QEMU guest metadata identify the virtualization platform, not the guest operating-system vendor.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-09T22:31:30+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-09T06:28:14+01:00`
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
