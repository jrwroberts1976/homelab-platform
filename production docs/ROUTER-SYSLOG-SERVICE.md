# Router Syslog Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Receiver:** `monitor-01.jameshouse` / `192.168.2.52`  
**Source:** ASUS `RT-AC86U` / `192.168.2.1`  
**Transport:** UDP/5514  
**Status:** operational; local rsyslog receiver plus Alloy/Loki ingestion  
**Last current-state review:** 14 September 2026

## Purpose

The ASUS RT-AC86U remote-log capability provides operational/network context without requiring another VM.

The service deliberately retains a local rsyslog file while also shipping the dedicated router log into Loki through Alloy.

## Current data path

```text
RT-AC86U 192.168.2.1
        |
        | remote syslog UDP/5514
        v
monitor-01 192.168.2.52
        |
        +--> rsyslog
        |      |
        |      +--> /var/log/homelab/router/rt-ac86u.log
        |      +--> logrotate
        |
        +--> Alloy 1.19.2
               |
               v
        Loki on 127.0.0.1:3100
               |
               v
             Grafana
```

The earlier documentation that described Alloy/Loki as future work is superseded.

## Current validated state

The existing receiver remains operational:

- rsyslog active on `monitor-01`;
- UDP/5514 configured as the dedicated router receiver;
- source filtering retained for router `.1`;
- `/var/log/homelab/router/rt-ac86u.log` is the dedicated local file;
- logrotate policy remains part of the design;
- zero failed systemd units were reported by the 14 September compact audit.

The earlier packet validation proved router forwarding to the receiver. Current IaC now additionally deploys Alloy router-log shipping on `monitor-01`.

Direct 14 September monitoring validation also proved Loki running and ready on TCP/3100 and Alloy active locally on TCP/12345.

## Alloy/Loki configuration

Current IaC uses:

```text
router log:       /var/log/homelab/router/rt-ac86u.log
receiver bind:    192.168.2.52:5514
Loki push URL:    http://127.0.0.1:3100/loki/api/v1/push
Loki ready URL:   http://127.0.0.1:3100/ready
environment:      homelab
job:              network-infrastructure
service:          router-syslog
device:           rt-ac86u
```

These stable service/device labels are preferred over high-cardinality labels derived from arbitrary message content.

## Security boundary

The receiver:

- binds to the dedicated router-syslog listener on `192.168.2.52:5514/udp`;
- accepts the expected router source `192.168.2.1`;
- is LAN-only;
- does not provide cryptographic authentication, confidentiality or integrity because the transport is UDP syslog.

Source-IP filtering is useful but is not equivalent to authenticated log transport.

The Loki push path is local to `monitor-01` and does not require exposing a separate external log-ingest endpoint for the router.

## Retention

Router logs remain written locally to:

```text
/var/log/homelab/router/rt-ac86u.log
```

Local rotation provides short-term resilience and troubleshooting access even if Loki is temporarily unavailable. Loki adds central querying/visualisation; it does not remove the value of the local file.

Retention should be tuned from observed log volume and available storage rather than arbitrary long-term defaults.

## Deployment / reconciliation

Normal controller:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

Receiver deployment path:

```bash
cd ~/projects/homelab-platform
bash IaC/scripts/deploy-router-syslog-receiver.sh
```

Alloy shipping is managed through:

```text
IaC/ansible/playbooks/monitor-router-alloy.yml
IaC/ansible/roles/monitor_router_alloy/
```

The receiver and shipper are related but separate concerns: rsyslog owns receipt/local persistence, while Alloy owns forwarding to Loki.

## Router forwarding configuration

Expected router destination:

```text
server: 192.168.2.52
port:   5514
```

Repeat an end-to-end packet/log proof after:

- router firmware/reset changes;
- receiver rebuild;
- rsyslog configuration changes;
- switch/network redesign affecting the path;
- major Alloy/Loki changes.

## Monitoring and alerting

`monitor-01` receives the normal host/platform monitoring coverage and Loki readiness checks are part of the central monitoring validation.

No content-based router-log alerting is required by default. Add log alerts only after representative messages are classified and the result is actionable.

Useful LogQL queries should use the managed stable labels rather than turning arbitrary IPs, usernames, PIDs or message text into labels.

## Definition of current done state

The router logging path is operational because:

- rsyslog is IaC-managed on `monitor-01`;
- UDP/5514 is the expected receiver;
- router source filtering exists;
- local rotation is configured;
- the dedicated router log exists as the local source of truth for receipt;
- Alloy router-log shipping is deployed through IaC;
- Loki is running/ready on `monitor-01`;
- the central monitoring platform and local Alloy service were directly validated on 14 September 2026.
