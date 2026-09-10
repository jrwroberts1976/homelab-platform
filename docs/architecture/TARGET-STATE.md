# Target-State Architecture

**Updated:** 10 September 2026  
**Status:** approved working target; implementation continues incrementally

The homelab has moved beyond the original greenfield discovery phase. Core host roles are now established and the remaining work is focused on access, logging, recovery and retiring the last legacy consolidation host.

## Core principles

- `admin-01` is the dedicated administration and IaC controller.
- The two Proxmox hosts remain standalone unless a future cluster design is separately justified and validated.
- Infrastructure services run in explicit VMs/LXCs rather than directly on the hypervisors.
- Physical Raspberry Pis are reserved for roles that benefit from location, media hardware, low power or direct peripheral access.
- Public ingress to selected internal services uses Cloudflare Tunnel + Access rather than direct router port-forwards.
- Monitoring and central logging are separate concerns but converge on `monitor-01`/Grafana for operations.
- Git/IaC and documented recovery paths are authoritative; manual GUI-only state is not.
- Legacy systems are removed only after persistent data, secrets and recovery dependencies are accounted for.

## Target host roles

| Asset | Target role |
|---|---|
| `admin-01` / Pi 3 / `.48` | Dedicated administration, SSH jump host, Git/Ansible/SOPS controller |
| `PROXMOX` / `.70` | Primary standalone Proxmox compute/storage host and `ntp-01` |
| `Proxmox-2` / `.71` | Secondary standalone Proxmox compute host and `ntp-02` |
| `monitor-01` / `.52` | Metrics, alerting, dashboards and central logging platform |
| `dns-01` / `.51` | Primary Pi-hole + Unbound resolver |
| `dns-02` / `.50` | Secondary Pi-hole + Unbound resolver |
| `mail-relay-01` / `.54` | Internal SMTP relay for homelab notifications |
| `sensor-01` / `.55` | Passive network/security sensor platform |
| `cloud-01` / `.53` | Private cloud/data service platform |
| `edge-01` / `.56` | Dedicated Cloudflare Tunnel connector / edge ingress host |
| `media-01` / Pi 5 / `.195` | Dedicated Kodi/media endpoint |
| current Pi 4 `TestServer` / `.220` | Rebuild as dedicated garden BirdNET-Go host after legacy retirement |
| `ids-01` | Retired; no active target role |

## Cloudflare access target

The approved remote-access architecture is:

```text
Internet
   |
   v
Cloudflare Zero Trust / Access
   |
   v
Cloudflare Tunnel
   |
   v
edge-01 (CT103 on Proxmox-2)
   |
   +--> only explicitly published internal services
```

Design rules:

- no inbound router port-forward is required for the tunnel;
- Cloudflare Access protects administrative web applications;
- prefer passkeys/security keys/strong MFA where supported, with TOTP fallback;
- machine/API integrations use service authentication rather than interactive MFA;
- tunnel credentials remain outside Git;
- adding a public hostname is a reviewed configuration change, not an implicit wildcard exposure.

## Monitoring and central logging target

`monitor-01` is the operations platform.

Current metrics stack:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter

Target logging stack:

- Loki on `monitor-01` or its directly managed monitoring stack;
- Alloy collectors on approved hosts/sources;
- low-cardinality labels;
- Git-managed scrape/collection policy;
- Grafana queries/dashboards for logs;
- health alerts for ingestion failures and storage pressure.

The existing ASUS router syslog receiver on `monitor-01` is the first validated central-log source. The old TestServer logging configuration is reference material only and is not migrated wholesale.

## DNS resilience target

The DNS architecture is complete in principle:

```text
dns-01  192.168.2.51  CT101 on Proxmox-2  primary
dns-02  192.168.2.50  CT100 on PROXMOX    secondary
```

Both run Pi-hole + Unbound. DHCP remains on the ASUS router and advertises the two resolver addresses. `192.168.2.48` is now `admin-01` and must never be treated as a DNS resolver merely because historical documents once used that address for DietPi.

## Security target

Passive monitoring and active vulnerability scanning remain separate roles.

`sensor-01` is the passive sensor platform on `PROXMOX`. The HP ProCurve port 24 mirror/SPAN path remains reserved for network capture. Suricata and Zeek deployment/validation should be documented and reproducible.

Greenbone/vulnerability-scanning placement must remain independent of the capture sensor and should not run directly on a Proxmox hypervisor.

## Backup and recovery target

Every infrastructure service needs both configuration reproducibility and a tested data-recovery path where data matters.

Priorities:

- define/test Proxmox guest backup and restore;
- keep Git/IaC outside any single homelab host;
- verify recovery of DNS, monitoring, mail relay, edge and cloud services;
- protect BirdNET data/configuration separately from the old TestServer image;
- complete the WD 4 TB SMART investigation before assigning it a dependable backup role;
- never use a disk with unresolved historical media errors as the sole copy of irreplaceable data.

## Raspberry Pi target roles

Physical Pi roles are now explicit:

- Pi 3 `admin-01`: administration only;
- Pi 5 `media-01`: Kodi/media only;
- Pi 4 currently named `TestServer`: clean rebuild for garden BirdNET-Go after migration cleanup.

The Pi 4 rebuild should not carry forward the historical general-purpose Docker estate.

## Network target

- ASUS RT-AC86U remains router/DHCP authority.
- HP ProCurve 2510G-24 remains the core wired switch.
- Port 24 remains the known mirror/SPAN destination.
- Local DNS uses `.51` + `.50`.
- Proxmox management remains `.70` + `.71`.
- Administrative access originates from `admin-01` wherever practical.
- A future router/switch clean rebuild remains separate maintenance work and must preserve recovery access and documented network intent first.

## Completion criteria for the current rebuild programme

The current programme is considered substantially complete when:

1. Cloudflare Tunnel/Access is operational through `edge-01` and selected services no longer depend on NPM/Authelia for external access;
2. Loki/Alloy central logging is operational on `monitor-01` with end-to-end validation;
3. TestServer legacy responsibilities are retired with backup/recovery gates satisfied;
4. the Pi 4 is rebuilt as the dedicated garden BirdNET-Go host;
5. Proxmox node/storage and mail-relay recovery runbooks exist and have been tested where practical;
6. diagrams, inventory, runbook registry and service documents agree with live placement.

See [OUTSTANDING-WORK.md](OUTSTANDING-WORK.md) for the current queue and [CURRENT-STATE.md](CURRENT-STATE.md) for the live estate.
