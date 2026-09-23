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
