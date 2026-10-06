# Migration Tracker

**Status:** CORE MIGRATION PROGRAMME SUBSTANTIALLY COMPLETE  
**Reviewed:** 6 October 2026

This tracker records the controlled migration from the former consolidated/legacy homelab layout into the current `homelab-platform` operating model.

Detailed staging and cutover evidence remains in dated migration/audit documents. This page records the **current migration status**, not the intermediate state observed during earlier gates.

## Safety boundary

- Do not delete historical repositories until unique useful content has been identified and migrated or deliberately archived.
- Do not retire workloads until persistence, secrets, monitoring and rollback/recovery requirements are understood.
- Do not treat retired hostnames as live targets.
- Do not retire backup/rollback evidence until replacement coverage and recovery confidence are explicit.
- Preserve accepted production data when reconciling Terraform or Ansible state.
- Treat the production `jameshouse-pve` cluster as current state; do not replay standalone-host procedures without an explicit recovery reason.

## Programme status

| Phase | Status | Current position / remaining outcome |
|---|---|---|
| 1. Hardware inventory | SUBSTANTIALLY COMPLETE | Active compute estate known; refresh physical network mapping as lifecycle work |
| 2. Workload inventory | COMPLETE FOR CORE ESTATE | Current host/VMID/address placement is canonical in `estate.json` / `CURRENT-STATE.md` |
| 3. Target architecture | CORE PLACEMENT IMPLEMENTED | Remaining work is recovery depth, resilience proof and hardening |
| 4. Public website migration | COMPLETE | Public portfolio does not depend on normal homelab availability |
| 5. Proxmox IaC / clustering | COMPLETE BASELINE | `jameshouse-pve`, dual Corosync links and QDevice are live; resilience testing remains |
| 6. Komodo / container operations | OPERATIONAL / MATURING | Core and Periphery commissioning complete on explicitly managed hosts; HTTPS/update-rollback maturity remains |
| 7. Workload migration | SUBSTANTIALLY COMPLETE | Legacy consolidated roles redistributed; remaining work is cleanup/recovery proof |
| 8. Monitoring/security separation | COMPLETE BASELINE | `monitor-01` and `sensor-01` are operational; logging/security pipelines live |
| 9. Jenkins / legacy delivery retirement | COMPLETE | Jenkins already removed; do not recreate a retirement task |
| 10. Legacy repo/state cleanup | IN PROGRESS / REVIEW | Remove/archive only after authority and unique-content/rollback review |
| 11. Documentation reconciliation | IN PROGRESS | 5 October audit complete; current-looking stale docs being reconciled |
| 12. Password manager | PLANNED / OPTIONAL | Product/design selection remains future work |

## Current core estate

| Host | Address | Current role |
|---|---:|---|
| `admin-01` | `192.168.2.48` | Administration / IaC controller / Corosync QNetd |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT100 on `PROXMOX` |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT101 on `Proxmox-2` |
| `monitor-01` | `192.168.2.52` | Monitoring/logging + active network discovery, VM202 on `Proxmox-2` |
| `cloud-01` | `192.168.2.53` | Nextcloud/PostgreSQL/Redis VM200 on `PROXMOX` |
| `mail-relay-01` | `192.168.2.54` | Postfix relay, CT102 on `PROXMOX` |
| `sensor-01` | `192.168.2.55` | Suricata/Zeek VM201 on `PROXMOX` |
| `edge-01` | `192.168.2.56` | Reserved edge CT103 on `Proxmox-2`; `cloudflared` absent |
| `greenbone-01` | `192.168.2.57` | Greenbone VM203 on `Proxmox-2` |
| `komodo-01` | `192.168.2.58` | Komodo Core CT104 on `PROXMOX` |
| `zabbix-01` | `192.168.2.59` | Zabbix CT105 on `PROXMOX` |
| `home-01` | `192.168.2.60` | Home Assistant OS VM204 on `PROXMOX` |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` node 1 |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` node 2; former discovery source retained for rollback/history |
| `media-01` | `192.168.2.195` | Kodi endpoint / primary Proxmox NFS backup target |
| `docker-01` | `192.168.2.220` | BirdNET-Go Docker host |

## Retired identities

- `TestServer` -> retired; Pi 4 hardware is now `docker-01`.
- `DietPi` -> retired; Pi 3 hardware is now `admin-01`.
- `ids-01` -> decommissioned.
- former `k3s-node-01` identity -> retired; hardware is now `media-01`.
- old `dns-02` at `.242` -> retired.

Historical repositories and dated audit documents may contain these names. Their presence in history does not make them current targets.

## Proxmox cluster migration

The former standalone design is superseded by the production cluster:

```text
cluster: jameshouse-pve
PROXMOX:   192.168.2.70 / Corosync link0 10.255.255.1
Proxmox-2: 192.168.2.71 / Corosync link0 10.255.255.2
admin-01:  QNetd third vote
```

Validated quorum uses 3 total votes with quorum 2 and QDevice present.

Current guest placement:

```text
PROXMOX
  CT100 dns-02
  CT102 mail-relay-01
  CT104 komodo-01
  CT105 zabbix-01
  VM200 cloud-01
  VM201 sensor-01
  VM204 home-01
  VM9000 / VM9001 templates

Proxmox-2
  CT101 dns-01
  CT103 edge-01
  VM202 monitor-01
  VM203 greenbone-01
```

Production disks remain node-local. The migration delivered cluster membership/quorum and unique VMIDs, not automatic guest-data HA.

Pre-cluster rollback LVs retained on `Proxmox-2` remain historical recovery evidence and should be removed only after explicit review.

## DNS migration

DNS replacement/cutover is complete:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

`admin-01` at `.48` is not a resolver. Current IaC includes both resolver cross-records.

## Monitoring / logging migration

`monitor-01` VM202 is the production monitoring/logging platform.

Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki are live. Grafana Alloy is deployed across the managed estate according to inventory scope.

### Network-discovery migration — COMPLETE

The single-owner cutover completed on **27 September 2026**.

Current owner: `monitor-01`.

Current monitor-side responsibilities include collector, selective enrichment, OS-evidence publication, trusted Proxmox guest refresh, targeted profiling, first-seen notification and network-host publication.

`Proxmox-2` is the former source. Its source discovery timers are disabled/inactive; retained files/snapshots are rollback/history evidence.

The staged 26–27 September gate narrative in `docs/operations/network-discovery-monitor01-migration.md` remains historical evidence. Do not interpret pre-cutover paragraphs there as current timer ownership.

## Security / sensing migration

`sensor-01` is operational with dedicated passive capture, Suricata and Zeek. The HP ProCurve mirrors ports 1–23 to port 24.

`greenbone-01` is the active LAN-only vulnerability scanner. Its managed scan/evidence path into the management report is operational.

CrowdSec is not currently deployed and is not part of the migrated production baseline.

## Container-management migration

`komodo-01` is the active Komodo Core control plane.

Komodo Periphery has been commissioned on explicitly managed production Docker hosts. Adoption preserved existing application workloads rather than recreating them.

Remaining container-management work is operational hardening/update-rollback maturity, not initial platform deployment.

## Backup migration

The former no-backup position is superseded.

Primary NFS target: `media-01`.

```text
PROXMOX
  media-backup-proxmox
  schedule 02:15
  guests 100,102,104,105,200,201,204

Proxmox-2
  media-backup-proxmox-2
  schedule 03:15
  guests 101,103,202,203
```

Observed unattended evidence includes CT105 and VM203. Isolated LXC restore proof exists for CT103.

Remaining recovery work belongs to normal backlog rather than migration cutover: representative QEMU restore, application-consistent `cloud-01` recovery, independent second copy and any still-missing unattended CT104/VM204 evidence.

## Home Assistant migration/commissioning

`home-01` is commissioned as VM204 on `PROXMOX` and is no longer a planned reservation.

Native backup, manual Proxmox backup/integrity proof, DNS and application reachability are proven. Remaining monitoring/recovery depth is normal operations work.

## Public website migration

Complete. The public portfolio is externally hosted and independent of normal homelab availability.

## Current next actions

These are **post-migration maturity tasks**, not unfinished cutovers:

1. continue repository documentation reconciliation from the 5 October audit;
2. prove Corosync link0 -> link1 failover and controlled one-node quorum behaviour when scheduled;
3. deepen backup/recovery with representative QEMU and application-level restores;
4. add an independent second backup copy;
5. remove retained pre-cluster rollback LVs only after explicit confidence review;
6. continue Komodo HTTPS/update-rollback hardening where useful;
7. refresh physical switch/cable mapping and review legacy SNMP/Telnet hardening;
8. deploy `cloudflared` only when an approved service requires it.

## Historical migration evidence

Detailed intermediate gate evidence remains in the dated architecture/application audits and migration runbooks. Preserve those files as point-in-time evidence; current operational truth comes from `IaC/inventory/estate.json` and `docs/architecture/CURRENT-STATE.md`.
