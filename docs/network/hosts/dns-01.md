# dns-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `dns-01` |
| Address | `192.168.2.51` |
| Type | lxc |
| Role | Pi-hole and Unbound, CT101 on Proxmox-2 |
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
- Summary generated: `2026-10-27T00:23:49+00:00`
- MAC identity: `bc:24:11:c3:75:ba`
- Observed IP address(es): `192.168.2.51`
- Connections: **72,414**
- Traffic sent: **3.8 MiB**
- Traffic received: **15.6 MiB**
- Top services: `dns` (72162), `ntp` (192), `ssl` (14), `http` (2)
- Top destination ports: `udp/53` (72099), `udp/123` (192), `tcp/53` (63), `icmp/3` (44), `tcp/443` (14), `tcp/80` (2)

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

- Assessed: `2026-10-29T17:01:31+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:c3:75:ba`
- Identity confidence: **high**
- OS confidence: **high**
- Exact OS: **Debian GNU/Linux 13 (trixie)**
- Manual review required: **No**

### Assessment summary

Managed Debian 13 LXC container CT101 on Proxmox-2, providing Pi-hole and Unbound DNS services. SSH and DNS are identified; ports 80, 443, and 9100 are open. No actionable Greenbone findings match the current host IP.

### Confirmed facts

- The canonical estate identity is dns-01, an LXC container named dns-01 on Proxmox-2.
- The container is CT101 with VMID 101 and is managed by Ansible.
- Authoritative Zabbix Agent 2 inventory reports Debian GNU/Linux 13 (trixie), kernel 7.0.14-20-pve, architecture x86_64.
- OpenSSH 10.0p2 Debian 7+deb13u4 is identified on TCP port 22.
- dnsmasq 2.93 with Pi-hole extra information is identified on TCP port 53.
- TCP ports 80, 443, and 9100 are open.
- The TLS certificate on port 443 has subject and issuer information identifying pi.hole and Pi-hole.
- Greenbone reports zero actionable findings matching this host IP.
- Patch telemetry reports three updates available, zero security updates available, and no reboot required.
- The bounded Loki sample contains network-connectivity wait-online timeout and error messages.

### Inferences

- The host functions as the estate's Pi-hole and Unbound DNS container, based on its canonical role and identified DNS/Pi-hole service.
- The Proxmox vendor attribution likely reflects the virtualization/container platform rather than the guest operating-system vendor.
- The sampled connectivity messages merit operational review, but the bounded log sample does not establish a persistent outage.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-10-30T09:14:32+00:00`
- Pending updates: **3**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-10-24T07:12:46+01:00`
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
