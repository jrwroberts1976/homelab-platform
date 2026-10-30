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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `24:4b:fe:5e:cc:c8`
- Observed IP address(es): `192.168.2.1`
- Connections: **1,110**
- Traffic sent: **6.1 MiB**
- Traffic received: **130 B**
- Top services: `dhcp` (7), `http` (1)
- Top destination ports: `udp/5514` (358), `udp/9999` (286), `udp/36996` (144), `tcp/2869` (140), `udp/1900` (98), `udp/61562` (18)

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

- Assessed: `2026-10-29T13:02:13+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `24:4b:fe:5e:cc:c8`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **Yes**

### Assessment summary

192.168.2.180 is an online ASUS-vendor device reporting the hostname _gateway. No ports, services, DNS hints, or OS fingerprints were available, so its exact role and operating system remain unresolved.

### Confirmed facts

- The device IP is 192.168.2.180.
- The observed hostname is _gateway.
- The MAC vendor is ASUSTek Computer.
- The device is marked online in inventory.
- Nmap OS identification is incomplete and returned no OS matches.
- No TCP or UDP ports were reported by Nmap.
- No actionable Greenbone findings matched this IP in the supplied scan result.

### Inferences

- The _gateway hostname suggests a gateway or other network-appliance role.
- The device likely uses embedded network-appliance firmware, but the exact operating system is unsupported by the evidence.

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
