<!-- estate-authority: IaC/inventory/estate.json -->
# Gate 3b: reviewed single-owner network-discovery cutover runbook (DRAFT)

**Status — 27 September 2026:** the user separately authorised and successfully completed source freeze, five-file protected final transfer and monitor-01 activation under change `GATE3B_20260927_01`. The production discovery owner is **monitor-01**; Proxmox-2's four discovery timers are disabled/inactive, and the monitor-01 collector, enricher, OS evidence and Proxmox guest refresh timers are enabled/active. The deep-profiler remains disabled. All 49 historical alert-registry entries survived unchanged; one new alerted device and one `network_device_alert_sent` journal event were observed, with one relay delivery in the window (SMTP message-ID correlation not yet performed). Prometheus/Grafana/Loki health checks passed, and network-host dashboard metric queries returned 49 fresh series per metric at the point of observation. Individual dashboard visual inspection and Gate 4 estate-wide audit are still open. The sections below are retained as **historical planning/execution and recovery instructions**, not permission to repeat the completed production cutover. Consult [current state](../architecture/CURRENT-STATE.md) and [migration history](network-discovery-monitor01-migration.md).

## Exact scope and safety boundary

Move only the network-host collector, targeted enricher, saved OS-evidence publisher and first-seen notifier from `Proxmox-2` (192.168.2.71) to `monitor-01` (192.168.2.52, eth0, VM202). Keep unrelated node exporter, Alloy, Grafana, Prometheus, other Proxmox services and their existing dashboards running. Deep Nmap profiling is **not** enabled by default. `admin-01` is the Ansible controller, never a scan worker. Do not mount `/etc/pve` into monitor-01: the staged enricher uses the independently verified cluster-wide Proxmox guest-MAC snapshot and authenticated strict-TLS API refresher.

**No rerun or recovery action without fresh, phase-specific explicit user approval, reviewed playbooks and current two-host checks.** The approved cutover must be divided into independently gated source freeze, protected final transfer, destination activation, and rollback phases; a single all-or-nothing playbook without hold points is unacceptable. Any gate failure stops before the next phase. Do not run earlier one-shot staging playbooks again.

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


## Gate 3b pre-activation recovery: interrupted freeze or partial transfer

**Draft added for review (never run as an implicit next step):** `IaC/ansible/playbooks/network-host-monitor01-preactivation-recover.yml`. This distinct emergency path addresses a freeze followed by an interrupted five-file transfer when monitor-01 may have zero, one, or several final files but has **never** been activated. It intentionally does **not** require the target alert registry, recipient or final-transfer backup to exist.

**Only after separate recovery approval:** verify all five target timers disabled and all destination services inactive; approval marker absent; collector unit has no alert post-hook or environment; no notifier process. Then verify the precise source freeze directory/change ID and the original eight systemd unit hashes, all five original frozen dataset/recipient SHA-256 values (including complete historical MAC alert registry), and that source timers and worker services remain inactive. Immediately recheck destination inactivity before restoring only source timers previously enabled and active at freeze. Preserve every partially transferred target file and any backups untouched for later reconciliation. No target restart, scan, notifier execution, deletion or file overwrite occurs during this recovery procedure.

**Out of scope / fail closed:** This path is not appropriate after any destination collector or email attempt, if the target cutover marker or notifier wiring exists, or if the source freeze never completed (e.g. no frozen data checksum manifest or partial timer stop). Such cases require separate manual investigation or the post-activation rollback with reconciled notification history. The usual rollback playbook intentionally refuses to resume source if the historical alert registry diverges.

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
3. **Draft added for review, NOT authorised/executed:** `network-host-monitor01-activate.yml` requires independent activation approval after verified Hold B. It checks original source isolation, complete five-file parity, preserved destination backup, exact notifier template, trusted guest snapshot and loaded refresh dependency; then it wires first-seen alerts, creates a protected cutover marker, refreshes guest identities, performs a single initial target collection and only then schedules discovery, refresh, enrichment and OS evidence. Deep Nmap profiling stays disabled. It stops at a provisional acceptance hold for notification and Grafana verification.
4. **Draft added for review, NOT authorised/executed:** `network-host-monitor01-rollback.yml` requires separate rollback approval, reads the exact protected source freeze manifest, disables/drains all five target timers and running workers, preserves complete post-target registry and fails closed if the target alert history differs from the original source registry. After a proven target drain and registry parity, it removes the target marker and restores only source timers recorded enabled/active before freeze. If new alerts occurred after activation, reconcile the complete delivered-alert history through a separately reviewed procedure; never blindly restore the source notifier. Offline structural tests and CI syntax checks have been added; independent interruption/recovery tests remain necessary.
5. Document the exact reviewed commit, approved operator/maintenance window, expected service state transitions, final evidence and post-cutover current-state update. No post-cutover claim until live verification.


## Disposable drill admission — no production side effects

The first executable drill preparation is `IaC/monitoring/drills/monitor01_disposable_preflight.py`. It is **read-only**: it SSHes into two already-created throwaway systemd VMs and checks expected `drill-source` / `drill-target` names, unique machine IDs, distinct lab-only addresses, no default route, no address or route to the production `192.168.2.0/24` network, and working systemd. Its fixed SSH commands collect only hostname, machine ID, interface addresses, routing and systemd version. It never executes migration playbooks, starts/stops services, copies data or sends messages.

Use a dedicated private Proxmox bridge without a physical uplink, no router/NAT, no mail-relay access and no direct LAN NIC on either disposable guest. Suggested lab range: `10.77.77.0/24` with `drill-source=10.77.77.11` and `drill-target=10.77.77.12`, but **do not assume these VMs exist**. Establish a separately approved, isolated controller path from `admin-01`; do not add a default route to the guests. Bootstrap known SSH host keys by separately verifying the VM console fingerprints, and use a disposable test key. Never put real MAC history, production `alerts.env`, production certificates, Proxmox API credentials or working SMTP destinations on test guests.

From the review worktree root:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 IaC/monitoring/drills/monitor01_disposable_preflight.py \\
  --source 10.77.77.11 --target 10.77.77.12 \\
  --user james --identity ~/.ssh/disposable-drill
```
Replace the sample addresses/key with actual test-only values after provisioning. If the admission fails, **stop**. The script deliberately does not substitute real hosts into production playbooks: their literal hostname/IP assertions must remain untouched, and an independent approved disposable-only adaptation and actual Ansible failure-injection exercise is still required. Record disposable VM IDs/hostnames, isolation evidence, controller reachability and the admission log before proceeding.

## Pre-production review and disposable-host evidence

The synthetic interruption suite `IaC/monitoring/tests/test_monitor01_interruption_scenarios.py` passed on 27 September 2026 against synthetic files and modelled state transitions. The last-moment exclusivity regression test also checks that all four Proxmox-2 source timers are rechecked **immediately before** the first active target collector invocation. These tests do not run Ansible against disposable hosts and do not prove live service drain, systemd ordering, SMTP suppression or rollback on a real machine.

**Required independent review and disposable pair drill before production approval:** use two isolated, deliberately non-LAN-connected disposable machines with synthetic MACs and an SMTP sink (never actual production recipients). Exercise the actual approval-gated Ansible phases with mock Proxmox API/guest data and deliberate failures: source stop during a oneshot; each of the five final-file copy boundaries; final SHA mismatch; stale guest map; notification wiring before marker; trusted refresh failure; interrupted initial collector; target alert history changing before rollback; and successful rollback with no new notifications. Collect actual timer/job statuses, private snapshot permissions, checksums, target inactive proof, synthetic notification sink counts, and source restoration evidence. Confirm the executable plays operate correctly with `hosts.yml` inventory mapped ONLY to the disposable pair and refuse accidental production addresses. No live-system manipulation or production-recipient email is permitted during the drill.

Before any real change, a reviewer other than the author must sign off the exact commit and the drill evidence, including recovery from a partial freeze where the frozen checksum manifest does not yet exist. **Existing pre-activation recovery requires a completed freeze manifest and intentionally cannot recover a partial source stop automatically; that remains a manual recovery case with separate approval.** Review the best-effort `ExecStartPost=-` semantics: collector service success does not prove SMTP delivery. The cutover owner must check the first-seen journal and relay delivery separately before marking migration accepted.

## Gate 4 execution — whole-network scan and installed-state evidence

Run the 27 September 2026 post-cutover network scan **from monitor-01** and managed-host audit **from admin-01** with the new read-only tools. The network scan explicitly probes the owned LAN `192.168.2.0/24` with Nmap host discovery and a **rate-limited, version-light selected-TCP-port probe**; it does not run NSE scripts, deep profiling, UDP sweeps or scan beyond the owned LAN. Review and obtain authorisation before widening scan scope or performing intensive vulnerability scans. Do not enable the dormant deep-profiler timer or rerun the migration.

Create a separate clean review worktree on `admin-01` at the latest validated Git commit, then from its repository root run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 IaC/monitoring/audits/postcutover_network_scan.py
```

The collector prints `EVIDENCE_DIRECTORY=/var/tmp/homelab-postcutover-audit-...`. Pass **that exact directory** to the following read-only Ansible facts playbook, then generate a conservative evidence-versus-inventory comparison:

```bash
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/postcutover-estate-evidence.yml \
  -e "audit_output_dir=/var/tmp/homelab-postcutover-audit-REPLACE_WITH_ACTUAL_TIMESTAMP"
cd ../..
PYTHONDONTWRITEBYTECODE=1 python3 IaC/monitoring/audits/compare_live_estate.py \
  /var/tmp/homelab-postcutover-audit-REPLACE_WITH_ACTUAL_TIMESTAMP
```

The evidence directory is mode 0700 and reports mode 0600; it contains IPs, observed MACs, open/listening ports and installed software versions, so never upload it to public Git. The runbook and JSON summary do **not** automatically rewrite production configuration or claim unknown hosts are down. Review SSH/Ansible recap for unreachable hosts, compare all observed packages, running services, containers, role declarations, ports, Proxmox placement, DNS, monitoring, backup schedules and actual restore evidence. Existing `CURRENT-STATE.md` historical pre-cutover paragraphs are clearly dated; compare against its current verified production section rather than historic plans. Record all gaps and evidence limitations in the Gate 4 drift register and propose a separate reviewed documentation-only PR.

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
