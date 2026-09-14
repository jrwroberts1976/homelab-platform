# Estate Audit — 14 September 2026

## Purpose

This document records the live-state reconciliation performed on 14 September 2026 after the outstanding repository branches were merged and local/remote branch cleanup was completed.

The audit compared the active Linux estate with `docs/architecture/CURRENT-STATE.md`, production service documents and the current Ansible desired state. Live evidence wins where the 12 September documentation is stale.

## Repository baseline

The repository was reconciled to `main` at the merged HP switch collector fix and all stale local/remote feature branches were removed. The abandoned `docker-01` to `birdnet-01` rename experiment was preserved as a local patch before its worktree was removed; the live identity remains `docker-01`.

## Active Linux estate audited

The compact audit covered:

- `admin-01`
- `dns-01`
- `dns-02`
- `monitor-01`
- `cloud-01`
- `mail-relay-01`
- `sensor-01`
- `edge-01`
- `PROXMOX`
- `Proxmox-2`
- `media-01`
- `docker-01`

## Live-state summary

| Host | Key validated state | Result |
|---|---|---|
| `admin-01` | Debian 13/aarch64, Node Exporter, Alloy 1.19.2 active after reconciliation, zero failed units | reconciled |
| `dns-01` | Pi-hole Core 6.4.3 / Web 6.6 / FTL 6.7, Unbound 1.22.0, Alloy 1.19.2, zero failed units | healthy |
| `dns-02` | Pi-hole Core 6.4.3 / Web 6.6 / FTL 6.7, Unbound 1.22.0, Alloy 1.19.2, zero failed units | healthy |
| `monitor-01` | Prometheus 3.14.0, Grafana 13.2.1, Alertmanager 0.34.0, Blackbox 0.28.0, Loki 3.7.7, Alloy 1.19.2, all checked health endpoints HTTP 200 | healthy |
| `cloud-01` | Nextcloud 34.0.3, PostgreSQL 18.6-alpine, Redis 8.2.9-alpine, cron, Alloy 1.19.2 | healthy |
| `mail-relay-01` | Postfix active, Node Exporter active, Alloy 1.19.2 | healthy |
| `sensor-01` | dedicated capture NIC present/up/promiscuous, Suricata 8.0.6 active/enabled, Zeek 8.0.10 active/enabled/running, Alloy 1.19.2 | capture phase operational |
| `edge-01` | reserved edge LXC, no `cloudflared`, Alloy 1.19.2 | healthy/reserved |
| `PROXMOX` | PVE 9.2.11, kernel 7.0.14-15-pve, Alloy 1.19.2, legacy network-host collector removed | healthy |
| `Proxmox-2` | PVE 9.2.2, kernel 7.0.2-6-pve, Alloy 1.19.2, active network-host collector | healthy |
| `media-01` | Kodi 21.3, Samba, Chrony, Node Exporter, Alloy 1.19.2 | healthy |
| `docker-01` | one healthy BirdNET-Go container using `ghcr.io/tphakala/birdnet-go:20260823`, Alloy 1.19.2 | healthy |

## Monitoring and logging reconciliation

The 12 September documents stated that Loki and Alloy were not deployed on `monitor-01`. That is now false.

Direct validation on 14 September proved these containers running on `monitor-01`:

```text
monitoring-loki-1         grafana/loki:3.7.7
monitoring-grafana-1      grafana/grafana:13.2.1
monitoring-prometheus-1   prom/prometheus:v3.14.0
monitoring-alertmanager-1 prom/alertmanager:v0.34.0
monitoring-blackbox-1     prom/blackbox-exporter:v0.28.0
```

Listeners were present on TCP/3000, 3100, 9090, 9093 and 9115. Native Alloy was listening locally on TCP/12345. Prometheus, Grafana, Alertmanager and Loki health checks all returned HTTP 200.

Alloy 1.19.2 is also deployed across the current baseline host population, including both Proxmox nodes, DNS, cloud, mail, media, BirdNET and edge hosts. `admin-01` was the one identified drift item and was reconciled successfully through the existing `alloy.yml` playbook using interactive become authentication.

## Router syslog reconciliation

The old documentation described Alloy/Loki ingestion as future work. Current IaC and live state now support the active path:

```text
ASUS RT-AC86U
  -> UDP/5514
  -> monitor-01 rsyslog
  -> /var/log/homelab/router/rt-ac86u.log
  -> Alloy
  -> local Loki on monitor-01
  -> Grafana
```

The existing rsyslog local file/rotation remains part of the design rather than being replaced by Loki.

## Network sensor reconciliation

The old Phase 1-only description is superseded.

Live validation on 14 September showed:

```text
management NIC: eth0
capture NIC:    enx00249b63b38a
capture flags:  UP, PROMISC, LOWER_UP
```

Suricata is active and enabled. `homelab-zeek.service` is active and enabled. `zeekctl status` reported the standalone Zeek process running. The capture enable gate exists at:

```text
/etc/homelab-network-sensor/capture-enabled
```

The HP switch is also now configured with mirror port 24 and monitoring sources 1 through 23. The older documentation that described port mirroring as disabled is no longer current.

## Network host collector placement

Current IaC targets `Proxmox-2` only. Live validation confirmed:

- `Proxmox-2`: collector timer enabled and active, five-minute cadence, current inventory present under `/var/lib/homelab-network-hosts/inventory.json`;
- `PROXMOX`: an obsolete earlier one-minute collector unit remained installed but inactive, with no inventory file.

The obsolete `PROXMOX` implementation was backed up under `/root/legacy-network-host-collector-20260914-060957` and removed. The active `Proxmox-2` collector remained enabled/active and continued updating its inventory.

## admin-01 remediation

The compact audit initially found one failed unit on `admin-01`:

```text
smartmontools.service
```

The cause was not disk failure. `admin-01` boots from an SD card (`mmcblk0`) and `smartd` exited because no SMART-capable device was available to monitor. The daemon was disabled/stopped and the failed state cleared. `smartmontools` remains installed for future use if a SMART-capable device is attached.

The audit also found that Alloy was absent even though `admin-01` belongs to the Ansible Alloy baseline. After clearing the failed unit, the existing Alloy playbook completed successfully:

```text
ok=47 changed=17 unreachable=0 failed=0
```

Post-deployment validation confirmed Alloy 1.19.2 installed, enabled and active, with zero failed systemd units.

## Package update snapshot

The compact audit reported the following available-package counts from the hosts' then-current APT metadata:

| Host | Reported updates |
|---|---:|
| `PROXMOX` | 61 |
| `Proxmox-2` | 152 |
| `admin-01` | 86 |
| `dns-01` | 43 |
| `dns-02` | 43 |
| `docker-01` | 74 |
| `edge-01` | 39 |
| `mail-relay-01` | 36 |
| `media-01` | 259 |
| `cloud-01` | 0 |
| `monitor-01` | 0 |
| `sensor-01` | 0 |

These counts are an audit snapshot, not proof that `apt update` was run immediately beforehand. They should feed the normal patch-management workflow rather than being treated as architectural drift.

## Documentation drift identified

The principal stale statements found were:

1. `CURRENT-STATE.md` and `MONITORING-SERVICE.md` said Loki/Alloy were not deployed on `monitor-01`.
2. `NETWORK-SENSOR-SERVICE.md` said the capture NIC was absent and Suricata/Zeek were inactive.
3. The network/sensor documents said HP switch port mirroring was disabled.
4. `ROUTER-SYSLOG-SERVICE.md` described Alloy/Loki ingestion as future work.
5. `MEDIA-SERVICE.md` described central Alloy/Loki logging as future-only even though Alloy is now deployed as part of the host baseline.
6. `CURRENT-STATE.md` said Alloy was inactive on `Proxmox-2`.

These are documentation defects, not reasons to roll the live estate backwards.

## Remaining follow-up

- reconcile the stale architecture and production-service documents to the live state recorded here;
- retain `edge-01` as reserved until Cloudflare Tunnel deployment is explicitly approved;
- continue backup/restore implementation and proof;
- process the package-update backlog through the normal patch-management workflow;
- continue network-host enrichment/dashboard work on `Proxmox-2`;
- keep the switch/router physical port map under review because the earlier 12 September map was superseded by activation of the SPAN configuration.
