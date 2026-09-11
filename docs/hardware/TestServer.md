# TestServer — Decommissioned Hardware Record

> **Status: DECOMMISSIONED**  
> The legacy `TestServer` host identity and consolidated Docker role are retired. Do not use `192.168.2.220` or the `TestServer` hostname as an active management/jump, deployment, monitoring, or application target.

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
| Final audit date | 2026-09-06 |

Audit artifact:

`/var/tmp/TestServer-audit-20260906T072451Z.txt`

SHA256:

`d6330f81585b919fe746a947f3013c82f00d329d76c979d2b2b9a0e25d801391`

## Historical workload summary

Before decommissioning, `TestServer` was a highly consolidated host carrying Docker and a large number of services including monitoring, BirdNET-Go, Komodo, Nginx Proxy Manager, Authelia, Jenkins, public-site workloads, CrowdSec, Uptime Kuma, SmokePing and other supporting services.

Those workloads have been or are being redistributed into dedicated infrastructure. Their presence here is historical evidence only and must not be interpreted as current service placement.

## Physical hardware future

The Raspberry Pi 4 hardware is retained for rebuild as a dedicated BirdNET-Go server. That future role must be documented under its new/current hostname once the rebuild is complete; the `TestServer` identity itself remains retired.

## Status

Historical hardware audit: **COMPLETE**  
Legacy TestServer role: **DECOMMISSIONED**  
Active service role under this identity: **NONE**  
Physical Pi 4: **RETAINED FOR BIRDNET-GO REBUILD**