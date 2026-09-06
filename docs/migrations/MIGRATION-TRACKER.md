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
| 1. Hardware inventory | IN PROGRESS | Every host has CPU, RAM, storage, network, OS, architecture and role recorded |
| 2. Workload inventory | NOT STARTED | Every service/container has an owner, dependency map and persistence classification |
| 3. Target architecture | NOT STARTED | Every workload has an approved destination |
| 4. Public website migration | NOT STARTED | `me.jrwroberts.co.uk` externally hosted and validated |
| 5. Proxmox IaC | NOT STARTED | New VMs provisioned reproducibly |
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

## Next action

Complete the current-state hardware and workload inventory before any further platform deployment.
