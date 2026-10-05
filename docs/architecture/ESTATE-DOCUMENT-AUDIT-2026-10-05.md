<!-- estate-authority: IaC/inventory/estate.json -->
# Estate Documentation Audit — 5 October 2026

**Status:** READ-ONLY AUDIT COMPLETE; REMEDIATION REQUIRED  
**Audit date:** 2026-10-05  
**Repository:** `jrwroberts1976/homelab-platform`  
**Audited branch baseline:** `main` at `23ad99d30748343386e65fdde357e2aa259582cb`

## Purpose

Audit the repository's human-facing operational documentation against the documented authority chain and the latest validated estate evidence. The audit does not authorise infrastructure changes and does not rewrite dated historical evidence merely because the live estate has moved on.

## Authority used

The repository's own authority policy is applied in this order:

1. validated live state;
2. `IaC/inventory/estate.json` for identity, address and lifecycle state;
3. `docs/architecture/CURRENT-STATE.md` for human current-state architecture;
4. Git-managed IaC for intended/deployed configuration;
5. production service docs and runbooks;
6. dated audits, migration records and historical evidence.

When a lower-authority document conflicts with a higher-authority source, the lower-authority document is considered stale.

## Canonical facts confirmed

The following current facts are consistent between the machine inventory, Ansible inventory, recent IaC and validated operator evidence:

### Managed Linux estate

There are 15 managed Linux systems:

| Host | IPv4 | Current role / placement |
|---|---:|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / IaC controller / SSH jump / Corosync QNetd |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT100 on `PROXMOX` |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT101 on `Proxmox-2` |
| `monitor-01` | `192.168.2.52` | Monitoring/logging and active network-discovery owner, VM202 on `Proxmox-2` |
| `cloud-01` | `192.168.2.53` | Nextcloud/PostgreSQL/Redis, VM200 on `PROXMOX` |
| `mail-relay-01` | `192.168.2.54` | Postfix relay, CT102 on `PROXMOX` |
| `sensor-01` | `192.168.2.55` | Suricata/Zeek passive sensor, VM201 on `PROXMOX` |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT103 on `Proxmox-2`; `cloudflared` absent |
| `greenbone-01` | `192.168.2.57` | Greenbone scanner, VM203 on `Proxmox-2` |
| `komodo-01` | `192.168.2.58` | Komodo Core control plane, CT104 on `PROXMOX` |
| `zabbix-01` | `192.168.2.59` | Zabbix platform, CT105 on `PROXMOX` |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` node 1 |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` node 2; former discovery source retained for rollback evidence |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint / primary Proxmox NFS backup target |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host |

`home-01` at `192.168.2.60` is also active as HAOS VM204 on `PROXMOX`, but it is intentionally outside the normal 15-host Ansible-managed Linux baseline.

### Proxmox cluster

- cluster name: `jameshouse-pve`;
- nodes: `PROXMOX` and `Proxmox-2`;
- preferred Corosync link0: `10.255.255.1/30` ↔ `10.255.255.2/30`;
- management-LAN link1 is the fallback;
- `admin-01` supplies QNetd/QDevice third vote;
- latest 5 October maintenance evidence: both PVE nodes at pve-manager 9.2.21 with running kernel `7.0.14-20-pve`;
- production guest placement is CT100/102/104/105 and VM200/201/204 on `PROXMOX`; CT101/103 and VM202/203 on `Proxmox-2`.

### Network discovery

The 27 September cutover is complete. `monitor-01` is the sole active owner of the collector, selective enricher, OS-evidence publisher, Proxmox guest refresh and first-seen notifier. `Proxmox-2` is the former source; source discovery timers are disabled/inactive and retained state is rollback/history evidence.

### DNS

The active resolver pair is:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

`admin-01` at `.48` is not a resolver. Current DNS IaC contains both `dns-01.jameshouse` and `dns-02.jameshouse` in the managed local-host set, so the older documented cross-resolver parity defect is no longer current.

### Monitoring and patching

- Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki run on `monitor-01`;
- the managed Linux estate contains 15 reporting Node Exporter/Zabbix Agent targets;
- Step 10 estate-wide Grafana overview is complete;
- current production dashboards include Home/operations, Hosts, Patch & Reboot Status, Node Detail links and network-host views;
- final patch telemetry after the 5 October controlled maintenance cycle was `15 reporting / 0 pending / 0 security / 0 reboot / 15 unattended-upgrades installed / 0 automatic reboot`;
- repeat monitoring deployment completed idempotently with `changed=0`, `failed=0`, `unreachable=0`.

### Backup state

The current scheduled Proxmox selections are:

```text
PROXMOX:   100,102,104,105,200,201,204
Proxmox-2: 101,103,202,203
```

CT105 and VM203 unattended evidence has been observed. CT104 and VM204 still require explicit first-unattended-run proof in the current evidence set. The primary NFS backup platform is operational; a representative QEMU restore, application-consistent `cloud-01` recovery and an independent second copy remain open.

### Security / access boundaries

- `sensor-01` capture is operational; Suricata and Zeek are active;
- switch port 24 is now the SPAN destination for ports 1–23;
- Greenbone is operational and integrated into the scheduled evidence/reporting workflow;
- router-hosted OpenVPN is the accepted production remote-access path;
- `cloudflared` is not deployed on `edge-01`;
- Authelia is not part of the current deployed architecture;
- CrowdSec must not be described as a currently deployed signal source unless it is reintroduced and validated.

## Current documents that require correction

### P0 — canonical/current-state contradictions

#### `docs/architecture/CURRENT-STATE.md`

The top active-estate section correctly records `monitor-01` as the active discovery owner, but a later pre-cutover section still says no source stop/cutover has occurred and that `Proxmox-2` remains the production owner. This is an internal contradiction in the canonical human current-state document.

Required remediation:

- clearly move/bracket the old Gate 2/Gate 3a material as historical staging evidence;
- add the verified 27 September cutover outcome before it;
- update the document review horizon through 5 October;
- add latest PVE maintenance versions as a dated later validation rather than rewriting the 17 September evidence;
- record the Step 10 Grafana/patch steady state.

#### `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md`

Current file still reports the 2 October patch cycle as `CURRENT FOCUS`, is last reconciled 23 September and ends delivery progress at Step 9 with Step 10 next.

Required remediation:

- mark the patch override COMPLETE/closed with final telemetry;
- add Step 10 COMPLETE with PRs #179, #180 and #181 plus visual validation/idempotence evidence;
- record Step 10 completion-notification status accurately rather than assuming it was sent;
- set this 5 October documentation audit to IN PROGRESS/REMEDIATION;
- separate the completed Grafana-estate foundation from remaining Project #3 AI-host-intelligence work;
- remove/qualify CrowdSec from current-source wording because it is not currently deployed.

### P1 — current architecture/planning documents

#### `docs/migrations/MIGRATION-TRACKER.md`

Stale current-looking statements include:

- network-discovery migration `IN PROGRESS` / cutover `NOT complete`;
- `Proxmox-2` described as current Network Host Collector;
- guest placement omits CT104, CT105, VM203 and VM204;
- monitoring section still describes the 26 September staging state as present operation;
- Jenkins retirement remains listed even though Jenkins is already removed;
- Komodo onboarding is still presented as future work after Periphery commissioning on managed Docker hosts.

#### `docs/architecture/TARGET-STATE.md`

Completed work still appears as future/current baseline:

- Network Host Collector claimed active on `Proxmox-2` only;
- `PROXMOX` backup set omits VM204;
- first unattended CT105/VM203 evidence is described as pending;
- Periphery onboarding is still broadly future work;
- Greenbone scan/evidence/report integration is described as not yet enabled even though it is operational.

#### `docs/architecture/INSTALLED-SOLUTIONS-CATALOGUE.md`

The catalogue still places Network Host Collector on `Proxmox-2`. It should place active discovery on `monitor-01` and distinguish the retained Proxmox-2 rollback state. Review Komodo Periphery and current patch/dashboard components at the same time.

#### `README.md`

The core estate table is largely correct, but later narrative still says:

- Komodo Periphery onboarding remains later work;
- Greenbone scheduled evidence/report pipeline is still being validated before enablement;
- some Network Hosts AI/manual/persistent-page stages remain future even though persisted generated host pages and AI assessment are live.

#### `IaC/README.md`

The top warning still says network discovery remains on `Proxmox-2` and the managed-estate table calls `Proxmox-2` the current Network Host Collector until migration. This contradicts the canonical inventory and 27 September cutover.

#### `IaC/ansible/README.md`

Stale statements include:

- DNS local-record parity defect that current DNS IaC has already corrected;
- Periphery onboarding still presented as future work.

### P1 — current hardware records

#### `docs/hardware/PROXMOX.md`

This is titled `Current Hardware Record` but still says:

- Proxmox 9.2.11 / kernel 7.0.14-15;
- standalone by design;
- old guest placement without CT104/CT105/VM204;
- sensor capture is future;
- zero scheduled PVE backup jobs.

All of those current-state claims are obsolete.

#### `docs/hardware/Proxmox-2.md`

This is titled current but still says:

- `ACTIVE — STANDALONE PROXMOX NODE`;
- Proxmox 9.2.2 / kernel 7.0.2-6;
- monitor-01 is VM200 rather than VM202;
- VM203 is absent;
- Alloy inactive;
- no scheduled backup job.

These are obsolete current-state claims.

#### `docs/hardware/admin-01.md`

Role/address/OS are correct, but the page omits the active Corosync QNetd role and records the pre-maintenance kernel 6.18.39 rather than the 5 October running 6.18.50 kernel.

#### `docs/hardware/media-01.md`

The identity is sound, but the page still says Alloy/Loki logging is future and does not treat the Proxmox NFS backup target as part of the primary role. Production service documentation already supersedes those statements.

#### `docs/hardware/docker-01.md`

Komodo commissioning is already documented correctly. The remaining stale statement is the historical claim that no estate-wide backup platform exists; this should be narrowed to the real unresolved issue: BirdNET persistent data lacks an independent application-data protection/restore proof. Latest kernel/package observations should be recorded only as dated evidence.

### P1 — production runbooks/service documents

#### `production docs/MONITORING-SERVICE.md`

Stale:

- monitor-01 placement VM200 instead of VM202;
- `Proxmox-2` described as standalone;
- Alloy 1.19.2 observation is superseded by the 5 October 1.20.1 maintenance state;
- active monitor-01 discovery ownership and Step 10 dashboards are absent.

#### `production docs/PROXMOX-BACKUP-RECOVERY.md`

Stale:

- status says first unattended CT105/VM203 runs pending;
- current scope/schedule omits VM204;
- manual `vzdump` example omits VM204;
- VM203 pending coverage gap should be replaced with CT104/VM204 evidence gaps.

`docs/architecture/BACKUP-STRATEGY.md` already contains the more current facts and should be used as the reconciliation source.

#### `production docs/GREENBONE-SERVICE.md`

Stale:

- first unattended VM203 run remains pending;
- Alloy 1.19.2 version evidence is old;
- current daily managed scan, evidence transfer and management-report integration are not reflected.

#### `production docs/NETWORK-SENSOR-SERVICE.md`

Architecture is still correct. Version observations are stale after 5 October maintenance: Suricata was validated live at 8.0.7 and Alloy at 1.20.1. Treat these as dated observations, not permanent pins.

#### `production docs/BIRDNET-SERVICE.md`

The claim that the estate has no active production backup platform is obsolete. The actual BirdNET-specific gap is persistent application data protection/restore. Komodo management should be acknowledged.

#### `production docs/MEDIA-SERVICE.md`

Backup architecture is broadly correct, but text referring to the two PVE nodes as `standalone` is obsolete. Alloy version observations are dated and should not be presented as latest after the 5 October patch cycle.

#### `production docs/DNS-SERVICE-RECOVERY-PLAN.md`

The `Known local-record parity defect` is obsolete. Current DNS IaC contains both resolver cross-records. Preserve the defect only as dated history if useful.

### P1 — runbook catalogue / machine-readable registry

#### `runbooks/README.md`

Stale:

- VPN service state still says implementation in progress despite production acceptance on 18 September;
- VM203 unattended backup still shown pending;
- coverage gaps repeat those old states.

#### `runbooks/registry.yml`

Stale machine-readable data includes:

- `remote_access_vpn.service_state: implementation_in_progress`;
- internal admin/DNS acceptance still marked pending after VPN production acceptance;
- monitoring target list omits several current managed Linux hosts;
- `PROXMOX` backup guest list is only `[100,102,200,201]`, missing CT104, CT105 and VM204;
- first unattended VM203 run still pending;
- backup coverage gap still centred on VM203 rather than CT104/VM204.

The registry also has incomplete service coverage relative to current production documentation: Greenbone, Zabbix, Home Assistant and Komodo are not represented as full operational runbook entries.

### P2 — network/operations documentation

#### `docs/network/SWITCH-PORT-MAP.md`

This is a valid 12 September evidence snapshot but its status wording can mislead because it says port mirroring is disabled and port 24 is the router uplink, while current architecture has port 24 as the active SPAN destination. Keep the old table as historical evidence but add a prominent superseded/current-state pointer.

#### `docs/operations/grafana-production-dashboards.md`

Production dashboard documentation predates the Step 10 patch dashboard. Reconcile it with the currently provisioned Home, Hosts and Patch & Reboot Status dashboards and the operational Node Detail navigation.

#### `docs/operations/unknown-device-reconciliation.md`

Some AI/manual/persistent GitHub host-page stages are still described as future even though generated host pages with persisted AI assessment are already present. Update the implementation-state boundary without rewriting dated evidence.

### P3 — generated network host pages

`docs/network/hosts/` is generated output and should not be manually normalised page by page. Generated records can intentionally contain dated evidence from different collection times. For example, an AI assessment may be older than a newer patch section. The generator should make evidence timestamps/staleness obvious and refresh according to the documented schedule. Audit generator/source logic rather than hand-editing generated host facts.

## Documents confirmed as deliberately historical or point-in-time

The following should generally **not** be rewritten to today's state merely because they contain old versions/placements:

- `docs/architecture/ESTATE-AUDIT-2026-09-14.md`;
- `docs/architecture/ESTATE-DOCUMENT-AUDIT-2026-09-16.md`;
- `docs/architecture/ESTATE-APPLICATION-AUDIT-2026-09-17.md`;
- `docs/architecture/MANAGEMENT-REPORT-EVIDENCE-2026-09-20.md`;
- `docs/architecture/NETWORK-OBSERVABILITY-CLOSEOUT-2026-09-14.md`;
- `docs/architecture/PATCH-CYCLE-CLOSEOUT-2026-09-14.md`;
- `docs/hardware/PVE2-HARDWARE-AUDIT-2026-09-08.md`;
- `docs/hardware/TestServer.md` where it is explicitly historical/retired;
- `docs/hardware/ids-01.md` where it is explicitly decommissioned;
- `docs/architecture/PROPOSED-LAYOUT.md`, which is explicitly marked superseded/historical;
- `docs/architecture/PROXMOX-CLUSTER-REBUILD-PLAN.md`, which is an implementation record rather than the current placement authority;
- completed migration/cutover evidence sections that are explicitly labelled historical.

Historical files may need only a clearer `superseded/current authority` banner if a reader could reasonably mistake them for active instructions.

## Documents currently in good shape

The following were found materially aligned with current architecture for their stated scope:

- `IaC/inventory/estate.json` — canonical identity/addressing/role inventory;
- `docs/architecture/DOCUMENT-AUTHORITY.md` — authority model;
- `docs/architecture/BACKUP-STRATEGY.md` — current backup sets/evidence and remaining CT104/VM204 gaps;
- `docs/architecture/HOME-AUTOMATION-DESIGN.md` — home-01 active state and remaining backup/monitoring work;
- `docs/network/VPN-REMOTE-ACCESS-DESIGN.md` — production OpenVPN acceptance and maintenance boundaries;
- `docs/operations/network-discovery-monitor01-migration.md` — current cutover header plus clearly historical staging evidence;
- `docs/operations/network-device-identification.md` — current monitor-01 ownership/evidence boundaries;
- `docs/operations/grafana-network-hosts.md` — current monitor-01 dashboard/discovery ownership, with historical sections labelled as such;
- `docs/architecture/STEP-10-ESTATE-GRAFANA-CLOSURE-2026-10-05.md` — Step 10 deployment/patch/idempotence evidence (add final visual `now-24h -> now` validation on next edit).

## Remediation order

### Phase A — authority and operator-safety documents

Update together first:

1. `CURRENT-STATE.md`;
2. `ACTIVE-INFRASTRUCTURE-BACKLOG.md`;
3. root `README.md`;
4. `TARGET-STATE.md`;
5. `INSTALLED-SOLUTIONS-CATALOGUE.md`;
6. `MIGRATION-TRACKER.md`;
7. `IaC/README.md`;
8. `IaC/ansible/README.md`;
9. `runbooks/README.md` and `runbooks/registry.yml`;
10. DNS recovery and Grafana production-dashboard docs.

These files can cause an operator to make the wrong decision today, so they take precedence over version-only refreshes.

### Phase B — hardware and service records

Reconcile:

- both Proxmox hardware records;
- admin/media/docker hardware pages;
- monitoring, backup/recovery, Greenbone, sensor, BirdNET and media production docs;
- switch map status banner/current-state pointer.

Preserve dated measurements as evidence while adding a newer validation section; do not silently rewrite old observations as if they were measured on 5 October.

### Phase C — generated documentation and CI

- make generated host-page evidence age/staleness explicit;
- verify the generator uses current `homelab_patch_*` metrics everywhere;
- extend documentation validation so current-looking docs cannot reintroduce retired discovery ownership, standalone-cluster language, stale VMIDs or retired patch metric names;
- add checks for the current backup guest sets and network-discovery owner where practical.

## Audit conclusion

The core infrastructure facts are recoverable and coherent because the canonical inventory, recent IaC and newest network/backup documentation agree. The repository as a whole is **not yet factually reconciled** because multiple files labelled `current`, `production` or operational contain superseded September state.

The highest operational risk is not missing data; it is conflicting data. The remediation should therefore update current-authority/operator documents first, preserve dated historical evidence, and add validation that prevents the same classes of drift from returning.
