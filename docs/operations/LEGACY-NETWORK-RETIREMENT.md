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
3. Record a private, permission-restricted backup or checksum evidence for
   files to be removed; never publish household MAC/domain/host records or
   sensitive historical evidence into GitHub logs.
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

Git commit history provides old code. Live-file backups are required before
removing deployed configuration. Do not automatically re-enable retired
collectors as rollback: reactivation requires an explicit separate approval.
If postflight fails, restore only the affected backed-up files and managed
Grafana dashboard/provider settings after diagnosis.

Update `docs/architecture/CURRENT-STATE.md` and `gpt-handover.md` from
observed *live* state after the approved production change, and close #287
only after postflight and merge.
