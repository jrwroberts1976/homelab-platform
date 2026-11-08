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
- MAC identity: `bc:24:11:8d:1b:c1`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

edge-01 is a managed LXC container on Proxmox-2 at 192.168.2.56. Exact OS is not established. Greenbone reports one high-severity Debian security advisory, while current patch telemetry reports no available updates; review the finding and patch state together.

### Confirmed facts

- The documented estate identity is edge-01, a reserved edge LXC identified as CT103 on Proxmox-2.
- The hostname is edge-01.jameshouse and the device is online at 192.168.2.56.
- The recorded vendor is Proxmox Server Solutions GmbH.
- The host is managed by Ansible.
- Nmap reported no TCP or UDP ports and no OS matches in the supplied baseline.
- Greenbone reports one matching high-severity Debian security advisory, DSA-6600-1, for package-related evidence.
- Patch telemetry is fresh, reports zero security updates and zero total updates, and indicates unattended upgrades are enabled.
- The sampled Loki data contains a systemd-networkd-wait-online error and multiple remote connection-reset messages.

### Inferences

- The device is likely a Linux-based container because it is documented as an LXC and exposes systemd journal evidence, but the exact distribution and version are unsupported.
- The Proxmox vendor attribution likely describes the virtualized/container estate rather than a directly identified guest operating system.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-11-08T11:44:20+00:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-11-08T06:57:53+00:00`
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
