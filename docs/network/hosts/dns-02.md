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

- Assessed: `2026-10-08T14:00:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:35:3b:11`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

dns-02 is CT100, a Proxmox LXC container running Debian GNU/Linux 13. It is documented as the Pi-hole and Unbound service host, with SSH, DNS, HTTP, HTTPS, and TCP/9100 ports open. No matching actionable Greenbone findings or pending updates were reported.

### Confirmed facts

- The canonical device name is dns-02.
- The device is an LXC container, CT100, managed by Proxmox on node PROXMOX.
- The documented role is Pi-hole and Unbound.
- Authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie) on x86_64.
- The reported kernel is 7.0.14-20-pve.
- The reported vendor is Proxmox Server Solutions GmbH.
- Open TCP ports are 22, 53, 80, 443, and 9100.
- TCP/22 is corroborated as OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP/53 is corroborated as dnsmasq 2.93 with Pi-hole information.
- The TLS certificate on port 443 identifies pi.hole.
- Greenbone reported zero matching actionable findings for this host IP.
- Patch telemetry reports zero available updates and no reboot required.

### Inferences

- The host identity is strongly established by the canonical estate record, Proxmox inventory, authoritative OS inventory, and matching service evidence.
- The device is functioning as a DNS filtering/resolution service host consistent with its documented Pi-hole and Unbound role.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-10T03:50:17+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-08T07:56:26+01:00`
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
