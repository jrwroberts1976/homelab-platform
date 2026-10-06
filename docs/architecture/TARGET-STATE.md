<!-- estate-authority: IaC/inventory/estate.json -->
# Target-State Architecture

**Status:** FUTURE / REMAINING WORK ONLY  
**Reviewed:** 6 October 2026

Implemented state belongs in `CURRENT-STATE.md`. This document intentionally contains only work that still needs to be built, hardened, proven or deliberately accepted.

## Design principles

- Git-managed desired state wherever practical.
- `IaC/inventory/estate.json` is the authority for asset identity and addressing.
- `IaC/` is the home for infrastructure/configuration automation.
- Existing production resources are reconciled rather than recreated merely to satisfy code.
- Production changes require identity, validation and rollback/recovery gates.
- Stable Ansible reconciliation should be idempotent.
- Secrets, Terraform state and recovery identities remain outside Git.
- Monitoring, backup and recovery are part of service completion.
- Current state, future design and historical evidence remain distinct.

## Implemented baseline — do not re-plan

The following are already live and must not be treated as future greenfield work:

- two-node `jameshouse-pve` cluster (`PROXMOX`, `Proxmox-2`) with dual Corosync links and QDevice/QNetd on `admin-01`;
- current cluster-unique guest placement including CT104, CT105, VM203 and VM204;
- Pi-hole/Unbound resolver pair on `dns-01` / `dns-02`;
- `monitor-01` Prometheus/Grafana/Alertmanager/Blackbox/Loki platform;
- 15-host managed Linux monitoring baseline with Zabbix Agent 2;
- Step 10 Grafana Home/Hosts/Patch/Node Detail estate foundation;
- Grafana Alloy logging baseline;
- router syslog to `monitor-01` / Loki;
- router-hosted OpenVPN remote access, operationally accepted 18 September 2026;
- production Nextcloud/PostgreSQL/Redis on `cloud-01`;
- `sensor-01` Suricata/Zeek passive sensing;
- HP ProCurve SPAN with ports 1–23 mirrored to port 24;
- `greenbone-01` vulnerability scanning and management-report evidence path;
- `komodo-01` Komodo Core control plane and commissioned Periphery on explicitly managed hosts;
- `home-01` Home Assistant OS VM204;
- `media-01` Kodi endpoint and primary Proxmox NFS backup target;
- `docker-01` BirdNET-Go host;
- `monitor-01` as the **single active network-discovery owner** after the 27 September cutover;
- persistent Network Hosts pages / Grafana publication / bounded host-assessment workflow;
- node-scoped Proxmox backup jobs:

```text
PROXMOX:   100,102,104,105,200,201,204
Proxmox-2: 101,103,202,203
```

- observed unattended backup evidence for CT105 and VM203;
- isolated LXC restore proof for CT103;
- controlled 5 October patch cycle completed with 15/15 reporting, zero pending updates, zero security updates, zero reboot-required hosts and zero automatic reboots.

## Priority 1 — recovery depth and second-copy resilience

Remaining outcomes:

- observe/record explicit first unattended proof for CT104 and VM204 if not already captured elsewhere;
- perform a representative isolated QEMU VM restore proof;
- prove application-consistent Nextcloud/PostgreSQL recovery for `cloud-01`;
- add an independent second physical/failure-domain copy for important data;
- protect BirdNET persistent data, user media and controller recovery state appropriately;
- protect recovery identities, SSH keys and SOPS/age material outside the running controller;
- add backup freshness/capacity monitoring where it gives actionable signal.

There is no requirement to collapse the two proven NFS namespaces merely because both nodes are in one cluster, and no requirement to deploy Proxmox Backup Server merely for completeness.

See `BACKUP-STRATEGY.md`.

## Priority 2 — Proxmox resilience proof

The cluster exists; the remaining work is proof and operational maturity:

- deliberately test loss of Corosync link0 and prove traffic continues over link1;
- perform a controlled single-node outage/quorum exercise while QDevice is available;
- add useful QDevice/Corosync-link health telemetry;
- document one-node maintenance behaviour;
- keep the current node-local-storage/manual-recovery position explicit;
- do not describe the cluster as automatic guest HA while guest disks remain node-local.

Shared storage / automatic guest HA remains out of scope unless explicitly reopened.

## Priority 3 — retire migration rollback state

Pre-cluster rollback LVs on `Proxmox-2` are historical evidence, not live guest disks.

Target outcome:

- prove they are unreferenced by current guests;
- retain sufficient off-node recovery evidence;
- remove them deliberately once rollback value is accepted as expired;
- record the cleanup so they cannot be mistaken for production storage.

## Priority 4 — lifecycle and container operations

Ongoing targets:

- continue security-only unattended patching with automatic reboot disabled;
- use controlled maintenance for full package/PVE upgrade cycles;
- preserve cluster/DNS/service safety gates during reboots;
- keep application/container image ownership separate from OS patching;
- use Komodo for justified routine container application/version operations;
- prove low-risk update/rollback ownership before retiring older Docker-management paths;
- complete Komodo HTTPS hardening;
- onboard additional Periphery hosts only where there is an explicit operational need.

`docker-01` remains intentionally single-purpose for BirdNET-Go unless a later reviewed design changes that role.

## Priority 5 — network hardening

### HP ProCurve

Remaining work:

- refresh the physical port map after the SPAN/cabling changes;
- review/remove unrestricted SNMP `public` where practical;
- assess mitigations for Telnet-only management;
- preserve sensor capture while changing management/security settings;
- validate forwarding after any physical/configuration change.

Do not invent physical port assignments that have not been observed.

### ASUS router

The router remains DHCP authority, AiMesh controller and OpenVPN endpoint.

A clean rebuild/reset is optional and must preserve WAN configuration, DHCP reservations, DNS advertisement, Wi-Fi/AiMesh state, OpenVPN, DDNS, routing, syslog and rollback access.

Remote-access service completion is **not** outstanding; remaining VPN work is maintenance/recovery documentation.

## Priority 6 — service-specific closeout

### Home Assistant

`home-01` is already commissioned. Remaining optional/operational work:

- external availability monitoring;
- deeper native/whole-VM recovery validation;
- explicit radio/coordinator design for Zigbee/Z-Wave/Thread/Bluetooth when needed.

No direct WAN exposure is approved by default; use the production VPN unless a later design explicitly chooses another method.

### Password manager

A password manager remains a planned optional application workstream.

Before deployment:

- select product deliberately;
- define trusted HTTPS access;
- keep secrets/recovery material outside Git;
- implement encrypted/off-host backup;
- prove restore before it becomes the only copy of important credentials;
- document emergency access independent of the running homelab;
- use MFA/passkeys where supported and appropriate.

No password-manager product is yet authoritative merely because it has been discussed.

### Edge / Cloudflare Tunnel

`edge-01` exists, but `cloudflared` is not deployed.

Deploy a tunnel only for a real approved service requirement, with credentials outside Git, reviewed origin policy, recovery/rotation documentation and useful monitoring.

## Priority 7 — observability and host intelligence

The core Grafana estate foundation is complete. Remaining value is in **quality and depth**, not recreating the base dashboards.

Future work can include:

- cluster/QDevice/link telemetry;
- low-noise service-specific Zabbix/Prometheus checks;
- stronger backup freshness/capacity visibility;
- refinement of Network Hosts evidence, AI confidence and manual-review workflow;
- preserve version/history for host descriptions and avoid silently overwriting human-approved conclusions;
- never treat unavailable telemetry as healthy;
- never send secrets or raw sensitive DNS/client data to AI.

CrowdSec is **not currently deployed** and must not be listed as an active signal source. Evaluate it only if future ingress exposure creates a justified need.

## Priority 8 — public web / analytics

The public portfolio should remain externally hosted so normal homelab outages do not remove public availability.

Future work may include:

- evidence-based review of `me.jrwroberts.co.uk`;
- Cloudflare edge/security observations;
- Umami or equivalent visitor analytics if justified;
- Grafana/Loki application/origin health where useful;
- unified dashboard only after the underlying data sources are defined.

## Completion criteria

The platform can be considered operationally mature when the remaining accepted goals are either proven or explicitly risk-accepted:

- representative LXC, QEMU and application restore evidence;
- independent second copy for important data;
- off-host controller recovery material;
- Corosync link-fallback and controlled single-node quorum proof;
- explicit node-local-storage/manual-recovery position retained or deliberately replaced;
- routine controlled patch/lifecycle management;
- current physical network mapping and reviewed switch/router hardening;
- useful, low-noise observability across metrics/logging/Zabbix;
- service ownership and IaC authority remain unambiguous;
- optional services are introduced only when their operational value justifies their recovery and maintenance burden.
