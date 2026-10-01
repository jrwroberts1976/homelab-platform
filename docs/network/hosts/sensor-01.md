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

- Assessed: `2026-10-01T11:14:17+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:3b:b9:e4`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

sensor-01 is a managed Debian 13 QEMU VM on Proxmox, documented as the Suricata and Zeek passive network sensor VM201. SSH and TCP/9100 are open; patch telemetry reports a reboot required and three updates available.

### Confirmed facts

- Canonical name is sensor-01 and the estate kind is VM.
- The VM is VM201 on PROXMOX and uses QEMU.
- The documented role is Suricata and Zeek passive network sensor.
- The host is managed by Ansible.
- Authoritative Zabbix Agent 2 facts identify Debian GNU/Linux 13 (trixie), x86_64, kernel 6.12.107+deb13-amd64.
- MAC/vendor evidence identifies Proxmox Server Solutions GmbH.
- TCP port 22 is open and provides OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 9100 is open and is labeled jetdirect by service discovery, without product/version details.
- Greenbone reported zero actionable findings matching this host IP.
- Patch telemetry is fresh, reports three updates available, and indicates a reboot is required.

### Inferences

- The host is a virtualized Linux-based security monitoring sensor rather than a physical network appliance.
- The TCP/9100 service purpose is not established from the available evidence.

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
