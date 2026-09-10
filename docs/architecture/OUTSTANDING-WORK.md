# Outstanding Work

**Updated:** 10 September 2026
**Controller:** `admin-01.jameshouse` / `192.168.2.48`

This register records approved or known next work for the current homelab. It is intentionally separate from historical migration notes so completed work is not confused with the active queue.

## 1. Cloudflare edge

`edge-01` is already built as Debian 13 LXC CT103 on `Proxmox-2` at `192.168.2.56`.

Completed:

- static LAN identity and local DNS record;
- root SSH via the `proxmox-automation` key;
- unprivileged LXC;
- `nesting=1` required for Debian 13/systemd mount behaviour;
- `/tmp` tmpfs capped at 192 MiB;
- systemd state `running` with zero failed units;
- outbound HTTPS and Cloudflare tunnel port 7844 connectivity validated.

Outstanding:

- install `cloudflared` from a controlled package source;
- create the Cloudflare Tunnel;
- register the connector without committing credentials;
- configure selected public hostnames/routes;
- place Cloudflare Access in front of administrative applications;
- prefer passkey/security-key capable MFA with TOTP fallback;
- use service authentication rather than interactive MFA for machine/API traffic;
- add monitoring and recovery guidance for the connector.

No inbound router port-forward is required for the Cloudflare Tunnel design.

## 2. Central logging

The metrics platform on `monitor-01` is operational: Prometheus, Grafana, Alertmanager and Blackbox Exporter are live.

Outstanding logging work:

- deploy a fresh Loki service on `monitor-01`;
- deploy/configure Alloy collectors for approved hosts and dedicated log sources;
- ingest `/var/log/homelab/router/rt-ac86u.log` from the validated router syslog receiver;
- define low-cardinality labels and retention;
- validate end-to-end log arrival and Grafana queries;
- add logging health metrics/alerts;
- retire old TestServer Alloy/Prometheus/Loki configuration only after the new path is proven.

The old TestServer logging stack is migration evidence, not the desired-state source.

## 3. TestServer retirement and BirdNET rebuild

`TestServer` (`192.168.2.220`) is a Raspberry Pi 4 legacy multi-purpose Docker host. It is no longer the administration controller.

Already retired/stopped from the legacy host include parts of the old dashboard/public-web and monitoring stack. Remaining work must be validated from live state before removal.

Hard gate before destructive cleanup:

- resolve/understand the failed `homelab-backup-testserver.service` history and prove required data/recovery material is protected.

Other retirement work includes:

- remove remaining Nginx Proxy Manager/Authelia dependencies after Cloudflare Access replacement is proven;
- reconcile Komodo/container-management ownership;
- remove legacy exporters/firewall exceptions when their monitoring dependency disappears;
- account for Jenkins/runner and any remaining Docker persistence;
- clean stale TestServer-only automation and SSH aliases.

Target reuse: clean-rebuild the Raspberry Pi 4 as the dedicated garden `birdnet-01` / BirdNET-Go host after retirement is complete.

## 4. Proxmox and storage

Both Proxmox nodes are operational as standalone hosts.

Outstanding:

- dedicated Proxmox node/service health runbook;
- dedicated SMART/storage diagnosis and recovery runbook;
- guest backup and restore policy with a tested restore path;
- complete the current WD 4 TB extended SMART test on `PROXMOX` and review the final self-test result plus SMART counters;
- do not treat the WD disk as the sole copy of irreplaceable data while its historical uncorrectable-sector evidence remains unresolved.

## 5. Network sensor and security

`sensor-01` exists as VM201 on `PROXMOX` at `192.168.2.55`.

Outstanding:

- finish Suricata/Zeek sensor deployment and validation;
- preserve the HP ProCurve port 24 SPAN/mirror design;
- document capture-path recovery and validation;
- keep vulnerability scanning and passive network sensing as separate roles.

## 6. Documentation and hygiene

- keep `admin-01` as the documented default controller;
- keep `ids-01` excluded from active inventory, monitoring and deployment scope;
- keep physical `media-01` documented as Raspberry Pi 5 at `192.168.2.195`;
- update diagrams whenever workload placement changes;
- remove obsolete Git branches only after content-equivalence or merge validation;
- keep the runbook registry synchronized with service documents in the same change.

## Completion rule

A task is not considered complete merely because a service starts. Completion requires the relevant combination of Git/IaC state, live validation, rollback/recovery evidence, monitoring and documentation to agree.
