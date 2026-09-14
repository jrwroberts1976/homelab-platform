# Target-State Architecture

This document describes the remaining target direction for the homelab after the 14 September 2026 estate reconciliation and the completion of the current Network Hosts / switch telemetry work.

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

The following work is implemented and must not be presented as future development:

- `admin-01` is the administration / IaC controller.
- `PROXMOX` and `Proxmox-2` are intentionally standalone Proxmox nodes.
- `dns-01` and `dns-02` provide the resolver pair.
- `monitor-01` provides Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki.
- Grafana Alloy is deployed across the managed estate, including the reconciled `admin-01` baseline.
- ASUS router syslog is retained locally on `monitor-01` and shipped into Loki through Alloy.
- `cloud-01` provides production Nextcloud/PostgreSQL/Redis.
- `mail-relay-01` provides the internal SMTP relay.
- `sensor-01` is an operational passive sensor with a dedicated capture interface, Suricata and Zeek.
- the HP ProCurve mirrors ports 1-23 to port 24 for the sensor capture path.
- `media-01` is the Raspberry Pi 5 Kodi endpoint.
- `docker-01` is the Raspberry Pi 4 BirdNET-Go Docker host.
- the Network Host Collector is active on `Proxmox-2` only.
- Network Hosts enrichment is active on its periodic production timer.
- the one-time deep profiler worker is active for newly discovered hosts.
- first-seen device email notification and Network Hosts Grafana dashboards are implemented.
- HP ProCurve SNMP telemetry is collected on `monitor-01`, exported through Node Exporter and available to Prometheus/Grafana.
- legacy `TestServer`, `DietPi`, `ids-01` and `k3s-node-01` identities are retired.

These completed capabilities should be maintained and improved, not re-planned as greenfield work.

## Priority 1 — backup and recovery

Backup and restore coverage is now the largest remaining platform gap.

Current evidence remains explicit:

- there is no active production Proxmox Backup Server;
- there is no proven estate-wide Restic/Backrest platform;
- representative VM/LXC and application restores are not yet proven;
- the 4 TB WD disk on `PROXMOX` must not be treated as the sole copy of important data.

Target outcome:

- choose and deploy an appropriate guest-backup platform, with PBS preferred when placement and storage are suitable;
- protect important application data independently where guest-level backup alone is insufficient;
- cover Nextcloud data and database state, BirdNET persistent data, relevant media data, controller state and recovery material;
- keep important secrets and recovery identities independently recoverable;
- define retention, verification and pruning;
- perform and document representative restores rather than treating successful backup jobs as proof of recovery.

See [Backup Strategy](BACKUP-STRATEGY.md).

## Priority 2 — controlled patch and lifecycle management

The 14 September estate audit identified a significant package-update backlog on several hosts.

Target outcome:

- process host updates through the existing controlled patch workflow;
- preserve service availability and recovery gates during Proxmox and production-service maintenance;
- keep Proxmox node versions deliberately managed rather than assuming both nodes must always be identical;
- keep application/container version ownership explicit.

### Container operations

Komodo is the preferred direction for routine Docker application/version operations where appropriate.

Before older Docker-management or delivery paths are retired:

- identify their current responsibilities;
- demonstrate equivalent Komodo control;
- protect secrets and persistent configuration;
- keep rollback possible;
- document which applications remain intentionally outside Komodo.

`docker-01` remains intentionally single-purpose for BirdNET-Go unless a later reviewed design changes that role.

## Priority 3 — network hardening and physical truth

### HP ProCurve

The current HP ProCurve 2510G-24 is operational as both the LAN switch and passive-sensor SPAN source.

Implemented state includes:

- port 24 as the mirror destination;
- ports 1-23 as mirror sources;
- SNMP telemetry into the monitoring platform.

Remaining network work:

- capture a new physical port map after the SPAN repatch rather than relying on the older 12 September map;
- replace or restrict the current unrestricted `public` SNMP community as part of a controlled hardening change;
- assess the legacy Telnet-only management path and available practical mitigations;
- preserve sensor capture while making management/security changes;
- validate normal forwarding after any physical or configuration change.

A switch reset/rebuild is optional and should happen only when current forwarding, VLAN, management, monitoring and patching requirements are captured and rollback is available.

### ASUS router

The ASUS RT-AC86U remains DHCP authority and AiMesh controller.

A future clean firmware/factory-reset rebuild remains optional. Before any such change, capture and protect:

- WAN configuration;
- DHCP reservations;
- DNS advertisement;
- Wi-Fi/AiMesh state;
- port forwards, VPN and routing policy;
- router syslog configuration;
- rollback access.

Approved resolver pair:

```text
192.168.2.51
192.168.2.50
```

`192.168.2.48` must not return as a resolver address.

## Priority 4 — observability and analytics expansion

The core metrics and logging platform is already live. Future observability work should add useful operational context rather than duplicate existing host-up telemetry.

Remaining direction:

- continue service-specific telemetry where it produces actionable information;
- use the Network Hosts inventory, enrichment, deep profiles and switch topology together for better device context;
- improve network dashboards where the live data demonstrates a useful operational need;
- build the planned Web Platform / Analytics dashboard combining Cloudflare edge/security information, Umami visitor analytics and origin/application health from Grafana/Loki;
- keep alerts actionable and avoid noisy policy-only rules.

## Security platform

### Passive detection

The passive sensor platform is implemented. Future work here is incremental hardening and tuning:

- tune Suricata and Zeek outputs based on useful signal rather than maximum volume;
- retain capture-interface isolation from management traffic;
- monitor sensor/log pipeline health;
- manage storage and retention deliberately;
- expand detection/runbooks only when they have an operational response.

### Vulnerability management

A future dedicated vulnerability-management service remains optional.

If Greenbone/OpenVAS is reintroduced, the preferred direction is a dedicated `security-01` workload on suitable x86 capacity, subject to:

- resource review;
- persistent-storage design;
- backup/restore coverage;
- IaC deployment;
- monitoring integration;
- a clear patch/remediation workflow.

It must not run directly on a Proxmox hypervisor.

## Edge / Cloudflare Tunnel

`edge-01` exists as CT 103 on `Proxmox-2`, but the connector workload is intentionally not deployed.

Deploy Cloudflare Tunnel only when there is a real service requirement. Before activation:

- define exactly which public services require the tunnel;
- keep connector credentials outside Git;
- deploy `cloudflared` through reviewed IaC;
- validate outbound tunnel connectivity and origin policy;
- document credential rotation and recovery;
- add useful monitoring without exposing sensitive connector detail.

Do not describe `edge-01` as an operational tunnel endpoint until that deployment is validated.

## Public services

Public/static workloads should continue to use external hosting where that reduces homelab dependency.

The personal portfolio site is an example of a workload that does not need to depend on home infrastructure for normal public availability.

## Password manager

A self-hosted password manager remains an optional future project.

Before deployment:

- choose the product and host intentionally;
- deploy through Git-managed IaC;
- keep recovery material outside Git;
- provide HTTPS;
- back up and restore-test persistent data;
- monitor availability;
- document an emergency recovery path independent of the running homelab.

## Completion criteria

The platform can be considered operationally mature when:

- backup coverage exists and representative restores are proven;
- controlled patch/lifecycle management is routine and documented;
- physical network mapping reflects the post-SPAN reality;
- remaining switch/router hardening decisions are completed or explicitly accepted;
- important application and infrastructure recovery paths are tested;
- observability remains useful and low-noise;
- service ownership and IaC authority remain unambiguous;
- optional new services are introduced only when their operational value justifies their recovery and maintenance burden.
