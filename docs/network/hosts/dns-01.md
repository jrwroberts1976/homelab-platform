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

- Assessed: `2026-10-15T16:04:13+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:c3:75:ba`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

dns-01 is the managed CT101 LXC container on Proxmox-2, providing Pi-hole and Unbound on Debian GNU/Linux 13. SSH and DNS services are confirmed; one Greenbone kernel-mitigation finding warrants review.

### Confirmed facts

- Canonical estate identity is dns-01, an LXC container managed by Ansible.
- The container is CT101 on Proxmox-2 and has the role Pi-hole and Unbound.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 7.0.14-20-pve.
- TCP ports 22, 53, 80, 443, and 9100 are open.
- OpenSSH 10.0p2 Debian 7+deb13u4 is confirmed on TCP port 22.
- dnsmasq 2.93 with Pi-hole extra information is confirmed on TCP port 53.
- A corroborated TLS service identified as webdav is reported on TCP port 443.
- The TLS certificate on port 443 has subject and issuer common name pi.hole.
- Greenbone reports one matching actionable finding: CVE-2022-40982, concerning missing Linux kernel mitigations for GDS/Downfall.
- Patch telemetry reports zero available security updates, zero total updates, and no reboot required.

### Inferences

- The device is a virtualized Linux service container rather than a physical network appliance.
- Its primary network function is DNS filtering and recursive resolution through Pi-hole and Unbound.
- The Proxmox vendor attribution identifies the virtualization platform context rather than necessarily the software vendor of the guest services.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-16T04:20:32+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-15T07:25:36+01:00`
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
