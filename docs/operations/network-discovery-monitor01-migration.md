<!-- estate-authority: IaC/inventory/estate.json -->
# Proposed: make monitor-01 the sole network-discovery and OS-investigation host

**Status as of 26 September 2026: Gate 1 preflight passed on both hosts;
Gate 2 staged and verified on monitor-01 with matching SHA-256 for all
three JSON files and eight recovered OS matches. The production collector
and enricher still run on Proxmox-2; monitor-01 scanning remains disabled.**
The authoritative present-tense inventory remains
[`docs/architecture/CURRENT-STATE.md`](../architecture/CURRENT-STATE.md)
until the live handover has been verified. Current collector and saved
deep-profile data are still on Proxmox-2. Grafana, Prometheus, OS
correlation and generated individual host dashboards already run on
monitor-01. The goal is to make **monitor-01** own the entire pipeline.

## Target architecture

```text
                       monitor-01 (VM202, eth0, 192.168.2.52)
ASUS DHCP/ARP hints ──>  network discovery and controlled Nmap profiling
                        │
                        ├── MAC-keyed inventory / preserved deep-profile state
                        ├── targeted service/TLS enrichment
                        ├── read-only saved OS-fingerprint publisher
                        ├── existing Node Exporter → Prometheus
                        └── existing Grafana and 50 individual host pages

admin-01: Ansible deployment controller only
Proxmox-2: historic source / protected migration snapshot only after cutover
```

After the **verified** cutover, Proxmox-2 remains an ordinary monitored
Proxmox host. It no longer collects network inventory, runs network
enrichment/deep profiling, or publishes per-device discovery/OS fingerprint
textfiles. Its ordinary Proxmox/node-exporter monitoring is unaffected.

`admin-01` remains the Ansible deployment controller, **not** a runtime
scanning or data-processing host.

## Gate 1: read-only preflight (safe to run now)

Use a clean checkout of the reviewed preflight commit, not an old deployment
worktree. The playbook reads Proxmox-2's existing source state **once**,
reports only counts/hashes and timer statuses, and checks monitor-01's LAN
route, actual network interface, Nmap availability, target state collision,
existing Docker stack and Node Exporter directory. It does not make changes.

```bash
REPO=/home/james/projects/homelab-platform
DEPLOY=/var/tmp/network-monitor01-preflight
git -C "$REPO" fetch origin main
git -C "$REPO" worktree add --detach "$DEPLOY" origin/main
cd "$DEPLOY/IaC/ansible"
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-monitor01-preflight.yml --syntax-check
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-monitor01-preflight.yml
```

Do not assume Proxmox-2's `vmbr0` is monitor-01's interface: this is a VM,
with a separate virtual NIC. Nmap source interface and its raw-socket/ARP
behaviour must be validated on monitor-01 before a single scan runs.
Existing access from monitor-01 to the ASUS router uses the already
commissioned router-only SSH key; do **not** copy the Proxmox host's SSH
secrets or change the router account.

**Gate 1 actually completed on 26 September 2026, unchanged on both
hosts** (`Proxmox-2: 6 ok / 0 changed`, `monitor-01: 9 ok / 0 changed`):

| Preflight finding | Verified result |
|---|---|
| Proxmox-2 current inventory | 49 device records |
| Deep profiles | 35 baseline, 13 complete, 1 pending |
| Existing TCP evidence | 13 profiles, 8 with Nmap OS matches |
| Evidence time | 0 newer TCP-scan timestamps; 13 legacy timestamp records |
| Proxmox-2 collector / enrichment timers | Enabled |
| Proxmox-2 deep profiler timer | Disabled |
| Proxmox-2 read-only Nmap evidence publisher | Enabled |
| monitor-01 gateway route | `192.168.2.1 dev eth0 src 192.168.2.52` |
| monitor-01 Nmap | Already installed |
| monitor-01 discovery, enrichment, profiler, OS-publisher timers | Not installed yet |
| monitor-01 inventory and dashboard timers | Enabled |
| Existing target migration state files | None (three root-only files may be staged) |

These results are the migration baseline, **not** evidence that scanner
ownership has changed. The September 24 quick TCP/ARP baseline run on
monitor-01 is separate from Proxmox-2's saved deep-profiler state.

## Gate 2: completed — protected staging without starting new scans

**Historical staging commands below are retained for audit only. Do not
rerun them against the now-populated monitor-01 target.**

Use `IaC/ansible/playbooks/network-host-monitor01-stage.yml`, introduced
in the staging PR. It has two gated plays:

1. On **Proxmox-2**, make a root-only timestamped snapshot under
   `/var/backups/homelab-network-migration/`, check SHA-256 of all
   three files both before and after copying, and reject concurrent
   changes. The live collector and enricher keep running.
2. Transfer that snapshot to **monitor-01** only through the existing
   encrypted Ansible connection, explicitly refusing pre-existing
   target files. Verify matching SHA-256 for inventory, deep profiles
   and enrichment state.
3. Install the three existing worker roles against monitor-01's verified
   `eth0` NIC, with **all scan timers disabled**. Install the compatible
   read-only Nmap fingerprint exporter and run it once. Its timer is
   **also disabled** until the single-owner cutover. The staging play
   expects the eight historical OS matches found by Gate 1.
4. Do **not** update live Grafana, replace its existing inventory
   publisher, change Proxmox-2 schedules or start any new scans in
   the staging play. The 50 generated host pages remain on monitor-01.

Run from admin-01 after merging the staging PR, in a **fresh worktree**,
not `/var/tmp/network-monitor01-preflight` or earlier OS worktrees:

```bash
REPO=/home/james/projects/homelab-platform
DEPLOY=/var/tmp/network-monitor01-stage
git -C "$REPO" fetch origin main
git -C "$REPO" worktree add --detach "$DEPLOY" origin/main
cd "$DEPLOY/IaC/ansible"
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-monitor01-stage.yml --syntax-check
ansible-playbook -i inventory/hosts.yml \
  playbooks/network-host-monitor01-stage.yml
```

**If any checksum changes or a target file is already present, STOP.**
Snapshots remain protected, and the original source continues serving
production. Do not automatically rerun after a partial transfer; inspect
the target hashes against the saved source snapshot.

### Verified guest identity and first-seen prerequisites (26 September 2026)

The original zero/zero `find` results on Proxmox-2 were misleading:
`/etc/pve/qemu-server` and `/etc/pve/lxc` are **symlinks**
into `nodes/Proxmox-2/`, so the initial check without `find -L`
did not traverse them. The corrected read-only check found **two local
QEMU VM configurations and two local LXC configurations**. The Proxmox
cluster resource API reported **13 guests/resources across both nodes**:
six running LXC containers, five running VMs and two stopped VM
templates. Only four of the running guests are local to Proxmox-2
(`dns-01`, `edge-01`, `monitor-01`, `greenbone-01`).

The existing enrichment worker uses host-local `/etc/pve` configuration
paths. Those symlinks provide *local-node* guest identities; copying
the worker into monitor-01's VM will not expose either Proxmox node's
configuration. Gate 3 therefore requires an **authorised, read-only
cluster-wide Proxmox API** lookup from monitor-01 (or a controlled
minimised export) that includes guest NIC MAC addresses, VMID, type,
node and name. Merely reading `/cluster/resources --type vm` is
insufficient for MAC-based enrichment: per-guest configuration lookup
and scoped API access must also be proven. Do not mount `/etc/pve`
on the monitoring VM or copy Proxmox host credentials to it.

The existing source first-seen notification configuration and registry
were also verified **present, root-owned and mode 0600**:
`/etc/homelab-network-hosts/alerts.env` and
`/var/lib/homelab-network-hosts/alerted-macs.json`.
Their presence does **not** prove monitor-01's recipient, SMTP path or
last-alert state is ready; protect the original files and synchronise
their current contents only at the final cutover. Verify a single
intentional test notification before disabling the old alert path.

### Read-only Proxmox API authentication verified (26 September 2026)

From `monitor-01`, a dedicated privilege-separated Proxmox token was
accepted by **both** Proxmox API endpoints (`192.168.2.70:8006` and
`192.168.2.71:8006`). Authenticated cluster resource requests returned
**HTTP 200 and 13 visible resources from each endpoint**. Individual
read-only configuration requests for `cloud-01` (QEMU VM 200 on
`PROXMOX`) and `dns-01` (LXC 101 on `Proxmox-2`) both returned
**HTTP 200 and one network interface**. The access issue was resolved by
assigning the required `VM.Audit` permission at `/vms` to both the
user and its privilege-separated token.

The manually stored token is on `monitor-01`, outside Git and not yet
wired into the staged enricher. Initial token diagnostics bypassed TLS;
subsequent Gate 2b successfully verified the certificate chain and
both requested API IP addresses using the independently authenticated
PVE cluster CA. No service
or timer has been activated. Do not expose token values in playbooks,
GitHub, logs or troubleshooting output. The old enricher remains active
on `Proxmox-2` and still reads host-local guest configuration.

### TLS certificate evidence and trusted-CA gate (26 September 2026)

Both PVE API nodes served valid-dated node certificates issued by the same
named PVE Cluster Manager CA. The presented `PROXMOX.jameshouse`
certificate covers `192.168.2.70`, `PROXMOX` and its FQDN and expires
7 September 2028; `Proxmox-2.jameshouse` covers `192.168.2.71`,
`Proxmox-2` and its FQDN and expires 12 September 2028.
Both hostnames also resolved correctly from monitor-01. These observations
were made using diagnostic OpenSSL inspection and **do not yet constitute
verified TLS certificate-chain trust**.

The separate `playbooks/network-host-monitor01-proxmox-tls.yml` gate
must run **from admin-01**, which already has authorised Ansible SSH
access to both PVE nodes. It reads each node's public
`/etc/pve/pve-root-ca.pem` over authenticated SSH, verifies the CA
basic constraint and expiry, requires both nodes to return **identical
CA bytes**, then installs the public cluster CA on monitor-01 as
`/etc/homelab-network-hosts/proxmox-ca.pem`. A preexisting different
destination CA causes a hard stop. It performs strict Python TLS
chain and requested-IP SAN verification on **both** nodes, using the
existing root-only `proxmox-api.env` credential only in monitor-01
memory. It requests both cluster inventories and two sample guest
configurations but never outputs token data or raw guest records.

The CA and strict-TLS playbook **PASSED on live hosts on
26 September 2026**, with `PROXMOX: 9 OK / 0 changed`,
`Proxmox-2: 9 OK / 0 changed`, and `monitor-01: 10 OK / 1 changed`;
zero failed or unreachable. Both independently retrieved CA hashes
matched, and monitor-01 now has the public CA at
`/etc/homelab-network-hosts/proxmox-ca.pem`. Its strict-TLS API
checks returned HTTP 200 with 13 visible resources on **each** PVE
node; the cloud-01 VM and dns-01 LXC config checks returned HTTP 200
with one NIC apiece. Do **not** rerun the non-overwrite Gate 2 staging
playbook. A successful gate does **not** enable the scan workers or
switch the production Grafana source.

### Gate 2c: verified read-only Proxmox MAC discovery (PASSED)

With trusted TLS proven, use
`playbooks/network-host-monitor01-proxmox-guests-check.yml` to install
and execute **only** a no-write guest MAC preflight on monitor-01.
The gate verifies the three preserved original JSON files and the
root-only API token, confirms all four new worker timers are still
disabled/inactive, and uses the verified local cluster CA for all API
requests. It reads and reconciles the resource lists from both PVE
nodes and then reads *each guest's actual network configuration* on
its owning node. It parses QEMU and LXC NIC MACs, excludes reusable
templates, refuses ambiguous/colliding live MAC identities, and prints
**aggregate counts only**, not token data or private MACs.

The preflight did **not** modify current inventory, deep profiles,
enrichment, first-seen alert state, existing Grafana source or
production services. The **26 September 2026 live Gate 2c run passed**:
`monitor-01: 15 OK / 1 changed / 0 failed`. It verified all four
new worker timers **disabled and inactive**, used the trusted cluster
CA to inspect **all 13** resource configurations (**9 on PROXMOX,
4 on Proxmox-2**), identified **11 running guests**, excluded
**two templates** and found **11 unique non-template guest MACs**.
The isolated probe executable was installed; **no Nmap ran**, and no
production state, alert registry or inventory was rewritten.

### Gate 2d: protected guest MAC snapshot (PASSED 26 September 2026)

The new
`playbooks/network-host-monitor01-proxmox-snapshot.yml`
requires the proven Gate 2c baseline and uses the same strictly verified
TLS credentials to compare the fresh 11 guest MACs against the **saved
LAN inventory**. It publishes a **separate, new root-only**
`/var/lib/homelab-network-hosts/proxmox-guests.json` containing
MAC-keyed guest identities only after a no-write dry-run passes.
It never overwrites an existing file, never touches the three original
staged JSON files, does not modify production Grafana, and refuses
to run with any of the four new timers active. Output consists only
of counts and a checksum; token secrets and raw MAC data stay local.
**Do not rerun this one-shot gate if a partial execution has created
the new snapshot.**

**Verified live outcome:** the Gate 2d playbook returned `monitor-01: 18 OK / 2 changed / 0 failed` on 26 September 2026. The publisher and protected snapshot creation steps completed without task failures. The independent root-only aggregate read-back subsequently verified **11 guest MACs, 49 saved LAN devices, 11 matches, zero unmatched** and snapshot mode **0600**. **Do not rerun Gate 2d**, because the protected guest-map file already exists.

The verified new snapshot is a *candidate enrichment input*, not a
production integration. The original Proxmox-2 `/etc/pve` local-file
lookup remains the role's default. Neither service scanning nor
worker timer activation occurred at Gate 2d.

### Gate 2e: opt in the inactive monitor-01 worker (PASSED 26 September 2026)

`playbooks/network-host-monitor01-proxmox-identity-stage.yml` has a
one-time guarded install for **monitor-01 only**. It requires all four
staged worker timers disabled/inactive and the existing enrichment
service inactive. It verifies and protects the SHA-256 of original
`inventory.json`, `deep-profiles.json`, `enrichment.json` and
`proxmox-guests.json`, retains a private rollback copy of the
original inert worker executable, then installs a strict root-only
snapshot reader. The worker's source is set to `snapshot` for this
staged VM only; the existing role default remains `local` on PVE2.

The gate runs `--identity-check` on the newly installed script.
That mode exits **before all Nmap/service/TLS probes**, before writing
inventory, enrichment, Prometheus metrics or guest state, and without
any Proxmox API credential. It must report the known 11-of-11 matched
MAC baseline and zero unmatched and verify all four original state
file hashes stayed identical. It **does not** start the enrichment
service, systemd timers, discovery, Grafana or first-seen notifier.

Snapshot age is currently limited to 48 hours to prevent use of
stale Proxmox ownership metadata. If the protected candidate snapshot
is older, the check will fail closed; establish a separate protected
API snapshot refresh path before enabling periodic enrichment.
**Do not rerun this one-time gate after a partial installation**:
the script and rollback file are collision-protected.

Gate 2e **passed live** with `monitor-01: 27 OK / 5 changed / 0 failed`. The no-scan identity check matched all **11** guest MACs against the **49** preserved LAN devices, with zero unmatched and a 1,800-second-old snapshot. All four protected JSON files remained unchanged, the original inactive worker was backed up, all four target timers stayed disabled, and no source collector, Grafana dashboard or notification was altered. Do not rerun the one-shot Gate 2e.


### Gate 2f: safeguarded guest snapshot refresh (PASSED 26 September 2026)

The new `playbooks/network-host-monitor01-proxmox-refresh-stage.yml`
is a separate, one-time test for safely updating the existing
`proxmox-guests.json`. It requires all four staged timers disabled and
the enricher inactive. It checks installed API publisher/reader source
hashes, protected token and verified CA, performs an authenticated
strict-TLS no-write dry run and requires the previously established
11-of-11 guest/LAN association.

The refresher uses an exclusive lock, checks both Proxmox API nodes and
guest NIC configurations, validates all new identities, and refuses
unexpected large visibility reductions. Before atomic replacement of
the guest map, it saves the original bytes under a SHA-256 filename in
a root-only backup directory. On API or validation failure the original
snapshot remains intact. The gate verifies that the inactive
`--identity-check` still reports all 11 matches and that the other
three preserved JSON files remain byte-identical. It neither runs Nmap
nor enables any worker timer, starts enrichment, changes production
Grafana or touches the active Proxmox-2 collector/notifier.

**26 September first Gate 2f attempt stopped safely at the pre-mutation
hash gate** (`monitor-01: 8 OK / 0 changed / 1 failed`). The
controller's Ansible `lookup('file', publisher_source)` used default
trailing-whitespace trimming, so it hashed fewer source bytes than
`ansible.builtin.copy` originally installed. The publisher's
reviewed Git file has not changed since Gate 2d and ends in a newline.
The same issue would affect the helper comparison. The repaired gate
uses `lookup('file', ..., rstrip=False)` for both and CI explicitly
checks both expressions. No refresher, backup directory, service or
timer was installed by the failed attempt. Retry only the reviewed
corrected Gate 2f playbook from a fresh post-fix commit, retaining the
original no-overwrite prerequisites. If either corrected hash still
differs, stop and inspect the target rather than bypassing the guard.

The **corrected Gate 2f live deployment PASSED**:
`monitor-01: 24 OK / 3 changed / 0 failed`. Authenticated strict-TLS
APIs refreshed **11** Proxmox MAC identities and matched **all 11**
against the **49** saved LAN records. The prior guest snapshot is
protected in the root-only SHA-256-named backup
(`baccc1106114302d1ab5cc116716d39eeeb08e15faa23921b9a0423d234c97e0`).
The new snapshot is root-owned mode 0600 and was **three seconds old**
at validation. All three original migration JSON files retained their
exact SHA-256 hashes. The four staged scanner, enrichment and
OS-publisher timers stayed disabled. No Grafana, notification registry
or original Proxmox-2 collector was changed. **Do not rerun Gate 2f.**

### Gate 2g: disabled snapshot-refresh units (PASSED 26 September 2026)

`playbooks/network-host-monitor01-refresh-units-stage.yml` is a
separate, one-time, monitor-01-only staging gate. It refuses changed
reviewed publisher, reader or refresher hashes; pre-existing units,
wrapper or approval marker; active/inactive worker mismatches; or
protected dataset changes. It installs an isolated root-only Bash
wrapper that sources the existing root-only token **inside the process**,
a hardened `homelab-proxmox-guest-refresh.service`, a
`homelab-proxmox-guest-refresh.timer` that remains **disabled**,
and a scoped drop-in on the inactive enrichment service.

The drop-in requires a successful trusted-API guest refresh to finish
*before* future enrichment starts and has
`ConditionPathExists=/etc/homelab-network-hosts/network-discovery-cutover-approved`.
The approval file must **not** exist during staging; it is reserved
for a later controlled cutover after stopping the source and final
state reconciliation. The gate reloads unit definitions only and
verifies all new and original timers remain disabled/inactive.
No refresh is executed, no Nmap is started and no alerts or Grafana
sources are changed. Do not rerun this stage if it partially installs
any files; inspect installed units and original hashes first.

**Verified live result:** Gate 2g returned `monitor-01: 35 OK /
5 changed / 0 failed`. The new six-hour refresh timer and all four
preexisting staged worker timers remain disabled and inactive; the
inactive enrichment service is guarded by the cutover approval marker
and a successful trusted refresh dependency. No Nmap scan, refresh run,
email notification, Grafana modification or source collector change
occurred. **Do not rerun this one-shot staging playbook.**

### Gate 2h: first-seen notification readiness (PASSED 26 September 2026)

`playbooks/network-host-monitor01-firstseen-preflight.yml` is
**read-only on both hosts**. On Proxmox-2 it verifies the existing
root-only `alerts.env` and `alerted-macs.json`, the installed notifier
and original collector post-hook, and reports only aggregate baseline,
alerted, new-device and pending-online counts. It confirms the source
collector's timer is still enabled; it **does not** print the recipient
or individual MACs and does not send a test email.

On monitor-01 it verifies that no target alerts.env, alert registry,
notifier or cutover approval marker was prematurely created, that all
**five** staged discovery and refresh timers remain disabled/inactive,
that the inactive enrichment service has its cutover-marker/refresh
safety dependencies, and that internal SMTP relay `192.168.2.54:25`
accepts one TCP connection without sending mail. It neither copies
credentials nor mutates state. A failure blocks the final source stop;
investigate any outstanding first-seen notifications before transfer.

**Verified live result:** Gate 2h returned `Proxmox-2: 9 OK /
0 changed / 0 failed` and `monitor-01: 11 OK / 0 changed /
0 failed`. The source notifier, protected registry/configuration
and scheduled collector passed validation. Monitor-01 had no first-seen
config, registry, notifier or cutover marker; all five timers were
disabled/inactive; SMTP TCP/25 was reachable without sending mail;
the staged enrichment cutover/refresh safeguards passed. A 27 September 2026 repeat source-only preflight passed: Proxmox-2 9 OK, 0 changed, 0 failed. At that time the source registry had 49 known MACs (40 baseline, 9 alerted, 0 other), while the source inventory had 49 device records and 48 distinct MACs. No inventoried MACs were missing from the registry and there were zero pending online first-seen messages. The three checked source timers were enabled. At final cutover, preserve the entire historical 49-entry alert registry rather than reconstructing it from the smaller current unique-MAC inventory. Recheck the figures after stopping the source because these counts are only a point-in-time measurement.

### Gate 2i: notifier staging encountered a pre-existing target script (27 September 2026)

`playbooks/network-host-monitor01-firstseen-notifier-stage.yml`
runs on **monitor-01 only**. It parameterises the notifier's collector
identity (the default remains `Proxmox-2` for the active source)
and installs the destination script as root-owned, mode 0750,
without executing it. The gate requires the destination recipient,
MAC registry, notifier and cutover marker all absent, five target
timers disabled/inactive and the collector service inactive and
unwired for any notifier. It confirms the rendered script has
`COLLECTOR_HOST = "monitor-01"` and valid Python syntax, but
**never imports or runs it**; doing so before importing the original
MAC registry could seed a second baseline. Source registry and SMTP
recipient remain untouched on Proxmox-2. SHA-256 checks require
all four protected monitor-01 state files unchanged.

The first Gate 2i attempt stopped safely with `monitor-01:
5 OK / 0 changed / 1 failed`: the unexpected existing target notifier
tripped the deliberate no-overwrite check. A separate read-only audit
found a regular root-owned mode-0750 script with valid Python syntax,
`COLLECTOR_HOST = "monitor-01"`, SHA-256
`c1bef0bf41c6cc2538e6b270f7667a4772b0ba98e3c4f7c54228512f1550d2dd`.
The target recipient, alert registry and cutover marker were absent,
and the collector service had no email post-hook or EnvironmentFile.
These observations establish an **inert** notifier but not its
installation provenance or exact equality to the reviewed template.
Do **not** delete, overwrite or execute the existing notifier.

A separate, read-only **Gate 2i-R**, in
`playbooks/network-host-monitor01-firstseen-notifier-verify.yml`,
compares the installed bytes to the approved monitor-01 template using
Ansible `template` in `check_mode`, with `diff: false` and
`no_log: true`. It must report `changed: false`, also verifying
file metadata, the absent alert registry/recipient/cutover marker,
disconnected collector, five inactive/disabled timers and unchanged
SHA-256 for all four protected JSON files. A changed result **blocks**
progress and does not overwrite the existing file. Do not rerun
the old one-shot Gate 2i.

**Gate 2i-R PASSED on 27 September 2026:** `monitor-01: 22 OK /
0 changed / 0 failed`. Ansible's check-mode template comparison returned
`changed: false`, confirming the existing notifier matches the
reviewed monitor-01 rendering without overwrite or execution.
The installed script's bytes and all four protected JSON file hashes
remained unchanged. The target recipient, first-seen registry and
cutover approval marker remained absent, the target collector still
had no email hook or recipient environment, and all five staged timers
remained disabled/inactive. The notifier is verified but intentionally
**not active**. Its original installation provenance is not established.

Following the verified Gate 2i-R, keep the destination notifier disconnected from
`ExecStartPost` and retain the source as the sole first-seen
alert owner. Only following a deliberate stop of source collector,
enricher and evidence timers and waiting for running jobs to finish
may the final protected source registry/configuration and all
three fresh JSON datasets be copied and verified on monitor-01.
Do not use a stale snapshot of the first-seen registry.

The first-seen alert registry/configuration still resides with the
production source on Proxmox-2. Preserve it and perform the final
stop-and-delta-sync before granting cutover approval and enabling
monitor-01 discovery.

**Known follow-ups before Gate 3:** the inactive monitor-01 enricher now uses the protected, refreshed cluster-wide Proxmox guest MAC snapshot; do not revert it to the Proxmox-2 local `/etc/pve` lookup. The first-seen email configuration and alert registry still require protected final synchronisation and a disabled target notifier deployment, with duplicate-message prevention verified before enabling target alerts. The staged monitor-01 collector deliberately has **notifications disabled**. Do not stop the source alerting path until the complete destination is verified.

**26 September staging outcome:** the source snapshot was retained at
`/var/backups/homelab-network-migration/20260926T095635`. The staging
playbook reported 14 OK / 2 changed / 0 failed on Proxmox-2 and 54 OK /
16 changed / 0 failed on monitor-01. All three target SHA-256 comparisons
passed; the local read-only exporter recovered eight historical Nmap OS
matches. The target collector, enricher, deep profiler and OS exporter
timers remain disabled, while the source collector and enricher continue.
**Do not rerun the staging playbook:** the target files now exist by design.

## Gate 3: deliberate single-owner cutover (not part of preflight)

**Entry status, 27 September 2026:** all staged guest-identity,
strict-TLS refresh, disabled timer, source first-seen readiness and
read-only destination notifier-template gates passed. This is *not*
approval to stop Proxmox-2; Gate 3 requires a separate explicit
cutover decision and a reviewed stop/sync/activate implementation.
The last source-only audit reported 49 known MACs (40 baseline and
nine alerted) with zero pending online messages, but that measurement
will change if devices join before the source is stopped.

**Hold points for the future cutover:**

1. **Before source stop**, separately check source timer/service
   states, last successful collector/enricher/notifier cycles, recent
   email failures, source registry count and target inactivity.
   Preserve source timer enablement and published metric details as
   rollback evidence. Do not run the staged destination notifier.
2. **Stop and freeze production source only with explicit approval.**
   Disable and stop source collector, selective enrichment, deep
   profiler (if scheduled) and old network-only OS evidence timers,
   wait for any active one-shot jobs and their notifier post-hooks to
   complete, then verify no source timer or service will restart during
   the transfer. Do not stop unrelated Proxmox monitoring.
3. **Fresh protected final source snapshot.** Only after the
   source is quiescent, capture the three original JSON datasets
   and *entire* historical `alerted-macs.json` and `alerts.env`;
   keep file owners/modes, original SHA-256 and source backups.
   Backup the existing staged target JSON and snapshot before any
   replacement. Never print or commit SMTP recipients, raw MACs,
   tokens or alert registry contents to Git, Ansible output or
   world-readable staging files.
4. **Source-to-target validation before activation.** Compare
   SHA-256 of the exact final source and target copies, parse all JSON,
   verify no MAC is lost from the complete historical registry and
   check inventory/registry intersection and pending-online counts
   *after* the source freezes. Revalidate protected root-only
   permissions and the target guest identity mapping against the
   fresh inventory; refresh guest map with the trusted API if needed.
   Any mismatch is a stop condition, not permission to re-seed alerts.
5. **Single-owner activation and rollback gate.** Only after those
   checks and a separate explicit cutover approval, install the
   reviewed notifier post-hook and protected recipient environment
   on the target. Prove source is still stopped, then enable
   monitor-01's intended collector/guest-refresh/enrichment schedules
   in the reviewed order; keep deep profiling a separate opt-in.
   Verify new MAC-keyed discovery, once-only first-seen behaviour,
   Prometheus labels and existing Grafana host-dashboard UIDs before
   removing any old network-only series. On failure, disable and
   drain all target workers *before* resuming source services with
   their prior state, and preserve both sets of JSON and alert
   registries for reconciliation.


- Record active Proxmox-2 collector, enrichment and notification
  states and their last successful collection. Stop **the old collector,
  enricher and old read-only OS-publisher timers** and wait for currently
  running jobs to finish. Preserve their previous enabled/disabled states
  as rollback data.
- **Final delta sync is mandatory:** the initial staged snapshot may be
  hours old, because the source collector and enricher remain active
  during Gate 2. After stopping the old jobs, take one *final* protected
  source snapshot of inventory, deep-profile and enrichment JSON, plus
  first-seen alert registry/configuration (if present). Back up the
  staged target files before replacing them, validate JSON schema and
  SHA-256 for both sides, then regenerate the read-only fingerprint
  metric on monitor-01. Do not use a stale Gate 2 snapshot as the
  production state.
- Verify the virtual NIC can perform LAN-local ARP discovery with its
  source address and the approved target/rate limits. Enable
  **monitor-01** collector first and verify new MAC-keyed inventory,
  presence history, Prometheus target labels and Grafana identities.
- Enable selective enrichment only after collector validation **and**
  replacing the old host-local `/etc/pve` Proxmox guest lookup; transfer
  the first-seen email configuration/registry before disabling source
  notifications. Enable deep profiling only as a separate explicit
  decision. Limit it to one recently seen device per run and retain
  existing cooldowns.
- Disable Proxmox-2's obsolete per-device evidence timer and retire only
  its **network discovery** `.prom` files after monitor-01 is stable;
  do not remove ordinary Proxmox node-exporter metrics.
- Reconcile `docs/architecture/CURRENT-STATE.md`, the three Ansible role
  inventory targets/defaults and the Grafana runbook **after** live
  verification. Do not present proposed deployment as already installed.

## Rollback

If monitor-01 fails either the inventory or OS-correlation checks:
leave its new scanning timers **disabled**, restore Proxmox-2's original
network collector/enrichment schedule only after ensuring no new
monitor-01 scanner is running, and retain both copies of all state.
The existing monitor-01 Grafana dashboards and Prometheus should remain
available throughout. Never start both active collectors concurrently.

**Do not** run the old
`playbooks/network-host-os-fingerprints.yml` as the monitor-01 migration
mechanism: it explicitly targets Proxmox-2 as the publisher. A separate
migration/cutover playbook must replace that legacy target only after
Gate 1 establishes the correct live interface and state layout.
