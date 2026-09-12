# TestServer — Decommissioned Hardware Record

> **Status: DECOMMISSIONED**
>
> The legacy `TestServer` host identity and consolidated Docker role are retired. Do not use the `TestServer` hostname as an active management/jump, deployment, monitoring or application target.
>
> The physical Raspberry Pi 4 has been rebuilt and is now `docker-01` at `192.168.2.220`.

## Historical identity

| Item | Final audited state |
|---|---|
| Legacy hostname | `TestServer` |
| Legacy address | `192.168.2.220/24` |
| Hardware | Raspberry Pi 4 Model B Rev 1.5 |
| OS at final audit | Debian GNU/Linux 13 (trixie) |
| Architecture | arm64 / aarch64 |
| CPU | ARM Cortex-A72, 4 cores |
| RAM | approximately 3.7 GiB |
| Historical system storage | approximately 1 TB MMC-backed root filesystem |
| Final legacy-role audit date | 2026-09-06 |

Audit artifact:

```text
/var/tmp/TestServer-audit-20260906T072451Z.txt
```

SHA256:

```text
d6330f81585b919fe746a947f3013c82f00d329d76c979d2b2b9a0e25d801391
```

## Historical workload summary

Before decommissioning, `TestServer` was a highly consolidated host carrying Docker and a large number of services including monitoring, BirdNET-Go, Komodo, Nginx Proxy Manager, Authelia, Jenkins, public-site workloads, CrowdSec, Uptime Kuma, SmokePing and supporting services.

Those workloads have been or are being redistributed into dedicated infrastructure. Their presence in this historical record must not be interpreted as current placement.

## Current physical-hardware role

The same Raspberry Pi 4 hardware is now:

```text
hostname: docker-01
address:  192.168.2.220
role:     dedicated BirdNET-Go Docker host
```

The `TestServer` identity remains permanently retired.

Current configuration and operational documentation should refer to `docker-01`, not `TestServer`.

## Status

Historical hardware audit: **COMPLETE**

Legacy TestServer role: **DECOMMISSIONED**

Active service role under `TestServer` identity: **NONE**

Physical Raspberry Pi 4: **ACTIVE AS `docker-01` / BIRDNET-GO**
