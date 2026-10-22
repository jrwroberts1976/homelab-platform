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

- Assessed: `2026-10-22T16:05:03+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:3b:b9:e4`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

sensor-01 is VM201 on PROXMOX, serving as the managed Suricata and Zeek passive network sensor. It runs authoritative Debian GNU/Linux 13 (trixie) facts from Zabbix Agent 2 and exposes corroborated OpenSSH on TCP/22. Two updates are available and a reboot is required; no actionable Greenbone findings currently match the host IP.

### Confirmed facts

- The canonical device name is sensor-01.
- The device is a VM identified as VM201 on PROXMOX.
- Its documented role is Suricata and Zeek passive network sensor.
- The VM guest type is QEMU.
- The vendor is reported as Proxmox Server Solutions GmbH.
- The authoritative OS is Debian GNU/Linux 13 (trixie), based on Zabbix Agent 2 inventory.
- The authoritative architecture is x86_64 with kernel 6.12.107+deb13-amd64.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 9100 is open.
- No actionable Greenbone findings currently match 192.168.2.55.
- Two updates are available, unattended upgrades are enabled, and a reboot is required.

### Inferences

- The device identity is strongly consistent across canonical estate data, Proxmox inventory, hostname, and network scan evidence.
- The host is a managed infrastructure VM rather than a physical endpoint.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-22T14:54:36+01:00`
- Pending updates: **2**
- Security updates pending: **0**
- Reboot required: **Yes**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-22T06:05:37+01:00`
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
