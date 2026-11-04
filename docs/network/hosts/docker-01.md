# docker-01 <!-- historical -->

> **RETIRED HISTORICAL RECORD — NOT AN ACTIVE HOST.** The former `docker-01` Raspberry Pi was repurposed as `router-01` (`192.168.2.1`). The old Docker/BirdNET workload and `asus-router` **gateway identity** are retired; the physical ASUS RT-AC86U remains in service at `192.168.2.2` as an access point/AiMesh controller, not as the routing gateway. Retain dated evidence below for history only; do not use this page for live inventory, monitoring or deployment. Current truth: `IaC/inventory/estate.json` and `docs/architecture/CURRENT-STATE.md`. <!-- historical -->
>
> Keep secrets and raw packet/DNS captures out of Git.

## Identity

| Field | Value |
|---|---|
| Canonical name | `docker-01` | <!-- historical -->
| Former address | `192.168.2.220` (historical; not an active `docker-01` assignment) | <!-- historical -->
| Type | physical |
| Former role | Raspberry Pi 4 BirdNET-Go Docker host (retired) |
| Managed by Ansible | Yes |
| State | **Retired** — successor identity `router-01` |

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

- Assessed: `2026-11-03T15:04:11+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `d8:3a:dd:5a:51:44`
- Identity confidence: **medium**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

Documented as an ASUS RT-AC86U router at 192.168.2.1, providing DHCP, AiMesh control, and OpenVPN remote access. The observed Raspberry Pi Trading MAC vendor conflicts with the documented model and warrants review; no exact OS or open services were identified.

### Confirmed facts

- Canonical estate identifies this device as ASUS RT-AC86U.
- Canonical estate identifies the device as a network router providing DHCP, AiMesh controller, and OpenVPN remote-access functions.
- The device hostname is router-01.jameshouse and telemetry hostname is router-01.
- The device IP address is 192.168.2.1.
- The observed MAC vendor is Raspberry Pi Trading.
- Nmap reported no TCP or UDP ports and no OS matches.
- No actionable Greenbone findings matched the current IP in the supplied scan data.
- The device was online at the time of inventory.

### Inferences

- The device is most likely an embedded router platform running vendor firmware.
- The canonical ASUS identity is more specific than the available network-service evidence, but the Raspberry Pi Trading vendor attribution creates an identity discrepancy.

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

> **Historical evidence only:** all changes described in this section were made before retirement of the `docker-01` role. Do not repeat these playbooks on `router-01` without a separately reviewed design. <!-- historical -->

**Verified 19 October 2026 live security change:** Read-only diagnostics identified `iptables v1.8.11 (nf_tables)`, INPUT ACCEPT with zero rules before installation, and Docker-controlled FORWARD/DOCKER chains; three of three Greenbone-side ICMP timestamp probes were answered before mitigation. Then `greenbone-icmp-timestamp-docker01-cutover.yml` installed a **single host INPUT-only IPv4 ICMP timestamp-request (type 13) DROP rule** plus dedicated one-shot persistence unit. Play recap `docker-01 ok=22 changed=3 failed=0`, `greenbone-01 ok=8 changed=0 failed=0`. Scanner-side ICMP timestamp responses now `NO_REPLY_OBSERVED` and ordinary ping PASS. Two Docker containers, Docker chain definitions/policy and BirdNET HTTPS were verified, without Docker restart. Manual rollback: `playbooks/greenbone-icmp-timestamp-docker01-rollback.yml`. Reboot persistence and fresh Greenbone scan clearance remain **unverified**. Risk acceptances are unchanged. <!-- historical -->

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
