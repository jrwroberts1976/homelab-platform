# Target-State Architecture

This document describes the remaining target direction for the homelab after the 14 September 2026 estate reconciliation, network-observability close-out and implementation of the primary Proxmox guest-backup platform.

Implemented state belongs in `CURRENT-STATE.md`; this document is intentionally limited to work that still needs to be built, hardened or proven.

## Design principles

- Git-managed desired state wherever practical.
- `IaC/` is the home for infrastructure, configuration and deployment automation.
- Existing production resources are reconciled rather than recreated merely to satisfy code.
- Production changes require identity, validation and rollback/recovery gates.
- Stable Ansible reconciliation should be idempotent.
- Secrets, Terraform state and recovery identities remain outside Git.
- Monitoring, backup and recovery are part of service completion, not optional extras.
- Current state, target state and historical evidence must remain clearly separated.

## Implemented platform baseline

The following capabilities are implemented and must not be presented as future greenfield work:

- `admin-01` is the administration / IaC controller.
- `PROXMOX` and `Proxmox-2` are currently standalone Proxmox nodes.
- `dns-01` and `dns-02` provide the resolver pair.
- `monitor-01` provides Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki.
- Grafana Alloy is deployed across the managed estate.
- ASUS router syslog is retained locally on `monitor-01` and shipped to Loki through Alloy.
- `cloud-01` provides production Nextcloud/PostgreSQL/Redis.
- `mail-relay-01` provides the internal SMTP relay.
- `sensor-01` is an operational passive sensor with a dedicated capture interface, Suricata and Zeek.
- the HP ProCurve mirrors ports 1–23 to port 24 for sensor capture.
- `media-01` is the Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target.
- `docker-01` is the Raspberry Pi 4 BirdNET-Go Docker host.
- the Network Host Collector is active on `Proxmox-2` only.
- Network Hosts enrichment, one-time deep profiling, first-seen notification and Grafana dashboards are implemented.
- HP ProCurve SNMP telemetry is collected on `monitor-01` and exposed to Prometheus/Grafana.
- the primary Proxmox guest-backup platform is implemented using isolated NFS namespaces on `media-01`.
- all seven production Proxmox guests have completed successful snapshot backup proof.
- CT103 has completed an isolated LXC restore/boot proof.
- Proxmox notification delivery through `mail-relay-01` is proven.
- the isolated nightly backup jobs are live: `PROXMOX` at 02:15 to `media-backup-proxmox` and `Proxmox-2` at 03:15 to `media-backup-proxmox-2`, both using snapshot mode, zstd, `keep-last=3` and the PVE notification system.
- schedule reconciliation is idempotent and was validated with zero failed systemd units on both PVE nodes.
- legacy `TestServer`, `DietPi`, `ids-01` and `k3s-node-01` identities are retired.

These completed capabilities should be maintained and improved, not re-planned from scratch.

## Priority 1 — recovery depth and second-copy resilience

The initial guest-backup platform is no longer the largest missing platform component. The remaining recovery work is about **depth, independence and proof**.

Current primary backup design:

```text
PROXMOX .70 -> media-backup-proxmox -> media-01:/srv/backup/pve-proxmox
Proxmox-2 .71 -> media-backup-proxmox-2 -> media-01:/srv/backup/pve-proxmox-2
```

The separate namespaces are intentional while the standalone hosts both contain an unrelated VMID `200`.

Remaining target outcomes:

- observe and record the first unattended overnight run;
- review capacity after several retention cycles;
- prove at least one QEMU VM restore;
- prove application-consistent Nextcloud/PostgreSQL recovery for `cloud-01`;
- add an independent second copy for important data;
- protect BirdNET persistent data, user media and controller recovery state;
- protect recovery identities, SSH keys and SOPS/age material outside the running controller;
- add stale/failed-backup monitoring where it produces actionable signal.

There is no requirement to deploy Proxmox Backup Server merely for completeness. PBS remains an optional future enhancement if deduplication, verification, remote sync, retention scale or operational requirements justify it.

See [Backup Strategy](BACKUP-STRATEGY.md).

## Priority 2 — evaluate a properly designed Proxmox cluster

The nodes are currently standalone and production does not depend on Corosync.

A future two-node cluster is worth reconsidering once the additional network hardware is available, but it is not yet approved current state.

Preferred design direction for review:

- retain the normal onboard/LAN interface for management, VM traffic and NFS;
- preserve the existing dedicated network-sensor/capture interface on `PROXMOX`;
- use dedicated StarTech USB Gigabit interfaces for a private Corosync link between the PVE nodes;
- use a QDevice/QNetd third vote on a separate host such as `admin-01`, subject to validation;
- make all guest VMIDs cluster-unique before joining nodes;
- do not reuse the passive scanning interface for Corosync;
- protect and verify all guests before cluster membership changes;
- retain rollback paths during the transition.

Because `cloud-01` and `monitor-01` are both currently VMID `200`, one must be renumbered before a single cluster can own both guests.

Only after cluster membership and guest identity are stable should the backup namespace design be reconsidered. Until then, keep the per-node isolated repositories.

## Priority 3 — controlled patch and lifecycle management

The package-update backlog identified by the 14 September estate audit was cleared through the controlled patch workflow on 14 September 2026.

The closeout evidence is recorded in [`PATCH-CYCLE-CLOSEOUT-2026-09-14.md`](PATCH-CYCLE-CLOSEOUT-2026-09-14.md).

The ongoing target is now routine lifecycle management:

- process future host updates through the existing controlled patch workflow;
- preserve service availability and recovery gates during Proxmox and production-service maintenance;
- deliberately manage PVE patch levels;
- keep application/container version ownership explicit.

### Container operations

Komodo is the preferred direction for routine Docker application/version operations where appropriate.

Before older Docker-management or delivery paths are retired:

- identify their current responsibilities;
- demonstrate equivalent Komodo control;
- protect secrets and persistent configuration;
- keep rollback possible;
- document applications intentionally outside Komodo.

`docker-01` remains intentionally single-purpose for BirdNET-Go unless a later reviewed design changes that role.

## Priority 4 — network hardening and physical truth

### HP ProCurve

The HP ProCurve 2510G-24 is operational as both LAN switch and passive-sensor SPAN source.

Implemented state includes:

- port 24 as the mirror destination;
- ports 1–23 as mirror sources;
- SNMP telemetry into the monitoring platform.

Remaining work:

- capture a new physical port map after the SPAN repatch;
- replace or restrict the unrestricted `public` SNMP community through a controlled change;
- assess practical mitigations for the legacy Telnet-only management path;
- preserve sensor capture while making management/security changes;
- validate forwarding after physical/configuration changes.

A switch reset/rebuild is optional and should occur only after current forwarding, VLAN, monitoring and rollback requirements are captured.

### ASUS router

The ASUS RT-AC86U remains DHCP authority and AiMesh controller.

A clean firmware/factory-reset rebuild remains optional. Before any such change, protect WAN configuration, DHCP reservations, DNS advertisement, Wi-Fi/AiMesh state, port forwards/VPN/routing policy, syslog configuration and rollback access.

Approved resolver pair:

```text
192.168.2.51
192.168.2.50
```

`192.168.2.48` must not return as a resolver address.

## Priority 5 — observability and analytics expansion

The core metrics/logging/network-observability platform is live. Future work should add useful operational context rather than duplicate host-up telemetry.

Remaining direction:

- continue service-specific telemetry where actionable;
- correlate Network Hosts inventory, enrichment, deep profiles and switch topology;
- build the planned Web Platform / Analytics dashboard combining Cloudflare edge/security information, Umami visitor analytics and origin/application health from Grafana/Loki;
- add backup freshness/storage-capacity visibility after unattended execution history is available;
- keep alerts actionable and low-noise.

## Security platform

### Passive detection

The passive sensor platform is implemented. Future work is incremental tuning and hardening:

- tune Suricata/Zeek outputs for useful signal;
- retain capture-interface isolation;
- monitor sensor/log-pipeline health;
- manage storage/retention deliberately;
- add detection runbooks only when there is an operational response.

### Vulnerability management

A future dedicated vulnerability-management service remains optional.

If Greenbone/OpenVAS is reintroduced, use a dedicated `security-01` workload on suitable x86 capacity, subject to resource review, persistent-storage design, backup/restore coverage, IaC deployment, monitoring integration and a clear remediation workflow.

It must not run directly on a Proxmox hypervisor.

## Edge / Cloudflare Tunnel

`edge-01` exists as CT103 on `Proxmox-2`, but the connector workload is intentionally not deployed.

Deploy Cloudflare Tunnel only when a real service requirement exists. Keep connector credentials outside Git, deploy through reviewed IaC, validate outbound connectivity/origin policy, document credential rotation/recovery and add useful monitoring.

Do not describe `edge-01` as an operational tunnel endpoint until validated.

## Public services

Public/static workloads should continue to use external hosting where that reduces homelab dependency. The personal portfolio site is an example of a workload that does not need home infrastructure for normal public availability.

## Password manager

A self-hosted password manager remains optional future work.

Before deployment, choose the product/host intentionally, deploy through Git-managed IaC, keep recovery material outside Git, provide HTTPS, back up and restore-test persistent data, monitor availability and document emergency recovery independent of the running homelab.

## Completion criteria

The platform can be considered operationally mature when:

- the isolated scheduled Proxmox backup path has an observed unattended success record;
- representative LXC, QEMU VM and application restores are proven;
- important data has an independent secondary copy;
- controller recovery state is protected off-host;
- controlled patch/lifecycle management is routine;
- physical network mapping reflects current SPAN/cabling reality;
- remaining switch/router hardening decisions are completed or explicitly accepted;
- observability remains useful and low-noise;
- service ownership and IaC authority remain unambiguous;
- any future PVE cluster is introduced only with dedicated Corosync networking, quorum design and cluster-unique guest IDs;
- optional new services are introduced only when their operational value justifies their recovery and maintenance burden.
