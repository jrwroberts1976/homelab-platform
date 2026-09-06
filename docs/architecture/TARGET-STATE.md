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
- Proxmox remains a candidate primary compute platform, subject to the completed capacity and recovery review.
- Raspberry Pis remain candidates for edge, appliance, location-dependent, test or lightweight roles, but no Pi role is assumed in advance.
- Komodo Core placement is undecided until all compute hosts are audited.
- Komodo Periphery will run only on Docker hosts approved in the final placement matrix.
- Renovate remains a hosted GitHub App candidate with repository configuration in Git.
- Jenkins / Stage 6 will retire after the replacement deployment path is proven.

No proposed VM such as `docker-core-01` or `monitoring-01` is approved until the full hardware audit is complete.

## Host-owned IaC direction

Future repository structure should make deployment ownership explicit, for example:

```text
hosts/
├── docker-core-01/
├── monitoring-01/
├── ids-01/
├── testserver/
├── birdnet-01/
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
