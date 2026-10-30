# asus-aimesh-181

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `asus-aimesh-181` |
| Address | `192.168.2.181` |
| Type | network |
| Role | ASUS AiMesh node |
| Managed by Ansible | No |
| State | Active |

## Network identity
- MAC address:
- Vendor/OUI:
- Hostname / DHCP name:
- VLAN / network:
- Physical location or hypervisor:

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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `04:d4:c4:b8:52:28`
- Observed IP address(es): `192.168.2.181`
- Connections: **3,491**
- Traffic sent: **3.2 MiB**
- Traffic received: **297.6 KiB**
- Top services: `ntp` (40), `ssl` (7), `dns` (1), `dhcp` (1)
- Top destination ports: `tcp/7788` (3113), `udp/9999` (136), `udp/123` (40), `tcp/443` (7), `udp/5353` (1), `udp/67` (1)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->
| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

## Internet / DNS activity
Use bounded domain/service summaries only; do not commit a complete household browsing history.

| Service / domain family | Example domains | Evidence source | Last observed | Interpretation |
|---|---|---|---|---|
| | | | | |

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-10-29T14:02:32+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `04:d4:c4:b8:52:28`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely an ASUS RT-AC86U wireless router running embedded firmware. The host exposes Dropbear SSH and web services; the exact firmware/OS is not established.

### Confirmed facts

- The hostname is RT-AC86U-5228.
- The inventory and Nmap vendor is ASUSTek Computer.
- The MAC address is 04:d4:c4:b8:52:28.
- TCP port 22 is open and identified as Dropbear sshd, protocol 2.0.
- TCP ports 80 and 8443 are open.
- Nmap reported a Linux 3.2–4.14 fingerprint with 100% match accuracy.
- DNS top domains include routerahs.asus.com and fwupdate.asuswrt-merlin.net.
- Greenbone reported zero matching actionable findings for the current IP; this does not prove the host is vulnerability-free.

### Inferences

- The RT-AC86U model-like hostname, ASUSTek vendor, and ASUS-related DNS domains strongly support identification as an ASUS RT-AC86U-class router.
- The device likely uses embedded Linux-based firmware, but the exact OS and firmware version are unsupported by the evidence.

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
