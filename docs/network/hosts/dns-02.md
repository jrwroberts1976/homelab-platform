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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `bc:24:11:35:3b:11`
- Observed IP address(es): `192.168.2.50`
- Connections: **105,129**
- Traffic sent: **4.0 MiB**
- Traffic received: **72.5 MiB**
- Top services: `dns` (104807), `ntp` (184), `ssl` (12)
- Top destination ports: `udp/53` (104610), `tcp/53` (198), `udp/123` (184), `icmp/3` (125), `tcp/443` (12)

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

- Assessed: `2026-10-01T11:14:11+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:35:3b:11`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC container CT100 providing Pi-hole and Unbound at 192.168.2.50. Authoritative inventory reports Debian GNU/Linux 13 (trixie), x86_64. Four security updates are available; no matching Greenbone findings were reported.

### Confirmed facts

- Canonical estate identity is dns-02, an LXC container named dns-02 on PROXMOX.
- The documented role is Pi-hole and Unbound, CT100 on PROXMOX.
- The authoritative Zabbix Agent 2 OS fact is Debian GNU/Linux 13 (trixie) on x86_64.
- The authoritative kernel is 7.0.14-17-pve.
- Open TCP ports are 22, 53, 80, 443, and 9100.
- OpenSSH 10.0p2 Debian 7+deb13u4 is identified on TCP port 22.
- dnsmasq 2.93 with extra information 'pi-hole' is identified on TCP port 53.
- The TLS certificate on port 443 identifies pi.hole and Pi-hole.
- The host has four security updates and five total updates available, with no reboot required.
- Greenbone reported zero actionable findings matching the current host IP.

### Inferences

- The device is best classified as a managed Linux-based infrastructure container rather than a standalone physical network appliance.
- The detected web and port-9100 service labels indicate exposed services, but their specific host functions are not established by the supplied evidence.

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
