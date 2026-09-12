# BirdNET-Go Production Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `docker-01`  
**Primary IPv4:** `192.168.2.220`  
**Platform:** Raspberry Pi 4 Model B Rev 1.5 / Debian 13  
**Status:** operational  
**Last current-state review:** 12 September 2026

## Purpose

`docker-01` is a deliberately single-purpose Docker host for BirdNET-Go.

The physical Raspberry Pi 4 formerly carried the retired `TestServer` identity and a large consolidated Docker estate. That design has been retired. Current intent is to keep this host focused on BirdNET-Go rather than rebuilding the old general-purpose workload set.

## Current live state

Validated 12 September 2026:

- Debian 13 / aarch64;
- Docker active/enabled;
- one Docker Compose project: `birdnet-go`;
- one BirdNET-Go application container running;
- container health: healthy;
- BirdNET-Go published on TCP/8080;
- Node Exporter active on TCP/9100;
- Prometheus ICMP and Node Exporter targets healthy;
- zero failed systemd units.

## Compose/application

Compose path:

```text
/opt/birdnet-go/compose.yml
```

Observed application image during the audit:

```text
ghcr.io/tphakala/birdnet-go:20260823
```

The image tag above is evidence of the 12 September state, not a permanent version pin for documentation. Container version/update policy should follow the approved operational workflow, with routine Docker application/version management moving toward Komodo where appropriate.

## Network

Primary documented service identity:

```text
docker-01
192.168.2.220
```

The host also had Wi-Fi active at `.221` during the audit, but the wired `.220` path is the primary service path.

Current wired evidence:

- Ethernet MAC `d8:3a:dd:5a:51:44`;
- HP ProCurve port 23;
- 1 Gbps full-duplex switch link.

BirdNET-Go application listener:

```text
TCP/8080
```

Node Exporter:

```text
TCP/9100
```

## Monitoring

Current central monitoring includes:

- ICMP probe to `.220`;
- Node Exporter scrape at `.220:9100`.

Both were healthy in the 12 September monitoring audit.

Future service-specific monitoring should be added only where it gives useful operational signals, for example application availability, capture/audio health or storage/database growth.

## IaC ownership

Ansible inventory group:

```text
birdnet_hosts
```

Current target:

```text
docker-01 -> 192.168.2.220
```

The retained playbook filename is:

```text
IaC/ansible/playbooks/birdnet-01.yml
```

The historical-looking filename does not change the current host identity; the playbook targets `docker-01` through inventory.

## Controller

Normal reconciliation is launched from:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired TestServer identity must not be used as the current controller.

## Role boundary

Do not silently reintroduce the former TestServer container estate onto `docker-01`.

Additional workloads require an explicit placement decision and should not be justified merely because Docker is already installed.

## Persistent data / backup gap

The current estate does not yet have an active production backup platform.

Identify which BirdNET-Go state is not reproducible from Git/container deployment, such as:

- application configuration not already managed in IaC;
- database/history;
- recordings or analysis data intended to be retained;
- device/audio-specific calibration/state where applicable.

Protect those assets through the future backup design. Do not waste primary backup capacity on reproducible container images/cache.

See:

```text
docs/architecture/BACKUP-STRATEGY.md
```

## Recovery model

Recovery should be application/data focused:

1. rebuild supported Debian on the Raspberry Pi 4 if required;
2. restore SSH/IaC access;
3. reconcile the BirdNET host through the approved Ansible path;
4. restore only the required persistent BirdNET-Go state;
5. validate audio/device access;
6. validate container health and TCP/8080;
7. validate Node Exporter/central monitoring;
8. run a second reconciliation and require no unintended drift.

Do not restore the former TestServer OS/container estate as the normal recovery method.

## Definition of current operational state

The service is operational because:

- the host is live at `.220`;
- Docker is active;
- exactly one intended Compose project/application container is present;
- BirdNET-Go reports healthy;
- TCP/8080 is published;
- Node Exporter monitoring is healthy;
- zero failed systemd units were observed.

Outstanding work:

- explicit persistent-data backup policy;
- restore testing;
- service-specific monitoring only where useful;
- container lifecycle integration with the approved Komodo workflow where appropriate.
