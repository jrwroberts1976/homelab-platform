# Router Syslog Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Receiver:** `monitor-01.jameshouse` / `192.168.2.52`  
**Source:** ASUS `RT-AC86U` / `192.168.2.1`  
**Transport:** UDP/5514  
**Status:** receiver IaC defined; router forwarding not yet configured

## Purpose

The ASUS RT-AC86U exposes limited monitoring telemetry. Its built-in remote log capability provides an additional source of operational and network context without introducing another VM or logging platform.

The first implementation deliberately stores router logs locally on `monitor-01`. Loki/Alloy ingestion is deferred until the central logging platform is deployed.

## Data path

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
        +--> logrotate (30 daily rotations)
        |
        +--> later: Alloy -> Loki -> Grafana
```

## Security boundary

The receiver:

- binds only to `192.168.2.52:5514/udp`;
- accepts messages only when rsyslog reports the source address as `192.168.2.1`;
- discards traffic arriving on this dedicated listener from any other source;
- does not expose TCP/514 or UDP/514;
- does not introduce a host-firewall framework solely for this listener.

The source-IP restriction is a filtering control, not cryptographic authentication. UDP syslog provides no confidentiality or integrity protection, so this listener is LAN-only.

## Retention

Router logs are written to:

```text
/var/log/homelab/router/rt-ac86u.log
```

Initial rotation policy:

- daily rotation;
- 30 retained rotations;
- compression enabled;
- empty logs are not rotated;
- rotated files remain local to `monitor-01`.

Retention can be revisited after real log volume is measured.

## Deployment

From TestServer:

```bash
cd ~/projects/homelab-platform
bash IaC/scripts/deploy-router-syslog-receiver.sh
```

The wrapper performs:

1. monitor-01 identity validation;
2. UDP/5514 collision detection;
3. Ansible syntax validation;
4. rsyslog installation and configuration;
5. `rsyslogd -N1` configuration validation;
6. exact listener/source-filter validation;
7. logrotate policy validation;
8. a second Ansible apply that must report `changed=0`.

## Router configuration gate

Do not configure the RT-AC86U remote-log destination until the receiver deployment has passed.

The intended router destination is:

```text
server: 192.168.2.52
port:   5514
```

After the router setting is applied, prove ingestion by generating or observing a benign router log event and confirming new lines arrive in `rt-ac86u.log` with plausible timestamps and router content.

## Alerting

`monitor-01` already receives the normal **standard alerting** coverage for host reachability, Node Exporter availability, CPU, memory and filesystem capacity.

No content-based router-log alerts are enabled initially. Alert rules should only be introduced after representative RT-AC86U messages have been observed and classified, to avoid noisy or low-value alerts.

## Future logging integration

When Alloy/Loki is deployed:

- ingest the dedicated router log rather than broad host syslog;
- add stable labels such as `job=router_syslog`, `device=rt-ac86u`, `host=router`;
- preserve the raw message;
- parse only fields that prove stable across the router firmware actually in use;
- keep local rotation as a short-term resilience layer unless central retention makes it unnecessary.

## Definition of done

The receiver phase is complete when:

- rsyslog is IaC-managed on monitor-01;
- UDP/5514 listens only on 192.168.2.52;
- the dedicated listener filters to 192.168.2.1;
- log rotation is configured;
- the deployment is idempotent;
- router forwarding is configured only after receiver validation;
- a real RT-AC86U message is proven in the dedicated log.
