<!-- estate-authority: IaC/inventory/estate.json -->
# Gate 3b: reviewed single-owner network-discovery cutover runbook (DRAFT)

**Status:** Planning/review only. This document neither authorises nor executes any production change. Source ownership remains on `Proxmox-2`; `monitor-01` remains inert. Gate 3a passed read-only on 27 September 2026. Consult [current state](../architecture/CURRENT-STATE.md) and [full migration history](network-discovery-monitor01-migration.md).

## Exact scope and safety boundary

Move only the network-host collector, targeted enricher, saved OS-evidence publisher and first-seen notifier from `Proxmox-2` (192.168.2.71) to `monitor-01` (192.168.2.52, eth0, VM202). Keep unrelated node exporter, Alloy, Grafana, Prometheus, other Proxmox services and their existing dashboards running. Deep Nmap profiling is **not** enabled by default. `admin-01` is the Ansible controller, never a scan worker. Do not mount `/etc/pve` into monitor-01: the staged enricher uses the independently verified cluster-wide Proxmox guest-MAC snapshot and authenticated strict-TLS API refresher.

**No execution before separate explicit user approval, reviewed mutating playbooks, and a new live Gate 3a pass.** The approved cutover must be divided into independently gated source freeze, protected final transfer, destination activation, and rollback phases; a single all-or-nothing playbook without hold points is unacceptable. Any gate failure stops before the next phase. Do not run earlier one-shot staging playbooks again.

## Pre-execution evidence gate (read-only)

- Re-run the existing `network-host-monitor01-cutover-preflight.yml` from a fresh pinned `main` checkout; ensure zero changed and zero failed on both hosts. Confirm expected VM/interface/route and no source notifier delivery errors in the preceding 24h.
- Record current source timer enablement and runtime, last successful collector/enricher/OS-publisher and notifier results, original unit contents and notification wiring, and any actual running one-shot jobs; preserve this data privately for exact rollback. Source deep-profiler schedule may differ and must be restored to its observed state.
- Require five monitor-01 timers disabled/inactive; target scanner/enricher/refresh jobs inactive; existing notifier identical to approved rendered template but disconnected; target alert env, registry and cutover marker absent. Keep four staged JSONs root-owned and 0600.
- Record source and destination original SHA-256 values; source inventory and complete first-seen registry counts, plus baseline/alerted/pending-online counts. Do **not** hardcode historical 49-record values as final totals; include all historical alert records, even those no longer in the live inventory.
- Revalidate strict-TLS API access to both Proxmox nodes and all present non-template guest MACs. A guest snapshot must remain within its 48h freshness limit at activation. Confirm SMTP relay TCP/25 access without sending email.
- Capture clean rollback conditions, backup location, maintenance-window approval, and the reviewed exact execution commit. No sensitive token, recipient, raw MAC or protected JSON contents in Git or Ansible logs.

## Hold point A: explicitly approved source freeze

**Only run after separately reviewed source-freeze playbook and explicit production-stop approval.**

1. Assert production source is exactly Proxmox-2 and destination still inert. Capture the four existing source network timer states and relevant original units, including enabled vs disabled values for rollback. Stop/disable source collector, enricher, deep profiler (if scheduled), and network-only OS-evidence timers; **do not touch ordinary Proxmox/node monitoring**.
2. Drain any in-flight one-shot jobs and collector `ExecStartPost` notifier activity. A successful timer stop alone is insufficient: wait for services to finish, verify no remaining worker/notifier process, and confirm no timer or other dependency can restart them. Fail closed on timeout or unexpected process.
3. Recheck source notification journal delivery errors and pending-online first-seen messages **after** drain. If pending or delivery errors remain, hold and investigate: do not copy or activate target alerting.
4. Capture source freeze time and hash the five protected files only after quiescence. Keep source disabled until either target validation/activation succeeds or an explicit rollback finishes.

## Hold point B: final private copy and validation

- Create a new immutable, timestamped, root-only (0700) snapshot directory on Proxmox-2. Snapshot **all five** files: `inventory.json`, `deep-profiles.json`, `enrichment.json`, the **complete** `alerted-macs.json`, and `alerts.env`. The source JSONs and registry must remain root-only 0600. Detect any source changes across the snapshot; mismatch is an immediate stop.
- Before replacing anything on monitor-01, create a separate timestamped 0700 backup of its existing **four** protected staged JSON files, including `proxmox-guests.json`, plus the existing disabled service/unit configuration. Refuse collisions/partial prior runs; do not overwrite previous backups.
- Transfer the frozen source snapshot only through the existing authenticated encrypted Ansible transport, with `no_log` wherever bytes may contain MACs or recipients; never use controller/world-readable temp copies. Replace the three staged source-data JSONs atomically and add the historical first-seen registry and protected recipient environment with correct root ownership and 0600 modes. Preserve the pre-existing, independently maintained `proxmox-guests.json` rather than copying a Proxmox-2 local-file guest view.
- Require exact SHA-256 parity for **all five** source/target copied files; schema-parse three datasets and the versioned full alert registry. Assert every source historical registry entry remains identical on target, zero inventoried MACs are absent from the registry, and zero pending-online first-seen events. Revalidate unique, collision-free guest identities against the **new final inventory**, refreshing the separate protected guest map under strict TLS if necessary.
- Keep all target timers inactive, notifier unwired and cutover marker absent throughout this phase. Validate source is still quiescent before declaring transfer ready. If any check fails, leave target disabled and use the controlled source rollback; do not re-seed alert registry.

## Hold point C: separately approved destination activation

After Hold B passes **and separate activation approval**, confirm source timer/service disablement again. Install/review the target-only notifier unit `ExecStartPost` and protected `EnvironmentFile`, retaining `COLLECTOR_HOST = "monitor-01"` and the copied historical registry. Check its rendered service wiring without executing notifier or dispatching a test email yet.

Introduce the target cutover approval marker **only after** verified source quiescence and full five-file parity. Run trusted API guest-map refresh before the first enrichment job. Enable/start only the reviewed discovery collector and its notification wiring, then enable ordered guest refresh, enrichment and saved OS-evidence timers after service/metric verification; preserve Grafana and Prometheus continuity. Deliberately leave deep-profiling timer disabled until separately opted in. Observe one controlled collector cycle, verify the historical registry did not trigger baseline re-notifications, and arrange **one intentional, nonduplicating test notification** with evidence of relay delivery. Confirm new MAC-keyed inventory, guest enrichment, OS-fingerprint metrics, expected Prometheus labels and all existing individual Grafana host dashboard UIDs. Do not remove old time series until replacement visibility is proven.

**Important:** implement notifier validation/test without sending to all historic MACs or regenerating the first-seen registry. Where an intentional test cannot be isolated safely, keep the notifier disabled and record that alerting validation remains incomplete; do not claim cutover complete.

## Hold point D: rollback and emergency stop

- **Before target activation:** keep monitor-01 disabled; restore the source original timer enablement and unit wiring from the preflight record only after proving all destination worker/notifier services are stopped.
- **After partial target activation:** stop and disable *all* target worker/refresh/evidence timers and drain services/notifier before restoring the source. Remove or quarantine the destination cutover marker **only within the reviewed rollback phase**. Retain both target and source datasets, complete alert registries and logs for reconciliation; account for any new alerts emitted by the target before reactivating old source to avoid duplicate notifications. If no safe registry reconciliation is proven, hold the source notifier off and escalate rather than blindly restart.
- Never run production source and destination collectors or first-seen notifiers simultaneously. Record restoration of previous source schedules, source notifier success, expected Grafana visibility and evidence parity.

## Engineering deliverables before requesting cutover approval

1. **Draft added for review, NOT authorised/executed:** `network-host-monitor01-source-freeze.yml` imports the read-only two-host Gate 3a, requires separate stop approval and change ID, preserves root-only timer/unit rollback evidence, stops only Proxmox-2 network timers, drains existing worker services and records frozen hashes of five source files. Must pass CI and independent code review before any production invocation; if a partial stop fails, the source may remain frozen and requires deliberate recovery.
2. **Draft added for review, NOT authorised/executed:** `network-host-monitor01-final-transfer.yml` requires an explicit separate transfer approval and the exact prior frozen source directory/change ID. It rechecks quiescence and frozen hashes, snapshots all five original files, backs up all four staged destination JSONs, transfers protected data including the complete alert registry and recipient environment, verifies five-file SHA-256 and guest identity, and stops before activation. It fails closed if the snapshot is stale or identities mismatch; a protected guest-map refresh would require its own reviewed procedure. Never run it against production until freeze, transfer and rollback playbooks pass independent review and the maintenance window is explicitly approved.
3. Separate `network-host-monitor01-activate.yml` with an explicit second approval gate, source-still-stopped assertion, isolated notifier setup and validated ordered startup.
4. Separate `network-host-monitor01-rollback.yml`, plus offline sandbox tests for interruption after each hold point. CI must syntax-check and enforce no accidental scan/email/service activation during planning.
5. Document the exact reviewed commit, approved operator/maintenance window, expected service state transitions, final evidence and post-cutover current-state update. No post-cutover claim until live verification.


## Gate 4: post-cutover whole-estate documentation and deployment audit (required)

**Trigger:** perform only after Gate 3 production cutover is complete and monitor-01 discovery, enrichment, first-seen notifications, Prometheus and Grafana are verified stable. Gate 4 is a separate read-only audit; it does not retroactively approve Gate 3 or authorise automatic configuration changes.

Use `IaC/inventory/estate.json` and `docs/architecture/CURRENT-STATE.md` as the authoritative expected estate, reconciling against deployed Ansible/Terraform definitions and each documented service/runbook. Include every active managed host and relevant network appliance, not only Proxmox-2 and monitor-01. Record audit timestamp, exact Git commit and live evidence collected per host.

- **Identity and placement:** actual hostname, management IP, operating system/release/kernel, Proxmox node and VM/CT ID, managed hardware, active/retired identity, network interfaces, DNS settings and routing versus current inventory and architecture diagrams.
- **Installed software and execution:** installed packages, containers/images and versions; enabled/running/failed systemd units and timers; published services, listeners/open ports and host firewalls; compare actual configurations, roles and ownership to declared IaC and service/port register without printing secrets.
- **Network and security:** router, switch, Pi-hole/Unbound parity, Proxmox cluster/quorum, VPN, Cloudflare configuration where verifiable, access boundaries, privileged credentials by *presence/permissions only*, TLS trust and expiration, and Greenbone/sensor status. Distinguish externally accessible ports from LAN-only and local listeners.
- **Monitoring and recovery:** Node Exporter/Alloy/Zabbix/Prometheus/Loki/Grafana health and coverage, alert routing, management-report evidence freshness, scheduled backups and at least documented restore evidence; do not infer a restore was proven merely because an archive exists.
- **Network-discovery ownership:** prove monitor-01 is the sole active collector/enricher/first-seen notifier; verify Proxmox-2 discovery timers disabled, complete historical MAC registry preserved, guest-MAC API refresh and freshness, no duplicate messages, current OS-evidence publication, individual host dashboard count/UIDs and host labels.
- **Drift register:** classify every finding as (a) documentation outdated, (b) actual configuration deviates from approved IaC, (c) intended feature still planned/not deployed, or (d) unverified due to missing evidence. Record expected state, observed state, source evidence, affected host, severity/operational impact, responsible owner and proposed correction. Do not silently rewrite deployment truth to match an outdated plan or change healthy production to match mistaken prose.

**Exit criteria:** publish a dated whole-estate audit report and discrepancies/action register; reconcile `CURRENT-STATE.md`, `estate.json`, service integration/port records, deployment/runbooks and architecture diagrams *against verified reality* through a separately reviewed documentation PR. Configuration changes to resolve operational drift require their own approval and rollback plan. Keep unverified items explicitly open; do not claim 100% compliance before live evidence supports it.
