# TestServer Retirement Plan

**Host:** `TestServer` / `192.168.2.220`
**Hardware:** Raspberry Pi 4 Model B Rev 1.5
**Target reuse:** clean garden `birdnet-01` / BirdNET-Go host
**Status:** retirement in progress; destructive cleanup blocked by backup/recovery gate

## Goal

Reduce the legacy multi-purpose TestServer to zero required platform dependencies, protect anything that must survive, then clean-rebuild the Raspberry Pi 4 as the dedicated garden BirdNET-Go host.

The target is **not** to preserve the historic general-purpose Docker host image.

## Current safety gate

Before deleting Docker data, Compose definitions, volumes, images or persistent directories solely for retirement, resolve and document the failed `homelab-backup-testserver.service` history and prove required data/recovery material is protected elsewhere.

A stopped service is not proof that its data can be deleted.

## Already moved or retired

The following responsibilities are no longer intended to make TestServer authoritative:

- administration / IaC controller -> `admin-01`;
- central metrics/alerting -> `monitor-01`;
- public engineering portfolio -> Cloudflare Pages;
- DNS -> `dns-01` + `dns-02` on Proxmox;
- router syslog receiver -> `monitor-01`;
- future external ingress -> Cloudflare Tunnel via `edge-01`.

Old TestServer Prometheus/Alloy/Loki state is reference material only. Fresh central logging will be built on `monitor-01`.

## Remaining retirement checks

Before final shutdown/reimage, establish live state for each remaining category and mark it either migrated, intentionally retired, or required on the future BirdNET host:

- BirdNET-Go and birdnet exporter;
- Nginx Proxy Manager and Authelia;
- Komodo Core/Periphery and related state;
- Jenkins and Docker-in-Docker;
- GitHub Actions self-hosted runner registration;
- local Docker registry;
- Uptime Kuma / AutoKuma;
- SmokePing;
- LibreSpeed;
- Portainer / agent;
- Dozzle;
- File Browser;
- WUD;
- CrowdSec components/exporters;
- any dynamic-DNS components;
- maintenance-page or other legacy public-web containers;
- remaining node exporter/cAdvisor/firewall exceptions;
- rsyslog/Postfix/Redis/Zabbix remnants;
- named Docker volumes and bind-mounted persistent data.

Do not assume historical audit state is still live; re-check before removal.

## External access cutover

Nginx Proxy Manager and Authelia may be retired only after Cloudflare Tunnel/Access has been proven for every internal service that still requires remote access.

The replacement path is:

```text
Internet -> Cloudflare Access -> Cloudflare Tunnel -> edge-01 -> selected service
```

Do not replace NPM/Authelia by opening direct router port-forwards.

## Monitoring cleanup

A temporary TestServer firewall exception previously allowed `monitor-01` to scrape ports `9100` and `9105`. Remove legacy monitoring exceptions/exporters when TestServer is no longer an approved monitoring target.

Central logging/metrics configuration must no longer depend on TestServer before reimage.

## CI / automation cleanup

The `docker-env` self-hosted GitHub Actions runner has been stopped/disabled while registration is preserved as rollback/reference. Before reimage:

- confirm no production workflow still requires it;
- remove registration only after replacement automation is proven;
- preserve any evidence required to recover or document Jenkins/runner behaviour;
- move container lifecycle/version ownership to the approved Komodo model.

## BirdNET data/configuration

Before reimage, explicitly identify what BirdNET material must survive:

- configuration;
- microphone/audio-device settings;
- species/location settings;
- database/history if retained;
- exporter/monitoring configuration;
- any recordings or analysis output that is intentionally preserved.

Back up only required state. Do not carry the complete old Docker estate into the clean BirdNET build.

## Rebuild target

After retirement gates pass:

```text
hostname: birdnet-01
hardware: Raspberry Pi 4
location: garden
authorized role: BirdNET-Go + required monitoring only
OS: clean supported Debian/Raspberry Pi OS base
management: admin-01 via SSH/Ansible
```

Networking, DNS, monitoring and backup records must be changed in the same controlled rebuild.

## Definition of done

TestServer retirement is complete when:

- no active production service depends on `TestServer` as a platform/controller;
- required persistent data and recovery material are protected;
- external ingress no longer depends on TestServer NPM/Authelia;
- monitoring/logging no longer depends on TestServer;
- legacy CI/runner responsibilities are retired or relocated;
- final live workload audit finds only intentionally preserved BirdNET migration data;
- the host can be safely reimaged without service loss;
- Git documentation records the transition to `birdnet-01`.
