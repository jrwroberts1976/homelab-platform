# TestServer Current-State Audit

Audit date: 2026-09-06  
Legacy hostname: `TestServer`  
Address: `192.168.2.220`  
Audit method: repository-controlled `scripts/audit-linux-host.sh`, executed locally as root in read-only mode.

Audit artifact on TestServer:

`/var/tmp/TestServer-audit-20260906T072451Z.txt`

SHA256:

`d6330f81585b919fe746a947f3013c82f00d329d76c979d2b2b9a0e25d801391`

## Identity

| Item | Current state |
|---|---|
| Hardware | Raspberry Pi 4 Model B Rev 1.5 |
| OS | Debian GNU/Linux 13 (trixie) |
| Kernel | 6.18.39+rpt-rpi-v8 |
| Architecture | arm64 / aarch64 |
| Virtualization environment | Bare metal |
| Legacy hostname | `TestServer` |

The current hostname is a discovery identifier only. It does not imply the machine's future role.

## CPU

| Item | Current state |
|---|---|
| CPU | ARM Cortex-A72 |
| Cores | 4 |
| Threads per core | 1 |
| Online CPUs | 0-3 |
| L2 cache | 1 MiB |

## Memory

| Item | Current state |
|---|---|
| RAM | 3.7 GiB |
| Used during audit | 2.3 GiB |
| Available during audit | 1.4 GiB |
| Swap | 2.0 GiB zram |
| Swap used during audit | approximately 780 MiB |

The host is already using compressed swap under its present workload.

## Storage

| Item | Current state |
|---|---|
| Primary device | `/dev/mmcblk0` |
| Capacity | 953.7 GiB |
| Root partition | 953.2 GiB ext4 |
| Root filesystem usable size | approximately 939 GiB |
| Used | approximately 266 GiB |
| Available | approximately 635 GiB |
| Root usage | 30% |
| LVM | Not installed |
| ZFS | Not installed |

The device is presented by Linux as MMC storage. The installed audit utilities could not provide SMART-style health data for it, so storage health is currently **UNKNOWN**, not failed.

## Raspberry Pi health

- Firmware throttle state during audit: `0x0`.
- CPU temperature during the initial hardware check: approximately 41.3 C.
- Thermal-zone CPU temperature later in the audit: approximately 43.3 C.
- No active thermal/throttling problem was observed.

## Network

| Item | Current state |
|---|---|
| Primary interface | `eth0` |
| Address | `192.168.2.220/24` |
| MAC | `d8:3a:dd:5a:51:44` |
| Link | 1000 Mb/s, full duplex |
| Gateway | `192.168.2.1` |
| DNS | `192.168.2.48`, `192.168.2.242` |
| Wi-Fi | Present but down |

The large number of Docker bridges and veth interfaces is a consequence of the present container estate and must not be mistaken for physical networking.

## Current platform services

System-level services observed include:

- Docker and containerd
- local Docker registry
- GitHub Actions self-hosted runner for `docker-env`
- CrowdSec firewall bouncer
- Redis
- rsyslog
- Zabbix Agent 2
- SSH
- unattended upgrades

One failed unit was present:

- `logrotate.service`

This should be investigated before destructive repurposing because it may affect retention of current logs needed during migration.

## Docker estate

Docker 26.1.5 was present.

At audit time:

- 34 containers existed.
- 33 were running.
- 1 was stopped.
- 312 images were stored.
- storage driver: overlay2.
- cgroup driver: systemd.

Detected Compose projects included:

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
- projects-jrwroberts-co-uk
- proxy-auth
- wud

The audit also captured per-container Compose ownership labels, bind mounts, named volumes and Docker networks without dumping environment variables or secret contents.

## Important runtime correction: Komodo

The live audit proves that Komodo **was running on TestServer** at audit time:

- `komodo-core`
- `komodo-periphery`
- `komodo-ferretdb`
- `komodo-postgres`

All four had been up for approximately 26 minutes when the audit ran.

This live evidence supersedes the earlier migration assumption that the Komodo bootstrap had not been deployed. No action is taken here; the running stack is now treated as current-state migration input.

## Other notable current workloads

Observed workloads include:

- BirdNET-Go plus BirdNET exporter
- Prometheus
- Alloy
- Loki, stopped at audit time
- node-exporter
- blackbox-exporter
- cAdvisor
- CrowdSec plus exporter
- Uptime Kuma / AutoKuma
- SmokePing
- LibreSpeed
- Nginx Proxy Manager
- Authelia
- Portainer plus agent
- Jenkins plus Docker-in-Docker
- Homepage and Dashy
- engineering portfolio site
- projects.jrwroberts.co.uk site
- dynamic DNS services
- WUD
- File Browser
- maintenance page

This confirms that the legacy TestServer is currently a highly consolidated multi-purpose host.

## Persistence observations

Persistent application data is primarily under:

- `/home/james/docker/data/`
- `/home/james/docker/stacks/`
- selected Docker named volumes
- legacy paths such as `/home/james/homelab/portainer/data`

The audit captured the mount relationship for every current container. These paths will form part of the workload-by-workload migration and backup review.

## Workload detectors

| Detector | Result |
|---|---|
| Docker | YES |
| k3s | NO |
| Pi-hole | NO |
| Unbound | NO |
| BirdNET | YES |
| Zabbix Agent 2 | YES |

## Current load snapshot

At audit time:

- load average: approximately `3.39 / 2.07 / 2.25`.
- BirdNET-Go was the highest CPU consumer at approximately 69%.
- Docker daemon was using approximately 28% CPU in the snapshot.
- Jenkins Java was the largest resident-memory process at roughly 532 MiB.
- Alloy was using roughly 263 MiB RSS.

This is a point-in-time snapshot, not a capacity benchmark, but it shows that the Pi is actively loaded by its existing consolidated role.

## Role-neutral audit conclusion

Hardware audit: **COMPLETE**  
Workload inventory: **CAPTURED FOR MIGRATION ANALYSIS**  
Future hostname: **UNASSIGNED**  
Future role: **UNASSIGNED**

No decision about this Raspberry Pi's future role should be made until the remaining physical hosts have been audited to the same standard.
