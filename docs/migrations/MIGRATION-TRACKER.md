# Migration Tracker

This tracker records the controlled migration from the former consolidated/legacy homelab layout into the current `homelab-platform` operating model.

## Safety boundary

- Do not delete a historical repository until its unique useful content has been identified and migrated or deliberately archived.
- Do not retire a workload until persistence, secrets, monitoring and rollback/recovery requirements are understood.
- Do not treat a retired hostname as a live target.
- Do not retire backup data until replacement coverage and restore testing are proven.
- Preserve accepted production data when reconciling Terraform or Ansible state.
- Treat the production `jameshouse-pve` cluster as current state; do not replay standalone-host procedures without an explicit disaster-recovery reason.

## Current programme

| Phase | Status | Current position / exit criteria |
|---|---|---|
| 1. Hardware inventory | SUBSTANTIALLY COMPLETE | Active compute estate identified; device-depth and physical network mapping remain lifecycle work |
| 2. Workload inventory | COMPLETE FOR CORE ESTATE | Core DNS, cloud, monitoring, mail, sensor, edge, media and BirdNET placements are explicit |
| 3. Target architecture | CORE PLACEMENT IMPLEMENTED | Remaining decisions focus on recovery depth, HA/storage, second-copy resilience and hardening |
| 4. Public website migration | COMPLETE | Public site no longer depends on normal homelab hosting |
| 5. Proxmox IaC / clustering | CLUSTER IMPLEMENTED | `jameshouse-pve`, dual Corosync links, QDevice and cluster-unique VMIDs are live; resilience testing remains follow-up work |
| 6. Komodo / container operations | IN PROGRESS / REVIEW | Move routine Docker operations to the approved Komodo workflow and retire redundant paths only after proof |
| 7. Workload migration | SUBSTANTIALLY COMPLETE | Former consolidated TestServer/ids-01 roles redistributed; remaining work is cleanup and recovery proof |
| 8. Monitoring/security separation | COMPLETE BASELINE | `monitor-01` and `sensor-01` are live; Suricata/Zeek capture and Loki/Alloy pipelines are operational |
| 9. Jenkins / legacy delivery retirement | REVIEW REQUIRED | Retire only after replacement delivery workflow is proven |
| 10. Legacy repo cleanup | IN PROGRESS | Remove/archive only after authority and unique-content review |
| 11. Public-readiness review | NOT STARTED | Repository safe and polished for optional public visibility |
| 12. Password manager | NOT STARTED | Product selected, IaC deployed, backed up, monitored and recovery-tested |

## Current core estate

| Host | Address | Current role |
|---|---:|---|
| `admin-01` | `192.168.2.48` | Administration / IaC controller / Corosync QNetd |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT100 on `PROXMOX` |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT101 on `Proxmox-2` |
| `monitor-01` | `192.168.2.52` | Monitoring/logging VM202 on `Proxmox-2` |
| `cloud-01` | `192.168.2.53` | Production Nextcloud VM200 on `PROXMOX` |
| `mail-relay-01` | `192.168.2.54` | Postfix relay, CT102 on `PROXMOX` |
| `sensor-01` | `192.168.2.55` | Active Suricata/Zeek VM201 on `PROXMOX` |
| `edge-01` | `192.168.2.56` | Reserved edge CT103 on `Proxmox-2`; cloudflared not deployed |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` node 1 / cluster anchor |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` node 2 / Network Host Collector |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint / primary Proxmox NFS backup target |
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

The 14 September development/documentation branch set has been consolidated into `main`; all remaining branch heads are now ancestors of `main` and contain no commits ahead of it.

## Proxmox cluster state

The former standalone design has been superseded by the production cluster:

```text
cluster: jameshouse-pve

PROXMOX
  management: 192.168.2.70
  Corosync link0: 10.255.255.1/30
  node ID: 1

Proxmox-2
  management: 192.168.2.71
  Corosync link0: 10.255.255.2/30
  node ID: 2

admin-01
  QNetd / third vote: 192.168.2.48:5403
```

Corosync link0 is the direct point-to-point preferred path at priority 20. The management LAN is link1 fallback at priority 5.

Validated quorum after QDevice setup:

```text
Expected votes: 3
Total votes:    3
Quorum:         2
Flags:          Quorate Qdevice
```

### Current guest placement

`PROXMOX`:

```text
CT100  dns-02
CT102  mail-relay-01
VM200  cloud-01
VM201  sensor-01
VM9000 Debian cloud template
VM9001 Debian cloud template with QGA
```

`Proxmox-2`:

```text
CT101  dns-01
CT103  edge-01
VM202  monitor-01
```

The duplicate standalone VMID 200 conflict was resolved by changing `monitor-01` to VM202.

Production disks remain on node-local `local-lvm`. Cluster quorum and migration capability are implemented; automatic guest HA after loss of a node-local disk owner is not.

## Cluster migration rollback state

The cluster cutover was performed with fresh off-node backups, preserved guest/storage/job configuration and retained local rollback volumes.

The old `.71` guest volumes were renamed rather than destroyed:

```text
precluster-20260914-vm-101-disk-0
precluster-20260914-vm-103-disk-0
precluster-20260914-vm-200-cloudinit
precluster-20260914-vm-200-disk-0
```

These are not active guest disks. Remove them only after fresh cluster-era backups and recovery confidence are explicit.

## DNS migration

DNS replacement and cutover are complete for the current design.

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

`192.168.2.48` is `admin-01`, not a resolver.

CT101 was migrated to `Proxmox-2` after cluster formation and validated with Pi-hole, Unbound, DNS resolution, network reachability and clean quorum state.

## `cloud-01`

`cloud-01` is the live production Nextcloud platform:

- VM200 on `PROXMOX`;
- Nextcloud/PostgreSQL/Redis operational;
- dedicated 200 GiB ext4 data filesystem mounted at `/srv/cloud-01-data`;
- application reachable on `.53:8080`;
- VM-level snapshot backup proven;
- application-consistent Nextcloud/PostgreSQL recovery still pending.

The former 4 TB WD disk is not the production cloud data disk and must not be the sole trusted backup copy.

## Monitoring and logging

The monitoring platform is operational on `monitor-01`, now VM202 on `Proxmox-2`.

Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki are live. Native Alloy is active and router syslog is ingested into Loki while retained locally.

Network Hosts discovery, enrichment, one-time deep profiling, first-seen notification and dashboards are operational. HP ProCurve telemetry is also exported into Prometheus/Grafana.

## `sensor-01`

The passive sensor platform is operational:

- VM201 on `PROXMOX`;
- dedicated capture NIC active in promiscuous mode;
- Suricata active;
- Zeek active;
- HP ProCurve ports 1–23 mirrored to port 24;
- Alloy ships Suricata/Zeek logs to Loki.

The capture interface remains dedicated to sensing and is not a Corosync or management interface.

## `edge-01`

`edge-01` is CT103 on `Proxmox-2` at `192.168.2.56`.

The host is operational, but the Cloudflare Tunnel connector is intentionally not deployed. Future work is to deploy it only when a real service requirement is approved.

## `docker-01`

The former TestServer Pi 4 is now `docker-01` at `192.168.2.220`.

It is a deliberately single-purpose BirdNET-Go Docker host. The retired `TestServer` identity must not be used as an administration, monitoring or deployment target.

## `admin-01`

The former DietPi Pi 3 is now the dedicated administration and IaC controller at `192.168.2.48`.

It also hosts `corosync-qnetd` for `jameshouse-pve`. It is deliberately not a DNS role.

## Network state

Current switch state includes:

- HP ProCurve 2510G-24, firmware Y.11.52;
- VLAN 1 untagged on ports 1–24;
- port 24 as SPAN destination;
- ports 1–23 as monitored sources;
- SNMP telemetry operational;
- unrestricted `public` SNMP community remains a hardening item;
- Telnet-only management remains a legacy-security constraint.

A refreshed physical port/cable map is still required after the sensor/cluster network changes.

## Backup state

The former no-backup position is superseded.

`media-01` now provides the proven primary Proxmox NFS backup target:

```text
PROXMOX   -> media-backup-proxmox   -> /srv/backup/pve-proxmox
Proxmox-2 -> media-backup-proxmox-2 -> /srv/backup/pve-proxmox-2
```

All seven production guests had successful backup evidence before cluster formation and CT103 has a proven isolated LXC restore/boot test.

The cluster-era backup policy has been reconciled through IaC. Current scheduled selections are `100,102,104,105,200,201,204` on `PROXMOX` and `101,103,202,203` on `Proxmox-2`. Unattended evidence has been observed for CT105 and for CT101/CT103/VM202/VM203; first unattended CT104 and VM204 proof remains open.

See `docs/architecture/BACKUP-STRATEGY.md` and `production docs/PROXMOX-BACKUP-RECOVERY.md`.

## Public website migration

Production hosting cutover is complete. The public portfolio no longer depends on normal homelab availability.

Retain migration documentation as historical/recovery evidence, but do not describe home hosting as the current production path.

## Current next actions

1. Onboard managed Docker hosts to Komodo deliberately, beginning with discovery/read-only validation and then a low-risk update/rollback proof.
2. Observe the remaining unattended CT104 and VM204 backup runs as routine maintenance evidence.
3. Prove a representative QEMU restore and application-consistent `cloud-01` recovery when recovery-depth work is resumed.
4. Test Corosync link0 loss and prove link1 fallback when physical access to the comms room is convenient.
5. Perform a controlled one-node maintenance/quorum test with QDevice available after the link-fallback test.
6. Decide whether node-local storage plus backup/manual recovery is sufficient or whether replication/shared storage and HA are justified.
7. Remove retained pre-cluster LVs only after fresh backup confidence is explicit.
8. Add an independent second backup copy and protect non-Proxmox persistent state when backup resilience is revisited.
9. Finish remaining router/switch hardening and physical-port mapping work when physical access is convenient.
10. Retire remaining legacy deployment/management paths only after replacements are proven.
