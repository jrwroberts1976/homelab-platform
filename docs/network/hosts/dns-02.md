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

- Assessed: `2026-10-01T10:06:08+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:35:3b:11`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC CT100 providing Pi-hole and Unbound DNS services. Linux is strongly indicated by Nmap and service evidence, but the exact guest OS is not established. Four security updates are available; no actionable Greenbone findings matched this IP.

### Confirmed facts

- The canonical estate identity is dns-02, an LXC container named CT100 on PROXMOX.
- The documented role is Pi-hole and Unbound.
- Proxmox inventory identifies the guest type as LXC and the vendor as Proxmox Server Solutions GmbH.
- The host is online at 192.168.2.50 and is named dns-02.jameshouse.
- OpenSSH 10.0p2 with Debian 7+deb13u4 is exposed on TCP port 22.
- dnsmasq 2.93 with extra information 'pi-hole' is exposed on TCP port 53.
- The TLS certificate on TCP port 443 identifies pi.hole and Pi-hole.
- Nmap identifies Linux matches with highest reported accuracy of 97%.
- Four security updates and five total updates are available; a reboot is not required.
- Greenbone reported zero actionable findings matching 192.168.2.50 in the supplied results.

### Inferences

- The device is best classified as a Linux-based service container rather than a physical appliance.
- The guest is likely Debian-based, but the supplied evidence does not establish an exact distribution or OS version.
- The TCP 80, 443, and 9100 service labels are tentative and do not by themselves establish additional host functions.

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
