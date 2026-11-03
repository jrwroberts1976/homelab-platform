# Legacy ASUS, HP ProCurve and MAC dashboard retirement — #287

**Status: DHCP discovery and legacy Grafana retirement COMPLETED and independently verified; GitHub merge/issue closure pending.**
**Active owner: `monitor-01`; gateway: `router-01`.**

## Purpose and exclusions

Remove the retired ASUS/HP collectors and MAC-generated per-device Grafana
pipeline while retaining independent `network_host_collector`, enrichment,
Proxmox guest identity snapshots, Nmap OS evidence, Zabbix, Greenbone, router
traffic metrics, Pi-hole and the `Homelab — Network Discovery` dashboard.

The HP ProCurve hardware may be recommissioned separately in the future.
Its past configuration and all removed source code remain in Git history;
do not infer it is currently connected. The router is not to be modified.

## Source changes

- Five old inventory/dashboard playbooks and the HP-specific SNMP playbook
  are replaced with fail-closed guards.
- Old collector roles, exporters, generator, generated dashboard templates,
  provisioned MAC/HP-only dashboard sources and unit files are removed.
- Independent OS evidence and host discovery continue without stale ASUS
  hostname/SQLite fallback sources.
- Keep `Homelab — Network Discovery` (independent host metrics), along with
  active router DHCP, core host, security and production dashboards.
- Never run obsolete playbooks to recover a collector without a new decision.

## Production readiness and operator approval

Production is not changed merely by pushing, validating or merging IaC.
Before approving the dedicated live cleanup:

1. Read-only confirm the four old timers are disabled and inactive:
   `asus-network-inventory`, `homelab-hp-switch-collector`,
   `homelab-network-device-inventory`,
   `homelab-network-host-dashboards`.
2. Inspect old unit files, exporter binaries, Prometheus textfile
   `homelab_network_devices.prom`, Grafana file-provider inventory,
   and any generated `network-hosts/net-host-*.json` files.
3. The operator has explicitly waived backups for this retirement and
   regenerable discovered-host reset. Do **not** create pre-cleanup copies
   or archives of retired files or discovery history. Record only non-sensitive
   counts, paths and service states; deletion of previous discovered-host data
   is intentionally irreversible. Never publish household MAC/domain/host
   records or sensitive evidence into GitHub logs.
4. Check that the independent Proxmox guest refresh failure has its own
   cause/owner; do **not** disable or erase it in this workstream.
5. Obtain explicit approval for the named files and service cleanup.
   Use a guarded Ansible playbook, not ad-hoc destructive commands.
6. Remove obsolete units, binaries, textfile metrics and provisioned
   dashboards only within the approved scope. Ensure Grafana dashboard DB
   entries are properly reconciled; removing JSON alone with
   `disableDeletion: true` is not sufficient.
7. Validate postflight: independent host collector, OS evidence,
   Prometheus, Zabbix, Loki, Grafana, router metrics, DHCP and QoS;
   no legacy timers re-enabled and no unrelated units modified.


### Staged operator-approved reset playbook

The read-only ownership/schema check is
`IaC/ansible/playbooks/network-host-dhcp-reset-preflight.yml`.
The implementation is
`IaC/ansible/playbooks/network-host-dhcp-discovery-reset.yml` and must
be run **only** after local syntax validation, review of the intended
destructive scope, and explicit operator approval flags. It includes the
read-only preflight as its first play. This is deliberately not part of
`monitoring.yml` or any scheduled automation.

The reset updates the installed monitor-01 host collector and AI resolver,
then deletes only these six regenerable JSON caches on monitor-01:
`inventory.json`, `deep-profiles.json`, `enrichment.json`,
`dns-evidence.json`, `ai-identification.json`, and
`ai-identification-public.json`. It also removes five obsolete
discovery textfile metrics; after one fresh 192.168.2.0/24 scan, it
seeds fresh per-MAC deep-profile **baseline** records, without launching
expensive deep scans, and restores timers.

It retains `alerted-macs.json` and adds only baseline entries for new
MACs from the one-time scan, preventing a first-seen email storm.
It never touches `proxmox-guests.json` or guest-refresh service,
Pi-hole/Unbound/dnsmasq, DHCP lease data or canonical estate records.
This is not a purge of pre-existing Prometheus/Loki historical series
or the old Grafana per-host pages; those follow a separate guarded
retirement step.

**Failure mode:** Once irreversible deletion starts, a failure leaves
the six discovery timers paused deliberately until the operator diagnoses
and safely resumes them. There is no live backup or automatic restoration,
at the operator's explicit request.

## Rollback boundary

Git commit history retains the retired IaC source and allows a new deployment
to be corrected or reverted, but **no live backup is to be made** for this
workstream. Deleted discovery history and removed Grafana records cannot
be restored without an independent pre-existing copy. Do not automatically
re-enable retired collectors as rollback: reactivation needs separate approval.
If postflight fails, stop the new collection safely, repair the IaC and
re-collect device evidence rather than attempting to restore deleted history.

Update `docs/architecture/CURRENT-STATE.md` and `gpt-handover.md` from
observed *live* state after the approved production change, and close #287
only after postflight and merge.

## Clean DHCP-era discovery reset — requested 3 November 2026

Operator explicitly requested discarding the **old discovered-host working set**
after the ASUS-to-`router-01` DHCP migration, **without backups**.

- Identify the currently active discovery owner *before* any action.
  Historical playbooks use `Proxmox-2` defaults, while staged cutover
  playbooks target `monitor-01`; do not guess which node is authoritative.
- Review timers, collector dependencies and schemas for `inventory.json`,
  derived enrichment/deep-profile and host-identity output. Stop only the
  identified producer/consumer services during a separately approved reset.
- Regenerate only discovery-derived state, and allow one approved new
  `192.168.2.0/24` discovery using the corrected, Ansible-managed collector.
  Any active pre-existing stale MAC/hostname maps must not repopulate it.
- **Never reset** `router-01` DHCP leases/reservations, canonical estate,
  Pi-hole DNS history, original Proxmox guest identity records,
  `alerted-macs.json`/notification secrets, or security event logs.
- Preserve the original protected first-seen registry to avoid 52+ fresh
  device-email alerts, and suppress first-seen notifications during the
  reset if needed. Do not erase or change client identity outside the
  discovery working set.
- Old historical series already stored in Prometheus/Loki will naturally
  outlive the reset until retention expires; a clear "new baseline" start
  time must be documented rather than promising to erase all historic
  metrics. Grafana old generated dashboards are retired separately.
- This is irreversible by operator choice. Fail closed if the active
  collector owner, schema or safe restart cannot be verified.

## 3 November 2026 — Post-rediscovery live legacy inventory

The operator's second successful no-backup rediscovery produced **38 fresh
hosts, 38 profile baselines and 56 retained first-seen entries**; all six
discovery timers were active after the reset. **Do not run that reset again.**

A subsequent read-only monitor-01 audit verified all **four** retired
`/usr/local/sbin/` collector executables are present; **52** per-host JSON
files remain at `/opt/monitoring/grafana/provisioning/dashboards/network-hosts`;
the old `Network Hosts` provider is still referenced in
`/opt/monitoring/grafana/provisioning/dashboards/homelab.yml`.
Grafana and Prometheus both returned HTTP 200.

The source provider has `disableDeletion: true`, which may leave Grafana
database dashboard entries after file removal. Do **not** merely delete JSON
files or redeploy the whole monitoring role (the current live network traffic
dashboard may have changes not reconciled to main).

New **read-only** preflight:
`IaC/ansible/playbooks/network-host-legacy-cleanup-preflight.yml`.
It validates the isolated legacy file scope, independent Network Discovery
and router DHCP dashboards, disabled obsolete timers, Grafana's file provider,
and (when the Docker volume is found) counts legacy entries in Grafana SQLite
in **read-only** mode. It never performs a backup or deletion. Use its result
to design a separately approved, narrowly targeted IaC cleanup; preserve
unrelated Grafana dashboards, router metrics and the Proxmox guest refresher.

## 3 November 2026 — Live Grafana API and provenance gate

- The running Grafana API returned 73 dashboards: 52 old generated
  host dashboards, 5 named retired dashboards, and **16 to preserve**,
  including the independent Network Discovery and router DHCP dashboards.
  API ownership is authoritative here; the old SQLite dashboard table
  returned no rows including protected dashboards and must NOT be edited.
- Grafana file provisioning has `disableDeletion: true`; simply
  deleting JSON would leave stale live dashboard records. Follow
  the official provider deletion lifecycle, scoped to the 57 old
  dashboards, with protected dashboards verified after each stage.
- Read-only `network-host-legacy-cleanup-preflight.yml` now checks
  the Grafana API's `meta.provisioned`,
  `meta.provisionedExternalId` and folder ID for every old UID
  against its exact file and expected provider, without publishing
  host identities or API credentials.
- Next: rerun read-only preflight from latest feature branch and
  require `grafana_api_provisioning_unverified=0` before any actual
  retirement. No backups, deletion or whole-stack redeploy have
  occurred in this Grafana cleanup. Keep #287 open.

## 3 November 2026 — Single generated Grafana dashboard canary staged

The live API attribution check passed: **52 generated** dashboards
plus **5 named** retired dashboards, all 57 sourced from expected
provider files/folders, with **0 mismatches**. There are 73 total
Grafana dashboards; **16 must be retained**. Source file inventory
is 4 obsolete executables, 8 old service/timer units, 5 retired
Homelab JSON and 52 generated JSON files. The former SQLite
dashboard table is empty and not representative of live Grafana.

The Network Hosts **generated** provider is configured with
`disableDeletion: false`, unlike the protected Homelab provider
(`disableDeletion: true`). Grafana documents source-driven
deletion, but upstream regression #109229 reported orphaned
provisioned dashboards in versions 12.1–12.4, so verify live
Grafana 13.2.4 with a *single* deletion rather than assume.

Staged `IaC/ansible/playbooks/network-host-legacy-dashboard-canary.yml`
as a distinct explicitly approval-gated, **no-backup** test.
It imports the same read-only ownership preflight, checks that
live generated source/API UIDs are exactly 52 and Grafana has
73 dashboards, removes **one** verified generated JSON file
without exposing any MAC-based UID, polls the active provider,
then requires **exactly 72** remaining live dashboards, **51**
generated, **5** named retired, and **all other 72 UIDs unchanged**.
It does not edit Grafana provider settings, restart any containers
or services, touch discovery data or delete any other dashboard.
On failed deletion it stops; do not automatically repeat it.
If successful, use the observed provider behaviour to plan
the remaining 56 retirements and retain all 16 other dashboards.

**Status: code-only canary prepared; not executed on production.**
Before intentionally running: fast-forward clean worktree,
verify `git diff --check` and playbook syntax. The canary requires
`legacy_grafana_canary_approved=true` and exact phrase
`RETIRE_ONE_LEGACY_GRAFANA_DASHBOARD_NO_BACKUP`.

## 3 November 2026 — Grafana canary passed; 56-dashboard bulk retirement staged

Operator ran the explicit no-backup `network-host-legacy-dashboard-canary.yml`:
`GRAFANA_CANARY=PASS`, Ansible `monitor-01 ok=28 changed=1 failed=0`.
The generated `Network Hosts` file provider automatically deleted
the one selected dashboard after its source JSON was removed (three
polling retries before success). **72 dashboards now exist:** 51
remaining generated, 5 named retired, and the **same 16 protected
dashboard UIDs**. Grafana and Prometheus remained healthy. No other
files or systemd units were removed. **Never run the canary again.**

`IaC/ansible/playbooks/network-host-legacy-live-retirement.yml`
now targets the **56 remaining** obsolete dashboards and the previously
verified four collector scripts and eight systemd unit files. Its
approval phrase is `RETIRE_56_LEGACY_DASHBOARDS_NO_BACKUP` and is
not included in scheduled playbooks or `monitoring.yml`. The playbook
rechecks the live 72/51/5/16 Grafana state, the 16 retained dashboard
UID fingerprint, exact provisioning attribution, collector inactivity
and live provider structure, then checks source files for any protected
Homelab-provisioned dashboards **before** temporarily switching its
`disableDeletion` flag. It performs Grafana-only restarts (brief
Grafana UI interruption), never a full monitoring stack restart,
and waits for the 16/0/0 Grafana postflight before removing the
obsolete binaries and units. A failed stage restores the protected
provider deletion setting where possible and stops for diagnosis.

Because this is a **no-backup** cleanup, do not assume dashboards can
be recovered if the new guarded procedure fails after source deletion.
Do not modify Grafana's SQLite database or delete unrelated
dashboard files. The operator must approve the 56-target run separately
after reviewing syntax, CI and source attribution. The unrelated
Proxmox guest-refresh failure and all new DHCP-era discovery remain
outside this scope.

## 3 November 2026 — Remaining legacy cleanup successful; read-only postflight

The operator executed the approved no-backup
`network-host-legacy-live-retirement.yml` on `monitor-01`.
Final recap: **ok=54, changed=8, failed=0, unreachable=0,
rescued=0, skipped=0**. The guarded 56-dashboard cleanup, final
provider reconciliation, 16 retained-dashboard UID hash checks,
removal of four obsolete executables and eight old systemd unit
files, and active discovery/Prometheus gates all completed in the
playbook's successful task flow. The supplied log contained the
final recap, so the exact live totals still require an **independent**
read-only validation.

Run `IaC/ansible/playbooks/network-host-legacy-retirement-postflight.yml`
only after syncing the clean dedicated worktree. It inspects exact
legacy file/unit absence, the two protected dashboard JSON files,
two permanent protected Grafana providers, all six discovery timers,
retained inventory and 56+ first-seen entries, live Grafana's
unchanged **16 UID** fingerprint, and Grafana/Prometheus health.
No backups, changes, deletes, scans, retries of retired pipelines,
systemd mutations or full-stack redeploy are included.

**Do not rerun** the prior irreversible DHCP reset, one-dashboard
canary or 56-dashboard bulk cleanup; all have already run.
After postflight, complete the GitHub source reconciliation,
review/merge the feature branch, update handover, and close #287
only when live and Git state agree. Existing unrelated Proxmox
guest-refresh failure remains untouched.

## 3 November 2026 — Independent final postflight PASSED

- Operator executed `network-host-legacy-retirement-postflight.yml` after the no-backup live retirement: **monitor-01 ok=14, changed=0, failed=0**.
- Verified **0** obsolete collector scripts, **0** old systemd units, **0** obsolete named Grafana JSON sources, and **0** generated per-MAC JSON sources.
- Grafana's actual HTTP API reports **16** dashboards, **0** obsolete; original protected 16 UID fingerprint verified. Both permanent Grafana providers are in place, with `disableDeletion: true`. Network Discovery and router DHCP dashboards remain.
- Independent discovery inventory contains **38** current host records and protected first-seen registry **56** entries; all **six** discovery timers active; Grafana and Prometheus healthy.
- The live bulk playbook passed separately **ok=54 changed=8 failed=0**. It had removed the remaining 56 legacy dashboards after a successful one-dashboard canary, four scripts, and eight units. No backups were taken by deliberate operator choice.
- No further live deletion is required. Do **not** repeat the DHCP reset, Grafana canary, or bulk cleanup. The final repository PR/merge and issue #287 status reconciliation are the remaining administrative steps; preserve the separate Proxmox guest-refresh failure as unrelated.

