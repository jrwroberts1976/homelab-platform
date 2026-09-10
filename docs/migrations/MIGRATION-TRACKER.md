# Migration Tracker

**Updated:** 10 September 2026  
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`

This tracker records the controlled migration from the legacy multi-purpose homelab into the current role-based platform.

## Safety boundary

- Do not delete legacy state until its unique data, configuration, secrets and recovery value are accounted for.
- Do not destroy TestServer Docker data while the backup/recovery gate is unresolved.
- Do not treat `ids-01` as an active rollback host; it is decommissioned.
- Do not migrate the old TestServer monitoring/logging stack wholesale. Build the approved `monitor-01` stack fresh from Git/IaC and validate it independently.
- Do not expose internal administrative services directly through router port-forwards when Cloudflare Tunnel/Access is the approved ingress path.
- Keep the two Proxmox hosts standalone unless a future cluster change has its own design, network and rollback validation.

## Programme status

| Phase | Status | Current position / exit criteria |
|---|---|---|
| 1. Hardware inventory | SUBSTANTIALLY COMPLETE | Core Proxmox and Raspberry Pi assets are identified; historical audits retained |
| 2. Workload inventory | IN PROGRESS | Remaining TestServer workloads still need final retirement ownership |
| 3. Target architecture | APPROVED WORKING STATE | Core host roles and IPs are now assigned |
| 4. Public website migration | COMPLETE | Public static site moved to Cloudflare Pages; home-hosted copy is not the production authority |
| 5. Proxmox IaC | OPERATIONAL / EXPANDING | DNS, monitoring, cloud, sensor, mail relay and edge guests now have explicit placement |
| 6. Komodo / container lifecycle | IN PROGRESS | Container update/version operations are moving to Komodo; legacy ownership cleanup remains |
| 7. Workload migration | IN PROGRESS | TestServer is being reduced to the workloads that still require migration/retirement |
| 8. Monitoring/security separation | IN PROGRESS | `monitor-01` metrics platform live; `sensor-01` exists; central logging and sensor completion remain |
| 9. Jenkins / legacy CI retirement | IN PROGRESS | Legacy runner/Jenkins retained only where rollback/reference is still needed |
| 10. Legacy repo/branch cleanup | IN PROGRESS | Old branches/repos removed only after content equivalence/merge proof |
| 11. Documentation/public readiness | IN PROGRESS | Estate docs, diagrams and runbook registry being reconciled to live state |
| 12. TestServer -> BirdNET rebuild | PLANNED | Pi 4 clean rebuild after legacy backup/dependency gates are closed |

## Current role allocation

| Host / service | Address | Placement | State |
|---|---:|---|---|
| `admin-01` | `192.168.2.48` | Physical Raspberry Pi 3 | Operational controller |
| `dns-02` | `192.168.2.50` | CT100 on `PROXMOX` | Operational |
| `dns-01` | `192.168.2.51` | CT101 on `Proxmox-2` | Operational |
| `monitor-01` | `192.168.2.52` | VM200 on `Proxmox-2` | Metrics/alerting operational; logging pending |
| `cloud-01` | `192.168.2.53` | VM200 on `PROXMOX` | Running; service work continues |
| `mail-relay-01` | `192.168.2.54` | CT102 on `PROXMOX` | Operational |
| `sensor-01` | `192.168.2.55` | VM201 on `PROXMOX` | Running; sensor work continues |
| `edge-01` | `192.168.2.56` | CT103 on `Proxmox-2` | Base host operational; Cloudflare tunnel pending |
| `PROXMOX` | `192.168.2.70` | Physical HP ProDesk | Operational standalone hypervisor |
| `Proxmox-2` | `192.168.2.71` | Physical ASUS ZenBook | Operational standalone hypervisor |
| `media-01` | `192.168.2.195` | Physical Raspberry Pi 5 | Operational Kodi/media endpoint |
| `TestServer` | `192.168.2.220` | Physical Raspberry Pi 4 | Legacy retirement source |
| `ids-01` | former `.242` | Decommissioned | Retired |

## Completed migration milestones

### DNS resilience

The old `.48 + .242` DNS design is retired. The active pair is now:

```text
dns-01  192.168.2.51  CT101 on Proxmox-2
dns-02  192.168.2.50  CT100 on PROXMOX
```

Both run Pi-hole + Unbound. Local DNS records are managed through Ansible and the ASUS router remains DHCP authority.

`192.168.2.48` has been reassigned to `admin-01`; it must not be treated as a legacy resolver.

### Dedicated administration host

`admin-01` is built from a clean Raspberry Pi OS/Debian 13 base and validated as the normal Git/Ansible/SSH controller. It can reach the managed estate using dedicated SSH identities and is represented in DNS/IaC.

### Monitoring platform

`monitor-01` is live on `Proxmox-2` with:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter

The old TestServer Prometheus/Alloy path is no longer the desired monitoring authority.

### Cloudflare edge base host

`edge-01` is live as CT103 on `Proxmox-2` at `192.168.2.56`:

- Debian 13
- 1 vCPU
- 768 MiB RAM
- 8 GiB disk
- unprivileged LXC
- `nesting=1` for Debian 13/systemd behaviour
- `/tmp` capped at 192 MiB
- zero failed units
- DNS/SSH/outbound Cloudflare connectivity validated

The tunnel and Access policies are the next implementation phase.

### Public web

The engineering portfolio production site is externally hosted on Cloudflare Pages. Legacy home-hosted copies are retirement/rollback evidence, not the production endpoint.

### media-01

`media-01` is a physical Raspberry Pi 5 at `192.168.2.195` and remains the dedicated Kodi/media endpoint. It is not a k3s node.

### ids-01

`ids-01` is decommissioned. Historical audit information is retained only for evidence and migration archaeology.

## Current high-priority work

### Cloudflare Tunnel and Access

1. install `cloudflared` on `edge-01`;
2. create/register the tunnel without committing credentials;
3. define selected public hostnames;
4. apply Cloudflare Access/MFA to administrative services;
5. validate that no direct inbound router port-forward is required;
6. document recovery and monitoring.

### Central logging

Build fresh on `monitor-01`:

```text
approved sources -> Alloy -> Loki -> Grafana
```

The validated router syslog file on `monitor-01` should be the first source. Add other hosts only through an explicit collection policy.

### TestServer retirement

Before destructive cleanup, resolve the backup/recovery uncertainty around `homelab-backup-testserver.service` and protect any required persistent data.

Then retire remaining legacy responsibilities, including NPM/Authelia dependencies once Cloudflare Access is proven, obsolete monitoring components, legacy CI/runner pieces and Docker data no longer required.

Final target: clean-rebuild the Raspberry Pi 4 as a garden `birdnet-01` / BirdNET-Go host.

### Proxmox storage and recovery

- complete the WD 4 TB extended SMART review on `PROXMOX`;
- define/test guest backup and restore;
- add dedicated Proxmox node-health and storage-health runbooks;
- keep Docker off the hypervisors themselves.

## Network/security work

- keep HP ProCurve port 24 reserved as the SPAN/mirror destination;
- complete `sensor-01` Suricata/Zeek deployment/validation;
- keep vulnerability scanning separate from passive sensing;
- retain the planned clean router/switch rebuild as separate maintenance work with recovery access proved first.

## Documentation rule

When a migration step changes live role, address, placement or recovery responsibility, update the relevant service document, architecture document and `runbooks/registry.yml` in the same reviewed change.

See:

- `docs/architecture/CURRENT-STATE.md`
- `docs/architecture/TARGET-STATE.md`
- `docs/architecture/OUTSTANDING-WORK.md`
- `runbooks/README.md`
- `runbooks/registry.yml`
