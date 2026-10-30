# edge-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `edge-01` |
| Address | `192.168.2.56` |
| Type | lxc |
| Role | Reserved edge LXC, CT103 on Proxmox-2; cloudflared not deployed |
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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `bc:24:11:8d:1b:c1`
- Observed IP address(es): `192.168.2.56`
- Connections: **10**
- Traffic sent: **18.2 KiB**
- Traffic received: **404.0 KiB**
- Top services: `ssl` (8), `http` (2)
- Top destination ports: `tcp/443` (8), `tcp/80` (2)

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

- Assessed: `2026-10-29T17:01:31+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:8d:1b:c1`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

edge-01 is CT103, a managed Debian 13 LXC on Proxmox-2. OpenSSH 10.0p2 is exposed on TCP/22 and TCP/9100 is open. No actionable Greenbone findings match the current IP; three updates are available.

### Confirmed facts

- Canonical identity is edge-01, a reserved edge LXC identified as CT103 on Proxmox-2.
- The Proxmox guest type is LXC and the Proxmox VMID is 103.
- Authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie), x86_64, with kernel 7.0.14-20-pve.
- The vendor is Proxmox Server Solutions GmbH.
- TCP/22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP/9100 is open; its Nmap service label was omitted.
- No actionable Greenbone findings match 192.168.2.56.
- Three updates are available, zero security updates are reported, and no reboot is required.

### Inferences

- The device is a managed Debian-based application or infrastructure container hosted by Proxmox rather than a standalone physical endpoint.
- The recorded role indicates this is reserved edge infrastructure; cloudflared is not deployed according to the canonical estate record.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-30T18:39:50+00:00`
- Pending updates: **3**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-24T06:07:50+01:00`
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
