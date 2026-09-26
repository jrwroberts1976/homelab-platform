<!-- estate-authority: IaC/inventory/estate.json -->
# Proposed: make monitor-01 the sole network-discovery and OS-investigation host

**Status as of 26 September 2026: Gate 1 preflight passed on both hosts;
Gate 2 staging playbook prepared but not yet deployed. The production
collector and enricher still run on Proxmox-2.**
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

## Gate 2: stage without starting new scans

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

**Known follow-ups before Gate 3:** the old enrichment worker derives
Proxmox guest identities from `/etc/pve`, which monitor-01 cannot read
locally; migrate that lookup to an authorised read-only source before
enabling the new enrichment schedule. The existing first-seen email
configuration and alert registry must also be reconciled; the staged
monitor-01 collector deliberately has **notifications disabled**.
Do not stop the source alerting path until the destination is verified.

## Gate 3: deliberate single-owner cutover (not part of preflight)

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
