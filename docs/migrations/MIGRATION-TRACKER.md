# Migration Tracker

This tracker records the controlled migration from the former consolidated/legacy homelab layout into the current `homelab-platform` operating model.

## Safety boundary

- Do not delete a historical repository until its unique useful content has been identified and migrated or deliberately archived.
- Do not retire a workload until persistence, secrets, monitoring and rollback/recovery requirements are understood.
- Do not treat a retired hostname as a live target.
- Do not activate `sensor-01` packet capture until the dedicated capture NIC, switch repatching and SPAN path are validated.
- Do not retire backup data until replacement coverage and restore testing are proven.
- Preserve accepted production data when reconciling Terraform or Ansible state.

## Current programme

| Phase | Status | Current position / exit criteria |
|---|---|---|
| 1. Hardware inventory | SUBSTANTIALLY COMPLETE | Active compute estate identified; remaining device-depth/network work is separate |
| 2. Workload inventory | CORE ESTATE MAPPED | Core DNS, cloud, monitoring, mail, sensor, edge host, media and BirdNET placements are explicit |
| 3. Target architecture | CORE PLACEMENT IMPLEMENTED | Remaining decisions concentrate on backup, Greenbone/security, sensor capture, edge workload and network redesign |
| 4. Public website migration | COMPLETE | Public site no longer depends on normal homelab hosting |
| 5. Proxmox IaC | CORE GUESTS DEPLOYED | Both nodes standalone by design; current core guests represented and validated |
| 6. Komodo / container operations | IN PROGRESS / REVIEW | Move routine Docker operations to the approved Komodo workflow and retire redundant paths only after proof |
| 7. Workload migration | IN PROGRESS | Major consolidated TestServer/ids-01 roles redistributed; remaining legacy dependencies/documentation to close |
| 8. Monitoring/security separation | IN PROGRESS | `monitor-01` live; `sensor-01` Phase 1 complete; capture NIC/packet engines still pending |
| 9. Jenkins / legacy delivery retirement | REVIEW REQUIRED | Retire only after replacement delivery workflow is proven |
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
| `sensor-01` | `192.168.2.55` | Network sensor VM on `PROXMOX`; Phase 1 complete |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT 103 on `Proxmox-2`; cloudflared not deployed |
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

Legacy repositories remain migration/reference sources until their unique content is deliberately reconciled or retired. Do not delete a legacy source merely because an equivalent-looking file now exists here.

## Proxmox state

### `PROXMOX`

```text
CT 100  dns-02
CT 102  mail-relay-01
VM 200  cloud-01
VM 201  sensor-01
```

### `Proxmox-2`

```text
CT 101  dns-01
CT 103  edge-01
VM 200  monitor-01
```

Both nodes are standalone by intent. The prior cluster experiment is closed.

## DNS migration

DNS replacement and cutover are complete for the current design.

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

`192.168.2.48` is `admin-01`, not a resolver.

Known remaining defect: `dns-02` currently lacks the `dns-01.jameshouse` managed local record because the current IaC host list does not include that cross-record. Correct this separately through reviewed IaC.

## `cloud-01`

The original staging concept is complete and superseded by the live production service.

Validated 12 September 2026:

- VM 200 on `PROXMOX`;
- Nextcloud 34.0.3;
- PostgreSQL healthy;
- Redis healthy;
- cron running;
- dedicated 200 GiB ext4 data filesystem mounted at `/srv/cloud-01-data`;
- application reachable on `.53:8080`;
- zero failed systemd units.

The former 4 TB WD disk is not the cloud production data disk. Backup/restore proof remains outstanding.

## Monitoring

The core monitoring platform is operational on `monitor-01`.

The 12 September audit found:

```text
active Prometheus targets: 23
healthy targets:           23
active alerts:             0
```

Prometheus, Grafana, Alertmanager and Blackbox are healthy. Loki and Alloy are not deployed on `monitor-01`.

## `sensor-01`

Phase 1 is complete and validated:

- VM exists and management plane is live;
- Suricata 8.0.6 installed;
- Zeek 8.0.10 installed;
- Node Exporter active;
- no dedicated capture NIC yet;
- Suricata and Zeek deliberately stopped.

Next gate:

1. receive/install the dedicated USB capture NIC;
2. agree the physical repatching plan;
3. move the current router connection away from switch port 24;
4. configure port 24 as the SPAN destination;
5. pass the capture NIC through to `sensor-01`;
6. prove mirrored packet arrival;
7. enable Suricata/Zeek through IaC;
8. validate logging, metrics and resource impact.

## `edge-01`

`edge-01` is CT 103 on `Proxmox-2` at `192.168.2.56`.

Host placement and operating-system health are proven. The Cloudflare Tunnel workload is **not deployed**: no `cloudflared` package, binary, service or process was found.

Future work is to design and deploy the connector when approved, not to “validate” an already-running connector.

## `docker-01`

The former TestServer Pi 4 is now `docker-01` at `192.168.2.220`.

It is a deliberately single-purpose BirdNET-Go Docker host. The retired `TestServer` identity must not be used as an administration, monitoring or deployment target.

## `admin-01`

The former DietPi Pi 3 is now the dedicated administration and IaC controller at `192.168.2.48`.

It is deliberately not a DNS role.

## Network state

Validated switch facts on 12 September 2026:

- HP ProCurve 2510G-24, firmware Y.11.52;
- VLAN 1 untagged on ports 1–24;
- STP disabled;
- port mirroring disabled;
- port 24 currently connects the primary ASUS router;
- port 24 is the planned future SPAN destination after deliberate repatching;
- management uses DHCP/BOOTP;
- unrestricted `public` SNMP community is configured and is a future hardening item.

The current port map is evidence, not the final target layout. Physical patching is expected to change when the sensor capture NIC arrives.

## Backup redesign

Backup/recovery is now the largest incomplete platform area.

Current state:

- no PBS server;
- zero scheduled PVE guest backup jobs on both Proxmox nodes;
- no active Restic/Backrest platform found on the active audited estate;
- restore testing not proven;
- 4 TB WD disk on `PROXMOX` blank/unallocated/unmounted and risk/POC-only.

Direction remains to establish healthy backup storage, automated jobs, independent copies and actual restore tests before calling recovery complete.

See `docs/architecture/BACKUP-STRATEGY.md`.

## Public website migration

Production hosting cutover is complete. The public portfolio no longer depends on normal homelab availability.

Retain migration documentation as historical/recovery evidence, but do not describe home hosting as the current production path.

## Current next actions

1. Complete the documentation authority/reconciliation change.
2. Design and implement backup/recovery coverage with restore testing.
3. Install and validate the dedicated `sensor-01` capture NIC when it arrives, then execute the controlled repatch/SPAN change.
4. Design and deploy `edge-01` cloudflared only when approved.
5. Correct the DNS local-record parity defect through reviewed IaC.
6. Finish remaining router/switch redesign and hardening decisions.
7. Retire remaining legacy deployment/management paths only after replacements are proven.
