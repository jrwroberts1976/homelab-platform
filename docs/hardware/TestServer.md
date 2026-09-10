# TestServer Current-State Audit

**Original audit:** 6 September 2026
**Current disposition updated:** 10 September 2026
**Hostname:** `TestServer`
**Address:** `192.168.2.220`
**Hardware:** Raspberry Pi 4 Model B Rev 1.5
**Current role:** legacy migration source
**Target role:** clean garden `birdnet-01` / BirdNET-Go host after retirement

The original audit proved that TestServer was a highly consolidated Docker/BirdNET/CI/monitoring host. It is no longer the preferred administration or monitoring authority. This document now treats that old runtime as migration evidence rather than the target architecture.

## Identity and hardware

| Item | Current / audited state |
|---|---|
| Hardware | Raspberry Pi 4 Model B Rev 1.5 |
| OS | Debian GNU/Linux 13 (trixie) |
| Architecture | arm64 / aarch64 |
| CPU | ARM Cortex-A72, 4 cores |
| RAM | approximately 3.7 GiB |
| Swap | approximately 2 GiB zram |
| Primary storage | approximately 1 TB MMC-presented device |
| Ethernet | 1 Gb/s |
| Address | `192.168.2.220/24` |

The original audit did not have SMART-style health visibility for the MMC-presented storage, so storage media health remains unknown rather than proven good.

## Current architectural status

Responsibilities already moved away from TestServer include:

- normal administration / IaC control -> `admin-01` (`192.168.2.48`);
- authoritative DNS -> `dns-01` (`.51`) + `dns-02` (`.50`);
- central metrics/alerting -> `monitor-01` (`.52`);
- public engineering portfolio -> Cloudflare Pages;
- router syslog receiver -> `monitor-01`;
- future selected internal ingress -> Cloudflare Tunnel through `edge-01` (`.56`).

The old TestServer Prometheus/Alloy/Loki configuration is not the desired-state source for the rebuilt monitoring/logging platform.

## Legacy Docker estate

The 6 September audit recorded Docker 26.1.5 with 34 containers, 33 running and one stopped. Compose/project ownership included:

- alloy
- availability
- birdnet-go
- cloudflare-ddns
- crowdsec
- dashboards
- engineering-portfolio
- komodo
- maintenance-page
- management
- monitoring
- projects
- proxy-auth
- wud

Notable workloads included BirdNET-Go, Prometheus, Alloy/Loki, Uptime Kuma, SmokePing, LibreSpeed, Nginx Proxy Manager, Authelia, Portainer, Jenkins/Docker-in-Docker, Dashy/Homepage, CrowdSec, WUD, File Browser, local registry and dynamic-DNS components.

Some of these have since been stopped or made non-authoritative. **Do not use this historical list as proof that a service is still running.** Re-check live state before retirement actions.

## Important runtime correction retained from the audit

Komodo was live on TestServer at the original audit, including Core, Periphery, FerretDB and PostgreSQL components. Container update/version operations are now intended to use Komodo, but ownership and final placement must be confirmed before TestServer is wiped.

## Persistence

Historically important persistent locations include:

- `/home/james/docker/data/`
- `/home/james/docker/stacks/`
- selected Docker named volumes
- legacy application-specific paths such as Portainer state
- BirdNET configuration/history/output that is intentionally retained

Every remaining persistent path must be classified as migrate, archive, rebuild-from-Git, or discard before reimage.

## Backup/recovery hard gate

A failed `homelab-backup-testserver.service` history remains unresolved. This is a hard gate against destructive cleanup of data, Compose definitions, named volumes or images solely for retirement.

Before reimage:

1. establish whether the failed job left any required data unprotected;
2. prove authoritative copies/repositories exist elsewhere;
3. test restore/recovery where the data is important;
4. record what can be safely discarded.

## Monitoring transition

TestServer may still expose legacy node/container/BirdNET metrics while retirement continues. A temporary firewall exception was previously introduced for `monitor-01` scraping of ports 9100/9105; remove such exceptions when the corresponding monitoring dependency is gone.

Fresh central logging will be built on `monitor-01`; old TestServer Alloy/Loki configuration should be retired after the new path is proven.

## External access transition

Nginx Proxy Manager and Authelia can be retired once Cloudflare Tunnel + Access is proven for every service that still needs remote access.

Target path:

```text
Internet -> Cloudflare Access -> Cloudflare Tunnel -> edge-01 -> selected service
```

Do not replace the old proxy/auth stack with ad-hoc router port-forwards.

## CI / runner transition

The repository-specific GitHub Actions runner has been stopped/disabled with registration retained as rollback/reference. Jenkins and Docker-in-Docker remain retirement candidates. Confirm no production workflow depends on them before final removal.

## Target rebuild

The Raspberry Pi 4 is intended to become a clean garden BirdNET-Go appliance after all legacy dependencies are closed.

Target characteristics:

- clean supported OS install;
- hostname `birdnet-01`;
- BirdNET-Go plus only required supporting/monitoring components;
- administered from `admin-01`;
- Git/IaC-managed configuration where practical;
- explicit backup/recovery for retained BirdNET state;
- no carry-forward of the general-purpose legacy Docker estate.

See `../migrations/TESTSERVER-RETIREMENT.md` for the controlled retirement sequence.

## Historical audit evidence

Original audit artifact:

```text
/var/tmp/TestServer-audit-20260906T072451Z.txt
```

SHA256:

```text
d6330f81585b919fe746a947f3013c82f00d329d76c979d2b2b9a0e25d801391
```

Historical audit status: **COMPLETE**
Current retirement status: **IN PROGRESS**
Reimage permission: **BLOCKED pending backup/recovery and remaining-dependency gates**
