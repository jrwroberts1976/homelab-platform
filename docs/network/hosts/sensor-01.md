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

- Assessed: `2026-11-03T18:04:04+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:3b:b9:e4`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

sensor-01 is a Proxmox-hosted VM serving as the managed Suricata and Zeek passive network sensor. Exact OS is not established. Greenbone reports two actionable findings; patch telemetry currently shows no pending updates, so both conditions merit review.

### Confirmed facts

- The device hostname is sensor-01.jameshouse and its telemetry hostname is sensor-01.
- The canonical estate identifies it as VM201 on Proxmox and assigns it the role of Suricata and Zeek passive network sensor.
- The device is online at 192.168.2.55.
- The recorded vendor is Proxmox Server Solutions GmbH.
- The device is managed by Ansible.
- Greenbone reports two matching actionable findings: a Debian security advisory and Linux kernel MMIO Stale Data mitigations findings.
- Patch telemetry is fresh, reports zero available updates, and indicates that a reboot is not required.
- No authoritative OS fact is available.

### Inferences

- The host is likely a Linux-based server VM because the matching security evidence references Debian and the Linux kernel.
- The exact Linux distribution, release, kernel version, and firmware are unsupported by the supplied evidence.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-11-08T10:04:42+00:00`
- Pending updates: **1**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-11-08T06:55:47+00:00`
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
