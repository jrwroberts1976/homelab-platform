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

- Assessed: `2026-10-22T17:02:35+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `d8:3a:dd:5a:51:44`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

docker-01 is a managed Raspberry Pi 4 running Debian 13 (trixie) on aarch64 and hosting BirdNET-Go in Docker. Open services include SSH, HTTP/HTTPS, and two additional open TCP ports. No matching actionable Greenbone findings were reported; 25 updates are available, including zero security updates.

### Confirmed facts

- The canonical estate identity is docker-01, a physical host managed by Ansible.
- The documented role is Raspberry Pi 4 BirdNET-Go Docker host.
- The vendor is Raspberry Pi Trading.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), with aarch64 architecture and kernel 6.18.50+rpt-rpi-v8.
- The hostname is docker-01.jameshouse and the IP address is 192.168.2.220.
- TCP ports 22, 80, 111, 443, and 9100 are open.
- OpenSSH 10.0p2 Debian 7+deb13u4 is identified on TCP port 22.
- nginx is identified on TCP ports 80 and 443, with TLS indicated on port 443.
- A Golang net/http server is identified on TCP port 8080.
- Greenbone reported zero matching actionable findings for the current host IP.
- Patch telemetry reports 25 updates available, zero security updates available, unattended upgrades enabled, and no reboot required.
- Bounded Loki samples contain BirdNET_V2.4 pipeline activity using the Garden Room USB Microphone.

### Inferences

- The host is serving infrastructure and application workloads consistent with its documented Docker-host role.
- The BirdNET-Go workload is evidenced by the documented estate role and sampled BirdNET_V2.4 application logs.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-24T09:02:56+01:00`
- Pending updates: **27**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-24T06:45:26+01:00`
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
