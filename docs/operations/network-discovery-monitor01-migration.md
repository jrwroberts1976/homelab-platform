# Proposed: make monitor-01 the sole network-discovery and OS-investigation host

**Status: migration preflight only. Not the live deployment truth.**
The authoritative present-tense inventory remains
[`docs/architecture/CURRENT-STATE.md`](../architecture/CURRENT-STATE.md)
until the live handover has been verified. Current collector and saved
deep-profile data are still on Proxmox-2. Grafana, Prometheus, OS
correlation and generated individual host dashboards already run on
monitor-01. The goal is to make **monitor-01** own the entire pipeline.

## Target architecture

```text
ASUS DHCP/ARP inventory ----                              monitor-01 (VM 202)            [network discovery and targeted Nmap]
   |                           /
   +-- collector (5 min) ------/
   +-- targeted service/OS investigation (separately controlled timer)
   +-- preserved MAC-keyed inventory.json, deep-profiles.json, enrichment.json
   +-- read-only saved OS-fingerprint publisher (5 min)
   +-- existing Node Exporter textfile directory
   +-- existing Prometheus + Grafana
   +-- existing data-only per-host dashboard generator (5 min)
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

Expected evidence from the 2026-09-26 diagnostic was **49 records**,
**13 completed profiles**, **8 Nmap OS-match records** and no
`tcp_scanned_at` values. These are historical counts, not a gate requiring
the network to stay frozen. Use the preflight's *actual* result before
building the transfer plan.

## Gate 2: stage preserved state (only after the preflight passes)

1. Back up and hash Proxmox-2's original `inventory.json`,
   `deep-profiles.json` and `enrichment.json`; never edit their original
   contents. Confirm their schema, owner, permissions and source SHA-256.
2. Check for existing similarly named files on monitor-01 and refuse to
   overwrite them. Transfer through an encrypted, controlled connection
   from admin-01 or a short-lived restricted account. Preserve root-only
   permissions and the MAC-keyed identity. Do not commit host identifiers
   or exported JSON to GitHub.
3. Install the existing collector, enricher, deep-profiler and OS-evidence
   publisher from IaC on **monitor-01 only**, using the preflight-discovered
   interface in place of `vmbr0`. Keep *all new scan timers disabled*.
4. Run the **read-only** OS evidence exporter on monitor-01 against the
   copied state, verify the eight available Nmap matches (or explain any
   invalid records), then update the monitor-01 inventory exporter to query
   its **local** metric series rather than `target_name="Proxmox-2"`.
   Continue strict current MAC + scanned IP correlation, documented OS
   precedence and no fingerprint panel for specifically known OS.
5. Rebuild host dashboards and verify the live Grafana API still indexes
   the 50 current device pages, preserving their MAC-based UIDs. Verify
   at least one previously unidentified device's conditional Nmap panel;
   a missing panel for a known OS is expected.

## Gate 3: deliberate single-owner cutover (not part of preflight)

- Record active Proxmox-2 collector and enrichment timer states and the
  last successful collection. Stop the old timers and wait for any running
  job to finish. Keep a protected rollback copy of all prior evidence.
- Verify the virtual NIC can perform LAN-local ARP discovery with its
  source address and the approved target/rate limits. Enable
  **monitor-01** collector first and verify new MAC-keyed inventory,
  presence history, Prometheus target labels and Grafana identities.
- Enable selective enrichment only after collector validation; enable
  deep profiling only as a separate explicit decision. Limit it to
  one recently seen device per run and retain existing cooldowns.
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
