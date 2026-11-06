# komodo-01

> Persistent private host record. Do not store passwords, API tokens, recovery keys, full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `komodo-01` |
| Address | `192.168.2.58` |
| Type | lxc |
| Role | Komodo container-management control-plane host, CT104 on PROXMOX; Docker, MongoDB and Komodo Core commissioned; application backup and isolated restore validated |
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

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
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

- Assessed: `2026-11-03T18:04:04+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `02:00:00:00:01:04`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

komodo-01 is the documented Komodo container-management control-plane LXC (CT104) on Proxmox. Docker, MongoDB, and Komodo Core are commissioned. No exact OS is available; Nmap reported no OS matches or open ports. Patch telemetry is current with no available updates, while sampled logs include network-online timeout errors.

### Confirmed facts

- The hostname is komodo-01.jameshouse and the telemetry hostname is komodo-01.
- The canonical estate kind is lxc, managed by Ansible, with role Komodo container-management control-plane host, CT104 on PROXMOX.
- Docker, MongoDB, and Komodo Core are documented as commissioned.
- The host is online at 192.168.2.58.
- Authoritative OS status is unavailable and the inventory OS field is empty.
- Nmap completed with no OS matches and no listed TCP or UDP ports.
- Patch status is ok, with zero available updates and unattended upgrades enabled.
- Greenbone reports zero actionable findings matching the current IP; this is not proof that the host is vulnerability-free.
- Sampled logs include a systemd-networkd-wait-online error and a timeout waiting for network connectivity.

### Inferences

- The device is a Linux-oriented container environment based on its documented LXC classification and container-management role.
- The exact guest distribution, kernel, and firmware cannot be determined from the supplied evidence.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-11-06T16:43:44+00:00`
- Pending updates: **3**
- Security updates pending: **0**
- Reboot required: **No**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-11-06T06:13:24+00:00`
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
