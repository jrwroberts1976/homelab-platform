<!-- estate-authority: IaC/inventory/estate.json -->
# Documentation and Estate Authority

This policy exists to prevent historical hostnames, retired addresses and superseded deployment assumptions from being reintroduced into current homelab designs.

## Source-of-truth order

Use this order whenever documentation, design work or operational instructions disagree:

1. **Validated live state** — direct evidence from the current systems when a change is being planned or verified.
2. **`IaC/inventory/estate.json`** — canonical machine-readable authority for current asset identity, addressing and lifecycle state.
3. **`docs/architecture/CURRENT-STATE.md`** — canonical human-readable description of the validated production estate.
4. **`IaC/`** — authoritative desired configuration for services and infrastructure that have been migrated and validated there.
5. **Production documents and runbooks** — operational guidance that must conform to the sources above.
6. **Audit records, old repositories and conversation history** — evidence only; never current deployment authority.

A lower item in this list must not override a higher item.

## Rules for new documents

New Markdown files under `docs/`, `production docs/` and `runbooks/` must include the following marker within the first 40 lines:

```text
<!-- estate-authority: IaC/inventory/estate.json -->
```

Before a design names a host, IP address, VM/LXC placement or deployment state, check `IaC/inventory/estate.json` and `CURRENT-STATE.md`.

Do not describe a planned asset as deployed. Planned assets belong in the `planned_assets` section of `estate.json` until they have been implemented and validated.

## Historical references

Retired names and addresses are guarded by CI. A new reference to a retired identity should normally be replaced with its current identity.

When a retired identity genuinely has to be mentioned for audit or migration history, the exact Markdown line must include:

```text
<!-- historical -->
```

This makes the exception explicit and reviewable instead of allowing an old name to look current by accident.

## Change procedure

When an asset is renamed, re-addressed, deployed or retired:

1. Validate the live change.
2. Update `IaC/inventory/estate.json` in the same pull request.
3. Update the Ansible inventory when the asset is Ansible-managed.
4. Update `CURRENT-STATE.md` to match.
5. Update affected design documents and runbooks.
6. Allow the `Estate and documentation guard` workflow to pass before merging.

Do not make a deployment identity change in only one document.

## Automated checks

`scripts/validate-estate.py` performs dependency-free checks for:

- duplicate active names and addresses;
- collisions between active and planned assets;
- retired identities accidentally becoming active again;
- agreement between `estate.json` and the `CURRENT-STATE.md` active-estate table;
- agreement between `estate.json` and `IaC/ansible/inventory/hosts.yml` for Ansible-managed assets;
- the authority marker on newly created operational/design Markdown documents;
- new references to retired names or addresses unless explicitly marked historical.

The validator is deliberately based on the Python standard library so it can run in GitHub Actions and locally without adding another package dependency.

## Local validation

Run the full estate consistency check with:

```bash
python3 scripts/validate-estate.py
```

To reproduce the changed-document checks between two commits:

```bash
python3 scripts/validate-estate.py --base <base-sha> --head <head-sha>
```

A passing check does not replace live validation, but it prevents known identity and documentation drift from being silently committed.
