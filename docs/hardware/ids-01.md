# ids-01 Current-State Audit

Audit date: 2026-09-06  
Legacy hostname: `ids-01`  
Address: `192.168.2.242`  
Audit method: repository-controlled `scripts/audit-linux-host.sh`, executed locally as root in read-only mode.

Audit artifact on ids-01:

`/var/tmp/ids-01-audit-20260906T072950Z.txt`

SHA256:

`9c68b98add0a354a3dbfe7765e3cf0256a42e20405f5e6a842fa6ef2b0ae6981`

## Identity

| Item | Current state |
|---|---|
| Hardware | ASUS ZenBook UX482EAR |
| OS | Debian GNU/Linux 13 (trixie) |
| Kernel | 6.12.107+deb13-amd64 |
| Architecture | x86-64 |
| Firmware | UX482EAR.308 dated 2023-10-05 |
| Legacy hostname | `ids-01` |

The current hostname is a discovery identifier only. It does not imply the machine's future role.

## CPU

| Item | Current state |
|---|---|
| CPU | 11th Gen Intel Core i5-1155G7 @ 2.50 GHz |
| Cores | 4 |
| Threads | 8 |
| Threads per core | 2 |
| Virtualization | VT-x |
| L3 cache | 8 MiB |

## Memory

| Item | Current state |
|---|---|
| RAM | approximately 15 GiB |
| Used during audit | approximately 4.6 GiB |
| Available during audit | approximately 10 GiB |
| Swap | approximately 15.7 GiB |
| Swap used during audit | approximately 1.3 GiB |

This is currently the strongest audited host by RAM capacity.

## Storage

| Item | Current state |
|---|---|
| Primary device | HFM512GD3JX013N NVMe |
| Capacity | 476.9 GiB |
| Root partition | 460.3 GiB ext4 |
| Root filesystem usable size | approximately 452 GiB |
| Used | approximately 120 GiB |
| Available | approximately 310 GiB |
| Root usage | 28% |
| LVM | Not installed |
| ZFS | Not installed |

### NVMe health

SMART health passed.

- Temperature: approximately 31 C.
- Percentage used: 0%.
- Data written: approximately 20.7 TB.
- Media/data integrity errors: 0.

Storage health is currently **GOOD**.

## Network

| Item | Current state |
|---|---|
| Active interface | `wlo1` |
| Address | `192.168.2.242/24` |
| Wi-Fi MAC | `08:6a:c5:87:21:34` |
| Ethernet adapter | `enx001a9f0c303b` |
| Ethernet capability | 1000 Mb/s full duplex |
| Ethernet link during audit | DOWN |
| Gateway | `192.168.2.1` |
| DNS | `192.168.2.48`, `192.168.2.242` |

The machine was using Wi-Fi as its live network path. The wired adapter supports gigabit Ethernet but had no link during the audit.

This matters for future role assignment: any latency-sensitive, high-throughput, monitoring, storage, backup or security role should be evaluated with the host wired.

## Current platform services

System-level services observed include:

- Docker and containerd
- Alloy
- CrowdSec and firewall bouncer
- Prometheus node exporter
- SMART monitoring
- Suricata
- Zabbix Agent 2
- SSH
- unattended upgrades

One failed unit was present:

- `docker-compose-version-sync.service`

This should be reconciled during the rebuild rather than carried forward automatically.

## Docker estate

Docker 29.7.2 was present.

At audit time:

- 31 containers existed.
- 24 were running.
- 7 were stopped.
- 42 images were stored.
- storage driver: overlayfs.
- cgroup driver: systemd.

Detected Compose projects included:

- greenbone-community-edition
- monitoring
- nebula-sync
- pihole-secondary
- restic-server

## Current workloads

### Monitoring

The host currently runs:

- Grafana
- Prometheus
- Loki
- Blackbox Exporter
- cAdvisor
- WUD
- Alloy as a host service
- Prometheus node exporter as a host service
- Zabbix Agent 2 as a host service

### Security

The host currently runs:

- Suricata as a host service
- CrowdSec as a host service
- CrowdSec firewall bouncer
- Greenbone Community Edition as a multi-container Docker stack

The Greenbone stack includes gvmd, PostgreSQL, OpenVAS/ospd components, Redis and feed/data containers. Some helper/migration containers were stopped, which is normal for one-shot components but must be understood during migration.

### DNS

A containerized secondary DNS stack is present:

- `pihole-secondary`
- `pihole2-unbound`
- `nebula-sync`

Port 53 is bound on `192.168.2.242`.

The generic host-binary detector reported Pi-hole/Unbound as absent because these services are containerized. The live Docker inventory is authoritative for this host.

### Backup

A Restic REST server is running on port 8000.

Its persistent data is mounted from:

- `/home/homelab-backup/rest-server/tls`
- `/home/homelab-backup/remote-repositories`

This is migration-critical state and must not be destroyed until backup/recovery ownership has been explicitly redesigned and verified.

## Persistence observations

Important persistent paths include:

- `/home/james/docker/data/monitoring/`
- `/home/james/docker/stacks/monitoring/`
- `/home/james/docker/stacks/pihole-secondary/`
- `/home/james/docker/stacks/nebula-sync/`
- `/home/homelab-backup/`
- numerous named Greenbone Docker volumes

The Greenbone stack relies heavily on named Docker volumes for PostgreSQL, vulnerability-test feeds, gvmd data, OpenVAS state, sockets and certificates.

These are migration dependencies, not disposable container state.

## Thermal and load snapshot

Temperatures observed:

- CPU/package: approximately 61 C.
- ACPI zone: approximately 75 C.
- Wi-Fi: approximately 33 C.

Load average during the audit was approximately `0.31 / 0.50 / 0.60`.

Notable resident-memory consumers included:

- Loki: approximately 1.2 GiB RSS.
- Prometheus: approximately 475 MiB RSS.
- ospd-openvas: approximately 328 MiB RSS.
- Alloy: approximately 309 MiB RSS.
- Grafana: approximately 297 MiB RSS.

The host had substantial free RAM and low system load despite its current workload set.

## Role-neutral audit conclusion

Hardware audit: **COMPLETE**  
Workload inventory: **CAPTURED FOR MIGRATION ANALYSIS**  
Future hostname: **UNASSIGNED**  
Future role: **UNASSIGNED**

Strengths:

- x86-64
- 4 cores / 8 threads
- VT-x
- approximately 16 GiB RAM
- healthy 512 GB-class NVMe
- substantial free disk and memory capacity

Constraints to consider later:

- laptop form factor
- current live network path is Wi-Fi
- current workload set includes security, monitoring, DNS and backup responsibilities that need controlled migration
- thermal behaviour should be observed again under sustained load if this machine is selected for a heavier future role

No future-role decision should be made until the remaining physical hosts have been audited to the same standard.
