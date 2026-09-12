# Current-State Architecture

This document records the validated current homelab estate as of 12 September 2026.

It describes what is live now. Historical host identities and earlier migration assumptions remain useful evidence, but they are not current deployment authority.

## Authority model

`homelab-platform/IaC/` is the authoritative location for infrastructure and service configuration that has been migrated and validated there.

Legacy repositories may remain authoritative/reference sources for areas not yet migrated. They must not be treated as current authority after their workload or configuration has been explicitly migrated and validated in `homelab-platform`.

## Active estate

| Asset | Address | Current role | State |
|---|---:|---|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / SSH jump / IaC controller | ACTIVE |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT 100 on `PROXMOX` | ACTIVE |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT 101 on `Proxmox-2` | ACTIVE |
| `monitor-01` | `192.168.2.52` | Prometheus, Grafana, Alertmanager and Blackbox, VM 200 on `Proxmox-2` | ACTIVE |
| `cloud-01` | `192.168.2.53` | Production Nextcloud/PostgreSQL/Redis, VM 200 on `PROXMOX` | ACTIVE |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix SMTP relay, CT 102 on `PROXMOX` | ACTIVE |
| `sensor-01` | `192.168.2.55` | Suricata/Zeek network-sensor platform, VM 201 on `PROXMOX` | ACTIVE — PHASE 1 COMPLETE |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT 103 on `Proxmox-2` | HOST ACTIVE — CLOUDFLARED NOT DEPLOYED |
| `PROXMOX` | `192.168.2.70` | Primary standalone Proxmox VE node | ACTIVE |
| `Proxmox-2` | `192.168.2.71` | Secondary standalone Proxmox VE node | ACTIVE |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi media endpoint | ACTIVE |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host | ACTIVE |
| ASUS RT-AC86U | `192.168.2.1` | Router / DHCP / AiMesh controller | ACTIVE |
| ASUS AiMesh node | `192.168.2.181` | Wireless mesh node | ACTIVE |
| ASUS AiMesh node | `192.168.2.218` | Wireless mesh node | ACTIVE |
| HP ProCurve 2510G-24 | `192.168.2.16` | Core managed switch | ACTIVE |

## Retired identities

The following names must not be treated as active production hosts:

- `TestServer` — retired identity for the Raspberry Pi 4 now operating as `docker-01`.
- `DietPi` — retired identity for the Raspberry Pi 3 now operating as `admin-01`.
- `ids-01` — decommissioned.
- historical `k3s-node-01` identity associated with `192.168.2.195` — retired; the host is `media-01`.
- former `dns-02` at `192.168.2.242` — retired.

Historical hardware and audit documents remain useful evidence but are not live configuration authority.

## Proxmox platform

The two Proxmox nodes are intentionally standalone. The earlier cluster experiment was deliberately rolled back and no production design currently depends on Corosync or shared cluster membership.

### `PROXMOX` — `192.168.2.70`

Validated live workload placement:

| Type | ID | Name | State |
|---|---:|---|---|
| LXC | 100 | `dns-02` | running |
| LXC | 102 | `mail-relay-01` | running |
| VM | 200 | `cloud-01` | running |
| VM | 201 | `sensor-01` | running |
| VM | 9000 | template | stopped |
| VM | 9001 | template | stopped |

### `Proxmox-2` — `192.168.2.71`

Validated directly on 12 September 2026:

- ASUSTeK ZenBook UX482EAR
- Intel Core i5-1155G7, 4 cores / 8 threads
- approximately 15 GiB RAM plus 8 GiB swap
- Proxmox VE 9.2.2, kernel 7.0.2-6-pve
- `local` and `local-lvm` storage active
- Chrony active
- Node Exporter active on TCP/9100
- Alloy inactive
- zero failed systemd units

Live guests:

| Type | ID | Name | State |
|---|---:|---|---|
| VM | 200 | `monitor-01` | running |
| LXC | 101 | `dns-01` | running |
| LXC | 103 | `edge-01` | running |

## DNS

Current resolver pair:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

Both workloads run Pi-hole + Unbound and passed direct public-resolution and DNSSEC checks during the 12 September audit.

The local-record parity defect found during the documentation review was corrected through managed IaC on 12 September 2026. Both resolvers now return:

```text
dns-01.jameshouse -> 192.168.2.51
dns-02.jameshouse -> 192.168.2.50
```

The focused reconciliation and final two-resolver run both completed successfully and the resulting managed state was idempotent.

`192.168.2.48` is now `admin-01` and must not be treated as a DNS resolver.

## Monitoring

`monitor-01` provides the central monitoring services.

Validated 12 September 2026 after adding `mail-relay-01` host monitoring:

- Prometheus healthy
- Grafana healthy, version 13.2.1
- Alertmanager healthy
- Blackbox Exporter healthy
- 25 active Prometheus targets
- 25 targets `up`
- 0 active Prometheus alerts

Observed target coverage includes DNS TCP probes, ICMP probes, Proxmox HTTPS probes and Node Exporter targets across the core estate. `mail-relay-01 .54` now has both ICMP and Node Exporter coverage.

Loki and Alloy are **not deployed on `monitor-01`**. Router syslog is collected locally through rsyslog pending a later central logging phase.

## Production cloud service

`cloud-01` is a live production Nextcloud platform.

Validated state:

- Debian 13 VM on `PROXMOX`
- 32 GiB OS disk
- dedicated 200 GiB ext4 data disk mounted at `/srv/cloud-01-data`
- Nextcloud 34.0.3
- PostgreSQL 18.6-alpine healthy
- Redis 8.2.9-alpine healthy
- cron container running
- application endpoint `192.168.2.53:8080`
- zero failed systemd units

Redis persistence was repaired during the estate audit by correcting the bind-directory ownership to the container's required numeric UID/GID. Persistence and health were revalidated afterward and the IaC role was updated in the earlier production fix.

The former 4 TB WD USB disk is **not** the cloud production data disk.

Backup and restore proof for important cloud data is still outstanding.

## Network sensor

`sensor-01` Phase 1 is complete and validated.

Current state:

- Debian 13 VM at `192.168.2.55`
- Suricata 8.0.6 installed with AF_PACKET support
- Zeek 8.0.10 installed under `/opt/zeek`
- Node Exporter active
- management networking healthy
- zero failed systemd units
- only management NIC present; no dedicated capture NIC
- Suricata deliberately stopped/disabled
- Zeek deliberately stopped

Phase 2 waits for the dedicated USB capture adapter, switch repatching and packet-arrival validation.

Do not activate packet engines until the dedicated capture path exists and is proven.

## Edge host

`edge-01` is a running Debian 13 LXC, CT 103 on `Proxmox-2`, at `192.168.2.56`.

Current audit evidence shows:

- no `cloudflared` package/binary;
- no cloudflared service;
- no cloudflared process;
- no Docker/Podman requirement;
- zero failed systemd units.

The host is reserved for a future Cloudflare Tunnel connector. The connector workload is **not deployed**.

## Mail relay

`mail-relay-01` is CT 102 on `PROXMOX` at `192.168.2.54`.

Validated state:

- Debian 13
- Postfix active/enabled
- SMTP listening on `192.168.2.54:25`
- relayhost `[smtp.gmail.com]:587`
- TLS encryption required for upstream relay
- SASL enabled
- queue empty at validation time
- Node Exporter active on TCP/9100
- Prometheus ICMP target `up`
- Prometheus Node Exporter target `up`
- zero failed systemd units

The internal relay ACL is intentionally restricted to the currently configured infrastructure addresses. Adding monitoring did not alter the relay service or its ACL.

## Media

`media-01` at `192.168.2.195` is the Raspberry Pi 5 Kodi endpoint.

Current validated role includes:

- Kodi active/enabled
- LightDM disabled
- Samba active/enabled
- SMB on TCP/445
- Chrony using the local Proxmox time service
- Node Exporter active on TCP/9100
- zero failed systemd units

The intended nftables policy is not deployed yet.

## Administration host

`admin-01` at `192.168.2.48` is the normal controller for homelab administration and IaC.

Production Ansible should normally be run from the checked-out `homelab-platform` repository on this host. It replaces the former use of TestServer as the administration/jump point.

## Docker / BirdNET host

The former TestServer Raspberry Pi 4 is now `docker-01` at `192.168.2.220`.

Validated state:

- Raspberry Pi 4 Model B Rev 1.5
- Debian 13 / aarch64
- Docker active/enabled
- one Compose project: `birdnet-go`
- one running healthy `birdnet-go` container
- BirdNET-Go exposed on TCP/8080
- Node Exporter active on TCP/9100
- zero failed systemd units

The host also has Wi-Fi at `.221`; the wired `.220` path is the primary documented service identity.

## Backup posture

The 12 September audit found **no active production backup platform**:

- zero scheduled Proxmox guest backup jobs on either node;
- no Proxmox Backup Server;
- no active Restic/Backrest service on the audited active estate;
- no mounted production backup repository;
- restore testing not proven.

The 4 TB WD disk attached to `PROXMOX` is blank/unallocated/unmounted and is POC/risk storage only. SMART overall health reports PASS but the device has two offline-uncorrectable sectors and an incomplete/aborted recent extended test. It must never be the sole copy of important data.

## Network infrastructure

### HP ProCurve

Validated 12 September 2026:

- HP ProCurve 2510G-24 / J9279A
- firmware Y.11.52
- management address observed at `192.168.2.16`
- VLAN 1 untagged on ports 1–24
- management configured as `dhcp-bootp`
- STP disabled
- port mirroring disabled
- SNMP community `public` configured as `Unrestricted`
- Telnet administration available; SSH unavailable

Current evidence-backed physical mappings include:

| Port | Current connection |
|---:|---|
| 3 | `media-01 .195` |
| 5 | Hive Hub `.7` (10 Mb/s link) |
| 17 | AiMesh node `.181` |
| 18 | `Proxmox-2 .71` and its guests |
| 19 | AiMesh node `.218` |
| 20 | `admin-01 .48` |
| 21 | `PROXMOX .70` and its guests |
| 23 | `docker-01 .220` wired Ethernet |
| 24 | primary ASUS router `.1` |

This is a dated current-state snapshot, **not the final patching plan**.

Port 24 is the planned future SPAN destination when the dedicated sensor USB NIC arrives. It is not currently a SPAN destination; mirroring is disabled and the router is currently patched there. The physical patching will be redesigned later as a separate controlled change.

### ASUS

The ASUS RT-AC86U remains gateway, DHCP authority and AiMesh controller. AiMesh nodes are at `.181` and `.218`.

Router syslog forwarding to `monitor-01 .52:5514/udp` is operational.

## Time service

The physical Proxmox hosts provide redundant LAN NTP:

```text
ntp-01.jameshouse -> 192.168.2.70
ntp-02.jameshouse -> 192.168.2.71
```

Both Chrony services were directly validated from `admin-01` on 12 September 2026.

## Remaining current-state work

Major outstanding work includes:

- design and deploy the `edge-01` Cloudflare Tunnel connector when approved;
- install/validate the dedicated `sensor-01` capture NIC and future SPAN path;
- build a real backup platform and prove restores;
- complete remaining router/switch redesign and hardening decisions;
- deploy central Loki/Alloy logging if still desired;
- finish service-specific observability and recovery documentation.

These are outstanding work items, not reasons to treat already validated hosts as undiscovered.
