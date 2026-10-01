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
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `bc:24:11:3b:b9:e4`
- Observed IP address(es): `192.168.2.55`
- Connections: **53**
- Traffic sent: **29.2 KiB**
- Traffic received: **147.6 MiB**
- Top services: `ntp` (42), `ssl` (11)
- Top destination ports: `udp/123` (42), `tcp/443` (11)

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
- MAC identity: `bc:24:11:3b:b9:e4`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

sensor-01 is a Proxmox QEMU VM (VMID 201) serving as the documented Suricata/Zeek passive network sensor. Linux and Debian-family evidence is present, but the exact OS is not established. OpenSSH 10.0p2 is exposed on TCP/22; TCP/9100 is open with a tentative JetDirect label. Three updates and a reboot are pending; Greenbone has no matching actionable findings.

### Confirmed facts

- The canonical estate identifies sensor-01 as a VM managed by Ansible with role "Suricata and Zeek passive network sensor, VM201 on PROXMOX".
- Proxmox reports a QEMU guest named sensor-01 with VMID 201 on node PROXMOX.
- The host is online at 192.168.2.55 and has hostname sensor-01.jameshouse.
- The recorded vendor is Proxmox Server Solutions GmbH.
- TCP/22 is open and directly identified as OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP/9100 is open; Nmap gives the tentative service label "jetdirect" without product or version details.
- Nmap completed OS identification and reported Linux fingerprint matches, including Linux 4.x-5.x, Linux 5.4-5.10, and Linux 6.0 candidates.
- Patching telemetry reports three updates available, zero security updates available, unattended upgrades enabled, and a reboot required.
- Greenbone completed successfully with zero matching actionable findings for this IP.

### Inferences

- The host is most consistent with a Debian-family Linux guest because the SSH service banner identifies a Debian package build and Nmap reports Linux matches.
- The exact distribution release and kernel version cannot be determined from the supplied evidence.
- The TCP/9100 service may be printer-protocol compatible, but its host function cannot be inferred from the tentative port label alone.

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
