# monitor-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `monitor-01` |
| Address | `192.168.2.52` |
| Type | vm |
| Role | Prometheus, Grafana, Alertmanager, Blackbox, Loki and active network discovery (collector, enricher, OS evidence, guest refresh, first-seen notifier), VM202 on Proxmox-2; discovery cutover verified 2026-09-27 |
| Managed by Ansible | Yes |
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
- Summary generated: `2026-10-20T00:21:45+01:00`
- MAC identity: `bc:24:11:0b:16:a2`
- Observed IP address(es): `192.168.2.52`
- Connections: **2,674**
- Traffic sent: **1.9 MiB**
- Traffic received: **4.8 MiB**
- Top services: `ssh` (595), `ssl` (147)
- Top destination ports: `tcp/22` (2525), `tcp/443` (148)

> This bounded summary intentionally excludes raw packet data and external destination IP history.
<!-- END AUTO:ZEEK-FLOW -->

Record reviewed, useful flow summaries rather than raw packet captures.

| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

### Expected flows

- 
- 

### Unexpected or investigated flows

- 

## Internet / DNS activity

Keep this section to **bounded domain/service summaries**. Do not commit a
complete household browsing history.

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

- Assessed: `2026-10-15T16:04:13+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:0b:16:a2`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

monitor-01 is a managed QEMU VM on Proxmox-2 running Debian GNU/Linux 13 (trixie), hosting the documented monitoring and discovery stack. Open services include corroborated OpenSSH on 22/tcp, Grafana HTTP on 3000/tcp, and an additional open 9100/tcp port. Greenbone reports two medium-severity Linux kernel mitigation findings; patch telemetry currently reports no available updates.

### Confirmed facts

- The canonical estate identifies the device as monitor-01, kind vm, managed by Ansible.
- The device is VM202 on Proxmox-2 and has QEMU guest type.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 6.12.111+deb13-cloud-amd64.
- The documented role includes Prometheus, Grafana, Alertmanager, Blackbox, Loki, and active network discovery functions.
- OpenSSH 10.0p2 Debian 7+deb13u4 is identified on TCP port 22 with corroborated service evidence.
- Grafana HTTP is identified on TCP port 3000 with corroborated service evidence.
- TCP port 9100 is reported open, but its Nmap service label is omitted.
- Greenbone reports two matching medium-severity Linux kernel mitigation findings for this host IP.
- Patch telemetry reports zero available security updates and no reboot required.

### Inferences

- The device is a Linux-based monitoring and observability server VM.
- The Proxmox vendor attribution is consistent with the documented QEMU VM placement and inventory vendor field.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-20T16:17:51+01:00`
- Pending updates: **1**
- Security updates pending: **0**
- Reboot required: **Yes**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-19T06:44:49+01:00`
- Patch state: **Attention required**

> Automatic reboot remains disabled by policy; reboot-required state is reported for controlled maintenance.
<!-- END AUTO:PATCHING -->

**19 October ICMP timestamp remediation plan — staged in Git, not deployed:** Read-only audits established `iptables v1.8.11 (nf_tables)`, INPUT ACCEPT with 0 rules, FORWARD DROP, 4 custom chains and absent nft CLI. Scanner-side tests observed 3 timestamp replies to 3 requests with normal ping. Prometheus/Grafana/Loki/Alertmanager run as containers in `/opt/monitoring/docker-compose.yml`, not standalone systemd services. Dedicated `monitor_icmp_timestamp` Ansible role and `greenbone-icmp-timestamp-monitor01-cutover.yml` propose only a comment-tagged ICMP type-13 DROP in host INPUT with persistence; preflight and after checks preserve Grafana HTTPS, running containers and Docker forwarding. Separate scoped rollback staged. **No host changes or new Greenbone scan completed.**

## Monitoring and security

**Live security verification 19 October 2026:** Git-managed host INPUT-only `iptables-nft` ICMP type-13 rule applied using `greenbone-icmp-timestamp-monitor01-cutover.yml`. User supplied passing recap `monitor-01 ok=25 changed=3 failed=0`, scanner `greenbone-01 ok=8 changed=0 failed=0`, zero unreachable. `MONITOR01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, `MONITOR01_ICMP_ECHO=PASS`; Grafana HTTPS, monitoring container identities and Docker forwarding policy unchanged; no container/Docker restart. Dedicated persistent systemd unit installed (reboot resilience not tested). Explicit ICMP-only rollback `playbooks/greenbone-icmp-timestamp-monitor01-rollback.yml` remains unused. Greenbone scan confirmation and accepted-risk register reconciliation still outstanding. Previous nearby Git-staged statements are superseded by this live evidence.


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
