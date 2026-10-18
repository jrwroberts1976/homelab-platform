# Homelab Platform Agent Instructions

These instructions apply to any AI assistant, coding agent or automated documentation tool working in this repository.

## Ansible-first execution and IaC-only changes

- **Use Ansible for all host-level operations**, including read-only diagnostics, service status checks, security validation, configuration, deployment and rollback. Run through the repository's Ansible inventory from `admin-01` rather than asking for direct SSH/manual host commands.
- **Any persistent infrastructure or service configuration change must first be represented in Git-managed Infrastructure as Code (IaC)**, ordinarily an Ansible role/playbook under `IaC/ansible/`. Review/diff it, validate its syntax and scope, apply through Ansible, and verify live state. Do not make undocumented one-off manual changes.
- Prefer checked-in, reusable **read-only Ansible playbooks** for investigations. Ansible ad-hoc modules are acceptable for one-time **read-only** queries, not for untracked configuration drift.
- Keep changes targeted and idempotent, preserve rollback, and require explicit approval before disruptive/rebooting/security-sensitive actions. An emergency manual exception requires explicit user approval and immediate reconciliation into IaC and `gpt-handover.md`.
- After each material user/agent change, update `gpt-handover.md` with implementation, test evidence (or clear absence of verification), and next action. A Git commit alone is not proof of live deployment.

## Mandatory estate preflight

Before creating or changing architecture, network, deployment, migration, recovery or operational documentation:

1. Read `IaC/inventory/estate.json`.
2. Read `docs/architecture/CURRENT-STATE.md`.
3. Read the relevant IaC inventory/configuration for the service being discussed.
4. Treat live validation evidence as higher authority than remembered context.

Do not use conversation history, old audit material, legacy repositories or model memory as current deployment authority.

## Identity and lifecycle rules

- `IaC/inventory/estate.json` is the canonical machine-readable source for current asset names, addresses and lifecycle state.
- An asset in `assets` may be described as current according to its recorded state.
- An asset in `planned_assets` must be described as planned/proposed/not yet deployed until implementation is validated and the inventory is updated.
- Anything in `retired_identities` must not be used as a current hostname or deployment target.
- Do not infer that an old hostname still exists because it appears in historical documentation.
- Do not silently invent replacement hostnames, IP addresses, VMIDs or workload placement.

If a requested design conflicts with the canonical estate inventory, flag the conflict instead of choosing the historical value.

## Documentation rules

New operational/design Markdown under `docs/`, `production docs/` or `runbooks/` must include:

```text
<!-- estate-authority: IaC/inventory/estate.json -->
```

within the first 40 lines.

A genuinely historical reference to a retired identity must be explicit and use the repository's historical marker described in `docs/architecture/DOCUMENT-AUTHORITY.md`.

Whenever a deployment identity/address changes, update the machine inventory, Ansible inventory where applicable, `CURRENT-STATE.md`, and affected documentation together.

## Validation

Before proposing a documentation or estate change as complete, run:

```bash
python3 scripts/validate-estate.py
```

For pull-request changes, the `Estate and documentation guard` workflow is expected to pass.

A passing repository check does not replace live verification for infrastructure changes.

## Cross-chat handover — mandatory

- Before starting work in a new chat or agent session, read the root `gpt-handover.md` as a current working pointer, then reconcile it against the canonical inventory, current-state architecture, relevant IaC and live evidence. It is not a replacement for those sources of truth.
- For **every user/agent-driven change** to source code, IaC, configuration, operational procedures, security disposition, architecture, documentation, or project priorities, update `gpt-handover.md` **as part of the same change**. Record the decision, files/commit, validation evidence or its absence, current work status and the exact next action. Do not defer the handover to a later session.
- Update `CURRENT-STATE.md` and the active backlog too where their authoritative facts/priorities have changed. Do not claim live validation just because a commit or documentation change exists.
- Purely automatic telemetry/status publication without a material decision or change in work status is exempt; reviewed findings and changed decisions are not.
- Keep credentials and sensitive details out of handovers. Do not promise future handover updates if you cannot edit the repository; clearly note that limitation.
