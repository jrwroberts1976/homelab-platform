# dns-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `dns-01` |
| Address | `192.168.2.51` |
| Type | lxc |
| Role | Pi-hole and Unbound, CT101 on Proxmox-2 |
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
- Summary generated: `2026-10-05T00:23:30+01:00`
- MAC identity: `bc:24:11:c3:75:ba`
- Observed IP address(es): `192.168.2.51`
- Connections: **33,295**
- Traffic sent: **1.7 MiB**
- Traffic received: **20.1 MiB**
- Top services: `dns` (33062), `ntp` (192), `ssl` (19), `http` (3)
- Top destination ports: `udp/53` (33002), `udp/123` (192), `tcp/53` (60), `tcp/443` (19), `icmp/3` (19), `tcp/80` (3)

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

- Assessed: `2026-10-01T11:33:46+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:c3:75:ba`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

dns-01 is CT101, a managed Proxmox LXC container running authoritative Debian GNU/Linux 13 (trixie) for Pi-hole and Unbound. Open services include SSH on 22/tcp and dnsmasq/Pi-hole DNS on 53/tcp; ports 80, 443, and 9100 are also open. No matching actionable Greenbone findings were reported.

### Confirmed facts

- The canonical device name is dns-01.
- The device is LXC container CT101 on Proxmox-2 and is managed by Ansible.
- The documented role is Pi-hole and Unbound.
- The authoritative OS is Debian GNU/Linux 13 (trixie) on x86_64.
- The authoritative OS facts come from Zabbix Agent 2.
- OpenSSH 10.0p2 Debian 7+deb13u4 is exposed on TCP port 22.
- dnsmasq 2.93 with Pi-hole context is exposed on TCP port 53.
- TCP ports 80, 443, and 9100 are open.
- The matching Greenbone actionable finding count is zero.
- Four security updates and five total updates are available; no reboot is required.

### Inferences

- The host is a Linux-based managed infrastructure service container.
- The Proxmox vendor attribution likely describes the virtualization environment rather than the application stack itself.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-05T12:01:29+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-04T12:32:41+01:00`
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
