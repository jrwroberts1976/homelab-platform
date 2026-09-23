# Alloy → Loki log inventory and audit

**Audit opened:** 2026-09-23  
**Status:** IN PROGRESS — do not interpret an IaC declaration or historical stream as current delivery.  
**Authority:** [CURRENT-STATE.md](CURRENT-STATE.md), [estate.json](../../IaC/inventory/estate.json), live installed Alloy configuration and Loki query results.

## Audit criteria

For each active host, independently establish (1) service status and deployed Alloy configuration; (2) exact configured log sources, collection method, filtering and labels; (3) Loki streams received in the last 24 hours; (4) latest event age for each host/job/source stream; (5) whether source events are expected to occur regularly; and (6) other log shippers or direct-to-Loki producers. Record **configured**, **observed**, **fresh**, **idle**, **missing**, and **not assessed** separately. Do not equate host heartbeat with coverage of application logs. No production changes or logging of secrets during audit.

## Known collection paths (IaC and production evidence)

| Source | Collection path | Loki job/labels | Status / caveats |
|---|---|---|---|
| Managed Linux systemd journal | Native Alloy `loki.source.journal` → `loki.process.journal_hygiene` → Loki | `job=systemd-journal` (default); `host`, `hostname`, `role`, `environment`, `source` | Baseline defined in Alloy role. Journal filter drops Ansible raw module invocation lines and benign Debian OpenSSH logout warning. Last 15-minute Loki host coverage 15/15 verified on 2026-09-23, but per-job freshness still to audit. |
| Docker containers | Alloy Docker discovery → `loki.source.docker` → Loki, enabled per host | `job=docker`; `host`, `hostname`, `container`, `service`, `role`, `environment`, `source` | Conditionally enabled. Previous 24-hour management evidence showed 2 reporting Docker hosts; verify which hosts, containers, active sources and log hygiene. |
| Pi-hole on `dns-01` and `dns-02` | `/var/log/pihole/pihole.log` → Alloy file source → strict event-token-only pipeline → Loki | `job=pihole`, `host`, `hostname`, `role=dns-resolver`, `source=pihole-event` | **Production verified 2026-09-23:** both resolvers deployed and healthy; 100 recent entries sampled per host, zero unexpected content. Tokens include `query[A]`, `query[AAAA]`, `forwarded`, `reply`, `gravity blocked`; `dns-01` also `query[HTTPS]`. **No raw client IP/domain is intended to leave host.** These samples are not an exhaustive historical privacy audit. |
| ASUS router syslog | Router UDP/5514 → `monitor-01` local router log → dedicated router Alloy pipeline → Loki | Verify live `job`, `source`, `device` labels | Described in current-state architecture; check exact installed configuration, last router event and rotation. |
| Network security/infrastructure | Existing Loki streams `job=network-security` and `job=network-infrastructure` | Verify exact labels and actual source | Both were present in previous 24-hour management evidence, one reporting host each; do not assume all Suricata/Zeek raw logs are sent. Their separate aggregate evidence is transferred by SFTP to management reporting. |

## Active-host audit matrix

The 15 managed Linux systems below were observed in Loki within a 15-minute window on 2026-09-23; **that is host presence only**, not proof of every source or current freshness at audit time. `home-01` is Home Assistant OS, not in the 15-host Linux Ansible baseline; audit its logging separately and do not assume native Alloy.

| Host | Baseline journal (historical) | Additional logs to verify in live Alloy/Loki | Per-stream current result |
|---|---|---|---|
| `admin-01` | observed host presence | controller, QNetd, recovery jobs if journalled | PENDING |
| `dns-01` | observed host presence | Pi-hole sanitised tokens **verified**; Unbound/FTL journal coverage to verify | PENDING full audit |
| `dns-02` | observed host presence | Pi-hole sanitised tokens **verified**; Unbound/FTL journal coverage to verify | PENDING full audit |
| `monitor-01` | observed host presence | router syslog; monitoring containers and any dedicated network log sources | PENDING |
| `cloud-01` | observed host presence | Nextcloud/PostgreSQL/Redis logs, if configured | PENDING |
| `mail-relay-01` | observed host presence | Postfix journal/mail logs | PENDING |
| `sensor-01` | observed host presence | Suricata/Zeek logs versus separate aggregate evidence | PENDING |
| `edge-01` | observed host presence | no cloudflared/NPM assumed deployed | PENDING |
| `greenbone-01` | observed host presence | Greenbone services/scan logs | PENDING |
| `komodo-01` | observed host presence | Komodo Core/MongoDB Docker logs | PENDING |
| `zabbix-01` | observed host presence | Zabbix Server/PostgreSQL/Nginx logs | PENDING |
| `PROXMOX` | observed host presence | Proxmox/Corosync/backup logs | PENDING |
| `Proxmox-2` | observed host presence | Proxmox/Corosync/network host collector logs | PENDING |
| `media-01` | observed host presence | Kodi/NFS/backup logs | PENDING |
| `docker-01` | observed host presence | BirdNET-Go/Komodo Periphery Docker logs | PENDING |
| `home-01` | NOT ASSESSED | Home Assistant OS; inspect supported HA logging integration separately | PENDING |

## Audit method

1. Run the read-only host-side Alloy service/configuration inventory through Ansible for managed Linux hosts. Report only source blocks and paths; never print service environment files, credentials, or full application log contents.
2. Query Loki `/loki/api/v1/series` over 24 hours for actual label combinations. Query `/loki/api/v1/query` using `max_over_time(timestamp({host=...})[24h])` or an equivalent bounded last-event query for per-stream freshness. Do not print raw log lines.
3. Reconcile both inventories. A configured source without a stream may be idle, misconfigured, or broken; investigate before assigning a status. An observed stream not represented in the current Alloy config may be historical, another shipper, or a direct producer.
4. Capture sample time, source label set, most recent event UTC, event age, status and privacy handling per stream. Preserve exact raw log locations only when configuration proves them.
5. Open separate remediation tasks for genuine gaps and legacy shipper consolidation; do not alter production during this read-only audit.

## Follow-up

Complete the per-host matrix from live evidence, then add a concise summary/link to CURRENT-STATE.md. Pi-hole 24-hour aggregate counts in the 06:00 management report remain a **separate outstanding integration**, not verified by successful Loki ingestion.

## First live audit — operator evidence, 2026-09-23

Read-only Ansible Alloy inspection and Loki `/series` query (`{host=~".+"}`, 24-hour window) returned **15 distinct hosts and 28 distinct host/job/source/container/service combinations**. This is stream presence over 24 hours, **not per-stream freshness or complete application log coverage**. Host-side Alloy inspection succeeded for 12 of 13 hosts in `alloy_hosts`; `admin-01` failed due to missing sudo password. `monitor-01` and `sensor-01` were not shown in that Ansible group output and require separate deployed configuration inspection.

| Host | Live configured Alloy sources (where inspected) | Loki sources observed over 24h | Gap / next check |
|---|---|---|---|
| `admin-01` | NOT ASSESSED (Ansible sudo password missing) | systemd-journal | Inspect local config without exposing secrets. |
| `dns-01` | journal; Pi-hole sanitised file | journal; Pi-hole | Check per-stream freshness. |
| `dns-02` | journal; Pi-hole sanitised file | journal; Pi-hole | Check per-stream freshness. |
| `monitor-01` | NOT ASSESSED in this Ansible group | router-syslog (`network-infrastructure`) | No journal stream observed in this 24h result; inspect live Alloy/other shippers. |
| `cloud-01` | journal | journal | Check whether application logs require additional collection. |
| `mail-relay-01` | journal | journal | Check Postfix event coverage/freshness. |
| `sensor-01` | NOT ASSESSED in this Ansible group | Suricata and Zeek (`network-security`) | No journal stream observed in this 24h result; inspect live Alloy/other shippers; separate SFTP aggregate evidence is not raw Loki coverage. |
| `edge-01` | journal | journal | Check freshness; no NPM/cloudflared assumed. |
| `greenbone-01` | journal; Docker discovery | journal; Docker: gsad, two ephemeral gvm-tools, gvmd, nginx, openvasd, ospd-openvas, pg-gvm, Komodo Periphery | Verify expected active containers and freshness; ephemeral streams can be historical. |
| `komodo-01` | journal; Docker discovery | journal; Docker: mongo | Komodo Core container stream not observed in this 24h result; investigate logging driver/activity. |
| `zabbix-01` | journal | journal | Check application logs and freshness. |
| `PROXMOX` | journal | journal | Check freshness. |
| `Proxmox-2` | journal | journal | Check freshness. |
| `media-01` | journal | journal | Check freshness. |
| `docker-01` | journal only | journal only | BirdNET-Go and Komodo Periphery Docker logs not observed; determine whether Docker log collection should be enabled after privacy review. |
| `home-01` | NOT ASSESSED (HAOS, outside managed Linux baseline) | none in this query | Separate supported HAOS logging assessment; not counted in 15 Linux hosts. |

**Totals:** 13 systemd-journal hosts; 2 Pi-hole hosts; 2 Docker hosts; router syslog on monitor-01; Suricata and Zeek on sensor-01. **Known gaps to investigate:** absent journal streams on monitor-01/sensor-01 in queried window; missing docker-01 container streams; only MongoDB Docker stream on komodo-01; admin-01 sudo access for audit. Do not change production or treat missing streams as outages without checking configuration and source activity.

## Specialist pipeline and freshness follow-up — operator evidence, 2026-09-23 ~07:38 UTC

Read-only live config inspection showed **monitor-01 Alloy active** with dedicated `loki.source.file "router_syslog"` tailing `/var/log/homelab/router/rt-ac86u.log`, and **sensor-01 Alloy active** with dedicated `loki.source.file "suricata"` tailing `/var/log/suricata/eve.json` and `loki.source.file "zeek"` tailing `/opt/zeek/spool/zeek/*.log`, each with corresponding processing. **Their absent systemd-journal streams are explained by these specialist installed configs, not demonstrated journal ingestion faults.** Do not assert they also collect journals without a separate configuration change.

A bounded 24-hour Loki query, `limit=1000` per host, showed most recent event ages at query time: `monitor-01` router syslog 4.8 min; `sensor-01` Suricata 0–0.1 min and Zeek 0–0.5 min across multiple label sets; `docker-01` journal newest 0.2 min (a second journal label set 96.2 min); `komodo-01` MongoDB 0.0 min and journal 0.3 min (another label set 7.7 min); `dns-01` Pi-hole 0.1 min and journal 0.4 min; `dns-02` Pi-hole 0.5 min and journal 0.4 min. These are **sampled returned streams**: query-wide limit can omit quieter streams, so do not claim exhaustive 24h source coverage. `admin-01` Alloy active but local config requires elevated access; earlier Ansible become failed with missing sudo password.

**Next reconciliation:** read-only inspect `docker-01` live Docker logging drivers/container list and Komodo Core logging driver/activity, then review Alloy Docker discovery enablement and privacy before proposing changes. Confirm source coverage/freshness for remaining hosts via per-stream queries. Home Assistant OS remains separately not assessed. Pi-hole aggregate integration into morning report remains outstanding.

## Docker logging-driver and container-state audit — operator evidence, 2026-09-23

Read-only Docker inspection completed on `greenbone-01`, `komodo-01`, `docker-01`: **all three daemon defaults and every listed container use `json-file`**. No incompatible logging driver explains absent Loki streams. Container status is point-in-time; a running container may not have emitted logs in the queried 24h window.

| Host | Running containers | Running containers not observed by name in prior 24h Loki `/series` | Explanation / action |
|---|---|---|---|
| `greenbone-01` | `gsad`, `gvmd`, `nginx`, `openvasd`, `ospd-openvas`, `pg-gvm`, `redis-server`, `komodo-periphery` (8) | `greenbone-community-edition-redis-server-1` | Docker Alloy source configured and seven other running container names observed; check whether Redis emitted logs and whether discovery includes it. Two ephemeral `gvm-tools-run-*` Loki streams are historical and are not current running containers. |
| `komodo-01` | `komodo-core-1`, `komodo-mongo-1` (2) | `komodo-core-1` | Docker Alloy source configured; MongoDB live. Check Core local log activity and Docker discovery/relabel before treating as ingestion fault. |
| `docker-01` | `birdnet-go`, `komodo-periphery-periphery-1` (2) | Both | Installed Alloy config is journal-only; Docker log collection not enabled. Review privacy/volume and enable Docker pipeline through IaC if approved. |

**Next read-only check:** obtain per-container `docker logs --since 24h` counts without exposing log lines, confirm Alloy Docker discovery on Greenbone/Komodo and verify whether the quiet/missing streams have events. If the local logs exist but Loki has no matching stream, investigate ingestion; if no local logs, mark source idle rather than broken. Avoid printing Docker inspect environment or raw logs.

## Docker local-log counts and /var/log scope decision — 2026-09-23

Operator sampled `docker logs --since 24h` with line counts (stderr included in count; no raw contents printed):

| Host | Running container | Local lines in 24h | Prior Loki observation | Assessment |
|---|---|---:|---|---|
| greenbone-01 | komodo-periphery-periphery-1 | 5 | present | delivered previously; freshness to verify |
| greenbone-01 | greenbone-community-edition-nginx-1 | 33077 | present | high-volume source; check retention/volume |
| greenbone-01 | greenbone-community-edition-gsad-1 | 2 | present | low-volume |
| greenbone-01 | greenbone-community-edition-gvmd-1 | 6 | present | low-volume |
| greenbone-01 | greenbone-community-edition-pg-gvm-1 | 48 | present | low-volume |
| greenbone-01 | greenbone-community-edition-ospd-openvas-1 | 5 | present | low-volume |
| greenbone-01 | greenbone-community-edition-openvasd-1 | 24 | present | low-volume |
| greenbone-01 | greenbone-community-edition-redis-server-1 | 0 | absent | idle locally; absence from Loki is not a demonstrated ingestion fault |
| komodo-01 | komodo-mongo-1 | 68975 | present | high-volume source; check retention/volume |
| komodo-01 | komodo-core-1 | 0 | absent | idle locally; absence from Loki is not a demonstrated ingestion fault |
| docker-01 | komodo-periphery-periphery-1 | 5 | absent | **collection gap:** Alloy journal-only on docker-01 |
| docker-01 | birdnet-go | 2 | absent | **collection gap:** Alloy journal-only on docker-01 |

**User-requested expanded scope:** audit **all `/var/log` entries across the active managed Linux hosts**, then add appropriate text-file logs to Alloy/Loki. Do not glob `/var/log/**` blindly: excludes must cover Pi-hole raw DNS logs (retain event-only pipeline), sensitive authentication/application logs where privacy is not approved, binary files (`wtmp`, `btmp`, `lastlog`, journals), duplicate journal-derived files, temporary/rotated/compressed files and high-volume sources requiring an explicit budget. For each host/path record existence, file type, size, read access by Alloy, rotation policy, privacy classification, desired labels and last Loki event. Use per-host allowlists or explicit reviewed path patterns. Do not silently change permissions or grant broad access to sensitive logs. Existing dedicated router and Suricata/Zeek pipelines must not be duplicated. **Status: inventory and design pending; no broad `/var/log` deployment claimed.**

The next safe read-only operator step is a metadata-only `/var/log` file inventory (no log contents) across `alloy_hosts`, followed by review of privacy, volume and duplication before IaC rollout. `admin-01` needs local `sudo` for its own metadata inspection.


## Estate /var/log metadata inventory — 2026-09-23

**Evidence:** [raw metadata inventory on audit branch](../../docs/architecture/evidence/alloy-var-log-inventory-20260923.txt) (branch \`audit/alloy-log-inventory\`, commit \`6f84d50\`). The branch must be reviewed before merging; the repository is private, but file paths and task filenames reveal internal topology and account names. No log bodies, configuration contents or credentials were collected. This is a point-in-time file inventory, **not** proof of active writes, Alloy readability, rotation health, Loki freshness or successful ingestion.

The Ansible \`alloy_hosts\` run returned twelve hosts successfully; \`admin-01\` failed remote privilege escalation and was inspected locally with sudo (17 files). The combined file has 871 lines including wrappers and separators. \`monitor-01\` and \`sensor-01\` have specialist configurations and were not scanned by this run. \`home-01\` is HAOS and outside the managed Linux baseline.

| Host | Files inventoried | Candidate sources or findings | Review outcome |
|---|---:|---|---|
| \`PROXMOX\` | 444 | Network-host JSONL (984 B), backup \`vzdump\` logs, Proxmox proxy access log (~6.5 MB), firewall log, package logs | Network-change JSONL and current backup job outcome worth evaluating; do not tail historical per-task logs or raw access data by default. |
| \`Proxmox-2\` | 206 | Network-host JSONL (~302 kB), \`vzdump\` logs, proxy access log (~6.4 MB), package logs | Same restrictions as PROXMOX; existing collector/report coverage must be checked before duplication. |
| \`media-01\` | 43 | Samba logs including client-specific names/IP filenames, Kodi/desktop context, Zabbix agent | Privacy review essential; use journal/metrics unless an actionable Samba failure signal is demonstrably missing. |
| \`cloud-01\` | 19 | Cloud-init and unattended-upgrades text logs, package logs | Avoid duplicating existing patch-report metrics or historical provisioning output. No Nextcloud app log observed under /var/log; check authoritative application storage separately. |
| \`docker-01\` | 19 | Mostly journal, package, boot/desktop and Zabbix logs | **Docker logs are outside /var/log:** prior audit confirmed local BirdNET-Go (2) and Periphery (5) lines/24h absent from Loki. Enable only after privacy review and scoped labels/filters. |
| \`greenbone-01\` | 18 | Package and unattended-upgrades text logs | Existing Docker discovery observes seven active sources; Redis emitted zero local lines in the sampled window. High-volume nginx source requires cost/retention review. |
| \`zabbix-01\` | 17 | \`zabbix_server.log\` (~129 kB), PostgreSQL (~368 kB), nginx access (~9 MB), nginx error (~613 kB), PHP-FPM | Candidate application diagnostics, but protect request/client data and database content; avoid raw nginx access ingestion pending explicit approval. |
| \`admin-01\` | 17 | Zabbix agent (~188 kB), provisioning/desktop logs | Local sudo audit complete; remote Ansible become remains an operational access issue, not proof of Alloy failure. |
| \`dns-01\` | 16 | Raw Pi-hole query log (~11.8 MB), FTL, updateGravity | **Do not forward raw DNS**. Preserve verified event-only Pi-hole pipeline; examine sanitized FTL/update outcome only if needed. |
| \`dns-02\` | 16 | Raw Pi-hole query log (~1.5 MB), FTL, updateGravity | Same privacy restriction as dns-01. |
| \`edge-01\` | 11 | Journal, package logs, idle empty syslog | No independent file source needed based on metadata alone. |
| \`mail-relay-01\` | 12 | Journal, package logs, idle empty syslog | Validate Postfix events in journal before adding any raw mail logs; protect addresses and message metadata. |
| \`komodo-01\` | 12 | Journal, package logs, idle empty syslog | Docker discovery present; Komodo Core had zero local log lines in prior sample, so absence from Loki is not a demonstrated fault. |

**Conservative source decisions:**
1. Do **not** recursively ingest \`/var/log\`: exclude binary journal/utmp files, rotated and historical files, Proxmox task trees, raw Pi-hole, proxy access files, Samba client-specific logs, sensitive mail/authentication data and duplicate journal-derived files.
2. Before a file-tail rollout, establish active-event frequency, logrotate behavior, read permissions for the \`alloy\` account, existing journal or aggregate coverage, data minimization, labels, retention and Loki freshness.
3. Prioritize the demonstrated \`docker-01\` gap with narrowly scoped, event-sanitized collection of BirdNET-Go and Komodo Periphery. Membership in the Docker group exposes privileged socket access; review the security implications before enabling the generic Docker source.
4. Next evaluate narrow, useful file/event coverage for the two Proxmox backup outcome streams, network-host change JSONL, Zabbix server failures and PostgreSQL errors; raw proxy and DB logs must not be copied without a separate privacy review.
5. Audit specialist \`monitor-01\` and \`sensor-01\` metadata separately and verify current Loki source-level freshness before closing Step 9.

**Step 9 status:** metadata review complete for the thirteen Ansible-group hosts (twelve remote, one local); specialist hosts and live per-source validation outstanding. No production deployment or ingestion validation is claimed.
