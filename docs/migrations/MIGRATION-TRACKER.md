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
| 4. Public website migration | NOT STARTED | `me.jrwroberts.co.uk` externally hosted and validated |
| 5. Proxmox IaC | BLOCKED — CAPACITY/RECOVERY | RAM upgrade decision and guest backup/recovery proof required before new primary VMs |
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
| Komodo / Renovate bootstrap | `docker-env` main | MERGED, NOT DEPLOYED |
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
- DietPi (`192.168.2.48`): hardware and workload audit captured. Raspberry Pi 3 with approximately 1 GiB RAM, 100 Mb/s Ethernet, native Pi-hole/Unbound, and an attached 4 TB-class backup disk. External HDD SMART health remains to be verified before this host audit is fully closed.
- BirdNET hardware identity: still to be reconciled; BirdNET-Go is currently also confirmed as a TestServer Docker workload.

## Next action

Complete the same full CPU, memory, disk, network, health and workload audit for every host before any further platform deployment or host-role decision.
