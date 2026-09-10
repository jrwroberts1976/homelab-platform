# ids-01 Historical Audit

**Original audit:** 6 September 2026
**Decommission status updated:** 10 September 2026
**Former hostname:** `ids-01`
**Former address:** `192.168.2.242`
**Lifecycle:** **DECOMMISSIONED / RETIRED**

`ids-01` is no longer an active homelab host. This document is retained only as historical evidence and migration archaeology. It must not be treated as a deployment, monitoring, DNS, backup, security or rollback target unless a task explicitly concerns historical cleanup/recovery evidence.

## Historical hardware identity

| Item | Audited state |
|---|---|
| Hardware | ASUS ZenBook UX482EAR |
| CPU | Intel Core i5-1155G7, 4 cores / 8 threads |
| RAM | approximately 15 GiB |
| Storage | 512 GB-class SK hynix NVMe |
| Architecture | x86-64 |
| Firmware | UX482EAR.308 |
| Network at audit | Wi-Fi active; gigabit USB Ethernet adapter present |

The hardware was later repurposed as the physical `Proxmox-2` host at `192.168.2.71`. Do not confuse the historical `ids-01` operating-system/workload snapshot with the current Proxmox-2 platform.

## Historical workloads

At the 6 September audit, `ids-01` carried a broad legacy workload set including:

- Grafana, Prometheus, Loki, Blackbox Exporter and Alloy;
- Suricata and CrowdSec;
- Greenbone Community Edition;
- containerized secondary Pi-hole/Unbound and Nebula Sync;
- Restic REST backup server;
- WUD and other supporting containers;
- Zabbix Agent 2 and node exporter.

Those responsibilities have been redesigned or moved. In particular:

- DNS is now `dns-01 .51` + `dns-02 .50` across the two Proxmox hosts;
- monitoring is now `monitor-01 .52` on `Proxmox-2`;
- central logging will be rebuilt fresh on `monitor-01` rather than restored from ids-01/TestServer state;
- passive sensing is assigned to `sensor-01 .55` on `PROXMOX`;
- the former `ids-01` hardware now serves as `Proxmox-2`, not as a general-purpose Docker/security host.

## Historical backup evidence

The original host included `/home/homelab-backup/` Restic-server state and remote repositories. Any historical backup references in this document are evidence only; current backup authority must be established from the rebuilt estate and tested restores.

## Historical storage health

The original audit reported the NVMe as healthy, with zero media/data-integrity errors and low wear. That evidence is useful for hardware history but does not replace current Proxmox host/storage monitoring.

## Why this file remains

Keep this document because it records:

- what services once lived on the old host;
- historical persistence paths that may explain archived backup data;
- the hardware identity before it became `Proxmox-2`;
- migration evidence that can help reconcile old repositories and backups.

Do **not** copy its old service list into current inventory or monitoring configuration.

## Historical audit artifact

```text
/var/tmp/ids-01-audit-20260906T072950Z.txt
```

SHA256:

```text
9c68b98add0a354a3dbfe7765e3cf0256a42e20405f5e6a842fa6ef2b0ae6981
```

Historical audit: **COMPLETE**
Active host status: **RETIRED**
Current hardware identity: **Proxmox-2 / 192.168.2.71**
