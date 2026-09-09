# Homelab Monitoring Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Status:** approved target design; IaC implementation starting  
**Primary host:** `monitor-01.jameshouse`  
**IPv4:** `192.168.2.52`  
**Placement:** VM on `Proxmox-2` / `192.168.2.71`

## Purpose

`monitor-01` becomes the authoritative monitoring platform for the rebuilt homelab.

The design replaces Zabbix as the target monitoring authority and standardizes on:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter

Loki/Alloy logging is deliberately deferred until the metrics platform is stable and real storage requirements are known.

## Initial VM target

- Debian 13
- 4 vCPU
- 6 GiB RAM
- 80 GiB system/data disk
- static IPv4 `192.168.2.52/24`
- gateway `192.168.2.1`
- DNS `192.168.2.51`, `192.168.2.50` (legacy `192.168.2.48` is forbidden)
- search domain `jameshouse`
- starts automatically with `Proxmox-2`

The VM is reproducible infrastructure. Persistent Prometheus/Grafana state is useful but is not treated as irreplaceable; configuration and dashboards should be provisioned from Git wherever practical.

## Failure-domain placement

Monitoring runs on `Proxmox-2` so loss of the primary `PROXMOX` host does not also remove the monitoring system.

This allows `monitor-01` to detect loss of:

- `PROXMOX`
- `dns-02`
- future `cloud-01`
- other workloads hosted on `PROXMOX`

The current USB management NIC on `Proxmox-2` remains a known hardware concern. Replacement adapters will be tested separately; monitoring deployment does not change the host bridge/NIC design.

## Initial monitored estate

| Target | IPv4 | Initial probe |
|---|---:|---|
| ASUS router | `192.168.2.1` | ICMP |
| `dns-02` | `192.168.2.50` | ICMP, DNS |
| `dns-01` | `192.168.2.51` | ICMP, DNS |
| `monitor-01` | `192.168.2.52` | local metrics |
| `PROXMOX` | `192.168.2.70` | ICMP, HTTPS, node metrics later |
| `Proxmox-2` | `192.168.2.71` | ICMP, HTTPS, node metrics later |
| `media-01` | `192.168.2.195` | ICMP |
| TestServer | `192.168.2.220` | ICMP, node/container metrics later |

Future `cloud-01` is reserved for `192.168.2.53`.

## IaC ownership

- Terraform/OpenTofu: VM definition, compute, storage, network and cloud-init
- Ansible: Debian baseline, Docker/Compose, service files, persistent directories and health checks
- Compose: Prometheus, Grafana, Alertmanager and Blackbox Exporter
- Prometheus configuration: Git-managed scrape/probe targets
- Grafana provisioning: Git-managed data source and dashboards where practical
- Alertmanager configuration: Git-managed routing with secrets supplied outside Git
- managed DNS: `monitor-01.jameshouse -> 192.168.2.52`

Manual GUI edits are not authoritative unless reconciled back into Git.

## Deployment stages

1. validate `192.168.2.52` is unused;
2. validate a free VM ID on `Proxmox-2`;
3. validate VM storage and Debian cloud-image/bootstrap path;
4. Terraform plan must contain only the expected monitoring VM/image changes;
5. create `monitor-01`;
6. wait for SSH;
7. apply Ansible monitoring role;
8. validate Prometheus, Grafana, Alertmanager and Blackbox health;
9. add managed local DNS;
10. prove ICMP/HTTPS/DNS probes against the current critical estate;
11. run the configuration a second time and require idempotence;
12. add node exporters and alert routing in later controlled changes.

## Initial ports

LAN-only management:

- Grafana: TCP/3000
- Prometheus: TCP/9090
- Alertmanager: TCP/9093
- Blackbox Exporter: TCP/9115

No monitoring management port is exposed directly to the Internet.

## Definition of done

The first monitoring phase is complete when:

- `monitor-01` is reproducibly provisioned through IaC;
- all four monitoring services are healthy;
- Grafana is reachable from the LAN;
- Prometheus successfully evaluates configured targets;
- both DNS resolvers are probed;
- both Proxmox hosts are probed;
- router reachability is probed;
- service configuration survives a redeploy without manual GUI repair;
- a second Ansible run reports no unintended changes.


## Proxmox DNS prerequisite evidence — 9 September 2026

Before deploying `monitor-01`, the system resolver configuration on both standalone Proxmox hosts is being reconciled through the Git-managed `proxmox_resolver` Ansible role.

Approved resolver state:

```text
search jameshouse
nameserver 192.168.2.51
nameserver 192.168.2.50
```

Live evidence now confirms `PROXMOX` (`192.168.2.70`) applied successfully with `ok=12 changed=1 unreachable=0 failed=0`. Post-apply validation resolved public DNS and `dns-01.jameshouse -> 192.168.2.51`. `Proxmox-2` had already been validated with the same managed resolver pair.

A second Ansible run across both hosts is still required to prove idempotence before the monitoring VM is provisioned.
