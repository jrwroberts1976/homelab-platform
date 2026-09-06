# Migration Tracker

This tracker records the controlled migration from the existing homelab repositories and runtime layout into `homelab-platform`.

## Safety boundary

- Do not delete a legacy repository until its unique useful content has been identified, migrated, and validated.
- Do not move a workload until its current runtime, dependencies, persistence, ports, secrets, monitoring, and rollback path are documented.
- Do not deploy Komodo on TestServer while the host-role review is in progress.
- Preserve the existing CrowdSec local drift until it is deliberately reconciled into Git.
- Jenkins remains available as rollback/reference until the replacement deployment path is proven.

## Current programme

| Phase | Status | Exit criteria |
|---|---|---|
| 1. Hardware inventory | IN PROGRESS | Every repurposable host has CPU, RAM, storage, network, OS, architecture, health and upgrade capacity recorded |
| 2. Workload inventory | NOT STARTED | Every service/container has an owner, dependency map and persistence classification |
| 3. Target architecture | NOT STARTED | Every repurposable host has an approved new role and every workload has an approved destination |
| 4. Public website migration | IN PROGRESS | `me.jrwroberts.co.uk` externally hosted and validated |
| 5. Proxmox IaC | BLOCKED — CAPACITY/RECOVERY | Prepare existing `pve-01` in place; RAM decision and GUI-based backup/recovery proof required before migrated production VMs |
| 6. Komodo / Renovate | PAUSED | Control plane placed on approved host and canary proven |
| 7. Workload migration | NOT STARTED | Approved services moved with rollback proof |
| 8. Monitoring/security separation | NOT STARTED | Monitoring and security roles validated |
| 9. Jenkins / Stage 6 retirement | NOT STARTED | Replacement path proven and Jenkins safely retired |
| 10. Legacy repo cleanup | NOT STARTED | Superseded repos deleted only after validation |
| 11. Public-readiness review | NOT STARTED | Repository safe and polished for optional public visibility |

## Known current authorities

| Area | Current source | Migration state |
|---|---|---|
| Docker Compose / TestServer IaC | `docker-env` | ACTIVE SOURCE |
| Homelab documentation | `home-lab-docs` | ACTIVE SOURCE |
| Komodo / Renovate bootstrap | `docker-env` main + live TestServer | DEPLOYED ON LEGACY TESTSERVER — TARGET PLACEMENT PENDING |
| Stage 6 / Jenkins version control | `homelab-container-version-control` | RETIREMENT CANDIDATE |
| Proxmox documentation / IaC | `proxmox` | REVIEW REQUIRED |
| Grafana alerting | `grafana-alerting` plus current monitoring IaC | REVIEW REQUIRED |

## Hostname reset

All repurposable hosts will receive a role-appropriate hostname where the current name does not match the approved target role. Current names remain discovery aliases only until cutover. Hostname changes will be implemented through IaC/configuration management after role assignment, with DNS/DHCP/monitoring/backup dependencies updated and validated in the same migration step.

## Repurpose decision

The migration is now a greenfield reassignment exercise for all repurposable compute hardware. Current host roles are not preserved by default. Hardware capability will be audited first, workloads second, and only then will new host roles be assigned.

Network infrastructure will also be audited, but routers/switches are only repurposed where a viable replacement role exists.

## Current audit progress

- PROXMOX: complete.
- TestServer: hardware and workload audit completed. Live evidence shows Komodo is currently running on TestServer; this supersedes the earlier assumption that it had not been deployed. No migration action has been taken.
- ids-01: hardware and workload audit complete. Current responsibilities include Suricata/CrowdSec, Greenbone, monitoring, secondary Pi-hole/Unbound and Restic server.
- media-01 (`192.168.2.195`): hardware and workload audit complete. Raspberry Pi 5 with approximately 8 GiB RAM and healthy 512 GB-class NVMe; current role is Kodi/media, not k3s. The stale `k3s-node-01.jameshouse` DNS alias remains to be corrected during hostname reset.
- DietPi (`192.168.2.48`): hardware/workload audit complete. Raspberry Pi 3 with approximately 1 GiB RAM, 100 Mb/s Ethernet and native Pi-hole/Unbound. Attached 4 TB-class backup HDD is DEGRADED: 7 current-pending sectors and 2 offline-uncorrectable sectors. Read-only inventory shows about 20 GiB in use. `monthly/` contains dated ids-01 archives (~7.5 GiB and ~12 GiB); `restic/` contains repositories for dietpi, homelab-vault, ids-01, historical k3s-node-01, and testserver. SOPS/age recovery material is also present. Reconcile these against current authoritative copies before replacement, stress testing, destructive changes or reuse; never print or commit the recovery identity.
- BirdNET capture hardware is a non-compute peripheral and is removed from the host-audit list. BirdNET-Go remains a TestServer Docker workload whose future compute placement is still to be decided.

## Security redesign

- Greenbone target: dedicated `security-01` VM on Proxmox after sufficient RAM is available.
- Suricata/network capture stays separate from Greenbone. Working target: `sensor-01` VM on Proxmox with a dedicated second NIC passed through from HP ProCurve mirror/SPAN destination port 24.
- Do not move Greenbone until the VM is provisioned through IaC and backup/restore coverage exists.

## Network rebuild

- HP ProCurve port 24 is confirmed as the mirror/SPAN destination.
- HP ProCurve will be factory-reset because the current lock-down is no longer a practical administration baseline. Preserve any obtainable evidence first; port 24 remains the confirmed mirror/SPAN destination.
- Plan a clean ASUS router firmware/factory reset and rebuild.
- Recreate DHCP reservations, DNS advertisement, AiMesh/Wi-Fi, QoS and required routing/firewall features from documented intent rather than restoring historical drift.
- Do not reset the router until current WAN/DHCP/DNS/Wi-Fi/AiMesh/port-forward/VPN state is captured and rollback access is proven.

See `docs/network/SWITCH-PORT-MAP.md` and `docs/network/ROUTER-RESET-PLAN.md`.

## HP ProDesk rebuild decision

The HP ProDesk will **not** be reinstalled. Its existing Proxmox VE installation is retained as `pve-01` and will be upgraded/configured in place. New guest workloads are still built fresh from IaC.

The ZenBook remains the clean-rebuild candidate for `pve-02`, after its existing workloads and backup data have been migrated/protected.

## Greenfield rebuild

- Factory-default / clean-install rebuilding is approved where it gives a cleaner reproducible platform.
- Switch rebuild comes before router rebuild so the wired forwarding layer is known during router cutover.
- Compute hosts may be wiped/reinstalled only after their unique data, recovery material and migration dependencies are protected.
- Prefer fresh OS/VM + IaC deployment + data restore over carrying old operating-system state forward.
- See `docs/migrations/GREENFIELD-REBUILD-PLAN.md`.

## Public website migration

Migration has started.

- Source repository: `jrwroberts1976/engineering-portfolio`.
- The site is already Astro static output with `npm run build` -> `dist/`.
- Target: Cloudflare Pages project `engineering-portfolio`.
- Cloudflare Pages project and custom-domain registration are represented in Terraform under `terraform/cloudflare/public-web/`.
- Custom-domain registration is disabled by default until a preview deployment is validated.
- The portfolio repository now has a manual Cloudflare Pages preview deployment workflow on branch `migration/cloudflare-pages`.
- Existing homelab hosting remains intact as rollback until external hosting and DNS cutover are proven.

Preview gate: **PASSED**. The Cloudflare Pages project exists, the migration preview deployed successfully, and the site was manually validated. Existing homelab hosting remains the rollback path.

Current cutover state: the previous `me.jrwroberts.co.uk` CNAME rollback state is recorded and the Cloudflare Pages custom-domain association has been initiated. Cloudflare currently reports the domain as **Initializing**. Do not retire the home-hosted site yet.

Immediate gate: wait for the Pages custom domain to become active, then validate production HTTPS/content and prove independence from the homelab origin.

## Backup redesign

GUI-first backup redesign is now a target requirement.

- Preferred long-term platform: Proxmox Backup Server, pending final host/storage placement.
- Transitional compatibility: Backrest may be used to browse/restore existing Restic repositories.
- Existing Restic/monthly backup data remains protected until replacement backups and restores are proven.
- Degraded DietPi backup HDD must not become the new primary datastore.

See `docs/architecture/BACKUP-STRATEGY.md`.

## Next action

Wait for `me.jrwroberts.co.uk` to become active on Cloudflare Pages, then complete production validation and independence proof before any router/switch reset.
