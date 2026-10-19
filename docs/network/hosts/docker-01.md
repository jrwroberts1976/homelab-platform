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

- Assessed: `2026-10-15T16:04:13+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `d8:3a:dd:5a:51:44`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

docker-01 is a managed physical Raspberry Pi 4 host running Debian GNU/Linux 13 (trixie) on aarch64, hosting BirdNET-Go in Docker. OpenSSH and a Go HTTP service are exposed. Greenbone reports three medium-severity kernel mitigation findings; patch telemetry shows no pending security updates and no reboot required.

### Confirmed facts

- Canonical estate identity is docker-01, a physical Raspberry Pi 4 BirdNET-Go Docker host.
- The vendor is Raspberry Pi Trading.
- Authoritative Zabbix Agent 2 facts report Debian GNU/Linux 13 (trixie), aarch64, kernel 6.18.50+rpt-rpi-v8.
- The host is online at 192.168.2.220 and uses hostname docker-01.
- TCP ports 22, 111, 8080, and 9100 are open.
- Port 22 provides corroborated OpenSSH 10.0p2 Debian 7+deb13u4.
- Port 8080 provides a corroborated Golang net/http server.
- Greenbone reports three matching medium-severity kernel mitigation findings: CVE-2022-27672, CVE-2017-5715, and CVE-2018-3639.
- Patch telemetry reports 0 security updates available, 10 total updates available, unattended upgrades enabled, and no reboot required.
- Bounded Loki samples show BirdNET_V2.4 processing audio from the Garden Room USB Microphone.

### Inferences

- The host is likely used as the estate's container workload node for BirdNET-Go, consistent with its canonical role and Docker-scoped logs.
- The exposed Go HTTP service on port 8080 may be an application or management endpoint, but its specific function is not established by the supplied evidence.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-19T13:01:26+01:00`
- Pending updates: **20**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-19T06:56:04+01:00`
- Patch state: **Healthy**

> Automatic reboot remains disabled by policy; reboot-required state is reported for controlled maintenance.
<!-- END AUTO:PATCHING -->

## Monitoring and security

**Verified 19 October 2026 live security change:** Read-only diagnostics identified `iptables v1.8.11 (nf_tables)`, INPUT ACCEPT with zero rules before installation, and Docker-controlled FORWARD/DOCKER chains; three of three Greenbone-side ICMP timestamp probes were answered before mitigation. Then `greenbone-icmp-timestamp-docker01-cutover.yml` installed a **single host INPUT-only IPv4 ICMP timestamp-request (type 13) DROP rule** plus dedicated one-shot persistence unit. Play recap `docker-01 ok=22 changed=3 failed=0`, `greenbone-01 ok=8 changed=0 failed=0`. Scanner-side ICMP timestamp responses now `NO_REPLY_OBSERVED` and ordinary ping PASS. Two Docker containers, Docker chain definitions/policy and BirdNET HTTPS were verified, without Docker restart. Manual rollback: `playbooks/greenbone-icmp-timestamp-docker01-rollback.yml`. Reboot persistence and fresh Greenbone scan clearance remain **unverified**. Risk acceptances are unchanged.

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
