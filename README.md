# Homelab Platform

Private migration workspace and future Infrastructure-as-Code authority for the JRW Roberts homelab.

## Status

This repository is currently **private** while the platform is being reviewed and rebuilt.

No legacy repository is authoritative here yet. Existing repositories remain the source of truth until each workload, configuration area, or document is explicitly migrated and validated.

## IaC authority

All new Infrastructure-as-Code is stored under [`IaC/`](IaC/). Terraform provisions infrastructure and Ansible configures operating systems/services. Do not add new IaC outside that directory.

The older top-level `terraform/` path predates this convention and will be migrated separately after its references and state handling are checked.

## Principles

- Git is the source of truth.
- Infrastructure changes are reviewed before deployment.
- Host ownership is explicit.
- Secrets are never stored in plaintext.
- Existing production state is discovered before it is changed.
- Migration is workload-by-workload with rollback paths.
- Legacy repositories are removed only after their useful content has been migrated and verified.

## Migration phases

1. Current-state hardware and workload inventory.
2. Target host-role design.
3. Repository and IaC structure.
4. Public-site migration.
5. Proxmox VM provisioning.
6. Komodo and Renovate rollout.
7. Workload migration by host.
8. Monitoring and security separation.
9. Jenkins / Stage 6 retirement.
10. Legacy repository cleanup.
11. Final documentation and public-readiness review.

See [the migration tracker](docs/migrations/MIGRATION-TRACKER.md) for progress.


## Production runbooks

- [DNS service recovery plan](production%20docs/DNS-SERVICE-RECOVERY-PLAN.md) — prerequisites, triage, service repair, CT rebuild, alternate-PVE recovery, validation, protection, DHCP cutover and total-DNS-outage recovery.
