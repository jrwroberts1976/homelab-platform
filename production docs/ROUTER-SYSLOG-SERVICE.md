# Router Syslog Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Receiver:** `monitor-01.jameshouse` / `192.168.2.52`  
**Source:** ASUS `RT-AC86U` / `192.168.2.1`  
**Transport:** UDP/5514  
**Status:** operational; receiver and router forwarding validated 10 September 2026; Alloy/Loki ingestion pending

## Purpose

The ASUS RT-AC86U exposes limited monitoring telemetry. Its built-in remote log capability provides an additional source of operational and network context without introducing another VM or logging platform.

The current implementation stores router logs locally on `monitor-01`. Real router forwarding has been proven end-to-end. Alloy/Loki ingestion is the next logging phase.

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
        +--> next: Alloy -> Loki -> Grafana
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

## Router forwarding validation

The RT-AC86U remote-log destination is configured as:

```text
server: 192.168.2.52
port:   5514
```

End-to-end forwarding was validated on 10 September 2026 from TestServer by capturing the receiver traffic on `monitor-01` while generating a benign router SSH event.

Observed packet path:

```text
192.168.2.1:50100 -> 192.168.2.52:5514/udp
```

The validation capture received three matching packets with zero packets dropped by the receiver kernel. The dedicated log simultaneously recorded real RT-AC86U events including Dropbear connection, public-key authentication success and disconnect messages.

The dedicated log path was confirmed as:

```text
/var/log/homelab/router/rt-ac86u.log
```

This proves the router-to-rsyslog local collection path. Repeat the same packet/log test after router firmware changes, receiver rebuilds, or syslog configuration changes.

## Alerting

`monitor-01` receives the normal **standard alerting** coverage for host reachability, Node Exporter availability, CPU, memory and filesystem capacity as those monitoring stages are enabled.

No content-based router-log alerts are enabled initially. Alert rules should only be introduced after representative RT-AC86U messages have been observed and classified, to avoid noisy or low-value alerts.

## Future logging integration

When Alloy/Loki is deployed:

- ingest the dedicated router log rather than broad host syslog;
- add only stable labels such as `job=router_syslog`, `device=rt-ac86u`, `device_type=router`, `vendor=asus` and `site=home`;
- preserve the raw message;
- do not promote source IPs, usernames, process IDs, destination addresses or message text to Loki labels;
- parse event fields at query time unless a field proves stable and low-cardinality;
- keep local rotation as a short-term resilience layer unless central retention makes it unnecessary;
- validate the full path from new router event to Loki query before declaring central ingestion operational.

Suggested initial Loki selector:

```logql
{job="router_syslog", device="rt-ac86u"}
```

## Definition of done

The local receiver phase is complete because:

- rsyslog is IaC-managed on monitor-01;
- UDP/5514 listens on the dedicated receiver;
- the listener filters to the RT-AC86U source;
- log rotation is configured;
- the deployment is designed to be idempotent;
- router forwarding is configured;
- real RT-AC86U packets have been captured at the receiver;
- real RT-AC86U messages have been proven in the dedicated log.

The next phase is complete only when Alloy tails this dedicated file, Loki receives the entries, and a Grafana/Loki query proves the end-to-end central logging path.
