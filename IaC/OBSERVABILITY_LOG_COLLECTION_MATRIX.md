# Observability Log Collection Matrix

This document records the approved host-by-host log collection scope for the homelab observability platform.

It exists to prevent blanket log ingestion. Each source must have a diagnostic, operational, security, or change-correlation purpose.

## Common rules

- Grafana Alloy is the standard Linux log collector.
- Loki labels remain low-cardinality: `environment`, `host`, `role`, `service`, `source`, and `job` where useful.
- IP addresses, usernames, request IDs, trace IDs, URLs, domains, container IDs, filenames, signatures, and arbitrary messages remain in the payload rather than Loki labels.
- Collect active files, not rotated `.1` or `.gz` files.
- Do not ingest duplicate syslog/auth/kern files when the same events are already available from journald unless a unique use case is demonstrated.
- Do not collect every file merely because it exists.
- Application log growth and local rotation must be bounded before central ingestion.

## Host profiles

| Host | Profile | Approved sources | Explicit exclusions / notes |
| --- | --- | --- | --- |
| `admin-01` | `controller` | systemd journal; SSH/sudo/auth events through journal; `homelab-controller-recovery.service` journal | No separate generic syslog/auth files while journald is authoritative. Recovery output is useful change/recovery evidence. |
| `docker-01` | `docker-birdnet` | systemd journal; Docker daemon; `birdnet-go` container stdout/stderr; `/opt/birdnet-go/data/logs/application.log` | Generic baseline Alloy 1.19.2 is deployed and proven end to end with `role=docker-birdnet`; the current active stage is journald-only. BirdNET container output and `application.log` remain deferred to the application/file-source stage. Module-specific debug files such as `analysis.log`, `birdnet.log`, `actions.log`, `access.log`, and similar remain local/on-demand initially. Do not ingest rotated BirdNET files. |
| `monitor-01` | `monitoring` | systemd journal; Grafana, Prometheus, Alertmanager and Blackbox container logs; `/var/log/homelab/router/rt-ac86u.log`; later Loki/Tempo/Alloy self-logs | Keep rsyslog UDP/5514 receiver. Do not ingest `rt-ac86u.log.1` as an active tail. Avoid duplicate generic syslog/auth files. |
| `PROXMOX` | `proxmox-primary` | systemd journal including PVE/kernel/ZFS/storage/Alloy; `/var/log/pveproxy/access.log`; `/var/log/vzdump/*.log`; `/var/log/homelab-network-hosts/events.jsonl`; Alloy self-health | Alloy 1.19.2 is deployed through the reusable `alloy` role and actively ships journald to central Loki. Shared hygiene filtering is configured for both observed Ansible wrapper formats plus the known benign Debian/OpenSSH logout warning. Do not tail historic `ifupdown2` debug trees or every per-UPID task file. |
| `Proxmox-2` | `proxmox-secondary` | systemd journal including PVE/kernel/ZFS/storage/Alloy; `/var/log/pveproxy/access.log`; `/var/log/vzdump/*.log` | Alloy 1.19.2 is deployed through the reusable `alloy` role and actively ships journald to central Loki with the same label contract and hygiene configuration as `PROXMOX`. Same file-source exclusions as primary Proxmox. |
| `dns-01` | `dns` | systemd journal; `/var/log/pihole/pihole.log`; `/var/log/pihole/FTL.log`; Unbound journal | Generic baseline Alloy 1.19.2 is deployed and proven end to end with `role=dns-resolver`; the current active stage is journald-only. Pi-hole/FTL file sources remain deferred to the application/file-source stage. Domain/client data remains payload, never labels. Do not ingest `.1`/`.gz` rotations. |
| `dns-02` | `dns` | systemd journal; `/var/log/pihole/pihole.log`; `/var/log/pihole/FTL.log`; Unbound journal | Generic baseline Alloy 1.19.2 is deployed and proven end to end with `role=dns-resolver`; the current active stage is journald-only. Pi-hole/FTL file sources remain deferred to the application/file-source stage. Same payload/rotation rules as `dns-01`. |
| `mail-relay-01` | `mail` | systemd journal, including Postfix | Generic baseline Alloy 1.19.2 is deployed and proven end to end with `role=mail-relay`, node-exporter health export, central heartbeat verification, genuine Postfix events in Loki and zero-drift idempotence. No standalone mail log is present; journal is authoritative. |
| `cloud-01` | `cloud` | systemd journal; Docker daemon; Nextcloud `/srv/cloud-01-data/data/nextcloud.log`; `app`, `cron`, PostgreSQL and Redis container logs | Generic baseline Alloy 1.19.2 is deployed and proven end to end with `role=cloud-host`; the current active stage is journald-only. Nextcloud application and Docker/container sources remain deferred to the application/file-source stage. Keep application/container identity as stable labels only. Do not label request IDs, URLs, users or client IPs. Redis secret must never appear in logs/argv. |
| `edge-01` | `edge` | systemd journal now; later `cloudflared` service journal when deployed | Generic baseline Alloy 1.19.2 is deployed and proven end to end with `role=edge-host`, node-exporter health export, heartbeat verification and zero-drift regression on existing Proxmox hosts. No additional application source yet. |
| `sensor-01` | `sensor` | systemd journal; `/var/log/suricata/eve.json`; `/var/log/suricata/suricata.log`; Zeek JSON logs | Dedicated capture NIC and SPAN traffic are proven. Suricata and Zeek are active. Dedicated sensor Alloy ships new Suricata EVE and Zeek JSON events to Loki with historical backfill disabled. Avoid duplicate `fast.log` alerts when equivalent EVE events exist. |
| `media-01` | `media` | systemd journal; `/home/james/.kodi/temp/kodi.log`; selected Samba service logs such as `log.smbd`, `log.nmbd`, `log.winbindd` | Generic baseline Alloy 1.19.2 is deployed and proven end to end on Raspberry Pi 5 ARM64 with `role=media-host`, node-exporter health export, central heartbeat verification and zero-drift idempotence. Kodi and Samba file sources remain deferred to the later application/file-source stage. |

## Current source observations

### `cloud-01`

- `cloud-01` is Debian 13 amd64 in a KVM guest and is proven through the generic Alloy baseline.
- Pinned Alloy `1.19.2-1` runs active with `role=cloud-host`; host-side acceptance proved `homelab_alloy_health_scrape_success=1`, write retries `0`, and dropped entries `0`.
- Central verification proved heartbeat query success `1`, heartbeat present `1`, heartbeat age about 128 seconds at acceptance, ICMP probe success `1`, and node-exporter `up=1`.
- Docker remained active during the rollout. Nextcloud `app` and `cron` containers were running, while PostgreSQL and Redis were both running with healthy container status.
- Nextcloud data directory: `/var/www/html/data`.
- Active Nextcloud application log on host: `/srv/cloud-01-data/data/nextcloud.log`.
- `app`, `cron`, PostgreSQL and Redis all use Docker `json-file` logging.
- The current Alloy stage remains journald-only; Nextcloud application and Docker/container logs are deferred until the application/file-source phase.

### `docker-01`

- `docker-01` is Debian 13 ARM64/aarch64 on a Raspberry Pi 4 and is proven through the generic Alloy baseline.
- Pinned Alloy `1.19.2-1` runs active with `role=docker-birdnet`; host-side acceptance proved `homelab_alloy_health_scrape_success=1`, write retries `0`, and dropped entries `0`.
- The final host-specific Alloy run was idempotent at `changed=0`, `failed=0`.
- Central verification proved heartbeat query success `1`, heartbeat present `1`, and heartbeat age about 41 seconds at acceptance. Existing ICMP and node-exporter monitoring were already healthy before promotion and did not require target changes.
- Docker remained active and the `birdnet-go` container remained running with healthy container status throughout acceptance.
- `birdnet-go` uses Docker `json-file` logging.
- Persistent mounts are `/opt/birdnet-go/config -> /config` and `/opt/birdnet-go/data -> /data`.
- Main file output is `/opt/birdnet-go/data/logs/application.log` at `info` level; it was present during acceptance.
- BirdNET `file_output` rotation is `max_size: 100` MB, `max_age: 30` days, and `max_rotated_files: 10`.
- BirdNET-Go module log zero-values inherit the parent `file_output` rotation settings, so the active module files are bounded rather than unlimited.
- The local module log directory was approximately 77 MB at discovery time, with high-volume debug sources including `analysis.log`, `actions.log`, and `birdnet.log`.
- The current Alloy stage remains journald-only. `birdnet-go` container output and `/opt/birdnet-go/data/logs/application.log` are deferred until the application/file-source phase; module debug files remain local/on-demand unless a demonstrated investigation use case justifies central ingestion.

### `media-01`

- `media-01` is Debian 13 on a Raspberry Pi 5 Model B and is the first ARM64/aarch64 proof target for the generic Alloy baseline.
- The standard reusable role installed pinned Alloy `1.19.2-1` without an architecture-specific code path; the existing `aarch64` support gate passed as designed.
- Alloy runs active/enabled with `role=media-host` and ships the systemd journal to central Loki. Kodi and Samba file sources are not activated yet.
- Host-side validation proved `homelab_alloy_health_scrape_success=1`, write retries `0`, dropped entries `0`, and clean idempotence at `changed=0`, `failed=0`.
- Central verification proved heartbeat query success `1`, heartbeat present `1`, heartbeat age about 84 seconds at acceptance, and no observability-pipeline alerts.
- Kodi service is systemd-managed.
- Current Kodi log: `/home/james/.kodi/temp/kodi.log`.
- Old/crash logs remain local unless an investigation explicitly needs them.
- Samba has multiple file logs; central collection is limited to core service logs initially when that later source stage is activated.

### `sensor-01`

- The dedicated USB capture NIC and switch SPAN path are proven and active.
- Suricata 8 is active and producing live EVE JSON at `/var/log/suricata/eve.json`.
- Zeek is active with boot persistence, JSON logging and Community ID enabled.
- Dedicated sensor Alloy ships new Suricata EVE and live Zeek JSON events to central Loki on `monitor-01`.
- Suricata-to-Loki and Zeek-to-Loki ingestion have both been proven end to end.
- Historical sensor-log backfill is intentionally disabled.

### Proxmox hosts

- `PROXMOX` and `Proxmox-2` both run pinned Alloy `1.19.2-1` from the Grafana APT repository under the reusable Ansible `alloy` role.
- Both hosts ship journald to `http://192.168.2.52:3100/loki/api/v1/push` with `environment=homelab`, canonical `host`, `role=proxmox-host`, `job=systemd-journal`, and `source=journal`.
- The Alloy HTTP endpoint is bound to `127.0.0.1:12345` only.
- Shared journal hygiene is configured to drop both observed Ansible module-wrapper forms: bare `Invoked with _raw_params=` payloads and prefixed `ansible-ansible... Invoked with` records. The final zero-new-wrapper confirmation from the last retest has not yet been captured in the documented evidence.
- Journal hygiene also drops only the exact known-benign Debian/OpenSSH `syslogin_perform_logout: logout() returned an error` message; other SSH events remain available to Loki.
- Each Proxmox host exports selected localhost-only Alloy write health into the existing node-exporter textfile collector, including scrape success, sent entries/bytes, write retries, and dropped entries/bytes.
- Each Proxmox host emits a five-minute `HOMELAB_ALLOY_HEARTBEAT` journal event. `monitor-01` independently queries Loki for those heartbeats and publishes per-host query-success, presence, newest timestamp, and age metrics.
- Prometheus alerting now distinguishes Alloy service failure, stale/local health collection, Loki write retries, dropped entries, central heartbeat query failure, stale heartbeat verification, and true end-to-end telemetry silence.
- Final validation proved both heartbeat streams present and fresh in Loki, all heartbeat queries succeeding, all eight pipeline-health rules loaded and inactive, no active alerts, and no failed units on `monitor-01`.
- The Alloy role was subsequently generalized into a profile-aware baseline. Regression runs after adding `edge-01` and `mail-relay-01` left both Proxmox hosts at `changed=0`, `failed=0`, proving the Proxmox profile remained zero-drift.
- PVE API access is recorded in `/var/log/pveproxy/access.log`.
- Per-task UPID files exist under `/var/log/pve/tasks`, but directly tailing every dynamic task file is not part of the initial Loki design.
- `vzdump` logs are useful backup/change evidence and may be collected in the next Proxmox file-source stage.

### `edge-01`

- `edge-01` is Debian 13 amd64 in an LXC guest and is the first non-Proxmox proof target for the generic Alloy baseline.
- The standard deployment installs and validates node-exporter first, then pinned Alloy `1.19.2-1` using the shared `alloy_hosts` contract.
- The Proxmox-specific `pveversion` gate is profile-controlled and is skipped for the edge profile; the remaining Debian, identity, Loki reachability, package, permissions, journal-access, readiness and failed-unit gates remain enforced.
- Alloy ships journald to central Loki with `environment=homelab`, `host=edge-01`, `role=edge-host`, `job=systemd-journal`, and `source=journal`.
- Alloy remains bound to `127.0.0.1:12345`; node-exporter exposes the selected health metrics on the normal Prometheus path.
- Host validation proved `homelab_alloy_health_scrape_success=1`, write retries `0`, dropped entries `0`, active health/heartbeat timers, and no failed units.
- Direct Loki validation returned multiple `HOMELAB_ALLOY_HEARTBEAT` events with the expected edge labels, proving end-to-end ingestion before central monitoring promotion.
- Central Prometheus/heartbeat monitoring now includes `edge-01` alongside the two Proxmox hosts.

### `monitor-01`

- Grafana, Prometheus, Alertmanager and Blackbox use Docker `json-file` logging.
- ASUS router syslog is received by rsyslog on UDP/5514 and written to `/var/log/homelab/router/rt-ac86u.log`.
- Dedicated monitor-side Alloy tails new ASUS router syslog entries and writes them to the local Loki instance on `127.0.0.1:3100`.
- Router-syslog-to-Loki ingestion, Alloy boot persistence and Ansible idempotence have been proven end to end.
- Historical router-log backfill is intentionally disabled.

### DNS hosts

- Pi-hole FTL and Unbound are active on both DNS hosts.
- Pi-hole query logs are materially larger than most service logs and therefore require controlled Loki retention.
- Both `dns-01` and `dns-02` are proven through the generic Alloy baseline. Pinned Alloy `1.19.2-1` runs with `role=dns-resolver`; Pi-hole FTL and Unbound remained active throughout both rollouts.
- Host-side acceptance on both resolvers proved `homelab_alloy_health_scrape_success=1`, write retries `0`, dropped entries `0`, and final idempotence at `changed=0`, `failed=0`.
- Central verification for `dns-01` proved heartbeat query success `1`, heartbeat present `1`, heartbeat age about 126 seconds at acceptance, DNS TCP probe success `1`, and node-exporter `up=1`.
- Central verification for `dns-02` proved heartbeat query success `1`, heartbeat present `1`, heartbeat age about 51 seconds at acceptance, DNS TCP probe success `1`, and node-exporter `up=1`.
- Both DNS resolvers remain journald-only in the current stage. `/var/log/pihole/pihole.log` and `/var/log/pihole/FTL.log` remain deferred until the application/file-source phase, when retention and payload handling can be controlled deliberately.

### `mail-relay-01`

- `mail-relay-01` is Debian 13 amd64 in an LXC guest and is the second non-Proxmox proof target for the generic Alloy baseline.
- Pinned Alloy `1.19.2-1` runs with `role=mail-relay`, `environment=homelab`, `job=systemd-journal` and `source=journal`.
- Host-side validation proved Alloy active/enabled, Postfix active, both Alloy health/heartbeat timers active, `homelab_alloy_health_scrape_success=1`, write retries `0`, dropped entries `0`, and no failed systemd units.
- Central verification proved heartbeat query success `1`, heartbeat present `1`, heartbeat age comfortably below the 600-second threshold, and no firing observability-pipeline alerts.
- Loki returned genuine Postfix `NOQUEUE:` events from the mail relay, proving the journald/Postfix path independently of Ansible diagnostic command text.
- The final Alloy idempotence run completed at `changed=0`, `failed=0`; the simultaneous regression run kept `PROXMOX`, `Proxmox-2`, and `edge-01` at zero drift as well.
- No standalone `/var/log/mail*` file is present; journald remains authoritative.

## Initial Alloy module model

```text
baseline-journal
controller
container-docker
birdnet
monitoring
router-syslog
proxmox
network-host-events
dns
mail
cloud
edge
sensor
media
```

Each host receives `baseline-journal` plus only the modules justified for its role.

## Rollout order

1. **Complete** — Deploy Loki on `monitor-01` with retention and Grafana datasource.
2. **Complete** — Repair primary `PROXMOX` Alloy endpoint and prove `PROXMOX -> Alloy -> Loki -> Grafana`.
3. **Complete** — Build the reusable Proxmox Alloy role, hygiene filters and validation gates.
4. **Complete** — Deploy and prove the reusable role on `Proxmox-2`, then reconcile `PROXMOX` through the same role with zero-drift/idempotence validation.
5. **Complete** — Add Loki/Alloy ingestion-health and telemetry-silence detection with host-side write metrics and independent end-to-end heartbeat verification.
6. **In progress** — Generic/profile-aware baseline is proven on `edge-01`, `mail-relay-01`, ARM64 `media-01`, `dns-01`, `dns-02`, `cloud-01`, and ARM64 `docker-01`; continue the reusable Alloy rollout to remaining low-risk Linux profiles host by host.
7. Add Docker/application file sources.
8. Add security telemetry after the sensor capture path is active and proven.

## Pending remediation before source activation

- Represent Ethernet-only policy for `admin-01` and `docker-01` in durable IaC rather than relying only on the current live NetworkManager state.
- Represent approved network-host identities in durable configuration so a collector database rebuild does not recreate known interfaces as unapproved.