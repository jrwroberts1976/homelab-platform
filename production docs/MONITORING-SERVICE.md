# Homelab Monitoring Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Primary host:** `monitor-01.jameshouse` / `192.168.2.52`  
**Placement:** VM200 on `Proxmox-2` / `192.168.2.71`  
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`  
**Status:** core metrics/alerting operational; central logging implementation pending

## Purpose

`monitor-01` is the authoritative monitoring platform for the rebuilt homelab.

Current core stack:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter

The old TestServer monitoring/logging stack is no longer the desired-state authority.

## VM baseline

```text
monitor-01.jameshouse
192.168.2.52
VM ID 200
Proxmox-2
4 vCPU
6144 MiB RAM
80 GiB local-lvm disk
Debian 13
```

DNS:

```text
192.168.2.51  dns-01
192.168.2.50  dns-02
```

`192.168.2.48` is `admin-01`; it must not be used as a legacy resolver.

## Failure-domain placement

Monitoring runs on `Proxmox-2` so failure of primary `PROXMOX` does not also remove monitoring for workloads hosted there.

The two hypervisors remain standalone; monitoring must not assume cluster/HA behaviour.

## Current monitored estate

Core/approved targets include:

| Target | IPv4 | Placement / purpose |
|---|---:|---|
| ASUS RT-AC86U | `192.168.2.1` | Router/gateway |
| `dns-02` | `192.168.2.50` | CT100 on PROXMOX |
| `dns-01` | `192.168.2.51` | CT101 on Proxmox-2 |
| `monitor-01` | `192.168.2.52` | Local monitoring VM |
| `cloud-01` | `192.168.2.53` | VM200 on PROXMOX |
| `mail-relay-01` | `192.168.2.54` | CT102 on PROXMOX |
| `sensor-01` | `192.168.2.55` | VM201 on PROXMOX |
| `edge-01` | `192.168.2.56` | CT103 on Proxmox-2; monitoring to be added with cloudflared deployment |
| `PROXMOX` | `192.168.2.70` | Primary PVE host |
| `Proxmox-2` | `192.168.2.71` | Secondary PVE host |
| `media-01` | `192.168.2.195` | Physical Raspberry Pi 5 |
| `TestServer` | `192.168.2.220` | Legacy retirement target; monitoring should be removed when no longer needed |

`ids-01` is decommissioned and must not be an active monitoring target.

## Current validation state

The monitoring application layer has been deployed and validated on `monitor-01`. Previous validation established:

- Prometheus healthy;
- Grafana healthy;
- Alertmanager healthy;
- Blackbox Exporter healthy;
- configured Prometheus targets reporting healthy at the time of validation;
- Blackbox DNS/ICMP/HTTPS probes succeeding for the then-approved core targets;
- Grafana Prometheus datasource provisioned and pointing at Prometheus;
- local DNS `monitor-01.jameshouse -> 192.168.2.52` published on both resolvers.

Changes to the estate, such as `edge-01`, must be added through Git-managed monitoring configuration rather than assumed covered by the earlier target count.

## Router syslog receiver

`monitor-01` already receives ASUS router syslog over UDP/5514 and writes:

```text
/var/log/homelab/router/rt-ac86u.log
```

This local collection path is operational and is the first approved source for the central logging rollout.

See `ROUTER-SYSLOG-SERVICE.md`.

## Central logging — next phase

The approved target is a **fresh** Loki/Alloy implementation associated with `monitor-01`:

```text
approved log sources
      |
      v
     Alloy
      |
      v
     Loki
      |
      v
    Grafana
```

Do not migrate the old TestServer Alloy/Loki configuration wholesale.

Initial logging sequence:

1. define Loki storage/retention/resource limits;
2. deploy Loki through Git/IaC;
3. configure Alloy for the dedicated router syslog file;
4. prove a new router event arrives in Loki and is queryable in Grafana;
5. add Loki/Alloy health monitoring;
6. add `edge-01` / cloudflared logs after the edge service is live;
7. add other sources only through explicit collection policy.

See `CENTRAL-LOGGING-SERVICE.md`.

## IaC ownership

- Terraform/OpenTofu: VM infrastructure where defined;
- Ansible: operating-system/application configuration;
- Prometheus configuration: Git-managed targets;
- Grafana provisioning: Git-managed datasources/dashboards where practical;
- Alertmanager: Git-managed routing with secrets outside Git;
- Loki/Alloy: must be added to the same Git/IaC authority rather than built as unmanaged local state.

Manual GUI edits are not authoritative unless reconciled back into Git.

## Network ports

LAN-only management/service ports currently include:

- Grafana TCP/3000
- Prometheus TCP/9090
- Alertmanager TCP/9093
- Blackbox Exporter TCP/9115
- router syslog UDP/5514

No monitoring management port should be directly exposed to the Internet.

If remote Grafana access is approved, publish it through `edge-01` + Cloudflare Tunnel + Cloudflare Access rather than a router port-forward.

## Alerting policy

Alerts should be actionable and tied to service/host outcomes. Avoid high-cardinality labels and noisy log-content alerting.

Normal priorities include:

- target/service unavailable;
- CPU/memory/filesystem pressure where thresholds are meaningful;
- DNS failure;
- Proxmox host/service failure;
- future Loki/Alloy ingestion/storage failure;
- future cloudflared/tunnel failure.

## Recovery

If the monitoring platform fails:

1. administer from `admin-01`;
2. verify `Proxmox-2` and VM200 status;
3. verify `monitor-01` DNS, network and systemd state;
4. validate application services independently;
5. restore/redeploy from Git/IaC before introducing manual drift;
6. preserve or restore persistent Grafana/Prometheus/Loki data only according to the documented backup policy.

## Definition of done for the current programme

The monitoring programme is complete when:

- core metrics/alerting remains reproducible and healthy;
- `edge-01` and other newly approved targets are represented;
- fresh Loki/Alloy central logging is operational;
- router logs are queryable end-to-end in Grafana;
- logging health/retention/recovery are documented;
- TestServer monitoring/logging dependencies are removed before its reimage.
