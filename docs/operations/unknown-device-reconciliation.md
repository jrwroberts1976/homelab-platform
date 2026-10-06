<!-- estate-authority: IaC/inventory/estate.json -->
# Selective Device Identification

**Status:** TARGETED IDENTIFICATION PIPELINE OPERATIONAL; MANUAL-REVIEW ESCALATION REMAINS PARTIAL  
**Production owner:** `monitor-01`  
**Current-state review:** 6 October 2026

## Scope and safety

`monitor-01` is the sole live owner of LAN discovery, enrichment, saved OS evidence, trusted Proxmox guest refresh, targeted Nmap profiling, DNS evidence correlation and generated Network Hosts views.

Do not restart the former discovery workers on `Proxmox-2`. Only `192.168.2.0/24` is in discovery scope; the Corosync interconnect is not a scanning target.

## Current deployed production state

The following stages are live:

1. five-minute collector on `monitor-01`;
2. selective enrichment and trusted Proxmox guest identity correlation;
3. targeted per-device Nmap TCP/service/OS profiling with cooldown/backlog controls;
4. weekly re-profiling of completed current devices;
5. bounded read-only DNS evidence from both `dns-01` and `dns-02`;
6. MAC/OUI, Nmap and DNS evidence correlation;
7. network inventory/Prometheus publication;
8. Grafana Network Hosts overview and generated MAC-backed host dashboards;
9. persistent generated Markdown host pages under `docs/network/hosts/`;
10. persisted bounded AI host assessment where the reviewed workflow has produced one.

The older statement that AI assessment and persistent GitHub host pages are entirely future work is obsolete.

Manual owner confirmation/escalation remains a distinct control. Do not claim every unresolved host receives a fully automated deduplicated manual-input email unless that path has been separately validated for the current implementation.

## Evidence precedence

Identification evidence is supporting evidence, not automatic authority.

Use this precedence:

1. canonical/current human-confirmed inventory facts;
2. reviewed persistent host notes/confirmed identity;
3. Proxmox guest mapping where applicable;
4. DHCP/hostname and MAC identity;
5. Nmap services/OS evidence;
6. bounded dual-Pi-hole DNS clues;
7. AI assessment as inferred evidence only.

AI, DNS or Nmap output never silently overwrites a human-confirmed/canonical identity.

## Privacy boundary

Raw household DNS history remains on the resolvers.

The central identification path receives only bounded evidence such as:

- query counts;
- a small number of top domains/signal examples;
- reviewed signal classes;
- observation timestamps.

Do not commit raw Pi-hole query logs, client browsing history, credentials, hidden model reasoning or unrestricted API responses to GitHub.

## Targeted profiler behaviour

Production uses the targeted profiler on `monitor-01`:

- one bounded device profile at a time;
- top-100 TCP/service/version-light profiling;
- Nmap OS evidence where available;
- no general NSE/UDP sweep in targeted mode;
- persistent MAC-keyed state;
- retry/cooldown handling;
- deterministic backlog spreading;
- weekly refresh of completed devices still present in current inventory.

A missing OS match or timeout is incomplete evidence, not proof that a device is malicious/offline.

## DNS evidence behaviour

The DNS evidence worker consumes read-only aggregate helpers on both resolvers.

Important properties:

- dual-resolver correlation;
- bounded seven-day evidence window anchored to profile timing where applicable;
- successful evidence normally collected once per relevant profile/version;
- failures respect retry cooldown;
- locally administered/random MACs are not assigned an OUI manufacturer from their apparent prefix;
- DNS can legitimately be absent because of retention, caching or client-side encrypted DNS.

## AI assessment

AI is a late-stage inference source, not the first identification step.

Only minimized evidence should be sent, such as:

- hostname/MAC/OUI/vendor;
- observed open services/ports;
- saved Nmap OS/service evidence;
- bounded DNS signal summaries;
- current source/evidence timestamps.

Persist AI output as inferred evidence with its confidence/uncertainty and observation time. Do not silently promote it to an authoritative OS/device fact.

## Persistent host pages

Generated Markdown host records under `docs/network/hosts/` are part of the deployed workflow.

A host page can contain:

- current hostname/IP/MAC/vendor;
- authoritative vs inferred OS/device type;
- observed services/ports;
- bounded DNS clues;
- Nmap evidence;
- AI assessment where present;
- manual-review status;
- evidence timestamps;
- patch/monitoring evidence for managed hosts where available.

Pages are generated/updated for the stable host identity rather than creating duplicates for ordinary reconnects/IP changes.

Generated pages are operational evidence outputs and must not be normalized manually one by one.

## Grafana relationship

Grafana is the live operator view for the same persisted identity/evidence state.

Generated host dashboards should expose:

- online/inventory state;
- MAC/vendor identity;
- Proxmox/DNS/Nmap evidence where available;
- current inferred/confirmed OS/device type;
- AI evidence and manual-review state where present;
- open ports/services;
- evidence freshness/last analysis.

A failed dashboard regeneration must not destroy the last good persistent host record.

## New-device handling

The existing collector's `host_discovered` event is the trigger for new-device identification. Ordinary unchanged reconnects should not create duplicate identification work.

A durable MAC-keyed processed-state record should prevent repeated work and duplicate notifications.

For a truly new unresolved device:

1. check canonical inventory/confirmed notes/Proxmox mapping;
2. queue targeted Nmap evidence;
3. obtain OUI and bounded dual-DNS evidence;
4. publish/update the private operational review state;
5. run bounded AI assessment only after deterministic evidence exists;
6. persist inferred/manual-review state;
7. update Grafana and the generated host page;
8. require human review before canonical identity changes.

## Manual review

When automated evidence cannot produce a usable assessment, maintain a MAC-keyed `manual_input_required` state rather than fabricating certainty.

Human-confirmed input is authoritative after review. Supporting Nmap/DNS/AI evidence remains history rather than being deleted.

Any automatic manual-review email path must be deduplicated and evidence-change aware; do not send repeated identical failure notifications.

## Historical Gate 4/offline tooling

`IaC/monitoring/audits/reconcile_unknown_devices.py` remains useful for offline reconciliation of retained audit evidence. It is non-scanning and must not be confused with the live `monitor-01` production pipeline.

Dated September audit commands/results remain historical evidence and do not define current implementation status.

## Operational validation

Validate the pipeline using current evidence rather than assumptions:

- collector/enricher/profiler/DNS timers active on `monitor-01` as designed;
- former source timers disabled on `Proxmox-2`;
- generated inventory metrics current;
- representative device profile contains expected source timestamps;
- Grafana Network Hosts data is fresh;
- generated host page updated for the same stable identity;
- AI evidence, if present, is labelled inferred;
- no raw household DNS data is committed.

## Remaining work

- continue refining manual-review/escalation behaviour and prove deduplication if automated email is used;
- extend evidence rules only when they improve identification quality;
- retain privacy bounds and fail-safe handling for unavailable sources;
- keep generated host pages/dashboard schemas aligned with the current evidence model.
