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


## Proxmox-2 storage import prerequisite evidence — 9 September 2026

The `local` datastore on `Proxmox-2` was reconciled through the Git-managed `proxmox_vm_import_storage` Ansible role so Terraform can import the pinned Debian cloud image.

First apply:

```text
Proxmox-2 : ok=9 changed=1 unreachable=0 failed=0 skipped=0
```

Second apply proved idempotence:

```text
Proxmox-2 : ok=8 changed=0 unreachable=0 failed=0 skipped=1
```

The role preserved the existing datastore definition and added only the required VM image `import` content capability. Final storage-stanza verification and a regenerated Terraform plan remain the next gates before VM creation.


## monitor-01 VM provisioning evidence — 9 September 2026

The first infrastructure phase is live and validated:

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

Terraform completed the VM creation with one approved resource added and no changes or destroys. Cloud-init validation confirmed the expected short hostname and FQDN, static `.52/24` address, gateway `.1`, active QEMU guest agent, and zero failed systemd units. A post-create Terraform plan reported no drift.

Durable Terraform state is held at:

```text
~/.local/state/homelab-iac/monitor-01/terraform
```

The application layer is defined separately through the `monitoring_stack` Ansible role. Initial pinned application versions are Prometheus v3.14.0, Grafana v13.2.1, Alertmanager v0.34.0, and Blackbox Exporter v0.28.0. Loki and Alloy remain deferred until the metrics platform is stable.


## Core monitoring application deployment evidence — 9 September 2026

The core monitoring application layer deployed successfully on `monitor-01`.

Controller-side health checks passed for all four initial services:

```text
prometheus=PASS
grafana=PASS
alertmanager=PASS
blackbox=PASS
```

The protected Grafana admin credential is stored outside Git at:

```text
~/.config/homelab-iac/monitoring.env
```

The deployment wrapper completed both the first Ansible apply and the idempotence run before performing the controller health checks. Loki and Alloy remain intentionally deferred until metrics/probe validation is complete.
