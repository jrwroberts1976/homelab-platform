# Target-State Architecture

This document describes the remaining target direction for the homelab.

Implemented state belongs in `CURRENT-STATE.md`; this document focuses on what still needs to be built, hardened or proven.

## Design principles

- Git-managed desired state wherever practical.
- `IaC/` is the home for new Terraform, Ansible and deployment automation.
- Existing production resources are reconciled rather than recreated merely to satisfy code.
- Production changes require identity, validation and rollback/recovery gates.
- Stable Ansible reconciliation should be idempotent.
- Secrets, Terraform state and recovery identities remain outside Git.
- Workloads should have explicit owners and target hosts.
- Monitoring, backup and recovery are part of service completion, not optional extras.
- Current state, target state and historical evidence must remain clearly separated.

## Implemented platform baseline

The following target decisions are already implemented:

- `admin-01` is the normal administration/IaC controller.
- `PROXMOX` and `Proxmox-2` are standalone Proxmox nodes.
- `dns-01` and `dns-02` provide the resolver pair at `.51` and `.50`.
- `monitor-01` provides the central monitoring stack.
- `cloud-01` provides production Nextcloud/PostgreSQL/Redis.
- `mail-relay-01` provides internal SMTP relay.
- `sensor-01` exists as the dedicated network-sensor VM and Phase 1 is complete.
- `media-01` is the Raspberry Pi 5 Kodi endpoint.
- `docker-01` is the Raspberry Pi 4 BirdNET-Go Docker host.
- `edge-01` exists as a reserved edge LXC, but the Cloudflare Tunnel workload is not deployed.
- legacy `TestServer`, `DietPi`, `ids-01` and `k3s-node-01` identities are retired.

These should no longer be presented as speculative future placements.

## Proxmox direction

The current design deliberately uses two standalone Proxmox nodes.

A future cluster is optional, not a current requirement. Do not retry clustering merely to make the nodes look symmetrical.

Any future cluster proposal requires:

- clean dedicated network-path validation;
- healthy NICs;
- proven Corosync/pmxcfs behaviour;
- backup/recovery coverage;
- a clear operational benefit.

Existing workloads do not need to move simply to balance guest counts between nodes.

## Security platform

### Network sensor

`sensor-01` Phase 1 is already complete.

The remaining target is Phase 2 capture activation:

```text
selected switch traffic
    -> HP ProCurve mirror/SPAN session
    -> future port 24 SPAN destination
    -> dedicated USB capture NIC
    -> PROXMOX USB passthrough
    -> sensor-01 capture interface
       -> Suricata
       -> Zeek
```

Required gates before activation:

- dedicated USB NIC installed;
- physical repatching plan agreed and documented;
- port 24 freed from its current primary-router connection;
- interface identity proven;
- no management dependency on the capture interface;
- switch mirroring explicitly configured;
- mirrored packet arrival validated;
- Suricata and Zeek configuration validated;
- storage/log-volume impact understood;
- monitoring/log forwarding validated.

Until then, packet engines remain intentionally disabled.

### Vulnerability management

Greenbone should remain separate from the passive sensor role.

The working long-term target remains a dedicated `security-01` workload on suitable x86 capacity, subject to:

- resource review;
- persistent-storage design;
- backup/restore coverage;
- IaC deployment;
- monitoring integration.

Greenbone must not run directly on a Proxmox hypervisor.

## Edge / Cloudflare Tunnel

`edge-01` is provisioned as CT 103 on `Proxmox-2` at `192.168.2.56`.

The remaining target is to design and deploy the actual Cloudflare Tunnel connector through reviewed IaC when approved.

Before deployment:

- define the exact public services that require the tunnel;
- keep connector credentials/secrets outside Git;
- install and manage `cloudflared` through the approved configuration path;
- validate outbound tunnel connectivity;
- validate routing/origin policy;
- document recovery/credential rotation;
- add appropriate monitoring without exposing sensitive connector detail.

Do not describe `edge-01` as an operational Cloudflare Tunnel workload until the connector is actually deployed and validated.

## Backup and recovery

The largest remaining platform gap is backup and restore coverage.

Current reality is intentionally explicit:

- there is no active PBS server;
- neither Proxmox node has scheduled guest backup jobs;
- no active estate-wide Restic/Backrest service was found during the 12 September audit;
- restore testing is not proven;
- the 4 TB WD disk on `PROXMOX` is blank/risk/POC storage, not a backup platform.

Long-term direction:

- Proxmox Backup Server remains the preferred VM/LXC backup platform if suitable placement/storage is approved;
- use healthy dedicated backup storage rather than a sole virtual disk on a compute node;
- preserve historical Restic repositories only where useful data/recovery evidence remains;
- provide at least two independently useful copies of important data;
- protect controller Terraform state, secrets and recovery identities independently;
- schedule verification/pruning/retention;
- perform actual restore tests.

A service is not fully recovery-ready merely because the application is healthy.

See [Backup Strategy](BACKUP-STRATEGY.md).

## Monitoring and observability

The core metrics platform is live on `monitor-01`.

The 12 September audit found 23 active Prometheus targets, all healthy, with zero active alerts.

Remaining direction:

- expand service-specific telemetry where it provides operational value;
- keep Node Exporter targets aligned with IaC desired state;
- add service-specific metrics instead of relying only on host-up status;
- deploy Loki/Alloy only through a deliberate central-logging design;
- ingest the existing router syslog file when the logging platform exists;
- build the planned Network Hosts dashboard using the enriched host gatherer;
- build the Web Platform / Analytics dashboard combining Cloudflare, Umami and origin/application health;
- retain alerting only where it produces actionable signals.

## Container operations

Komodo is the preferred direction for routine Docker application/version operations where appropriate.

Before any old Docker-management path is retired:

- its current responsibilities must be identified;
- equivalent Komodo control must be demonstrated;
- secrets and persistent configuration must be protected;
- rollback must remain possible.

Jenkins and older delivery paths can be retired only after the replacement path is proven.

`docker-01` remains intentionally single-purpose for BirdNET-Go unless a later design explicitly changes that role.

## Network direction

### Switch

The current switch is an HP ProCurve 2510G-24 on VLAN 1.

Port 24 is **not currently a SPAN destination**. Mirroring is disabled and the primary ASUS router is currently connected there.

Target direction:

- retain the current 12 September port map as evidence only;
- design a deliberate future repatch once the sensor USB capture NIC arrives;
- move the router/uplinks to the agreed final ports;
- reserve/repurpose port 24 as the SPAN destination;
- configure mirroring only during the controlled sensor Phase 2 change;
- prove normal LAN connectivity and mirrored packet arrival after repatching.

A later switch reset/rebuild remains permissible only after current forwarding, VLAN, management and patching requirements are captured.

Security-hardening items to address in a later network change include the current unrestricted `public` SNMP community and legacy Telnet-only management path.

### Router

The ASUS router remains DHCP authority.

A future clean firmware/factory-reset rebuild remains an option, but only after:

- WAN settings are recorded;
- DHCP reservations are represented in documentation/Git;
- DNS advertisement is captured;
- Wi-Fi/AiMesh state is captured;
- port forwards, VPN and routing policy are recorded;
- rollback access is proven;
- the switch repatch/management path is understood.

Approved DNS pair:

```text
192.168.2.51
192.168.2.50
```

`192.168.2.48` must not return as a resolver address.

## DNS parity target

Both resolvers should provide the same managed local DNS record set.

The current `dns-02` omission of `dns-01.jameshouse` is a known IaC parity defect. Correct it through reviewed IaC; do not normalize it through undocumented GUI edits.

## Naming policy

Current validated role names should be retained unless there is a real operational reason to change them.

Do not rename hosts merely to enforce an abstract naming pattern.

Any future hostname change must update, in the same controlled change:

- DNS;
- DHCP/reservations;
- monitoring;
- SSH identity/known-host handling;
- backup jobs;
- IaC inventory;
- documentation.

## Public services

Public/static workloads should continue to use external hosting where that reduces homelab dependency.

The personal portfolio site is an example of a workload that does not need to depend on home infrastructure for normal public availability.

## Password manager

A self-hosted password manager remains a future project.

Before deployment:

- choose the product and host intentionally;
- deploy through Git-managed IaC;
- keep recovery material outside Git;
- provide HTTPS;
- back up and restore-test its persistent data;
- monitor availability;
- document an emergency recovery path independent of the running homelab.

## Completion criteria

The current architecture can be considered mature when:

- backup and restore coverage is proven;
- sensor capture is live and validated;
- the edge tunnel is deployed only if/when required and has a recovery path;
- remaining legacy operational dependencies are retired;
- network rebuild/repatch decisions are complete;
- monitoring/logging gaps are addressed;
- DNS local-record parity is reconciled;
- service ownership and IaC authority are unambiguous;
- key recovery procedures are tested rather than merely documented.
