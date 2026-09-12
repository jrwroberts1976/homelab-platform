# Router Syslog Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Receiver:** `monitor-01.jameshouse` / `192.168.2.52`  
**Source:** ASUS `RT-AC86U` / `192.168.2.1`  
**Transport:** UDP/5514  
**Status:** operational; local receiver and router forwarding validated; Alloy/Loki ingestion not deployed  
**Last current-state review:** 12 September 2026

## Purpose

The ASUS RT-AC86U remote-log capability provides operational/network context without requiring another VM.

The current implementation stores router logs locally on `monitor-01`. Central Loki/Alloy ingestion is a future phase, not current state.

## Current data path

```text
RT-AC86U 192.168.2.1
        |
        | remote syslog UDP/5514
        v
monitor-01 192.168.2.52
        |
        +--> rsyslog
        |
        +--> /var/log/homelab/router/rt-ac86u.log
        |
        +--> logrotate
        |
        +--> future: Alloy -> Loki -> Grafana
```

## Current validated state

The 12 September audit confirmed:

- rsyslog active/enabled on `monitor-01`;
- UDP/5514 listening on `.52`;
- source filtering configured for router `.1`;
- `/var/log/homelab/router/rt-ac86u.log` exists and is actively updating;
- logrotate configuration exists;
- zero failed systemd units.

The earlier end-to-end packet test on 10 September 2026 proved actual router forwarding to the receiver. That historical test was launched from the then-current TestServer administration context; TestServer is now retired and should not be used for current deployment commands.

## Security boundary

The receiver:

- binds to the dedicated router-syslog listener on `192.168.2.52:5514/udp`;
- accepts the expected router source `192.168.2.1`;
- is LAN-only;
- does not provide cryptographic authentication, confidentiality or integrity because the transport is UDP syslog.

Source-IP filtering is useful but is not equivalent to authenticated log transport.

## Retention

Router logs are written to:

```text
/var/log/homelab/router/rt-ac86u.log
```

Current local rotation provides short-term resilience. Retention can be revisited after central logging is deliberately deployed and real log volume is understood.

## Deployment / reconciliation

Normal controller:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

Approved wrapper:

```bash
cd ~/projects/homelab-platform
bash IaC/scripts/deploy-router-syslog-receiver.sh
```

The wrapper manages/validates:

- `monitor-01` identity;
- UDP/5514 collision/listener state;
- Ansible configuration;
- rsyslog configuration validation;
- source filtering;
- logrotate policy;
- idempotence.

## Router forwarding configuration

Expected router destination:

```text
server: 192.168.2.52
port:   5514
```

The 10 September packet validation observed real UDP traffic from the router to `.52:5514` and matching router events in the dedicated file.

Repeat an end-to-end packet/log proof after:

- router firmware/reset changes;
- receiver rebuild;
- rsyslog configuration changes;
- switch/network redesign affecting the path.

## Monitoring and alerting

`monitor-01` itself receives the normal host/platform monitoring coverage.

No content-based router-log alerting is required by default. Add log alerts only after representative messages are classified and the result is actionable.

The audit also observed frequent router SSH-related log activity associated with an internal infrastructure source. Treat that as an item for later attribution/documentation, not as a reason to change the router during this documentation pass.

## Future logging integration

Loki and Alloy are **not deployed on `monitor-01`** today.

If/when central logging is implemented:

- ingest only the dedicated router log rather than broad host syslog;
- use stable low-cardinality labels such as `job=router_syslog`, device/vendor/site identifiers;
- preserve raw messages;
- avoid usernames, process IDs, destination IPs or full message text as Loki labels;
- validate the complete path from a fresh router event to a Loki query before declaring central ingestion operational.

Suggested future selector:

```logql
{job="router_syslog", device="rt-ac86u"}
```

## Definition of current done state

The local receiver phase is complete because:

- rsyslog is IaC-managed on `monitor-01`;
- UDP/5514 listens on the expected receiver;
- router source filtering exists;
- rotation is configured;
- real router packets were proven end-to-end;
- real router messages are present in the dedicated log;
- the file remained live during the 12 September audit.

The central logging phase remains future work until Alloy and Loki are deliberately deployed and validated.
