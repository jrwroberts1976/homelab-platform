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
| 4. Public website migration | COMPLETE — AUTOMATION HARDENING | `me.jrwroberts.co.uk` is externally hosted on Cloudflare Pages and manually validated; production GitHub Actions deployment still needs final merge/proof |
| 5. Proxmox IaC | IN PROGRESS — DNS-02 CUTOVER COMPLETE | Existing `PROXMOX` retained; rebuilt `pve2` remains standalone; CT 100 `dns-02` is provisioned/configured and validated; ASUS DHCP now advertises `.48 + .50`; final Terraform protection apply remains |
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
- ids-01: retired / no longer present. Historical audit data remains useful for migration archaeology, but it is not a current workload authority and must not be treated as a live rollback host.
- media-01 (`192.168.2.195`): hardware and workload audit complete. Raspberry Pi 5 with approximately 8 GiB RAM and healthy 512 GB-class NVMe; current role is Kodi/media, not k3s. Backup-replica audit shows ~12 GiB under `/home/homelab-backup/replica`: `ids-01/repository` (~2.4 GiB) and `ids-01/remote-repositories` (~9.5 GiB) containing dietpi, historical k3s-node-01 and testserver Restic-like repositories. No homelab-vault repository, monthly archive tree or SOPS/age recovery files were found in this replica tree, so it is not yet a complete replacement for the degraded DietPi disk. The stale `k3s-node-01.jameshouse` DNS alias remains to be corrected during hostname reset.
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

Production hosting cutover is complete.

- Source repository: `jrwroberts1976/engineering-portfolio`.
- Framework: Astro static output with `npm run build` -> `dist/`.
- Target: Cloudflare Pages project `engineering-portfolio`.
- Production URL: `https://me.jrwroberts.co.uk`.
- A manual production deployment was completed and validated on 7 September 2026.
- Normal public-site hosting is now external to the homelab.
- The prior home-hosted state is retained only as rollback reference until the automated deployment path is proven.
- Production workflow implementation exists in `engineering-portfolio` PR #16 and still needs merge/production validation.

See `docs/migrations/PUBLIC-WEB-CUTOVER.md` and `production docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md`.

## Proxmox second-node work — 7 September 2026

A fresh second Proxmox node was built as `pve2` at `192.168.2.71` and fully patched before a cluster trial.

Validated package state included:

- Proxmox VE 9.2.0
- kernel `7.0.14-15-pve`
- `pve-manager` 9.2.11
- `pve-cluster` 9.1.6
- Corosync 3.1.10-pve3
- `qemu-server` 9.2.7

The node joined the `Home-lab` cluster and reached two-node quorum, but its local `pmxcfs` configuration database did not complete synchronisation. This caused missing/incomplete `/etc/pve` state, certificate update blocking, and `pveproxy` failure on the second node.

The trial was deliberately rolled back:

- `pve2` was removed from `Home-lab`
- `PROXMOX` returned to a one-node cluster at config version 5
- `pve2` was separated locally using `pmxcfs -l`
- `pve2` returned to a clean standalone state with only `/etc/pve/nodes/pve2`
- no Corosync config remains on `pve2`

Network troubleshooting also found RX errors/drops on the current USB management NIC. This is a concern, but it has **not** been proven to be the original cause of the `pmxcfs` failure.

Current decision:

- retain the existing USB NIC for management for now
- validate the incoming second NIC independently
- use the new NIC as the preferred dedicated Corosync / VM-migration path if testing is clean
- do not retry the cluster join until standalone `pve2` and the new NIC are both proven healthy

See `docs/migrations/PROXMOX-SECOND-NODE-2026-09-07.md`.

## DNS resilience redesign — 7 September 2026

The replacement path for the current secondary DNS service is now approved in principle.

Target:

- `dns-01`: existing physical Raspberry Pi 3 at `192.168.2.48`, Pi-hole + Unbound
- `dns-02`: new unprivileged Debian LXC on `PROXMOX`, Pi-hole + Unbound, approved address `192.168.2.50/24`, CT ID `100`
- ASUS router remains DHCP authority and now advertises both validated resolvers: `192.168.2.48` and `192.168.2.50`
- the previous `dns-02` at `192.168.2.242` has been removed; ASUS DHCP no longer advertises `.242` and now uses replacement `dns-02` at `192.168.2.50`

The infrastructure definition now lives under:

`IaC/terraform/proxmox/dns-02/`

The previous `dns-02` at `192.168.2.242` has already been removed. ASUS DHCP has now been changed to advertise replacement `dns-02` at `192.168.2.50` alongside `dns-01` at `.48`. Live preflight selected CT ID `100`, confirmed `vm-ssd` capacity, confirmed the existing Debian 13.6 LXC template, and approved `192.168.2.50/24` for `dns-02`. Terraform then created CT 100 successfully. First-boot validation exposed Debian 13/systemd 257 mount failures; enabling LXC nesting resolved them. The interface was standardized to `eth0`, SSH key bootstrap was proven, systemd reports `running` with zero failed units, and the final Terraform plan reports no drift. The scoped `iac@pve!opentofu` token cannot independently submit the provider's full LXC feature structure, so the initial nesting enablement required a one-time `root@pam` `pct set` operation. Service configuration is now expressed through `IaC/ansible/`. The first live apply on 7 September 2026 completed with `ok=37 changed=13 unreachable=0 failed=0`. From TestServer, `dns-02` answered public DNS over both UDP and TCP, returned `dns-02.jameshouse -> 192.168.2.50`, matched `dns-01` for the existing `testserver.jameshouse` record, returned `SERVFAIL` for deliberately broken DNSSEC, and blocked a domain present in its gravity database as `0.0.0.0`. A controlled TestServer test temporarily overrode NetworkManager to use only `192.168.2.50`; `/etc/resolv.conf` contained only that resolver, normal libc name resolution succeeded for public and local names, and HTTPS to `https://example.com` returned HTTP 200. ASUS DHCP was then changed from `.48 + .242` to `.48 + .50`. A Windows Wi-Fi client received the new pair directly, and a freshly renewed TestServer Ethernet lease also received `.48 + .50`. This completes the replacement DNS client/router cutover.

## Backup redesign

GUI-first backup redesign is now a target requirement.

- Preferred long-term platform: Proxmox Backup Server, pending final host/storage placement.
- Transitional compatibility: Backrest may be used to browse/restore existing Restic repositories.
- Existing Restic/monthly backup data remains protected until replacement backups and restores are proven.
- Degraded DietPi backup HDD must not become the new primary datastore.

See `docs/architecture/BACKUP-STRATEGY.md`.

## Next action

1. Complete standalone `pve2` service validation and test the incoming second NIC before any further cluster attempt.
2. Merge/prove the Cloudflare Pages production workflow in `engineering-portfolio` so the manual upload path becomes fallback-only.
3. Run the final reviewed Terraform plan/apply for `dns-02` so the now-enabled `protect_after_build = true` desired state protects CT 100.
4. Continue reconciling unique content on the degraded DietPi backup disk before any destructive host rebuild.
