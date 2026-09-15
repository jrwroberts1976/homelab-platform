# Homelab Platform Agent Instructions

These instructions apply to any AI assistant, coding agent or automated documentation tool working in this repository.

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
