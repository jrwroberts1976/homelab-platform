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

- Evidence source: `sensor-01` Zeek connection telemetry
- Rolling window: 24 hours
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `bc:24:11:c3:75:ba`
- Observed IP address(es): `192.168.2.51`
- Connections: **580,170**
- Traffic sent: **22.3 MiB**
- Traffic received: **383.3 MiB**
- Top services: `dns` (579220), `ntp` (192), `ssl` (12)
- Top destination ports: `udp/53` (578270), `tcp/53` (957), `icmp/3` (739), `udp/123` (192), `tcp/443` (12)

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
- MAC identity: `bc:24:11:c3:75:ba`
- Identity confidence: **high**
- OS confidence: **medium**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Managed Proxmox LXC container CT101 providing Pi-hole and Unbound DNS services. Linux is strongly indicated; exact OS is not established. Four security updates and five total updates are available for review. No matching actionable Greenbone findings were reported for 192.168.2.51, which does not prove the host is vulnerability-free.

### Confirmed facts

- The canonical estate record identifies dns-01 as an LXC container, managed by Ansible, with the role Pi-hole and Unbound on CT101 on Proxmox-2.
- The Proxmox cluster API identifies guest type lxc, name dns-01, node Proxmox-2, and VMID 101.
- The host is online at 192.168.2.51 and has hostname dns-01.jameshouse.
- Nmap completed OS detection and identified Linux 4.15–5.19 as its highest-confidence match at 96%.
- OpenSSH 10.0p2 with Debian 7+deb13u4 is detected on TCP port 22.
- dnsmasq 2.93 with extra information pi-hole is detected on TCP port 53.
- TCP ports 80, 443, and 9100 are open; Nmap labels them webdav, SSL webdav, and jetdirect respectively, without product or version evidence.
- Greenbone reported zero matching actionable findings for this host IP.
- Patch telemetry reports four security updates and five total updates available; unattended upgrades are disabled and no reboot is required.

### Inferences

- The host is most likely a Debian-family Linux userspace running inside a Proxmox LXC container, based on the Debian OpenSSH build and Linux Nmap fingerprint.
- The detected DNS service is consistent with the documented Pi-hole role.
- The exact Linux distribution release and kernel version cannot be established from the supplied evidence.
- The Nmap labels for ports 80, 443, and 9100 are tentative because they lack corroborating product or version evidence.

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
