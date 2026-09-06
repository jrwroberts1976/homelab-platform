# Target-State Architecture

This is a working design, not yet approved as final.

## Greenfield repurpose principle

All repurposable compute hosts are being reassessed from first principles. Existing host names and current workloads do **not** determine their future role.

The final role for each host will be chosen only after the estate-wide audit compares:

- CPU capability and architecture
- RAM capacity and upgrade options
- storage capacity, health and performance
- network interfaces and placement
- power draw and physical location
- workload dependencies and resilience requirements
- backup/recovery requirements
- image/platform compatibility
- expected growth and maintenance burden

Current workloads will be treated as migration inputs, not as reasons to preserve the present host role.

## Working direction

- Public portfolio website: external static hosting where possible.
- The existing HP ProDesk Proxmox installation will be retained as `pve-01`; no bare-metal OS rebuild is planned. It will be upgraded/configured in place after capacity and recovery gates are satisfied.
- The ASUS ZenBook is the working target for `pve-02`, providing secondary Proxmox compute with `pbs-01`, monitoring and management workloads.
- Raspberry Pis remain candidates for edge, appliance, location-dependent, test or lightweight roles, but no Pi role is assumed in advance.
- Komodo Core placement is undecided until all compute hosts are audited.
- Komodo Periphery will run only on Docker hosts approved in the final placement matrix.
- Renovate remains a hosted GitHub App candidate with repository configuration in Git.
- Jenkins / Stage 6 will retire after the replacement deployment path is proven.
- BirdNET capture hardware is treated as a non-compute peripheral. Only the BirdNET-Go software workload needs compute placement.

No proposed VM such as `docker-core-01` or `monitoring-01` is approved until the full hardware audit is complete.

## Host-owned IaC direction

Future repository structure should make deployment ownership explicit, for example:

```text
hosts/
├── docker-core-01/
├── monitoring-01/
├── ids-01/
├── testserver/
└── pihole-*/
```

Shared roles, modules and policy may be reused, but a deployable workload must have an explicit target host.


## Host naming

This rebuild includes a deliberate hostname reset.

- Existing hostnames are treated as legacy identifiers only.
- Final hostnames must describe the approved future role of the machine.
- Hostnames will not be changed until the hardware audit and target-role decision are complete.
- During discovery, assets are tracked by current hostname, IP address, MAC address and hardware model so identity is not lost when names change.
- DNS, DHCP reservations, monitoring targets, SSH known-host records, backup jobs and IaC inventories must be updated as part of each hostname cutover.
- A hostname change is considered incomplete until the new identity is represented in Git and all dependent systems are validated.

Working naming pattern:

```text
<role>-<nn>
```

Examples only, not yet approved assignments:

```text
pve-01
docker-01
monitoring-01
security-01
dns-01
edge-01
```

No current machine is entitled to keep its existing hostname simply because that is its present role.


## Backup direction

The rebuilt backup platform must provide a web GUI while preserving Git/IaC as the configuration authority.

Working preference:

- Proxmox Backup Server as the long-term estate backup platform, subject to final host/storage placement.
- Backrest may be used as a transitional GUI for the existing Restic repositories during migration.
- The degraded DietPi-attached 4 TB-class disk is not an acceptable long-term primary datastore.
- No legacy backup path is retired until verification and restore testing proves replacement coverage.

See [Backup Strategy](BACKUP-STRATEGY.md).


## Security workload direction

Greenbone should move off the legacy `ids-01` host and become a dedicated **`security-01` VM** on the Proxmox platform, subject to the Proxmox RAM upgrade and final capacity plan.

Working allocation:

- 4 vCPU
- 6–8 GiB RAM
- 80–120 GiB virtual disk initially
- Debian VM
- Greenbone Community Edition deployed through Docker Compose/IaC

Greenbone should **not** run directly on the Proxmox hypervisor.

The network IDS/sensor role should remain separate from Greenbone. The working target is a dedicated `sensor-01` VM on Proxmox receiving mirrored traffic through a dedicated second physical NIC passed directly to the VM, while `security-01` performs vulnerability scanning over the normal LAN.

This separation gives us:

```text
HP ProCurve port 24 (mirror/SPAN destination)
└── dedicated second NIC on pve-01
    └── direct passthrough to sensor-01 VM
        └── Suricata

pve-01
└── security-01 VM
    └── Greenbone Community Edition
```

If the Proxmox host is not upgraded to enough RAM, Greenbone remains on its existing host until an alternative x86 placement is approved; it must not be squeezed onto an under-provisioned VM.


## Network rebuild direction

- HP ProCurve **port 24** is confirmed as the mirror/SPAN destination.
- Port 24 is reserved for the dedicated Suricata capture path and must not carry normal management/data traffic.
- Remaining switch ports will be labelled only after MAC-table/cabling discovery.
- The ASUS router will receive a clean firmware/factory-reset rebuild before final DHCP and QoS policy is applied.
- DHCP remains on the ASUS router in the working design.
- DHCP reservations, DNS advertisement and QoS policy will be documented in Git before final cutover.

See:

- [Proposed Layout](PROPOSED-LAYOUT.md)
- [HP ProCurve Port Map](../network/SWITCH-PORT-MAP.md)
- [Router Clean-Rebuild Plan](../network/ROUTER-RESET-PLAN.md)


## Greenfield rebuild policy

Factory-default and clean-OS rebuilds are now an explicit part of the target architecture where they produce a simpler and more reproducible result than preserving historical state.

- HP ProCurve: planned factory-default rebuild; port 24 remains the known mirror/SPAN destination.
- ASUS router/AiMesh: planned clean firmware/factory-reset rebuild.
- Compute hosts: fresh OS/install permitted where roles change materially or legacy state is highly entangled, **except `pve-01` (HP ProDesk), whose current Proxmox installation is explicitly retained and changed in place**.
- Preserve required data/configuration and recovery evidence first; do not preserve an old OS merely to preserve an application.
- No wipe/reset occurs until persistent data, secrets, rollback and target IaC are accounted for.

See [Greenfield Rebuild Plan](../migrations/GREENFIELD-REBUILD-PLAN.md).
