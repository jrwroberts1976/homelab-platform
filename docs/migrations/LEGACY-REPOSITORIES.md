# Legacy Repository Review

No repository in this list should be deleted merely because it looks old. Each must be checked for unique useful content, current dependencies and recovery value first.

## Authority rule

`homelab-platform/IaC/` is authoritative for configuration that has been explicitly migrated and validated here.

A legacy repository may still be:

- the authority for an area not yet migrated;
- a reference source for recovery/history;
- a retirement candidate once unique useful content is reconciled.

Do not describe an entire legacy repository as the current authority merely because some live configuration originated there. Authority should be decided workload/configuration area by area.

| Repository | Current disposition |
|---|---|
| `docker-env` | **KEEP / REVIEW** — legacy Docker/SOPS source; retain until remaining unique workload/secrets references are deliberately reconciled with current service/IaC ownership |
| `home-lab-docs` | **KEEP / REVIEW** — historical/operational documentation source; migrate unique current recovery knowledge before any retirement decision |
| `homelab-container-version-control` | **RETIREMENT CANDIDATE** after Jenkins / Stage 6 and replacement container-update workflow are proven closed |
| `homelab-infrastructure` | **REVIEW** then likely retire if no unique current IaC/recovery content remains |
| `homelab-overview-docs` | **REVIEW** for unique recovery/documentation evidence |
| `homelab` | **REVIEW CAREFULLY** before any deletion |
| `pihole-install` | **DELETION CANDIDATE** if still empty and no workflow references it |
| `grafana-alerting` | **REVIEW** and reconcile any still-current alert rules before retirement |
| `new-server-induction` | **REVIEW** for reusable induction/Ansible logic |
| `homelab-backup-restore` | **KEEP / REVIEW HIGH PRIORITY** for historical recovery material while the new backup platform remains unimplemented |
| `homelab-security-review` | **REVIEW** for reusable security automation/evidence |
| `proxmox` | **KEEP / REVIEW** until remaining unique Proxmox IaC/recovery content is reconciled with `homelab-platform` |

Training, portfolio and unrelated website repositories are outside homelab-platform cleanup unless separately reviewed.

## Retirement gate

A legacy repository can be archived/deleted only after:

1. unique useful configuration/documentation is identified;
2. current production dependencies are checked;
3. recovery value is assessed;
4. secrets/state references are understood without exposing secret contents;
5. authoritative replacements are validated where required;
6. links/workflows that still reference the repository are updated;
7. rollback/history retention needs are satisfied.

Repository cleanup is therefore a migration activity, not a cosmetic GitHub tidy-up.
