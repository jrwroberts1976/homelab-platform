# Documentation Review — 12 September 2026

## Purpose

This register records the estate/documentation reconciliation performed on 12 September 2026.

The review compared repository documentation with direct read-only evidence from the active homelab. It is a **documentation review**, not an infrastructure deployment/change record.

No router reset, switch repatching, SPAN configuration, Cloudflare Tunnel deployment, DNS IaC correction, firewall deployment or backup-platform installation is authorised by this document.

## Review principles

Documents were classified as one of:

- **current authority** — should describe the live estate accurately;
- **target state** — should describe future intent only;
- **historical evidence** — preserve what was true/planned at the time rather than rewriting history;
- **missing documentation** — create a current page where sufficient live evidence exists;
- **recovery/runbook risk** — stale operational instructions corrected before lower-risk descriptive drift.

A documentation edit does not equal a live configuration change or a recovery test.

## Key live-state findings used by the review

### Administration / retired identities

- `admin-01 .48` is the normal IaC/SSH controller.
- `TestServer` is retired; its Pi 4 hardware is `docker-01 .220`.
- `DietPi` is retired; its Pi 3 hardware is `admin-01 .48`.
- `ids-01` is decommissioned.

### DNS

- `dns-01 .51` and `dns-02 .50` are the current Pi-hole + Unbound pair.
- `.48` is not a resolver or fallback resolver.
- both resolvers passed public/DNSSEC checks.
- the review found that `dns-02` lacked the `dns-01.jameshouse` local record because the shared IaC list contained `.50` but not `.51`.
- follow-on infrastructure work on 12 September added the missing `.51` managed record, reconciled both resolvers, and proved both `.51` and `.50` resolve `dns-01.jameshouse -> 192.168.2.51` and `dns-02.jameshouse -> 192.168.2.50`; the IaC change is tracked in PR #64.

### Monitoring

- `monitor-01 .52` is operational.
- Prometheus, Grafana, Alertmanager and Blackbox are healthy.
- 23 active Prometheus targets were observed; all 23 were healthy.
- zero active Prometheus alerts were observed.
- Loki and Alloy are not deployed on `monitor-01`.
- the observed 23-target set did not include a `cloud-01` probe/exporter target.

### Cloud

- `cloud-01 .53` is live production Nextcloud/PostgreSQL/Redis.
- production data uses a dedicated 200 GiB VM disk at `/srv/cloud-01-data`.
- the 4 TB WD USB disk is not the cloud production data disk.
- backup/restore proof is not complete.

### Sensor

- `sensor-01 .55` Phase 1 is complete.
- Suricata 8.0.6 and Zeek 8.0.10 are installed.
- no capture NIC is attached yet.
- Suricata/Zeek are deliberately stopped pending Phase 2.

### Edge

- `edge-01 .56` LXC exists and is healthy.
- `cloudflared` is not installed/running.
- the Cloudflare Tunnel workload is not deployed.

### Mail relay

- `mail-relay-01 .54` is operational Postfix.
- upstream relay is Gmail smart-host on TCP/587 with TLS/SASL.
- Node Exporter/Prometheus monitoring is not currently deployed for this CT.

### Docker / BirdNET

- `docker-01 .220` is a dedicated Raspberry Pi 4 BirdNET-Go Docker host.
- one BirdNET-Go Compose project/container is running and healthy.
- Node Exporter is active.

### Media

- `media-01 .195` is operational as the Raspberry Pi 5 Kodi endpoint.
- Kodi, Samba, Chrony and Node Exporter are live.
- nftables is not deployed.
- `hostname -f` returned the short hostname `media-01`; the local DNS name `media-01.jameshouse` is therefore documented separately from host FQDN state.

### Backup

- zero scheduled Proxmox guest backup jobs were found on either node.
- no PBS server is deployed.
- no active estate-wide Restic/Backrest service was found.
- restore testing is not proven.
- the 4 TB WD disk on `PROXMOX` is blank/unallocated/unmounted risk/POC storage only.

### Switch / patching

Live HP ProCurve audit proved:

- firmware Y.11.52;
- VLAN 1 untagged ports 1–24;
- management configured via DHCP/BOOTP;
- STP disabled;
- port mirroring disabled;
- SNMP community `public` is `Unrestricted`;
- port 24 currently connects the primary ASUS router;
- port 24 is only the **planned future** SPAN destination.

Physical patching is expected to change when the dedicated sensor USB capture NIC arrives. The 12 September port map is therefore a dated evidence snapshot, not the target layout.

## Documents reconciled

### Repository overview / authority

- `README.md`
- `docs/migrations/LEGACY-REPOSITORIES.md`

The root README now reflects the current migrated authority model rather than describing `homelab-platform` only as a future authority. Legacy repository disposition is now explicitly per-workload/per-area rather than assuming whole-repository authority.

### Runbooks / recovery

- `runbooks/README.md`
- `runbooks/registry.yml`
- `production docs/DNS-SERVICE-RECOVERY-PLAN.md`

Major correction: normal controller is `admin-01`, and `.48` is no longer a DNS fallback.

The runbook registry now distinguishes current operational services from incomplete recovery coverage and records backup/Proxmox/logging/edge gaps explicitly.

### Architecture / migration

- `docs/architecture/CURRENT-STATE.md`
- `docs/architecture/TARGET-STATE.md`
- `docs/architecture/BACKUP-STRATEGY.md`
- `docs/architecture/PROPOSED-LAYOUT.md`
- `docs/migrations/MIGRATION-TRACKER.md`
- `docs/migrations/GREENFIELD-REBUILD-PLAN.md`

`PROPOSED-LAYOUT.md` and `GREENFIELD-REBUILD-PLAN.md` are now explicitly historical/superseded rather than pretending their earlier placements are current.

### Production services

Reconciled:

- `production docs/CLOUD-SERVICE.md`
- `production docs/MONITORING-SERVICE.md`
- `production docs/NETWORK-SENSOR-SERVICE.md`
- `production docs/MEDIA-SERVICE.md`
- `production docs/ROUTER-SYSLOG-SERVICE.md`
- `production docs/TIME-SERVICE.md`

New current service pages:

- `production docs/MAIL-RELAY-SERVICE.md`
- `production docs/BIRDNET-SERVICE.md`

Reviewed/left materially unchanged:

- `production docs/CLOUDFLARE-PAGES-PRODUCTION-PIPELINE.md`

The Cloudflare Pages pipeline document states that `engineering-portfolio` PR #16 is still open. That was checked against GitHub during this review and remained true on 12 September 2026, so the dated automation status was not rewritten.

### Public web migration

Reviewed/left materially unchanged:

- `docs/migrations/PUBLIC-WEB-CUTOVER.md`

Its production-cutover conclusion remains compatible with the current architecture: the public portfolio is served from Cloudflare Pages rather than depending on the normal homelab origin. Its PR #16 automation note remains current as of the review date.

### Network

- `docs/network/SWITCH-PORT-MAP.md`
- `docs/network/ROUTER-RESET-PLAN.md`

The switch port map now records current evidence separately from future repatching intent. Port 24 is not described as an active SPAN destination.

### Hardware

Reconciled:

- `docs/hardware/PROXMOX.md`
- `docs/hardware/media-01.md`

New current hardware pages:

- `docs/hardware/Proxmox-2.md`
- `docs/hardware/docker-01.md`

Reviewed/retained as historical evidence rather than rewritten:

- `docs/hardware/TestServer.md`
- `docs/hardware/ids-01.md`
- `docs/hardware/PVE2-HARDWARE-AUDIT-2026-09-08.md`
- `docs/migrations/PROXMOX-SECOND-NODE-2026-09-07.md`

`docs/hardware/admin-01.md` was already substantially current and did not require a broad rewrite.

### IaC documentation

- `IaC/README.md`
- `IaC/ansible/README.md`

Inventory-group wording now distinguishes a provisioned host from a deployed application, notably for `edge-01`. Protected Pi-hole configuration and the retained `birdnet-01.yml` filename/current `docker-01` target distinction are documented.

## Repository documentation inventory outcome

The review explicitly inventoried:

- root `README.md`;
- all files under `docs/architecture/`;
- all files under `docs/hardware/`;
- all files under `docs/migrations/`;
- all files under `docs/network/`;
- all files under `production docs/`;
- `runbooks/README.md` and `runbooks/registry.yml`;
- IaC README surfaces relevant to current host/service ownership.

This means the pass was not limited to files found by the original stale-term grep.

## Follow-on infrastructure changes after the review

### DNS local-record parity — resolved 12 September 2026

The documentation review identified a real parity defect: `dns-02 .50` did not resolve `dns-01.jameshouse` because the shared `pihole_local_hosts` list contained only the `dns-02 .50` resolver record and relied on a per-host self-record for the other entry.

Follow-on work:

- added `192.168.2.51 dns-01.jameshouse dns-01` to the shared managed host list;
- reconciled `dns-02` first using `playbooks/dns-local-records.yml --limit dns-02`;
- proved `dns-01.jameshouse -> 192.168.2.51` through `dns-02`;
- confirmed public recursion through `dns-02` remained healthy;
- reconciled both resolvers;
- proved both resolvers return `.51` for `dns-01` and `.50` for `dns-02`;
- second/final reconciliation reported `changed=0`, `failed=0`;
- committed the one-line IaC correction as `96850fc` on `fix/dns-local-record-parity-20260912`;
- opened homelab-platform PR #64.

The defect is therefore no longer an active operational gap. The full destructive DNS recovery workflow was not repeated, so its earlier recovery-validation date remains valid.

## Known remaining documentation / operational gaps

### High priority

1. **Backup/recovery implementation and runbooks**
   - deploy an actual backup platform;
   - configure jobs;
   - protect controller state/secrets appropriately;
   - perform restore tests.

2. **Proxmox node health/recovery runbook**
   - services;
   - pmxcfs/PVE management diagnosis;
   - guest impact and recovery ordering.

3. **Proxmox storage/SMART recovery runbook**
   - device identity;
   - SMART interpretation;
   - Proxmox storage status;
   - degraded-device replacement/recovery.

4. **Central logging**
   - Loki/Alloy is not deployed on `monitor-01`;
   - router syslog currently remains local only.

### Medium priority

5. **`edge-01` Cloudflare Tunnel**
   - workload not deployed;
   - design/deployment/recovery docs should be completed when implementation is approved.

6. **Mail relay recovery testing**
   - current service is documented and operational;
   - full rebuild/credential restoration/end-to-end relay recovery is not proven.

7. **Sensor Phase 2 / physical repatching**
   - wait for dedicated USB capture adapter;
   - design final switch patch layout;
   - repurpose port 24 as SPAN destination;
   - prove packet arrival before enabling engines.

8. **Network hardening/rebuild decisions**
   - unrestricted SNMP `public` community;
   - Telnet-only switch management;
   - STP/VLAN/rebuild decisions;
   - router clean-reset decision.

9. **media-01 firewall**
    - nftables remains designed but not deployed.

## Validation-date rule

A documentation edit does not equal a recovery test.

For example, DNS service health was rechecked on 12 September, but the destructive DNS rebuild/recovery workflow was not repeated. The DNS recovery runbook therefore retains its earlier full recovery-validation date while also recording the current-state review date.

Likewise, creating a current mail-relay service page does not mean a full mail-relay disaster-recovery exercise was performed.

## Current authority links

Use these first:

```text
README.md
docs/architecture/CURRENT-STATE.md
docs/architecture/TARGET-STATE.md
docs/migrations/MIGRATION-TRACKER.md
runbooks/README.md
runbooks/registry.yml
IaC/README.md
IaC/ansible/README.md
```

Historical plans/audits should be consulted for evidence and migration context, not current execution authority.