# docker-01 — Current Hardware Record

> **Status: ACTIVE — DEDICATED BIRDNET-GO HOST**  
> Current-state review: 12 September 2026

`docker-01` is the Raspberry Pi 4 that formerly carried the retired `TestServer` identity. It has been rebuilt into a deliberately narrow Docker/BirdNET-Go role.

## Identity

| Item | Current state |
|---|---|
| Hostname | `docker-01` |
| Host-reported FQDN | `docker-01` (short hostname returned by `hostname -f`) |
| Primary service address | `192.168.2.220/24` |
| Secondary Wi-Fi address | `192.168.2.221/24` |
| Hardware | Raspberry Pi 4 Model B Rev 1.5 |
| OS | Debian GNU/Linux 13 (trixie) |
| Architecture | arm64 / aarch64 |
| Primary role | BirdNET-Go Docker host |
| Virtualization | Bare metal |

Local DNS provides the documented service name for `.220`; the host itself should not be described as having a configured FQDN until that is deliberately reconciled.

The retired `TestServer` identity must not be used as an administration, monitoring or deployment target.

## Compute

| Item | Current state |
|---|---|
| RAM | approximately 3.7 GiB usable |
| Swap | approximately 2 GiB zram |

The host is intentionally single-purpose. Capacity planning should preserve enough headroom for BirdNET-Go/audio processing rather than reintroducing the former consolidated Docker estate.

## Storage

Current root storage observed during the 12 September audit:

- approximately 953.7 GiB device capacity;
- ext4 root filesystem;
- approximately 939 GiB filesystem capacity;
- approximately 8.2 GiB used at audit time.

Persistent BirdNET-Go data/configuration should have an explicit backup policy. Container images and other reproducible runtime artifacts are not primary backup data.

## Network

Current interfaces:

| Interface/path | Address | Current role |
|---|---:|---|
| Ethernet | `192.168.2.220` | primary documented service path |
| Wi-Fi | `192.168.2.221` | secondary active path |

Routing observed:

- Ethernet default route metric approximately 100;
- Wi-Fi default route metric approximately 600.

Ethernet MAC:

```text
d8:3a:dd:5a:51:44
```

The HP ProCurve switch learns that MAC on **port 23**, validating the current wired patch.

The ARP view from `admin-01` returned the Ethernet MAC for both `.220` and `.221`; do not infer the Wi-Fi interface's physical switch mapping from that neighbour entry.

## Docker

Validated current Docker state:

- Docker active/enabled;
- Docker package/version observed: `26.1.5+dfsg1`;
- one Compose project: `birdnet-go`;
- Compose file: `/opt/birdnet-go/compose.yml`;
- exactly one BirdNET-Go application container running;
- application container healthy;
- BirdNET-Go published on TCP/8080.

Observed image:

```text
ghcr.io/tphakala/birdnet-go:20260823
```

This snapshot records what was running on 12 September 2026; image/version management should follow the approved container-operations workflow rather than being hard-coded forever in documentation.

## Komodo management

Commissioned on 18 September 2026 as the first Docker host managed through Komodo.

Validated state:

- Komodo Periphery `2.3.3`;
- deployed and maintained through the `komodo_periphery` Ansible role;
- outbound connection to Komodo Core at `http://192.168.2.58:9120`;
- no inbound Periphery management port published;
- remote host terminals disabled;
- remote container terminals disabled;
- Periphery private/public identity persisted through `/config/keys`;
- persistent identity proven across forced container recreation;
- active Periphery environment contains no onboarding credential in steady state;
- successful keyless login to Komodo Core proven;
- steady-state Ansible run completed with `changed=0`;
- BirdNET-Go remained running and healthy throughout commissioning.

The Komodo onboarding mechanism is bootstrap-only. It is not part of the normal host runtime configuration.

Komodo provides the management plane for this Docker host; it does not change the workload boundary. `docker-01` remains a dedicated BirdNET-Go host and must not become a replacement for the retired TestServer container estate.

## Monitoring

Node Exporter is active on TCP/9100.

Current Prometheus coverage:

- ICMP probe to `.220` — healthy;
- Node Exporter `.220:9100` — healthy.

## Current listeners of note

Observed service listeners include:

- SSH TCP/22;
- BirdNET-Go TCP/8080;
- Node Exporter TCP/9100;
- RPC-related TCP/111.

Do not assume every listener is intended for Internet exposure. The host is a LAN application endpoint.

## Role boundaries

`docker-01` should remain focused on BirdNET-Go unless a future design explicitly changes that decision.

Do not silently recreate the former TestServer workload set on this host.

In particular, current intent is **not** to make `docker-01` the primary:

- IaC/controller host;
- monitoring platform;
- DNS resolver;
- reverse proxy/public application host;
- Jenkins host;
- security scanner/sensor;
- general-purpose legacy Docker consolidation host.

## IaC ownership

Ansible inventory group:

```text
birdnet_hosts
```

Current target:

```text
docker-01 -> 192.168.2.220
```

The retained playbook filename `birdnet-01.yml` is an implementation interface; its current target is `docker-01`.

## Backup/recovery gap

The 12 September estate audit found no active estate-wide backup platform.

For this host, determine and protect the BirdNET-Go state that is not reproducible from the container image/IaC, such as configuration, database/history or other user-generated data.

See `docs/architecture/BACKUP-STRATEGY.md`.

## Status

Hardware role: **ACTIVE**  
OS: **DEBIAN 13**  
Docker: **ACTIVE**  
BirdNET-Go: **ACTIVE / HEALTHY AT AUDIT**  
Node Exporter: **ACTIVE**  
Primary wired switch port: **23**  
Legacy TestServer identity: **RETIRED**
