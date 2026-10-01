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
- Summary generated: `2026-10-01T00:23:08+01:00`
- MAC identity: `bc:24:11:0b:16:a2`
- Observed IP address(es): `192.168.2.52`
- Connections: **949**
- Traffic sent: **1.7 MiB**
- Traffic received: **124.9 MiB**
- Top services: `ssh` (570), `ssl` (197), `http` (12), `dns` (5)
- Top destination ports: `tcp/22` (578), `tcp/443` (172), `tcp/8443` (35), `tcp/80` (29), `tcp/53` (8), `tcp/9443` (8)

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

- Assessed: `2026-10-01T11:32:32+01:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:0b:16:a2`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Managed Debian 13 VM202 on Proxmox-2 providing Prometheus, Grafana, Alertmanager, Blackbox, Loki, and network-discovery services. OpenSSH, Grafana HTTP, and port 9100 are reported; two updates are pending and a reboot is required. No matching actionable Greenbone findings were reported.

### Confirmed facts

- The canonical estate identity is monitor-01, kind vm, role managed by Ansible.
- The VM is QEMU guest monitor-01, VMID 202, on Proxmox-2.
- The MAC vendor and inventory vendor are Proxmox Server Solutions GmbH.
- Authoritative Zabbix Agent 2 facts identify the OS as Debian GNU/Linux 13 (trixie), architecture x86_64, with kernel 6.12.107+deb13-cloud-amd64.
- Open services are OpenSSH 10.0p2 Debian 7+deb13u4 on TCP port 22, Grafana HTTP on TCP port 3000, and TCP port 9100 reported with the jetdirect label.
- The host is online at 192.168.2.52 and has hostname monitor-01.jameshouse in inventory and Nmap metadata.
- Patching reports two updates available, no security updates available, and a reboot required.
- Greenbone reports zero matching actionable findings for the current host IP.

### Inferences

- This is a managed infrastructure and observability collector VM based on its documented estate role and exposed Grafana/SSH services.
- The platform family is Debian Linux, directly supported by the authoritative OS fact.

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
