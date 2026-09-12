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
- `dns-02` currently lacks the `dns-01.jameshouse` local record because of a known IaC parity defect.

### Monitoring

- `monitor-01 .52` is operational.
- Prometheus, Grafana, Alertmanager and Blackbox are healthy.
- 23 active Prometheus targets were observed; all 23 were healthy.
- zero active Prometheus alerts were observed.
- Loki and Alloy are not deployed on `monitor-01`.

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

### Runbooks / recovery

- `runbooks/README.md`
- `runbooks/registry.yml`
- `production docs/DNS-SERVICE-RECOVERY-PLAN.md`

Major correction: normal controller is `admin-01`, and `.48` is no longer a DNS fallback.

### Architecture / migration

- `docs/architecture/CURRENT-STATE.md`
- `docs/architecture/TARGET-STATE.md`
- `docs/architecture/BACKUP-STRATEGY.md`
- `docs/architecture/PROPOSED-LAYOUT.md`
- `docs/migrations/MIGRATION-TRACKER.md`
- `docs/migrations/GREENFIELD-REBUILD-PLAN.md`

`PROPOSED-LAYOUT.md` and `GREENFIELD-REBUILD-PLAN.md` are now explicitly historical/superseded rather than pretending their earlier placements are current.

### Production services

- `production docs/CLOUD-SERVICE.md`
- `production docs/MONITORING-SERVICE.md`
- `production docs/NETWORK-SENSOR-SERVICE.md`
- `production docs/MEDIA-SERVICE.md`
- `production docs/ROUTER-SYSLOG-SERVICE.md`
- `production docs/TIME-SERVICE.md`

New current service pages:

- `production docs/MAIL-RELAY-SERVICE.md`
- `production docs/BIRDNET-SERVICE.md`

### Network

- `docs/network/SWITCH-PORT-MAP.md`
- `docs/network/ROUTER-RESET-PLAN.md`

### Hardware

- `docs/hardware/PROXMOX.md`

New current hardware pages:

- `docs/hardware/Proxmox-2.md`
- `docs/hardware/docker-01.md`

Historical hardware/audit pages such as `TestServer.md`, `ids-01.md` and `PVE2-HARDWARE-AUDIT-2026-09-08.md` were intentionally retained as historical evidence rather than rewritten.

### IaC documentation

- `IaC/README.md`
- `IaC/ansible/README.md`

Inventory-group wording now distinguishes a provisioned host from a deployed application, notably for `edge-01`.

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

7. **DNS local-record parity**
   - fix `dns-02` missing `dns-01.jameshouse` through reviewed IaC;
   - do not paper over it with manual Pi-hole GUI drift.

8. **Sensor Phase 2 / physical repatching**
   - wait for dedicated USB capture adapter;
   - design final switch patch layout;
   - repurpose port 24 as SPAN destination;
   - prove packet arrival before enabling engines.

9. **Network hardening/rebuild decisions**
   - unrestricted SNMP `public` community;
   - Telnet-only switch management;
   - STP/VLAN/rebuild decisions;
   - router clean-reset decision.

10. **media-01 firewall**
    - nftables remains designed but not deployed.

## Validation-date rule

A documentation edit does not equal a recovery test.

For example, DNS service health was rechecked on 12 September, but the destructive DNS rebuild/recovery workflow was not repeated. The DNS recovery runbook therefore retains its earlier full recovery-validation date while also recording the current-state review date.

## Current authority links

Use these first:

```text
docs/architecture/CURRENT-STATE.md
docs/architecture/TARGET-STATE.md
docs/migrations/MIGRATION-TRACKER.md
runbooks/README.md
runbooks/registry.yml
IaC/README.md
IaC/ansible/README.md
```

Historical plans/audits should be consulted for evidence and migration context, not current execution authority.
