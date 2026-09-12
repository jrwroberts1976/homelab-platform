# Target-State Architecture

This document describes the remaining target direction for the homelab.

Many decisions that were previously listed here as proposals have now been implemented. Implemented state belongs in `CURRENT-STATE.md`; this document focuses on what remains to reach the intended operating model.

## Design principles

- Git-managed desired state wherever practical.
- `IaC/` is the home for new Terraform, Ansible and deployment automation.
- Existing production resources are reconciled rather than recreated merely to satisfy code.
- Production changes require identity, validation and rollback/recovery gates.
- Stable Ansible reconciliation should be idempotent.
- Secrets, Terraform state and recovery identities remain outside Git.
- Workloads should have explicit owners and target hosts.
- Monitoring, backup and recovery are part of service completion, not optional extras.

## Implemented platform baseline

The following target decisions are already implemented:

- `admin-01` is the normal administration/IaC controller.
- `PROXMOX` and `Proxmox-2` are standalone Proxmox nodes.
- `dns-01` and `dns-02` provide the resolver pair at `.51` and `.50`.
- `monitor-01` provides the central monitoring stack.
- `cloud-01` provides production Nextcloud/PostgreSQL/Redis.
- `mail-relay-01` provides internal SMTP relay.
- `sensor-01` exists as the dedicated network-sensor VM.
- `media-01` is the Raspberry Pi 5 Kodi endpoint.
- `docker-01` is the Raspberry Pi 4 BirdNET-Go Docker host.
- `edge-01` exists as the Cloudflare Tunnel edge workload.
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

`sensor-01` is already built.

The remaining target is Phase 2 capture activation:

```text
HP ProCurve port 24
└── mirror/SPAN traffic
    └── dedicated capture NIC
        └── sensor-01
            ├── Suricata
            └── Zeek
```

Required gates before activation:

- dedicated NIC installed;
- interface identity proven;
- no management dependency on the capture interface;
- SPAN traffic validated;
- Suricata and Zeek configuration validated;
- storage/log-volume impact understood;
- monitoring and log forwarding validated.

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

## Backup and recovery

The long-term platform must provide reliable backup plus restore testing.

Working direction:

- Proxmox Backup Server remains the preferred estate backup platform if suitable host/storage placement is approved.
- Existing Restic-compatible repositories are preserved until replacement coverage and restore tests exist.
- legacy or degraded storage must not be promoted into a new primary backup role merely because it contains historical data.
- recovery material must be protected independently of the running homelab.

A service is not considered fully production-ready until important persistent data has a documented restore path.

See [Backup Strategy](BACKUP-STRATEGY.md).

## Monitoring and observability

The core monitoring platform is live on `monitor-01`.

Remaining direction:

- expand host/service telemetry where it provides operational value;
- keep Node Exporter targets aligned with Ansible/IaC desired state;
- add service-specific metrics instead of relying only on host-up status;
- continue Loki/log standardisation where appropriate;
- build the planned Network Hosts dashboard using the enriched host gatherer;
- build the Web Platform / Analytics dashboard combining Cloudflare, Umami and origin/application health;
- retain alerting only where it produces actionable signals.

Monitoring configuration should continue to be reconciled through Git-managed IaC.

## Container operations

Komodo is the preferred direction for routine Docker application/version operations where appropriate.

Before any old Docker-management path is retired:

- its current responsibilities must be identified;
- equivalent Komodo control must be demonstrated;
- secrets and persistent configuration must be protected;
- rollback must remain possible.

Jenkins and older Stage 6 delivery paths can be retired only after the replacement path is proven.

## Network direction

### Switch

HP ProCurve port 24 remains reserved for the sensor mirror/SPAN path.

A switch configuration reset/rebuild remains permissible, but only after current forwarding, VLAN and management requirements are captured.

### Router

The ASUS router remains DHCP authority.

A future clean firmware/factory-reset rebuild remains an option, but only after:

- WAN settings are recorded;
- DHCP reservations are represented in documentation/Git;
- DNS advertisement is captured;
- Wi-Fi/AiMesh state is captured;
- port forwards, VPN and routing policy are recorded;
- rollback access is proven.

The approved DNS pair is:

```text
192.168.2.51
192.168.2.50
```

`192.168.2.48` must not return as a resolver address.

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
- remaining legacy operational dependencies are retired;
- network rebuild decisions are complete;
- monitoring/logging gaps are addressed;
- service ownership and IaC authority are unambiguous;
- key recovery procedures are tested rather than merely documented.
