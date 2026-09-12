# Migration Tracker

This tracker records the controlled migration from the former consolidated/legacy homelab layout into the current `homelab-platform` operating model.

## Safety boundary

- Do not delete a historical repository until its unique useful content has been identified and migrated or deliberately archived.
- Do not retire a workload until persistence, secrets, monitoring and rollback/recovery requirements are understood.
- Do not treat a retired hostname as a live target.
- Do not activate `sensor-01` packet capture until the dedicated capture NIC and SPAN path are validated.
- Do not retire backup data until replacement coverage and restore testing are proven.
- Preserve accepted production data when reconciling Terraform or Ansible state.

## Current programme

| Phase | Status | Current position / exit criteria |
|---|---|---|
| 1. Hardware inventory | SUBSTANTIALLY COMPLETE | Active compute estate identified; remaining router/switch/device-depth work continues separately |
| 2. Workload inventory | IN PROGRESS — CORE ESTATE MAPPED | Core DNS, cloud, monitoring, mail, sensor, edge, media and BirdNET placements are explicit |
| 3. Target architecture | IN PROGRESS — CORE PLACEMENT IMPLEMENTED | Remaining decisions concentrate on backup, Greenbone/security, sensor capture and legacy retirement |
| 4. Public website migration | COMPLETE / FOLLOW-UP AUTOMATION AS REQUIRED | Public site no longer depends on normal homelab hosting |
| 5. Proxmox IaC | IN PROGRESS — CORE GUESTS DEPLOYED | Both nodes standalone by design; current core guests represented and validated |
| 6. Komodo / container operations | IN PROGRESS / REVIEW | Move routine Docker operations to the approved Komodo workflow and retire redundant paths only after proof |
| 7. Workload migration | IN PROGRESS | Major consolidated TestServer/ids-01 roles redistributed; remaining legacy dependencies to identify and close |
| 8. Monitoring/security separation | IN PROGRESS | `monitor-01` live; `sensor-01` built; capture NIC/packet engines still pending |
| 9. Jenkins / Stage 6 retirement | REVIEW REQUIRED | Retire only after replacement delivery workflow is proven |
| 10. Legacy repo cleanup | IN PROGRESS | Remove/archive only after authority and unique-content review |
| 11. Public-readiness review | NOT STARTED | Repository safe and polished for optional public visibility |
| 12. Password manager | NOT STARTED | Product selected, IaC deployed, backed up, monitored and recovery-tested |

## Current core estate

| Host | Address | Current role |
|---|---:|---|
| `admin-01` | `192.168.2.48` | Administration / IaC controller |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT 100 on `PROXMOX` |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT 101 on `Proxmox-2` |
| `monitor-01` | `192.168.2.52` | Monitoring VM on `Proxmox-2` |
| `cloud-01` | `192.168.2.53` | Production Nextcloud VM on `PROXMOX` |
| `mail-relay-01` | `192.168.2.54` | Postfix relay, CT 102 on `PROXMOX` |
| `sensor-01` | `192.168.2.55` | Network sensor VM on `PROXMOX` |
| `edge-01` | `192.168.2.56` | Cloudflare Tunnel connector, CT 103 on `Proxmox-2` |
| `PROXMOX` | `192.168.2.70` | Primary standalone Proxmox node |
| `Proxmox-2` | `192.168.2.71` | Secondary standalone Proxmox node |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host |

## Retired identities

- `TestServer` — retired; its Pi 4 hardware is now `docker-01`.
- `DietPi` — retired; its Pi 3 hardware is now `admin-01`.
- `ids-01` — decommissioned.
- `k3s-node-01` identity at `.195` — retired; host is `media-01`.
- old `dns-02` at `.242` — retired.

Historical repositories and audit documents may still contain these names. Their presence in history must not be interpreted as current placement.

## Authority migration

For migrated areas, `homelab-platform/IaC/` is the current desired-state authority.

Legacy repositories such as historical Docker, Proxmox, monitoring and documentation repositories remain migration/reference sources until their unique content is deliberately reconciled or retired.

Do not delete a legacy source merely because an equivalent-looking file now exists here.

## Proxmox state

### `PROXMOX`

Validated live guests:

```text
CT 100  dns-02
CT 102  mail-relay-01
VM 200  cloud-01
VM 201  sensor-01
```

### `Proxmox-2`

Validated live guests:

```text
CT 101  dns-01
CT 103  edge-01
VM 200  monitor-01
```

The prior cluster experiment is closed. Both nodes are currently standalone by intent. Any future cluster work requires a new explicit design and validation change.

## DNS migration

DNS replacement and cutover are complete for the current design.

Current resolver pair:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

`192.168.2.48` is now `admin-01`, not a resolver. The old `.242` secondary resolver has been removed.

Current IaC represents resolver configuration and local DNS management. Remaining DNS work should focus on drift detection, resilience testing and ensuring no stale `.48` or `.242` resolver dependencies remain.

## `cloud-01`

The original staging concept is complete and superseded by the live production service.

Current validated state:

- VM 200 on `PROXMOX`;
- Nextcloud 34.0.3;
- PostgreSQL healthy;
- Redis healthy;
- cron running;
- dedicated 200 GiB ext4 data filesystem;
- data at `/srv/cloud-01-data/data`;
- production deployment wrapper validated;
- second Ansible run idempotent;
- zero failed units.

A Redis persistence fault discovered during the estate audit was corrected both live and in IaC by reconciling the bind-directory numeric ownership to UID 999 / GID 1000.

## Node Exporter / monitoring

The Node Exporter role now handles irrelevant OpenIPMI failures on virtual guests without removing the collector tooling.

Live validation on `dns-02` and `sensor-01` proved:

- OpenIPMI disabled/inactive where no IPMI device exists;
- zero failed systemd units;
- Node Exporter healthy;
- second run `changed=0`.

The production Node Exporter wrapper currently validates eight healthy Prometheus targets:

```text
dns-01
dns-02
monitor-01
sensor-01
PROXMOX
Proxmox-2
media-01
docker-01
```

Prometheus, Grafana, Alertmanager and Blackbox also pass controller health checks.

## `sensor-01`

The VM is built and its management plane is live.

Phase 1 is intentionally incomplete:

- no dedicated capture NIC is attached yet;
- Suricata is disabled/stopped;
- Zeek is stopped;
- capture-interface configuration remains empty.

Next sensor migration gate:

1. attach the dedicated capture NIC;
2. identify and validate it;
3. confirm HP ProCurve port 24 SPAN traffic;
4. enable packet engines through IaC;
5. validate logging, metrics and resource impact.

## `media-01`

`media-01` is operational as the Raspberry Pi 5 Kodi endpoint. The earlier `k3s-node-01` role is retired.

Future work is incremental hardening and observability rather than a greenfield host-role decision.

## `docker-01`

The former TestServer Pi 4 is now `docker-01` at `192.168.2.220`.

Its active role is the BirdNET-Go Docker host. Do not use the retired `TestServer` identity as an administration, monitoring or deployment target.

## `admin-01`

The former DietPi Pi 3 is now the dedicated administration and IaC controller at `192.168.2.48`.

This is deliberately no longer a Pi-hole/DNS role.

## `edge-01`

`edge-01` is CT 103 on `Proxmox-2` at `192.168.2.56`.

Its host placement is proven. Direct cloudflared service/process validation remains an outstanding current-state check because the connector is outbound and does not need an inbound listener on TCP/7844.

## Security redesign

Greenbone remains separate from the passive network sensor.

Working target:

- dedicated `security-01`;
- suitable x86 resources;
- IaC deployment;
- backup/restore coverage;
- monitoring integration.

Do not combine Greenbone with the passive capture VM merely for convenience.

## Network work

Known current facts:

- HP ProCurve port 24 is the mirror/SPAN destination;
- router remains DHCP authority;
- current resolver pair is `.51 + .50`;
- switch/router clean-rebuild work remains separately controlled.

Do not reset either network device until configuration intent and rollback access are recorded.

## Backup redesign

Backup and recovery remain one of the largest incomplete programme areas.

Direction:

- evaluate and implement Proxmox Backup Server where appropriate;
- preserve useful historical Restic repositories until migrated or intentionally archived;
- perform actual restore testing;
- keep recovery identities outside Git;
- avoid treating historically degraded storage as the new primary backup platform.

See `docs/architecture/BACKUP-STRATEGY.md`.

## Public website migration

Production hosting cutover is complete. The public portfolio no longer depends on normal homelab availability.

Retain the relevant migration documentation as historical and recovery evidence, but do not describe home hosting as the current production path.

## Password manager project

A self-hosted password manager remains a future project.

Requirements before deployment:

- choose the product and target host intentionally;
- deploy through Git-managed IaC;
- keep secrets and recovery material outside Git;
- provide HTTPS;
- include persistent-data backup and restore testing;
- add availability and service monitoring;
- document an emergency recovery path independent of the running homelab.

## Current next actions

1. Complete repository and documentation authority reconciliation.
2. Install and validate the dedicated `sensor-01` capture NIC.
3. Validate `edge-01` cloudflared directly.
4. Continue backup-platform and recovery design with restore testing.
5. Finish remaining network-device audit/rebuild decisions.
6. Retire remaining legacy deployment and management paths only after their replacements are proven.
