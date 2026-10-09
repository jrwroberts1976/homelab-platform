# docker-01

> Persistent private host record. Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `docker-01` |
| Address | `192.168.2.220` |
| Type | physical |
| Role | Raspberry Pi 4 BirdNET-Go Docker host |
| Managed by Ansible | Yes |
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
- MAC identity: `d8:3a:dd:5a:51:44`
- Observed IP address(es): `192.168.2.220`
- Connections: **41**
- Traffic sent: **73.8 KiB**
- Traffic received: **3.9 MiB**
- Top services: `ssl` (35), `http` (5), `dns` (1)
- Top destination ports: `tcp/443` (35), `tcp/80` (5), `udp/5353` (1)

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

- Assessed: `2026-10-08T15:00:50+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `d8:3a:dd:5a:51:44`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

docker-01 is a managed physical Raspberry Pi 4 running Debian GNU/Linux 13 on aarch64 as a BirdNET-Go Docker host. Open services include corroborated OpenSSH on 22/tcp and a Golang HTTP server on 8080/tcp; 111/tcp and 9100/tcp are also open. No matching actionable Greenbone findings or pending updates were reported, while sampled logs show Loki ingestion and Docker log-streaming errors requiring review.

### Confirmed facts

- The canonical device name is docker-01.
- The device is documented as a physical Raspberry Pi 4 BirdNET-Go Docker host.
- The device is managed by Ansible.
- The vendor is Raspberry Pi Trading.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), with aarch64 architecture and kernel 6.18.50+rpt-rpi-v8.
- 22/tcp is open and provides OpenSSH 10.0p2 Debian 7+deb13u4; the service evidence is corroborated.
- 8080/tcp is open and provides a Golang net/http server; the service evidence is corroborated.
- 111/tcp and 9100/tcp are open.
- There are zero matching actionable Greenbone findings for the current host IP.
- Patch telemetry reports zero available updates and no reboot required.
- The sampled Loki data contains repeated log-delivery HTTP 400 errors and Docker log-streaming errors.

### Inferences

- The host is a Raspberry Pi-based Linux server used to run containerized workloads.
- The documented Docker-host role is consistent with the observed SSH and HTTP services, but the supplied evidence does not identify the application exposed on port 8080.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-09T16:29:38+01:00`
- Pending updates: **3**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-08T06:19:13+01:00`
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
