# Selective device identification (staged)

<!-- estate-authority: IaC/inventory/estate.json -->

## Scope and safety

The live owner of LAN discovery, enrichment, saved OS evidence and guest identity remains **monitor-01**. Do not enable the legacy deep profiler or restart collectors on Proxmox-2. Only `192.168.2.0/24` is in scope; the Corosync network must not be scanned.

`IaC/monitoring/audits/reconcile_unknown_devices.py` is the offline, **non-scanning** decision stage. It reads existing Gate 4 evidence plus the canonical `IaC/inventory/estate.json`. Known, documented devices are excluded from its unresolved queue; unknowns are enriched with available MAC manufacturer, saved Nmap OS candidates, and aggregated DNS clues. The tool does **not** declare a device known solely because Nmap returns an OS candidate. It does not change canonical inventory, device names or notes.

## Run on admin-01 against the September 27 audit

```bash
RUN=/var/tmp/homelab-postcutover-audit-20260927T114824+0100
REPO=/var/tmp/homelab-gate4-review
python3 "$REPO/IaC/monitoring/audits/reconcile_unknown_devices.py" "$RUN" \
    --estate "$REPO/IaC/inventory/estate.json" \
    --oui "$RUN/ieee-oui.csv" \
    --dns "$RUN/dns-clues.json"
```

Omit `--oui` or `--dns` if those optional files do not exist. The output `unresolved-devices.json` is root/private-mode and separates `known_devices` from `unresolved_devices` and `no_direct_or_nmap_os_evidence`. DNS records are optional aggregates in this format:

```json
[
  {"ip":"192.168.2.206","server":"dns-01","query_count":12,
   "top_domains":["service.example"]},
  {"ip":"192.168.2.206","server":"dns-02","query_count":3,
   "top_domains":["another.example"]}
]
```

Produce DNS aggregates via a separately approved, **read-only** restricted collection from Pi-hole FTL on dns-01 and dns-02; filter to the unresolved IP queue, use a seven-day history window, and keep at most five domains per IP per server. DNS may be absent because of retention, privacy settings, client-side DoH or cache. Do not replicate full household DNS logs to GitHub. OUI is a public IEEE registry downloaded once; locally administered MACs are never assigned manufacturers from their apparent prefixes.

## Intended new-device-triggered pipeline

1. Existing monitor-01 collector continues on its proven five-minute discovery timer. Its existing `host_discovered` event in `/var/log/homelab-network-hosts/events.jsonl` is the trigger; do **not** run a new periodic identity sweep of every device. `host_identity_changed` may trigger only when the MAC changes to an unfamiliar value. Ordinary `host_online` events and unchanged IP leases do not start identification.
2. A separate, durable and idempotent consumer of those events checks canonical inventory, confirmed device notes and current Proxmox guest mapping **before** adding a device to the unresolved queue. Maintain a persistent processed-event/MAC record so restarts or repeated discovery do not trigger duplicate work. Do not create a second new-device email; enrich the existing notification or send a single follow-up only when new evidence is available.
3. **Nmap first:** queue one separately approved, low-rate, individually timed TCP service/version and OS-fingerprint scan of that specific new unknown device. Record completed XML per IP+MAC and enforce a retry cooldown; do not scan the subnet or enable the old deep profiler. A timeout or missing OS match is an incomplete identification, not proof the device is offline.
4. **Then MAC and DNS:** use the existing DHCP hostname and MAC OUI registry; query seven-day aggregated history for that IP from both dns-01 and dns-02 if Nmap alone does not identify it. A randomised/local MAC and absent DNS are uncertain, not evidence of an intruder.
5. Publish evidence and an unresolved private Grafana review card. Owner confirmation updates editable notes and, after reviewed Git, canonical inventory; DNS domains and OS guesses never automatically confirm a device. Preserve the review status across reconnects and IP changes when a reliable MAC identity is available.
6. An optional low-frequency **health check of the queue** may retry previously failed lookups after DNS activity occurs; it must never rescan the whole subnet or re-identify already confirmed devices.

## Existing profiler reused — staged changes

The repository already contains a MAC-keyed pending queue, first-run baseline,
fresh ARP verification, persisted partial results, 24-hour retry cooldown, and
an existing OS evidence exporter. The full-scan profiler remains **disabled**
on the live monitor-01 host.

The existing profiler template now supports an explicitly selected
`network_host_deep_profiler_scan_mode: targeted`. This mode runs a bounded
100-top-TCP-port service/version and Nmap OS scan against one freshly verified
MAC/IP at a time, with no NSE or UDP scanning. The legacy scan remains the
inactive default; no existing source host is activated.

A dedicated
`IaC/ansible/playbooks/network-host-monitor01-targeted-profiler-stage.yml`
requires separate execution approval, preserves the existing worker under
`/var/backups/homelab-targeted-profiler/`, installs the targeted variant
only on monitor-01, and leaves its timer disabled. The new PR CI checks
existing offline profiler recovery tests, targeted TCP-only tests and Ansible
syntax. Stage and live activation are distinct actions.

**Deployment status:** The offline reconciler, targeted-mode changes, existing-profiler tests and inert deployment playbook are staged in this PR. The event consumer, persistent deduplication, restricted SSH DNS summary retrieval, and gated single-device scan are **not yet deployed**. Existing new-device email and collector already work; this PR does not change those live services.
