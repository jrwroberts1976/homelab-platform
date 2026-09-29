# Selective device identification

<!-- estate-authority: IaC/inventory/estate.json -->

## Scope and safety

The live owner of LAN discovery, enrichment, saved OS evidence and guest identity remains **monitor-01**. Do not restart legacy collectors on Proxmox-2. Only `192.168.2.0/24` is in scope; the Corosync network must not be scanned.

**Current production state, 29 September 2026:** the targeted monitor-01 deep
profiler is active, completed current devices are re-profiled weekly, and the
automatic dual-Pi-hole DNS evidence timer is enabled/active. DNS evidence is
retrieved through restricted read-only helpers on `dns-01` and `dns-02`,
correlated with MAC/vendor and Nmap service evidence, consumed by the network
inventory exporter and displayed in Grafana. The production Fire TV validation
proved this flow end to end. See
[Automated network-device identification](network-device-identification.md)
for the deployed implementation. The AI assessment, manual escalation and
persistent generated GitHub host-page stages described later in this document
remain planned rather than deployed.

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

The production DNS path now uses restricted, **read-only** Pi-hole FTL helpers on dns-01 and dns-02. The seven-day window is anchored to the associated Nmap profile timestamp so useful evidence can still be recovered for devices that are currently offline. Raw household DNS history stays on the resolvers. monitor-01 receives only bounded query counts, at most five top domains, reviewed signal classes and at most three examples per signal. DNS may still be absent because of retention, client-side DoH or cache. Do not replicate full household DNS logs to GitHub. OUI is a public IEEE registry downloaded once; locally administered MACs are never assigned manufacturers from their apparent prefixes.

## Intended new-device-triggered pipeline

1. Existing monitor-01 collector continues on its proven five-minute discovery timer. Its existing `host_discovered` event in `/var/log/homelab-network-hosts/events.jsonl` is the trigger; do **not** run a new periodic identity sweep of every device. `host_identity_changed` may trigger only when the MAC changes to an unfamiliar value. Ordinary `host_online` events and unchanged IP leases do not start identification.
2. A separate, durable and idempotent consumer of those events checks canonical inventory, confirmed device notes and current Proxmox guest mapping **before** adding a device to the unresolved queue. Maintain a persistent processed-event/MAC record so restarts or repeated discovery do not trigger duplicate work. Do not create a second new-device email; enrich the existing notification or send a single follow-up only when new evidence is available.
3. **Nmap first:** queue one separately approved, low-rate, individually timed TCP service/version and OS-fingerprint scan of that specific new unknown device. Record completed XML per IP+MAC and enforce a retry cooldown; do not scan the subnet or enable the old deep profiler. A timeout or missing OS match is an incomplete identification, not proof the device is offline.
4. **Then MAC and DNS:** use the existing DHCP hostname and MAC OUI registry; query seven-day aggregated history for that IP from both dns-01 and dns-02 if Nmap alone does not identify it. A randomised/local MAC and absent DNS are uncertain, not evidence of an intruder.
5. Publish evidence and an unresolved private Grafana review card. Owner confirmation updates editable notes and, after reviewed Git, canonical inventory; DNS domains and OS guesses never automatically confirm a device. Preserve the review status across reconnects and IP changes when a reliable MAC identity is available.
6. A weekly **incomplete-evidence recheck** revisits only devices whose required identification data is still missing. It refreshes OUI and dual-Pi-hole DNS evidence and may rerun the targeted single-device Nmap scan only when the saved profile/cooldown policy permits it. It must never rescan the whole subnet or re-identify already confirmed devices.
7. **AI is the final identification stage, never the first.** After Nmap, hostname, OUI/vendor, observed services/ports and current summaries from both dns-01 and dns-02 have been collected, send only that minimised device evidence to the configured AI API and ask for an OS assessment. Do not send raw household DNS logs. Persist the returned OS candidate, rationale/evidence summary, confidence/uncertainty and model observation time as inferred evidence; AI output does not silently become an authoritative OS fact.
8. If the AI stage cannot produce a usable OS assessment, persist `manual_input_required=true` for that MAC-keyed host, expose that state on the host review/page, and send one deduplicated email through the existing homelab SMTP relay to `jrwroberts1976@gmail.com` stating that no OS was found and manual input is required. Weekly rechecks may enrich the same record, but must not send repeated identical failure emails unless the evidence materially changes or the manual-review state is explicitly reset.
9. Manual owner input is authoritative for that host after review. The confirmed value should be written to the host's editable/canonical record and clear `manual_input_required`; inferred Nmap, DNS and AI evidence remains retained as supporting history rather than being deleted.
10. **Update Grafana after the identification state is persisted.** Regenerate the existing MAC-keyed host dashboard so the current OS, evidence source, DNS/OUI/Nmap/AI summaries, manual-review state and last/next identification checks are visible. Grafana is the live operational view; a failed dashboard refresh must not discard the last good host record.
11. **Then create or update a persistent GitHub host page.** Generate a Markdown page for the stable host identity under a dedicated network-host documentation area (for example `docs/network/hosts/`) and keep a generated index linking all host pages. The page should contain the current hostname/IP/MAC/vendor, authoritative or inferred OS and source, observed services/ports, bounded dns-01/dns-02 clues, Nmap evidence, AI assessment, manual-review status and evidence timestamps. Never commit raw Pi-hole query logs, secrets, API responses containing hidden reasoning, or other household browsing history. When the host is manually confirmed or later re-identified, update the same page rather than creating a duplicate.

## Existing profiler reused — current production behaviour

The repository profiler retains its MAC-keyed queue, fresh identity checks,
persisted partial results and retry controls. Production uses the targeted mode
on `monitor-01`: one bounded top-100-TCP service/version-light and Nmap OS
profile at a time, with no NSE or UDP scan in targeted mode.

The controlled baseline backlog is spread deterministically across seven days.
Completed devices that remain in current inventory are then re-profiled weekly
so changes to open TCP ports, service/version evidence and supporting Nmap OS
evidence can be detected. Historical records remain preserved but are not
rescanned unless their MAC is current.

The DNS evidence role is also deployed. Its five-minute timer does not cause a
DNS query every five minutes for every device; it gives the worker frequent
opportunities to process newly completed profiles. A successful record is
normally collected once per profile, while failures respect the configured
retry cooldown. Evidence-version changes can deliberately trigger a bounded
refresh after collector upgrades.

**Deployment status:** targeted Nmap profiling, weekly completed-host
re-profiling, restricted dual-Pi-hole DNS evidence, MAC/Nmap/DNS correlation,
inventory publication and Grafana display are live. The later AI decision
stage, deduplicated manual-input email fallback and generated persistent GitHub
host pages remain future work.
