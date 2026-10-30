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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `d8:3a:dd:5a:51:44`
- Observed IP address(es): `192.168.2.220`
- Connections: **45**
- Traffic sent: **290.3 KiB**
- Traffic received: **132.3 MiB**
- Top services: `ssl` (40), `http` (4), `dns` (1)
- Top destination ports: `tcp/443` (40), `tcp/80` (4), `udp/5353` (1)

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

- Assessed: `2026-10-29T17:01:31+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `d8:3a:dd:5a:51:44`
- Identity confidence: **low**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

192.168.2.1 is documented as the ASUS RT-AC86U router, DHCP server, AiMesh controller, and OpenVPN endpoint, but current inventory identifies an online _gateway with Raspberry Pi Trading hardware and Nmap results resembling several Linux/NAS platforms. Identity requires manual review.

### Confirmed facts

- The canonical estate record labels this device ASUS RT-AC86U, named asus-router, with router, DHCP, AiMesh-controller, and OpenVPN-endpoint roles.
- The device is online at 192.168.2.1 with hostname and telemetry hostname _gateway.
- Inventory and Nmap identify the vendor as Raspberry Pi Trading; MAC address is d8:3a:dd:5a:51:44.
- TCP ports 22, 53, 80, 443, 111, 8443, and 9100 are reported open across the supplied evidence.
- Port 8443 is reported as HTTPS-alt and presents a Let's Encrypt certificate for jrwroberts1976.asuscomm.com.
- Nmap reports nginx on ports 80 and 443.
- The Nmap OS matches are conflicting and include Western Digital My Cloud, Linux kernel 3.x through 5.x, and QNAP QTS.

### Inferences

- The host is likely a Linux-based embedded gateway or network appliance, but the supplied evidence does not establish the exact hardware or firmware.
- The canonical ASUS router identity conflicts with the Raspberry Pi Trading inventory identity and the _gateway hostname.
- The differing SSH service reports—Dropbear in enrichment and OpenSSH in the Nmap profile—should be treated as unresolved service evidence.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-27T10:09:59+00:00`
- Pending updates: **2**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-25T17:09:48+00:00`
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
