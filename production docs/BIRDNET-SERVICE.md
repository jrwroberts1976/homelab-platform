<!-- estate-authority: IaC/inventory/estate.json -->
# BirdNET-Go Production Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `docker-01`  
**Primary IPv4:** `192.168.2.220`  
**Platform:** Raspberry Pi 4 Model B Rev 1.5 / Debian 13  
**Status:** OPERATIONAL / KOMODO-MANAGED DOCKER HOST  
**Last current-state review:** 6 October 2026

## Purpose

`docker-01` is a deliberately single-purpose Docker host for BirdNET-Go.

Earlier consolidated-host identities for this hardware are historical only. <!-- historical -->

## Current live state

Current validated operating model:

- Debian 13 / aarch64;
- running kernel `6.18.50+rpt-rpi-v8` after the controlled 5 October reboot;
- Docker active/enabled;
- BirdNET-Go production Compose workload under `/opt/birdnet-go/compose.yml`;
- BirdNET-Go published on TCP/8080;
- Node Exporter active;
- Grafana Alloy active;
- Zabbix Agent 2 active;
- Komodo Periphery active;
- no failed systemd units after maintenance;
- pending OS updates 0;
- reboot required no.

Exact BirdNET-Go image tags are dated runtime observations and should not be treated as permanent documentation pins.

## Network

Primary service identity:

```text
docker-01
192.168.2.220
```

A secondary Wi-Fi address at `.221` may also be present, but `.220` is the documented production path.

Important listeners:

```text
22/TCP    SSH
8080/TCP BirdNET-Go
9100/TCP Node Exporter
```

The host is LAN/VPN administered and is not an Internet-facing application server.

## Komodo management

`docker-01` is a commissioned Komodo-managed host.

Current controls include:

- Periphery outbound to Komodo Core on `komodo-01` (`192.168.2.58:9120`);
- no deliberately published inbound Periphery management listener;
- remote host/container terminals disabled;
- persisted Periphery identity under `/config/keys`;
- steady-state operation without retained onboarding credentials;
- Git-managed Komodo resource definition;
- existing BirdNET workload adopted without forced recreation.

Routine container/application version management belongs to Komodo rather than the OS patch workflow.

## Monitoring and logging

Current central coverage includes:

- ICMP/availability;
- Node Exporter host metrics;
- Grafana Alloy/Loki logging;
- Zabbix Agent 2;
- Docker/container health visibility;
- patch telemetry.

Add service-specific BirdNET checks only where they are actionable, such as web availability, audio/capture health or persistent-state growth.

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

The filename is an implementation interface; the current host identity remains `docker-01`.

Normal reconciliation runs from `admin-01`.

## Role boundary

Keep `docker-01` focused on BirdNET-Go. Do not use the presence of Docker as justification for general-purpose workload consolidation.

## Persistent data / backup position

The estate **does** have an operational Proxmox guest-backup platform, so the previous claim that no production backup platform exists is obsolete.

However, that platform does not automatically protect this physical Raspberry Pi's BirdNET-Go application state.

The current BirdNET-specific gap is to identify, protect and restore-test non-reproducible state such as:

- application configuration not already managed in Git/IaC;
- database/history;
- recordings or retained analysis data;
- audio/device calibration/state where applicable.

Do not spend primary backup capacity on reproducible container images/cache.

## Recovery model

1. rebuild supported Debian on the Raspberry Pi 4 if required;
2. restore approved SSH/IaC access;
3. reconcile the host through Ansible;
4. restore only required persistent BirdNET-Go state;
5. validate audio/device access;
6. validate Docker, BirdNET-Go and TCP/8080;
7. validate Komodo Periphery, Node Exporter, Alloy and Zabbix;
8. run a second reconciliation and require no unintended drift.

## Definition of operational state

The service is operational when `docker-01` is reachable on `.220`, Docker/BirdNET-Go are healthy, TCP/8080 is available, Komodo/monitoring agents are healthy and no failed systemd units are present.

## Outstanding work

- explicit BirdNET persistent-data backup policy;
- restore proof for that persistent state;
- service-specific monitoring only where useful.
