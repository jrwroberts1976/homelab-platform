# asus-router

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `asus-router` |
| Address | `192.168.2.1` |
| Type | network |
| Role | ASUS RT-AC86U router, DHCP, AiMesh controller and OpenVPN remote-access endpoint |
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
- Summary generated: `2026-10-09T00:23:16+01:00`
- MAC identity: `24:4b:fe:5e:cc:c8`
- Observed IP address(es): `192.168.2.1`
- Connections: **1,411**
- Traffic sent: **7.2 MiB**
- Traffic received: **255 B**
- Top services: `dhcp` (17), `http` (2)
- Top destination ports: `udp/9999` (574), `udp/5514` (358), `udp/1900` (243), `udp/45280` (143), `udp/7788` (53), `udp/68` (17)

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

- Assessed: `2026-10-08T11:05:00+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `24:4b:fe:5e:cc:c8`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Identified as the ASUS RT-AC86U router at 192.168.2.1, serving as the documented router, DHCP, AiMesh controller, and OpenVPN endpoint. Exact operating system is not established by the supplied evidence.

### Confirmed facts

- The canonical estate record identifies this device as an ASUS RT-AC86U named asus-router.
- Its documented role is Router, DHCP, AiMesh controller and OpenVPN remote-access endpoint.
- The device is online at 192.168.2.1 and has vendor ASUSTek Computer.
- TCP port 22 exposes Dropbear sshd protocol 2.0.
- TCP port 53 exposes Cloudflare public DNS.
- TCP port 80 is open.
- TCP port 8443 exposes HTTPS-alt with TLS.
- The TLS certificate for port 8443 is for jrwroberts1976.asuscomm.com and is issued by Let's Encrypt.
- No matching actionable Greenbone findings were reported for the current IP; this does not establish that the device is vulnerability-free.
- The supplied Nmap profile has no OS matches and reports missing OS evidence.

### Inferences

- The device is consistent with embedded router firmware associated with the ASUS RT-AC86U.
- The exact operating system and firmware version cannot be determined from the supplied evidence.

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
