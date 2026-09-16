<!-- estate-authority: IaC/inventory/estate.json -->
# Target-State Architecture

This document describes the remaining target direction for the homelab after the September 2026 estate reconciliation, production `jameshouse-pve` cluster formation, primary Proxmox guest-backup implementation, Greenbone commissioning and selection of the router-hosted OpenVPN remote-access path.

Implemented state belongs in `CURRENT-STATE.md`; this document is intentionally limited to work that still needs to be built, hardened or proven.

## Design principles

- Git-managed desired state wherever practical.
- `IaC/inventory/estate.json` is the machine-readable authority for asset identity and addressing.
- `IaC/` is the home for infrastructure, configuration and deployment automation.
- Existing production resources are reconciled rather than recreated merely to satisfy code.
- Production changes require identity, validation and rollback/recovery gates.
- Stable Ansible reconciliation should be idempotent.
- Secrets, Terraform state and recovery identities remain outside Git.
- Monitoring, backup and recovery are part of service completion, not optional extras.
- Current state, target state and historical evidence must remain clearly separated.
- New addresses and VMIDs are allocated only after live/canonical collision checks; do not invent replacements for occupied identities.

## Implemented platform baseline

The following capabilities are implemented and must not be presented as future greenfield work:

- `admin-01` is the administration / IaC controller and external Corosync QNetd host.
- `PROXMOX` and `Proxmox-2` are members of the two-node `jameshouse-pve` Proxmox cluster.
- the cluster uses dedicated Corosync link0 (`10.255.255.1/30` ↔ `10.255.255.2/30`) with management-LAN link1 fallback.
- `admin-01` supplies the QDevice third vote through `corosync-qnetd`.
- all production guest IDs are cluster-unique; `monitor-01` is VM202 and `greenbone-01` is VM203.
- current guest placement is CT100/CT102/VM200/VM201 on `PROXMOX` and CT101/CT103/VM202/VM203 on `Proxmox-2`.
- `dns-01` and `dns-02` provide the resolver pair.
- `monitor-01` provides Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki.
- Grafana Alloy is deployed across the managed estate.
- ASUS router syslog is received on `monitor-01` and shipped to Loki through the dedicated Alloy router-log pipeline.
- the ASUS RT-AC86U runs the selected OpenVPN remote-access endpoint; external authentication and tunnel establishment have been observed.
- `cloud-01` provides production Nextcloud/PostgreSQL/Redis.
- `mail-relay-01` provides the internal SMTP relay.
- `sensor-01` is an operational passive sensor with Suricata and Zeek.
- the HP ProCurve mirrors ports 1–23 to port 24 for sensor capture.
- `greenbone-01` is an operational LAN-only Greenbone Community vulnerability scanner with feeds ready, commissioning scan complete, VM backup integrity proven and Proxmox protection enabled.
- `media-01` is the Raspberry Pi 5 Kodi endpoint and primary Proxmox NFS backup target.
- `docker-01` is the Raspberry Pi 4 BirdNET-Go Docker host.
- the Network Host Collector is active on `Proxmox-2` only.
- Network Hosts enrichment, deep profiling, first-seen notification and Grafana dashboards are implemented.
- HP ProCurve SNMP telemetry is collected on `monitor-01`.
- the primary Proxmox guest-backup platform uses node-scoped NFS namespaces on `media-01`.
- the `Proxmox-2` backup job is IaC-reconciled to `101,103,202,203`.
- CT103 has completed an isolated LXC restore/boot proof.
- Proxmox notification delivery through `mail-relay-01` is proven.
- legacy `TestServer`, `DietPi`, `ids-01` and `k3s-node-01` identities are retired.

These completed capabilities should be maintained and improved, not re-planned from scratch.

## Priority 1 — complete backup and recovery proof

Current storage design remains:

```text
PROXMOX .70 -> media-backup-proxmox -> media-01:/srv/backup/pve-proxmox
Proxmox-2 .71 -> media-backup-proxmox-2 -> media-01:/srv/backup/pve-proxmox-2
```

Current scheduled guest sets are:

```text
PROXMOX
  100,102,200,201

Proxmox-2
  101,103,202,203
```

The schedule is reconciled through IaC. The unattended 16 September cycle succeeded for `101,103,202`; VM203 has separate manual snapshot and Zstandard-integrity proof and is now included in the job.

Remaining outcomes:

- observe and record the first unattended 03:15 cycle that includes VM203;
- review capacity after several retention cycles;
- prove at least one representative QEMU VM restore;
- prove application-consistent Nextcloud/PostgreSQL recovery for `cloud-01`;
- add an independent second copy for important data;
- protect BirdNET persistent data, user media and controller recovery state;
- protect recovery identities, SSH keys and SOPS/age material outside the running controller;
- add stale/failed-backup monitoring where it produces actionable signal.

There is no requirement to collapse the two proven NFS namespaces merely because the hosts share a cluster, and no requirement to deploy Proxmox Backup Server merely for completeness.

See [Backup Strategy](BACKUP-STRATEGY.md).

## Priority 2 — cluster resilience proof and HA decision

Cluster creation is complete. Remaining resilience work:

- deliberately test loss of Corosync link0 and prove traffic moves to link1 without loss of membership;
- perform a controlled single-node outage/quorum exercise while QDevice is available;
- monitor QDevice reachability and Corosync link health;
- document planned maintenance behaviour for one-node shutdowns;
- decide whether node-local storage plus backup/manual recovery is sufficient;
- if automatic guest failover is required, design storage replication or shared storage before enabling HA;
- do not describe the cluster as guest-HA capable while production disks remain only on node-local `local-lvm`.

The cluster itself is not a substitute for guest-data availability.

## Priority 3 — retire migration rollback state after fresh proof

The cluster migration deliberately retained pre-cluster local LVs on `Proxmox-2`:

```text
precluster-20260914-vm-101-disk-0
precluster-20260914-vm-103-disk-0
precluster-20260914-vm-200-cloudinit
precluster-20260914-vm-200-disk-0
```

These are rollback evidence, not active guest disks.

Target outcome:

- confirm the renamed LVs are not referenced by any live guest;
- preserve required off-node backup/configuration evidence;
- remove the retained LVs deliberately once their rollback value has expired;
- record the cleanup so they are never mistaken for active storage.

## Priority 4 — controlled patch and lifecycle management

The 14 September package-update backlog was cleared through the controlled patch workflow. Ongoing targets are:

- process future host updates through the controlled patch workflow;
- preserve service availability and recovery gates during clustered Proxmox maintenance;
- deliberately manage PVE patch levels;
- keep application/container version ownership explicit;
- use Komodo for routine Docker application/version operations once its production workflow has been proven;
- retire older Docker-management paths only after equivalent control, secrets handling and rollback are demonstrated.

`docker-01` remains intentionally single-purpose for BirdNET-Go unless a later reviewed design explicitly changes that role.

## Priority 5 — network hardening and remote access

### HP ProCurve

The HP ProCurve 2510G-24 is operational as LAN switch and passive-sensor SPAN source. Remaining work:

- capture a fresh physical port map after SPAN/cabling changes;
- replace or restrict the unrestricted `public` SNMP community through a controlled change;
- assess practical mitigations for the legacy Telnet-only management path;
- preserve sensor capture while making management/security changes;
- validate forwarding after physical/configuration changes.

Do not invent physical switch-port assignments where they have not been validated.

### ASUS router

The ASUS RT-AC86U remains DHCP authority, AiMesh controller and the selected OpenVPN remote-access endpoint.

A clean firmware/factory-reset rebuild remains optional and must preserve WAN configuration, DHCP reservations, DNS advertisement, Wi-Fi/AiMesh state, OpenVPN, DDNS, required routing policy, syslog configuration and rollback access.

Approved resolver pair:

```text
192.168.2.51
192.168.2.50
```

`192.168.2.48` must not return as a resolver address.

### Remote-access VPN completion

The former dedicated `vpn-01`/WireGuard target is superseded. Do not allocate a VMID or LAN address for `vpn-01` unless a future architecture review deliberately replaces the current design.

The selected service is ASUS OpenVPN Server 1. Remaining completion work is:

- prove intended internal administration access from a genuinely external network;
- verify both internal DNS resolvers through the VPN;
- confirm ASUS DDNS is configured and the exported client profile uses a stable hostname rather than depending on the current numeric WAN address;
- prove the router/OpenVPN events can be queried in Loki through the existing router-syslog pipeline;
- document router-reset/replacement recovery and client re-enrolment;
- keep OpenVPN client profiles, passwords and protected certificate material outside Git.

See [VPN Remote-Access Design and Implementation Record](../network/VPN-REMOTE-ACCESS-DESIGN.md).

## Priority 6 — planned service expansion

Three additional services are now explicit planned workstreams. No new hostname, IP address, VMID or placement is allocated merely by recording them here; each gets a separate design/preflight before deployment.

### Password manager

Build a self-hosted password-management service, but choose the product and placement deliberately before implementation.

Minimum design gates:

- product selection based on supported clients, export/recovery capability and maintainability;
- HTTPS and a defined trusted access path;
- protected secrets and recovery material outside Git;
- encrypted/off-host backup of persistent data;
- proven restore before the service becomes the sole copy of important credentials;
- monitored service availability;
- documented emergency access if the homelab, DNS or VPN is unavailable;
- MFA/passkey capability where supported and appropriate.

No product is recorded as selected yet. Do not silently treat Vaultwarden, Bitwarden or another candidate as approved until the choice is made.

### Home Assistant

Build Home Assistant as the home-automation control plane.

Design/preflight must decide:

- Home Assistant OS VM versus another supported deployment model;
- placement on the current Proxmox cluster;
- required USB/Zigbee/Z-Wave/Bluetooth passthrough, if any;
- local-only versus approved remote-access model;
- DNS naming and certificate approach;
- backup and restore of Home Assistant configuration/state;
- monitoring without leaking entity/state data unnecessarily;
- failure behaviour for automations that affect the physical home.

Prefer local control and avoid making the Home Assistant management UI directly WAN-accessible merely for convenience.

### Docker management platform

Komodo remains the preferred direction for Docker application/version management, consistent with the current lifecycle-management plan.

Before production adoption:

- choose the management-server placement independently of the managed Docker hosts;
- define how agents/endpoints authenticate;
- keep API keys and deployment secrets outside plaintext Git;
- prove deployment/update/rollback on a low-risk workload first;
- confirm it can manage required Docker stacks without bypassing the Git/IaC authority model;
- define what Komodo owns versus Ansible/Compose/GitHub workflows;
- retire superseded Watchtower/WUD/manual update paths only after equivalent visibility and rollback are demonstrated;
- send useful service/audit logs to the existing monitoring/logging platform where practical.

This workstream must not automatically turn `docker-01` into a general-purpose application host; placement is a separate design decision.

## Priority 7 — observability and analytics expansion

The core metrics/logging/network-observability platform is live. Future work should add useful operational context rather than duplicate host-up telemetry:

- add cluster-specific health for Corosync links, vote/quorum state and QDevice reachability;
- continue service-specific telemetry where actionable;
- correlate Network Hosts inventory, enrichment, deep profiles and switch topology;
- build the planned Web Platform / Analytics dashboard combining Cloudflare edge/security information, Umami visitor analytics and origin/application health from Grafana/Loki;
- add backup freshness/storage-capacity visibility after more unattended history is available;
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

Greenbone/OpenVAS is now implemented as `greenbone-01` VM203 on `Proxmox-2`; it is not future greenfield work.

Remaining vulnerability-management work is operational:

- observe feed freshness and resource/storage growth;
- retain LAN-only exposure;
- address the low-severity ICMP timestamp finding through reviewed IaC if remediation is desired;
- define an explicit image-digest/update policy if rolling Community Container tags become operationally undesirable;
- observe the first unattended VM203 backup;
- maintain a repeatable scan/remediation workflow.

The active scanner remains separate from `sensor-01` passive detection.

## Edge / Cloudflare Tunnel

`edge-01` exists as CT103 on `Proxmox-2`, but the connector workload is intentionally not deployed.

Deploy Cloudflare Tunnel only when a real service requirement exists. Keep connector credentials outside Git, deploy through reviewed IaC, validate outbound connectivity/origin policy, document credential rotation/recovery and add useful monitoring.

## Public services

Public/static workloads should continue to use external hosting where that reduces homelab dependency. The personal portfolio site is an example of a workload that does not need home infrastructure for normal public availability.

## Completion criteria

The platform can be considered operationally mature when:

- post-cluster scheduled Proxmox backups have an observed unattended success record including VM203;
- representative LXC, QEMU VM and application restores are proven;
- important data has an independent secondary copy;
- controller recovery state is protected off-host;
- Corosync link fallback and QDevice-assisted single-node maintenance behaviour are proven;
- the HA/storage decision is explicit rather than assumed;
- controlled patch/lifecycle management is routine;
- physical network mapping reflects current SPAN/cabling reality;
- remaining switch/router hardening decisions are completed or explicitly accepted;
- remote administrative access uses the documented router-hosted VPN rather than directly exposed management services;
- vulnerability scanning remains maintainable and recovery-aware;
- observability remains useful and low-noise;
- service ownership and IaC authority remain unambiguous;
- optional new services are introduced only when their operational value justifies their recovery and maintenance burden.
