# Homelab Network and Service Layout — Historical Snapshot

> **SUPERSEDED / HISTORICAL**  
> Original mixed live/target snapshot: 9 September 2026.  
> This document is retained to show the migration design at that point in time. It must not be used as current operational authority.

Use instead:

- [`CURRENT-STATE.md`](CURRENT-STATE.md) — what is live now;
- [`TARGET-STATE.md`](TARGET-STATE.md) — what remains to be built/proven;
- [`../migrations/MIGRATION-TRACKER.md`](../migrations/MIGRATION-TRACKER.md) — migration progress;
- [`../network/SWITCH-PORT-MAP.md`](../network/SWITCH-PORT-MAP.md) — current switch evidence plus future repatching intent.

## Why this document was superseded

The 9 September diagram deliberately mixed current and planned state while the estate was moving quickly. By 12 September several of its major assumptions were already obsolete:

- `TestServer .220` is retired; the physical Pi 4 is `docker-01` and is no longer the controller;
- `.48` is `admin-01`, not a retired/legacy DNS endpoint;
- `cloud-01` is live production rather than planned;
- `mail-relay-01` is live production rather than planned;
- `sensor-01` is built and Phase 1 is complete rather than merely planned;
- `edge-01` exists as a host but the Cloudflare Tunnel workload is not deployed;
- `monitor-01` is operational rather than an implementation placeholder;
- current Node Exporter/Prometheus coverage is larger than the original five-target design;
- switch port 24 is not currently a SPAN destination: mirroring is disabled and the primary ASUS router is currently patched there.

Keeping those statements in a document labelled as a current/live layout would create ambiguity, so this file is now explicitly archival.

## Original design themes retained as history

The original layout captured several design ideas that remain useful context:

- two standalone Proxmox nodes;
- `.51 + .50` as the intended DNS pair;
- central monitoring on the secondary Proxmox host;
- separate passive network-sensor VM;
- eventual dedicated SPAN/capture path;
- internal SMTP relay rather than distributing Gmail credentials;
- Git-managed Terraform/Ansible for new workloads;
- retirement of consolidated legacy hosts.

Those ideas were subsequently implemented or refined in different ways.

## Current replacement view

As of 12 September 2026 the live core estate is:

```text
ASUS RT-AC86U .1
        |
        v
HP ProCurve 2510G-24 .16
        |
        +-- PROXMOX .70
        |     +-- CT100 dns-02 .50
        |     +-- CT102 mail-relay-01 .54
        |     +-- VM200 cloud-01 .53
        |     +-- VM201 sensor-01 .55
        |
        +-- Proxmox-2 .71
        |     +-- CT101 dns-01 .51
        |     +-- CT103 edge-01 .56 (host only; cloudflared not deployed)
        |     +-- VM200 monitor-01 .52
        |
        +-- admin-01 .48
        +-- media-01 .195
        +-- docker-01 .220
        +-- AiMesh .181 / .218
```

For detailed service state, backup gaps, switch-port evidence and future design, follow the current documents linked above.

## Historical handling rule

Do not update this file every time the live estate changes. Its purpose is now to preserve the 9 September transition context while pointing operators to the documents that carry current authority.
