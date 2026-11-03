# Legacy ASUS, HP ProCurve and MAC dashboard retirement — #287

**Status: CODE-ONLY SOURCE RETIREMENT STAGED; NOT DEPLOYED.**
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
