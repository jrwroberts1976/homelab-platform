# Selective device identification (staged)

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

## Intended scheduled pipeline

1. Existing monitor-01 collector/enricher/OS evidence publication continue at their current proven intervals.
2. After each successful collection, generate a read-only snapshot of the current inventory and OS evidence, then run the reconciliation stage. Preserve output from the prior run if any required source is missing or invalid.
3. For **only** the unresolved queue, collect DHCP hostnames, aggregate DNS clues from dns-01 and dns-02, and refresh local OUI data periodically. Do not probe devices that already have a confirmed identity.
4. If still unresolved, place IPs into a **separately approved** low-rate, individually timed targeted Nmap queue. Keep the deep profiler disabled. Persist per-device XML and avoid repeating completed probes until an explicit retry interval or identity change.
5. Publish a private review queue and Grafana counts. Suggest probable identities with supporting clues, but let the owner confirm them in editable notes. After confirmation, amend canonical inventory via reviewed Git; never auto-promote guesses.
6. Notify only on *new* unresolved MAC/IP identities or meaningful identity changes, with deduplication. Never send every domain or every detection as email.

**Deployment status:** Reconciliation code and offline tests are committed to the draft PR. Periodic orchestration, SSH permissions for private DNS extracts, timer and targeted scan approval are **not deployed** by this change. Do not claim end-to-end automation until those stages are explicitly validated on the live hosts.
