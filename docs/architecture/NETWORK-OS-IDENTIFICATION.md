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
