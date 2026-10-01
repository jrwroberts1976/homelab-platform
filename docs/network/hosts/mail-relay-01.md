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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `bc:24:11:a5:cb:28`
- Observed IP address(es): `192.168.2.54`
- Connections: **17**
- Traffic sent: **180.6 KiB**
- Traffic received: **70.6 KiB**
- Top services: `ssl` (17), `smtp` (11)
- Top destination ports: `tcp/587` (11), `tcp/443` (6)

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

- Assessed: `2026-10-01T10:06:08+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:a5:cb:28`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Proxmox LXC CT102 identified as the managed internal Postfix SMTP relay. Linux is strongly indicated, but the exact distribution and kernel version are not established by the supplied evidence. SSH and SMTP are confirmed open; port 9100 has a tentative JetDirect label. No matching actionable Greenbone findings or pending updates were reported.

### Confirmed facts

- The canonical estate record identifies the device as mail-relay-01, an LXC container and internal Postfix SMTP relay, CT102 on PROXMOX.
- The Proxmox inventory identifies guest type lxc, name mail-relay-01, node PROXMOX, and VMID 102.
- The host is online at 192.168.2.54 and has hostname mail-relay-01.jameshouse.
- TCP port 22 is open and runs OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP port 25 is open and runs Postfix smtpd.
- TCP port 9100 is open and is labeled jetdirect by Nmap, without product or version evidence.
- Nmap completed OS identification and reported Linux matches, with the strongest match covering Linux kernel generations 4.X and 5.X.
- Greenbone reported zero matching actionable findings for the current host IP.
- Patch telemetry reports zero available updates, zero security updates, and no reboot required.

### Inferences

- The guest is most consistently classified as a Linux-based general-purpose server environment.
- The OpenSSH Debian package suffix supports a Debian-packaged userspace, but does not establish the exact operating system or release.
- The port 9100 label alone is insufficient to conclude that the host is a printer or print server.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

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
