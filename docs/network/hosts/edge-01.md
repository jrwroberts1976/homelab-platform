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

- Assessed: `2026-10-01T11:33:55+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:8d:1b:c1`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

edge-01 is CT103, a managed Debian GNU/Linux 13 LXC on Proxmox-2. SSH is provided by OpenSSH 10.0p2; TCP port 9100 is open with no service label supplied. No actionable Greenbone findings currently match this host.

### Confirmed facts

- The canonical estate identity is edge-01, a reserved edge LXC identified as CT103 on Proxmox-2.
- Proxmox inventory identifies the guest type as LXC and the vendor as Proxmox Server Solutions GmbH.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), x86_64, with kernel 7.0.14-17-pve.
- TCP port 22 is open and provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4 using protocol 2.0.
- TCP port 9100 is open; its Nmap service label was omitted.
- No actionable Greenbone findings match 192.168.2.56.
- Patch telemetry reports zero available updates and no reboot required at collection time.
- The sampled logs include repeated SSH authentication failures and network-online timeout/protocol error messages.

### Inferences

- This host is a managed Linux container rather than a standalone physical device or VM.
- The reserved edge role is operational metadata; cloudflared is documented as not deployed.
- The SSH authentication failures merit review, but the bounded log sample does not establish compromise.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-05T16:14:20+01:00`
- Pending updates: **2**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-05T06:31:59+01:00`
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
