# home-01

> Persistent private host record. Do not store passwords, API tokens, recovery keys, full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `home-01` |
| Address | `192.168.2.60` |
| Type | vm |
| Role | Home Assistant OS 18.2, VM204 on PROXMOX |
| Managed by Ansible | No |
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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `02:00:00:00:02:04`
- Observed IP address(es): `192.168.2.60`
- Connections: **8,776**
- Traffic sent: **8.9 MiB**
- Traffic received: **12.5 MiB**
- Top services: `http` (6054), `ssl` (2309), `ntp` (68), `dns` (28)
- Top destination ports: `tcp/58153` (5910), `tcp/853` (1498), `tcp/443` (837), `udp/1900` (288), `tcp/80` (144), `udp/123` (68)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->
| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

### Expected flows
- 

### Unexpected or investigated flows
- 

## Internet / DNS activity
Keep only bounded domain/service summaries, not complete browsing history.

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

- Assessed: `2026-10-29T13:02:13+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:02:04`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Likely Home Assistant host at 192.168.2.165, identified by hostname, Home Assistant DNS activity, and an aiohttp HTTP service. Exact OS is not established. Router telemetry also lists the hostname at 192.168.2.60, so the address association merits review.

### Confirmed facts

- The observed hostname is homeassistant.
- The current host IP is 192.168.2.165.
- TCP port 80 is open and identified with corroborated evidence as aiohttp, Python 3.14.3.
- TCP port 111 is open; no service label is available in the supplied evidence.
- Nmap reports Linux 4.15–5.19 as its highest-confidence OS match, but this is an identification result rather than an authoritative OS fact.
- DNS telemetry includes checkonline.home-assistant.io, _checkdns.home-assistant.io, version.home-assistant.io, and beekeeper.hivehome.com.
- The router telemetry lists hostname homeassistant at 192.168.2.60.
- No actionable Greenbone findings match 192.168.2.165; this does not prove the host is vulnerability-free.

### Inferences

- The hostname and Home Assistant-related DNS activity strongly support identification as a Home Assistant home-automation host.
- The host likely runs on a Linux-based platform, but the exact distribution, kernel, firmware, and version are unsupported by the evidence.
- The vendor association with Home Assistant is inferred from the hostname and DNS activity rather than a direct vendor record.

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
