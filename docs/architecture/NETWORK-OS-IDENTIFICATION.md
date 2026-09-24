# Network host OS identification — staged design

Status: design and Phase 1 Nmap evidence export in this PR. No deployment or additional scans authorised by this change.

## Existing capabilities (verified in repository)
- Current collector: `Proxmox-2`, inventory `/var/lib/homelab-network-hosts/inventory.json`.
- Deep profiler already runs Nmap `-O --osscan-guess -sV` on **new** MACs after a fresh ARP presence check. It retains top OS matches, Nmap-reported accuracy, service CPEs, banners and selected NSE output in `deep-profiles.json`.
- Existing MACs are deliberately baselined, not automatically scanned. One expensive profile at most per worker run. Deployment and timer gates default to **false**.
- Enricher separately collects service banners, TLS certificate identities and local Proxmox VM/LXC identities by MAC.

## Phase 1 — reuse existing evidence (this PR)
- Export `homelab_network_host_os_info{mac,ip,os,os_family,os_generation,source="nmap",accuracy} 1` for completed deep profiles **only when Nmap has an OS match**.
- `accuracy` is Nmap's fingerprint match estimate; it is not our independent confidence score or a verification claim.
- No additional Nmap invocation, privilege change, timers, or deployment. No guess for missing profiles.

## Phase 2 — verified local evidence (separate change)
- Gather `/etc/os-release`, `uname -srm` and machine architecture from managed Linux hosts through approved Ansible/node-exporter textfile paths. Only mark distribution/version *verified* when directly read from the host; kernel alone gives kernel family/version, not necessarily distribution.
- Use approved Windows management data where available. Do not infer Windows versions from ports alone.
- Match managed hosts to discovery inventory using canonical inventory identity; validate MAC/IP mappings and stale records before merging.

## Phase 3 — correlate, classify, explain
- Correlate local facts, Nmap `os_matches`, service CPE/banners, NSE SMB hints, MAC vendor, DHCP and existing Greenbone evidence. Avoid treating a MAC vendor as proof of OS.
- Priority: verified local > validated authoritative inventory > corroborated Nmap/service evidence > single weak hint > unknown.
- Produce `os_display`, `os_family`, `source`, `confidence` (verified/high/medium/low/unknown), `observed_at`, `evidence[]`, `conflicts[]`, and `review_required` in a separate persistent OS-identification JSON file. Never overwrite verified facts with inference.
- Optional AI consumes a bounded, redacted evidence JSON; it may suggest family/version with rationale but cannot silently override verified facts. Do not transmit internal IPs, hostnames, service banners or certificate subjects to external AI without an explicit privacy decision. Deterministic fallback must work with AI disabled.

## Phase 4 — dashboard integration
- Add a joined Host Inventory view with `Hostname`, `IP`, `Operating System`, `Confidence`, `Source`. Prefer `Unknown` over empty or fabricated values.
- Use `ip`/validated MAC join and avoid dropping unmatched hosts. Retain detailed evidence and timestamps in Network Device Detail.
- PR #141 owns the Network Hosts dashboard redesign; coordinate there after evidence schema is validated.

## Safety and acceptance
- No new scanning of baselined devices without explicit approval and a bounded target list.
- Do not change existing collector timers or default deploy gates as part of OS classification.
- Tests: no-match, multiple matches, service-only hints, conflicting local/Nmap results, stale IP/MAC reuse, malformed state, metric escaping, idempotent writes and no new scans.
- Deploy only after backup of `inventory.json`, `deep-profiles.json` and textfile metrics, with read-only metric verification and rollback.

## Phase 3a — passive update-traffic evidence (design; disabled by default)
- Consume **metadata only** from existing Pi-hole DNS query logs and Zeek DNS/connection logs, if those logs are already collected and authorised. The existing Zeek IaC enables JSON logs and MAC metadata in conn.log; verify DNS log collection, Loki labels, retention and resolver attribution on live systems before writing an ingestion adapter.
- Do not assume every DNS query identifies the actual originating device: a shared resolver, NAT, proxy, container or cached lookup can misattribute it. Match observed source IP to the discovery inventory's IP/MAC identity **at the observation timestamp**. Mark unattributed/shared-resolver observations unusable for per-device classification.
- Use a version-controlled, reviewable domain-indicator registry with exact/suffix boundaries and attribution limits. Illustrative indicators: `security.ubuntu.com` and `archive.ubuntu.com` (Ubuntu repositories); `deb.debian.org` and `security.debian.org` (Debian repositories); `windowsupdate.com` and `update.microsoft.com` (Microsoft update infrastructure); `swcdn.apple.com` and `mesu.apple.com` (Apple update infrastructure). Generic `dl.google.com` is **not** proof of Android. A query indicates contact with a service, not that an update was installed or that the device runs the vendor's OS.
- Only score an update-domain indicator when corroborated by a second independent evidence family (local facts, Nmap OS fingerprint, service CPE or an authoritative inventory record). Repeated DNS queries alone are not independent corroboration. Keep per-device evidence counts, first/last seen and originating sensor, not full browsing histories.
- Prefer bounded aggregation (e.g. 7-day rolling window) and short raw-event retention according to the existing logging policy. Never store URLs, HTTP bodies, credentials or personal browsing history for OS identification. Treat TLS SNI/Zeek connection metadata as optional and potentially absent with ECH/DoH.
- AI consumes **aggregated, minimised** signals (e.g. `ubuntu_update_seen=true`, `nmap_family=Linux`, counts and freshness), never raw DNS logs. No external AI transfer of host identifiers or network logs without explicit opt-in and a documented processor/privacy decision.
- Conflicts (e.g. Windows local facts plus Ubuntu repository traffic) should explain a likely VM/container/package-download possibility and request review, **not** overwrite verified OS.

### Passive evidence acceptance tests
1. Ubuntu update domain + Nmap Linux match -> Ubuntu *candidate*, never verified.
2. Microsoft update domain alone -> unknown OS; no Windows claim.
3. Generic Google download domain -> no Android inference.
4. Shared DNS resolver IP -> discard for device attribution.
5. DHCP IP reassignment within evidence window -> avoid transferring evidence to new MAC.
6. Repeated lookups from one sensor -> do not inflate independent-source confidence.
7. Conflicting locally verified OS -> retain verified fact and flag conflict.
8. Missing DNS/Zeek telemetry -> pipeline remains functional with Nmap/local evidence.
