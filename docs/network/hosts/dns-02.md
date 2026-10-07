# dns-02

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `dns-02` |
| Address | `192.168.2.50` |
| Type | lxc |
| Role | Pi-hole and Unbound, CT100 on PROXMOX |
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

- Assessed: `2026-10-01T11:33:24+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:35:3b:11`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC container CT100 running Debian GNU/Linux 13, providing Pi-hole/dnsmasq and Unbound-related DNS infrastructure. OpenSSH and DNS services are confirmed; four security updates are available.

### Confirmed facts

- The canonical estate identity is dns-02, role Pi-hole and Unbound, CT100 on PROXMOX.
- Proxmox identifies the guest as an LXC container named dns-02 with VMID 100.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie) on x86_64 with kernel 7.0.14-17-pve.
- The inventory and Nmap data identify the vendor as Proxmox Server Solutions GmbH.
- TCP port 22 is open and provides OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 53 is open and provides dnsmasq 2.93; the service metadata includes pi-hole.
- TCP ports 80, 443, and 9100 are open.
- The TLS certificate on port 443 has subject and issuer values identifying pi.hole and Pi-hole.
- Greenbone reports zero matching actionable findings for the current host IP.
- Patching telemetry reports four security updates available and no reboot required.

### Inferences

- This is a managed DNS infrastructure container rather than a physical network appliance.
- The Pi-hole certificate and dnsmasq metadata strongly support Pi-hole as the primary application identity.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-07T14:03:24+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-04T12:32:47+01:00`
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
