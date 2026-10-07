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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-10-01T11:34:08+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `d8:3a:dd:5a:51:44`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

docker-01 is a physical Raspberry Pi 4 BirdNET-Go Docker host running authoritative Debian GNU/Linux 13 (trixie) on aarch64. Open services include SSH on 22, HTTP on 8080, and open ports 111 and 9100. No matching actionable Greenbone findings were reported; 16 security updates are available.

### Confirmed facts

- The canonical estate name is docker-01.
- The device is documented as physical and managed by Ansible.
- Its canonical role is Raspberry Pi 4 BirdNET-Go Docker host.
- The vendor is Raspberry Pi Trading.
- Authoritative Zabbix Agent 2 facts report architecture aarch64.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie).
- TCP port 22 is open and provides OpenSSH 10.0p2 Debian 7+deb13u4.
- TCP port 8080 is open and provides a Golang net/http server.
- TCP ports 111 and 9100 are open; their Nmap service labels were omitted.
- Greenbone reported zero matching actionable findings for the current host IP.
- Patch telemetry reports 16 security updates and 131 total updates available, with no reboot required.

### Inferences

- The host is a Raspberry Pi 4-based Linux server supporting Docker workloads, consistent with its canonical estate role.
- The HTTP service on port 8080 may provide an application or management endpoint, but its specific application is not established by the supplied evidence.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-07T12:16:08+01:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-05T21:24:51+01:00`
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
