<!-- estate-authority: IaC/inventory/estate.json -->
# Router Syslog Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Receiver:** `monitor-01.jameshouse` / `192.168.2.52`  
**Source:** ASUS `RT-AC86U` / `192.168.2.1`  
**Transport:** UDP/5514  
**Status:** operational; local rsyslog receiver plus Alloy/Loki ingestion  
**Last current-state review:** 16 September 2026

## Purpose

The ASUS RT-AC86U remote-log capability provides operational/network context without requiring another VM.

The service deliberately retains a local rsyslog file while also shipping the dedicated router log into Loki through Alloy. The same path now carries OpenVPN server events from the router, including authentication, tunnel establishment, address assignment and disconnect/error messages.

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
        +--> Alloy
               |
               v
        Loki on 127.0.0.1:3100
               |
               v
             Grafana
```

The earlier documentation that described Alloy/Loki as future work is superseded.

## Current validated state

The receiver was revalidated live on 16 September 2026 from `admin-01`:

- rsyslog is receiving the ASUS router stream on `monitor-01`;
- `/var/log/homelab/router/rt-ac86u.log` existed and was actively updating;
- recent OpenVPN server messages were present in the dedicated router log;
- a successful external OpenVPN username/password authentication and tunnel establishment were visible in the file;
- the observed VPN session included TLS 1.3 control-channel negotiation and an AES-256-GCM data channel;
- Alloy's live `/etc/alloy/config.alloy` contains the dedicated `loki.source.file "router_syslog"` source;
- the source points at `/var/log/homelab/router/rt-ac86u.log`;
- stable labels include `service="router-syslog"` and `device="rt-ac86u"`;
- the repository already contains the dedicated `monitor_router_alloy` role that manages this pipeline.

This confirms the router-to-rsyslog-to-Alloy path is not configuration drift: it is represented in the current IaC through the dedicated router Alloy role.

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

The implementation is maintained by:

```text
IaC/ansible/playbooks/monitor-router-alloy.yml
IaC/ansible/roles/monitor_router_alloy/
```

These stable service/device labels are preferred over high-cardinality labels derived from arbitrary message content. OpenVPN usernames, public client IP addresses, source ports and process IDs should remain in log content rather than becoming Loki labels.

## Security boundary

The receiver:

- binds to the dedicated router-syslog listener on `192.168.2.52:5514/udp`;
- accepts the expected router source `192.168.2.1`;
- is LAN-only;
- does not provide cryptographic authentication, confidentiality or integrity because the transport is UDP syslog.

Source-IP filtering is useful but is not equivalent to authenticated log transport.

The Loki push path is local to `monitor-01` and does not require exposing a separate external log-ingest endpoint for the router.

Router/OpenVPN logs may contain usernames, public source addresses and other connection metadata. Treat Loki/Grafana access as operationally sensitive and do not copy unnecessary connection metadata into public documentation.

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
- OpenVPN server rebuild or certificate regeneration where logging behaviour changes;
- receiver rebuild;
- rsyslog configuration changes;
- switch/network redesign affecting the path;
- major Alloy/Loki changes.

## Monitoring and alerting

`monitor-01` receives the normal host/platform monitoring coverage and Loki readiness checks are part of the central monitoring validation.

Useful Loki selection starts with the managed labels:

```logql
{job="network-infrastructure", service="router-syslog", device="rt-ac86u"}
```

OpenVPN-focused investigation can then filter message content, for example by `ovpn-server`, authentication result or connection lifecycle message, without creating dynamic labels for usernames or IP addresses.

No content-based router-log alerting is required by default. Add log alerts only after representative messages are classified and the result is actionable; repeated VPN authentication failure may be a future candidate if it can be made low-noise.

## Definition of current done state

The router logging path is operational because:

- rsyslog is IaC-managed on `monitor-01`;
- UDP/5514 is the expected receiver;
- router source filtering exists;
- local rotation is configured;
- the dedicated router log exists as the local source of truth for receipt;
- Alloy router-log shipping is deployed through IaC;
- the dedicated Alloy file source was verified live on 16 September 2026;
- OpenVPN connection/authentication events were observed in the router log during external VPN testing;
- Loki is the central destination for the stream.
