<!-- estate-authority: IaC/inventory/estate.json -->
# docker-01 — Current Hardware Record

**Status:** ACTIVE — DEDICATED BIRDNET-GO DOCKER HOST  
**Current-state review:** 6 October 2026

## Identity

| Item | Current state |
|---|---|
| Hostname | `docker-01` |
| Primary service address | `192.168.2.220/24` |
| Secondary Wi-Fi address | `192.168.2.221/24` |
| Hardware | Raspberry Pi 4 Model B Rev 1.5 |
| OS | Debian GNU/Linux 13 (trixie) |
| Running kernel | `6.18.50+rpt-rpi-v8` |
| Architecture | arm64 / aarch64 |
| Primary role | BirdNET-Go Docker host |
| Virtualization | Bare metal |

Earlier host identities for this hardware are historical only. <!-- historical -->

## Compute and storage

- approximately 3.7 GiB usable RAM;
- approximately 2 GiB zram swap;
- approximately 1 TB ext4 root storage;
- persistent BirdNET-Go state is the important non-reproducible data set on this host.

The host remains intentionally single-purpose so BirdNET-Go/audio processing retains predictable capacity.

## Network

| Interface/path | Address | Current role |
|---|---:|---|
| Ethernet | `192.168.2.220` | primary service/management path |
| Wi-Fi | `192.168.2.221` | secondary active path |

BirdNET-Go is published on TCP/8080 on the primary LAN path.

## Docker and BirdNET-Go

Current operating model:

- Docker active/enabled;
- BirdNET-Go is the production application workload;
- Compose source is `/opt/birdnet-go/compose.yml`;
- BirdNET-Go container health is monitored operationally;
- application/container version management is owned through the approved Komodo workflow rather than the OS patch workflow.

The exact BirdNET image tag is a dated runtime observation, not a permanent documentation pin.

## Komodo management

`docker-01` is a commissioned Komodo-managed Docker host.

Current controls include:

- Komodo Periphery connected outbound to Core on `komodo-01` (`192.168.2.58:9120`);
- no inbound Periphery management port deliberately exposed;
- remote host/container terminals disabled;
- Periphery identity persisted under `/config/keys`;
- steady-state operation without retained onboarding credentials;
- Git-managed Komodo resource definition for the host/workload;
- existing BirdNET workload adopted without forced recreation during commissioning.

The host remains dedicated to BirdNET-Go even though Komodo provides the management plane.

## Monitoring and patching

Current baseline includes:

- Node Exporter;
- Grafana Alloy;
- Zabbix Agent 2;
- Docker/container health visibility through the central platform;
- controlled patch-status telemetry.

The 5 October maintenance cycle included the Raspberry Pi kernel update and a controlled reboot. Post-reboot validation confirmed:

- running kernel `6.18.50+rpt-rpi-v8`;
- Docker active;
- BirdNET-Go healthy;
- Komodo Periphery running;
- WayVNC disabled/inactive;
- Alloy and Zabbix active;
- no failed systemd units;
- pending updates 0;
- reboot required no.

## Backup/recovery position

The estate now has an operational Proxmox backup platform, so the old statement that no estate-wide backup platform exists is obsolete.

The remaining `docker-01` gap is narrower: BirdNET-Go persistent application/configuration/history data still needs an explicit independent protection and restore proof. Container images and reproducible runtime artifacts are not the primary backup target.

## Role boundaries

Do not turn this host into the general administration server, DNS resolver, monitoring server, reverse proxy, security scanner or miscellaneous Docker consolidation host. Additional workloads require a separate reviewed design.

## Status

Hardware role: **ACTIVE**  
OS: **Debian 13**  
Kernel: **6.18.50+rpt-rpi-v8**  
Docker: **ACTIVE**  
BirdNET-Go: **ACTIVE**  
Komodo Periphery: **ACTIVE**  
Grafana Alloy: **ACTIVE**  
Zabbix Agent 2: **ACTIVE**  
Application-data backup/restore proof: **OUTSTANDING**
