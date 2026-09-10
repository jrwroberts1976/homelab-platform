# Central Logging Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Primary platform:** `monitor-01.jameshouse` / `192.168.2.52`  
**Status:** planned; router local syslog collection is already operational

## Purpose

Provide a fresh, Git-managed central logging path for the rebuilt homelab using Alloy collectors and Loki storage/querying, surfaced through Grafana on `monitor-01`.

The old TestServer Alloy/Loki configuration is migration evidence only. It is not the desired-state source and must not be copied wholesale into the new platform.

## Target architecture

```text
approved host logs / dedicated service logs
             |
             v
            Alloy
             |
             v
        Loki on monitor-01
             |
             v
           Grafana
```

The first validated source is the ASUS router syslog path:

```text
RT-AC86U 192.168.2.1
  -> UDP/5514
  -> monitor-01 rsyslog
  -> /var/log/homelab/router/rt-ac86u.log
  -> Alloy (planned)
  -> Loki (planned)
  -> Grafana (planned)
```

## Design rules

- Build Loki/Alloy fresh from Git/IaC.
- Add sources deliberately; do not ingest every file merely because it exists.
- Keep labels low-cardinality. Host, service/job, environment and device type are acceptable; message text, usernames, PIDs and arbitrary addresses are not labels.
- Preserve raw log messages where practical and parse high-cardinality fields at query time.
- Do not commit credentials, API tokens or secret-bearing environment files.
- Keep local rotation for important dedicated files until central retention and recovery are proven.
- Logging failure must not break the source application.

## Initial source order

1. ASUS router dedicated syslog file on `monitor-01`.
2. `monitor-01` service logs needed to operate the monitoring platform.
3. `edge-01` / `cloudflared` logs after the tunnel service is deployed.
4. Proxmox host/system logs where operational value is clear.
5. `sensor-01` Suricata/Zeek logs after the sensor pipeline is stable.
6. Other hosts only after retention and label impact are reviewed.

## Implementation sequence

1. define Loki storage, retention and resource limits for `monitor-01`;
2. deploy Loki through the monitoring IaC role/stack;
3. deploy Alloy configuration for the first source;
4. validate file permissions and source read access;
5. send logs to Loki and verify successful ingestion;
6. query the first source from Grafana;
7. add health metrics/alerts for Loki and Alloy;
8. document retention and backup/rebuild policy;
9. repeat source-by-source rather than importing the legacy TestServer configuration.

## Router source validation

The local receiver phase is already proven. The dedicated file is:

```text
/var/log/homelab/router/rt-ac86u.log
```

Suggested initial selector:

```logql
{job="router_syslog", device="rt-ac86u"}
```

The central logging phase is not complete until a newly generated router event can be found through Loki/Grafana after traversing the full path.

## Monitoring

Monitor at least:

- Loki process/container health;
- Alloy process/service health;
- ingestion errors/retries;
- Loki storage usage;
- query readiness;
- age of latest expected log for critical sources where meaningful.

Alert only on actionable failure conditions; do not create content-alert noise before representative logs have been classified.

## Recovery

If logs stop arriving:

1. verify source application/service still emits logs;
2. verify local file/journal contains fresh entries;
3. verify Alloy can read the source;
4. inspect Alloy errors/backpressure;
5. verify Loki readiness/storage availability;
6. query Loki directly before blaming Grafana;
7. restart only the failing layer after configuration is verified;
8. rebuild from Git/IaC if local configuration has drifted or become unrecoverable.

## Definition of done

Central logging is operational when Loki is running on the approved monitoring platform, Alloy sends at least the router source end-to-end, Grafana can query it, health/retention are documented, the deployment is reproducible and the old TestServer logging stack is no longer required as a production dependency.
