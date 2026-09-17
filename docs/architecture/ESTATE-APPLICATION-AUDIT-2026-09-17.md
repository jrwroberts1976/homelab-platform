<!-- estate-authority: IaC/inventory/estate.json -->
# Estate Application Audit — 17 September 2026

## Purpose

This record captures the read-only application audit performed across the current homelab estate on 17 September 2026.

The audit question was deliberately narrow: **is the intended workload actually installed and operational on each current host, and where does live state differ from current IaC or documentation?**

No remediation was performed during the audit. Live state was treated as evidence and compared with `IaC/inventory/estate.json`, `docs/architecture/CURRENT-STATE.md` and the current IaC implementation.

## Summary

No missing core server application was found in the active estate.

The live estate is broadly commissioned and operational. One clear application-completeness gap was found on `media-01`; several configuration/documentation housekeeping items were also identified.

| Host | Intended workload | Result |
|---|---|---|
| `admin-01` | SSH jump host, IaC controller, Corosync QNetd, controller recovery | PASS |
| `dns-02` | Pi-hole + Unbound | PASS |
| `dns-01` | Pi-hole + Unbound | PASS |
| `monitor-01` | Prometheus, Grafana, Alertmanager, Blackbox Exporter, Loki, router syslog ingestion | PASS |
| `cloud-01` | Nextcloud, PostgreSQL, Redis | PASS — Redis configuration drift reconciled; final IaC zero-drift closeout proven 17 September |
| `mail-relay-01` | Postfix relay | PASS |
| `sensor-01` | Suricata + Zeek passive sensor | PASS |
| `edge-01` | Reserved edge LXC | PASS — host commissioned; `cloudflared` intentionally absent |
| `greenbone-01` | Greenbone Community vulnerability scanner | PASS |
| `komodo-01` | Komodo Core + MongoDB | PASS |
| `zabbix-01` | Zabbix + PostgreSQL + TimescaleDB + Agent 2 + Nginx/PHP | PASS — LXC mount-baseline housekeeping recorded |
| `PROXMOX` | Proxmox VE cluster node 1 | PASS |
| `Proxmox-2` | Proxmox VE cluster node 2 + Network Host Collector | PASS |
| `media-01` | Kodi + Samba media share + Proxmox NFS backup target | OPERATIONAL — three managed Kodi add-ons absent |
| `docker-01` | BirdNET-Go | PASS |
| `home-01` | Home Assistant OS | PASS |

## Key live evidence

### `admin-01`

- Debian 13 on Raspberry Pi 3 Model B.
- zero failed systemd units;
- SSH active on TCP/22;
- Ansible, `ansible-playbook`, Git and Python installed;
- `corosync-qnetd` enabled/active on TCP/5403;
- both PVE nodes connected to QNetd;
- QNetd reported two connected clients and one cluster;
- controller-recovery timer and path units enabled/active;
- all managed recovery scripts executable;
- fresh encrypted controller-recovery bundle created at approximately 03:16 on 17 September;
- Alloy, Node Exporter and Zabbix Agent 2 enabled/active.

### DNS pair

Both `dns-01` and `dns-02` passed:

- Pi-hole Core 6.4.3 / Web 6.6 / FTL 6.7;
- Unbound 1.22.0;
- DNS on TCP/UDP 53 and Unbound on loopback 5335;
- recursive resolution;
- valid DNSSEC response with AD flag;
- broken DNSSEC response returning SERVFAIL;
- Pi-hole forwarding through `127.0.0.1#5335`;
- managed local record parity;
- five enabled adlists;
- Alloy, Node Exporter and Zabbix Agent 2 active.

### `monitor-01`

- Prometheus 3.14.0, Grafana 13.2.1, Alertmanager 0.34.0, Blackbox Exporter 0.28.0 and Loki 3.7.7 running;
- Prometheus ready and expected jobs/rules loaded;
- Grafana database health `ok`;
- Loki ready;
- Alertmanager and Blackbox endpoints healthy;
- Loki heartbeat metrics present and successful for the expected source hosts;
- Alloy enabled/active;
- router syslog listener active on UDP/5514;
- router log present and current;
- Node Exporter and Zabbix Agent 2 active.

### `cloud-01`

- Nextcloud, PostgreSQL and Redis containers operational;
- Nextcloud HTTP status endpoint healthy with maintenance disabled;
- PostgreSQL accepting connections;
- dedicated data filesystem mounted correctly;
- Alloy, Node Exporter and Zabbix Agent 2 active.

Audit finding: the live Redis container originally used a mounted `redis.conf`/`requirepass` configuration while the current IaC path expected the `.env`/`REDIS_PASSWORD` pattern. Redis itself remained healthy and authenticated; this was configuration reconciliation work rather than an application outage.

Remediation completed later on 17 September 2026:

- Redis was reconciled to the IaC-managed `.env`/`REDIS_PASSWORD` model and the unused legacy `redis.conf` was removed;
- the Nextcloud administrator, PostgreSQL owner/bootstrap and Redis credentials exposed during diagnostic output were rotated without exposing replacement values in the closeout evidence;
- PostgreSQL authentication was proven over the application network, the database container was recreated with current environment metadata, and Nextcloud remained on its established `oc_admin` application role;
- Redis used a temporary dual-password ACL bridge while Nextcloud was moved to the new credential; the Redis container was then recreated from the IaC-managed secret, after which the old Redis password was rejected and its ACL hash was absent;
- app and cron containers were reconciled to the rotated environment, while PostgreSQL and Redis health and Nextcloud HTTP 200 status remained healthy;
- obsolete secret-bearing staging, rollback and temporary artifacts were purged from `admin-01` and `cloud-01` while live configuration files were preserved;
- final production IaC closeout returned `changed=0` in check mode, approved reconciliation and the second idempotence run, with zero unreachable/failed tasks;
- final health validation reported Nextcloud 34.0.3 healthy, required containers running, PostgreSQL and Redis healthy, dedicated storage validation passing and no failed systemd units.

The `cloud-01` Redis configuration-drift remediation is therefore **CLOSED**.

### `mail-relay-01`

- Postfix enabled/active;
- internal SMTP listener on TCP/25;
- Gmail relay host configured on port 587;
- SASL enabled and TLS encryption required;
- intended `mynetworks` policy present;
- relay password maps protected;
- upstream TCP/587 reachable;
- queue empty;
- Alloy, Node Exporter and Zabbix Agent 2 active.

This audit did not send an end-to-end test message.

### `sensor-01`

- Suricata 8.0.6 active;
- Zeek 8.0.10 active;
- dedicated capture interface up/promiscuous with the intended identity;
- Suricata `eve.json` current;
- Zeek logs current and contain `community_id`;
- managed Zeek service active;
- Alloy, Node Exporter and Zabbix Agent 2 active.

### `edge-01`

The reserved edge LXC is healthy with observability commissioned. Docker/Podman/Cloudflared are absent by design. This matches the current reserved-edge role and is not a missing application finding.

### `greenbone-01`

- Docker/Compose present;
- Greenbone Compose tree present;
- all expected Greenbone containers running/healthy where checks are defined;
- HTTPS on `.57:443` returned 200;
- Alloy, Node Exporter and Zabbix Agent 2 active.

### `komodo-01`

- Docker 29.8.1 / Compose 5.5.1;
- MongoDB 8.0.32 healthy;
- Komodo Core 2.3.3 running;
- `.58:9120` returned HTTP 200;
- recent application backup sets present;
- Zabbix Agent 2 active.

Alloy and Node Exporter are not currently assigned to the Komodo inventory group and were therefore not treated as application drift.

### `zabbix-01`

- PostgreSQL, Zabbix Server, Zabbix Agent 2, Nginx and PHP-FPM active;
- Zabbix 7.0.30 and PostgreSQL 17;
- TimescaleDB 2.29.2 installed and active in the Zabbix database;
- web frontend returned HTTP 200;
- Agent 2 listening on TCP/10050 and server on TCP/10051;
- unattended CT105 backup from the 02:15 schedule was observed on 17 September.

Three mount-related failed units were observed earlier in the audit on the unprivileged LXC (`dev-mqueue.mount`, `run-lock.mount`, `tmp.mount`). They do not prevent Zabbix operation and remain a baseline-cleanup item.

### Proxmox cluster

Both nodes reported:

- Debian 13;
- PVE/pve-manager 9.2.20;
- kernel `7.0.14-17-pve`;
- zero failed systemd units;
- `pve-cluster`, `pvedaemon`, `pveproxy`, `pvestatd`, Corosync and QDevice active;
- cluster `jameshouse-pve` quorate;
- expected votes 3, total votes 3, quorum 2, `Quorate Qdevice`;
- Corosync link0 and link1 connected;
- dedicated heartbeat interface/address correct;
- Chrony healthy;
- Alloy, Node Exporter and Zabbix Agent 2 active.

Current workload placement observed:

```text
PROXMOX
  CT100 dns-02
  CT102 mail-relay-01
  CT104 komodo-01
  CT105 zabbix-01
  VM200 cloud-01
  VM201 sensor-01
  VM204 home-01
  VM9000/9001 templates stopped

Proxmox-2
  CT101 dns-01
  CT103 edge-01
  VM202 monitor-01
  VM203 greenbone-01
```

`Proxmox-2` Network Host Collector timer was enabled/active and its inventory and Prometheus textfile metrics were freshly updated during the audit. The collector service is `Type=oneshot`, so being inactive between timer executions is expected.

### `media-01`

Operational evidence:

- Debian 13 on Raspberry Pi 5;
- zero failed units;
- Kodi 21.3 installed and active;
- exactly one `kodi.bin` process;
- `/srv/media` with Movies/TV/Music/plugins directories;
- Samba enabled/active and `Media` share points at `/srv/media`;
- TCP/445 listening;
- NFS server enabled/active;
- both PVE nodes authorised to the expected backup exports;
- 338 GiB free during audit;
- current unattended backups present for both PVE nodes;
- Alloy, Node Exporter and Zabbix Agent 2 active.

Application-completeness gap:

```text
weather.openmeteo                    ABSENT
service.subtitles.opensubtitles-com  ABSENT
plugin.program.autocompletion        ABSENT
```

These three add-ons are expected by the current media IaC and should be reconciled only after this audit record is merged and reviewed.

### `docker-01`

- Debian 13 ARM64;
- zero failed units;
- Docker/Compose active;
- expected BirdNET-Go directories present;
- pinned `ghcr.io/tphakala/birdnet-go:20260823` image running healthy;
- web endpoint returned 302 as expected;
- host USB microphone present;
- BirdNET-Go enumerated stable USB ID `usb-id:0c76:161e:`;
- five-second live-audio check produced 78 matching microphone events;
- current BirdNET data/log activity present;
- Alloy, Node Exporter and Zabbix Agent 2 active.

### `home-01`

`home-01` is now a commissioned active Home Assistant VM rather than a planned reservation.

Observed state:

- VM204 running on `PROXMOX`;
- HAOS 18.2;
- Home Assistant Core 2026.9.2;
- Supervisor 2026.09.2, healthy and supported;
- 2 vCPU, 4096 MiB RAM, 32 GiB `vm-ssd` disk;
- OVMF/q35;
- VirtIO network with MAC `02:00:00:00:02:04`;
- QEMU guest agent enabled and functional;
- `onboot=1`;
- `protection=1`;
- HTTP application endpoint on port 80 returned 200;
- unauthenticated `/api/` returned 401, proving the API endpoint is live;
- both DNS resolvers return `192.168.2.60` for `home-01.jameshouse`;
- `http://home-01/` returned 200;
- native Home Assistant backup exists;
- manual Proxmox VM204 snapshot backup completed and passed compressed archive/VMA integrity validation;
- VM204 is included in the `PROXMOX` 02:15 nightly schedule.

Remaining evidence gates are the first unattended VM204 backup, external service monitoring and deeper restore/recovery proof.

## Backup observations from 17 September

The audit observed current unattended backup archives on `media-01` for the 17 September schedules.

Confirmed evidence includes:

- CT105 (`zabbix-01`) in the `PROXMOX` 02:15 run;
- CT101, CT103, VM202 and VM203 in the `Proxmox-2` 03:15 run;
- VM204 manual backup at approximately 07:59 with prior integrity validation.

The audit output did not include CT104 in the displayed tail of the `PROXMOX` repository, so this record does not claim first unattended CT104 proof from that output.

## Open remediation / reconciliation backlog

1. Reconcile the three missing IaC-managed Kodi add-ons on `media-01`.
2. Review the `zabbix-01` LXC mount-unit baseline and remove false/noisy failed-unit conditions if appropriate.
3. Add external monitoring for `home-01` and observe its first unattended scheduled backup.
4. Reconcile documentation and canonical truth so `home-01` is active rather than planned.
5. Review the Network Host Collector timer desired-state default versus the validated live enabled timer before changing either side.
6. Review the retained generic `media-backup` storage after confidence in the split node-specific repositories is accepted.
7. Reconcile the `admin-01` Git worktree back to `main` after repository branch cleanup.
8. Continue recovery-depth work: representative QEMU restore, application-consistent Nextcloud/PostgreSQL recovery and independent second-copy protection.

`cloud-01` Redis/configuration remediation is closed and is no longer part of the open backlog.

## Audit conclusion

The estate audit found a commissioned, operational platform rather than a partially deployed one. No core server application is missing. The `cloud-01` Redis configuration-drift finding has been reconciled and closed. Remaining work is bounded to the media application-completeness issue plus other configuration, documentation, monitoring and recovery-depth reconciliation.