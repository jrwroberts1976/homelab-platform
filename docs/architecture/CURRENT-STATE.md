# Current-State Architecture

This document records the validated current homelab estate as of 12 September 2026.

It describes what is live now. Historical host identities and earlier migration assumptions remain useful for migration archaeology, but they are not current deployment authority.

## Authority model

`homelab-platform/IaC/` is the authoritative location for infrastructure and service configuration that has been migrated and validated there.

Legacy repositories may remain authoritative for areas not yet migrated. They must not be treated as current authority after their workload or configuration has been explicitly migrated and validated in `homelab-platform`.

## Active estate

| Asset | Address | Current role | State |
|---|---:|---|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / SSH jump / IaC controller | ACTIVE |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT 100 on `PROXMOX` | ACTIVE |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT 101 on `Proxmox-2` | ACTIVE |
| `monitor-01` | `192.168.2.52` | Prometheus, Grafana, Alertmanager and Blackbox, VM 200 on `Proxmox-2` | ACTIVE |
| `cloud-01` | `192.168.2.53` | Production Nextcloud/PostgreSQL/Redis, VM 200 on `PROXMOX` | ACTIVE |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix SMTP relay, CT 102 on `PROXMOX` | ACTIVE |
| `sensor-01` | `192.168.2.55` | Suricata/Zeek network-sensor platform, VM 201 on `PROXMOX` | ACTIVE — CAPTURE PHASE PENDING |
| `edge-01` | `192.168.2.56` | Cloudflare Tunnel edge connector, CT 103 on `Proxmox-2` | ACTIVE — DIRECT APP VALIDATION REMAINS |
| `PROXMOX` | `192.168.2.70` | Primary standalone Proxmox VE node | ACTIVE |
| `Proxmox-2` | `192.168.2.71` | Secondary standalone Proxmox VE node | ACTIVE |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi media endpoint | ACTIVE |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host | ACTIVE |
| ASUS RT-AC86U | `192.168.2.1` | Router / DHCP / AiMesh controller | ACTIVE |
| ASUS AiMesh node | `192.168.2.181` | Wireless mesh node | ACTIVE |
| ASUS AiMesh node | `192.168.2.218` | Wireless mesh node | ACTIVE |
| HP ProCurve 2510G-24 | `192.168.2.16` | Core managed switch; port 24 mirror/SPAN destination | ACTIVE |

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

Validated directly from the node on 12 September 2026:

| Type | ID | Name | State |
|---|---:|---|---|
| VM | 200 | `monitor-01` | running |
| LXC | 101 | `dns-01` | running |
| LXC | 103 | `edge-01` | running |

## DNS

The current resolver pair is:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

Both resolver workloads use Pi-hole + Unbound.

`192.168.2.48` is now `admin-01` and must not be treated as a DNS resolver. The retired `.242` resolver identity must not reappear in DHCP, DNS, monitoring or deployment configuration.

## Monitoring

`monitor-01` provides the central monitoring services.

Production wrapper validation on 12 September 2026 confirmed:

- Prometheus: PASS
- Grafana: PASS
- Alertmanager: PASS
- Blackbox Exporter: PASS

Prometheus currently has eight validated Node Exporter targets, all `up`:

```text
dns-01       192.168.2.51:9100
dns-02       192.168.2.50:9100
monitor-01   192.168.2.52:9100
sensor-01    192.168.2.55:9100
PROXMOX      192.168.2.70:9100
Proxmox-2    192.168.2.71:9100
media-01     192.168.2.195:9100
docker-01    192.168.2.220:9100
```

## Production cloud service

`cloud-01` is a production Nextcloud platform.

Validated state:

- Debian 13 VM on `PROXMOX`
- Nextcloud 34.0.3
- PostgreSQL healthy
- Redis healthy
- cron container running
- application endpoint on `192.168.2.53:8080`
- dedicated 200 GiB ext4 data filesystem at `/srv/cloud-01-data`
- user data at `/srv/cloud-01-data/data`
- zero failed systemd units

Redis runs as UID 999 / GID 1000. A persistence fault discovered during the estate audit was traced to the bind-mounted `/data` parent directory being owned by root. The live ownership was corrected and the Ansible role now reconciles the Redis state directory with the correct numeric ownership. `BGSAVE`, authenticated `PING`, RDB status, AOF status and Docker health were validated after the repair.

The production cloud deployment wrapper has subsequently completed its storage, application, container-health and idempotence gates successfully.

## Network sensor

`sensor-01` exists and is deliberately in Phase 1.

The management interface is live at `192.168.2.55`, but the dedicated capture interface has not yet been attached.

Until the dedicated USB/SPAN capture NIC is present and validated:

- Suricata remains stopped/disabled.
- Zeek remains stopped.
- the empty capture-interface setting is intentional.
- Ansible must not activate packet engines.

HP ProCurve port 24 remains the reserved mirror/SPAN destination for the future capture path.

## Mail relay

`mail-relay-01` is CT 102 on `PROXMOX`.

Validated state:

- Debian 13
- Postfix active
- SMTP listening on TCP/25
- zero failed systemd units

## Media

`media-01` at `192.168.2.195` is the Raspberry Pi 5 Kodi endpoint. Its historical `k3s-node-01` identity is retired.

The current media role includes Kodi, SMB media access, Chrony and Node Exporter. Remaining media hardening and observability work is incremental work rather than a host-role decision.

## Administration host

`admin-01` at `192.168.2.48` is the normal controller for homelab administration and IaC.

Production Ansible should normally be run from the checked-out `homelab-platform` repository on this host. It replaces the former use of TestServer as the normal administration/jump point.

## Docker / BirdNET host

The former TestServer Raspberry Pi 4 has been rebuilt as `docker-01` at `192.168.2.220`.

Its current dedicated workload is BirdNET-Go. The `TestServer` name remains historical and must not be used as an active deployment target.

## OpenIPMI on virtual guests

Debian's Prometheus Node Exporter package chain can install `prometheus-node-exporter-collectors`, `ipmitool` and `openipmi`.

On guests without an IPMI device this previously left an irrelevant failed `openipmi.service`. The Node Exporter Ansible role now:

- checks for `/dev/ipmi0` and `/dev/ipmi/0`;
- disables OpenIPMI when no IPMI hardware exists;
- clears the irrelevant failed state;
- retains the collector/tool packages;
- verifies zero failed units.

This was live-validated and proved idempotent on `dns-02` and `sensor-01`.

## Network infrastructure

### HP ProCurve

Known state:

- HP ProCurve 2510G-24
- management address `192.168.2.16`
- firmware Y.11.52
- VLAN 1 untagged across ports 1–24 in the audited state
- port 24 is the known mirror/SPAN destination
- Telnet administration is available
- SSH is not available

A wider network configuration clean-up remains a separate controlled change.

### ASUS

The ASUS RT-AC86U remains the router, DHCP authority and AiMesh controller.

Any future reset/rebuild must preserve WAN, DHCP, DNS, Wi-Fi, AiMesh, routing and rollback evidence before change.

## Remaining current-state validation gaps

The major compute and workload placements are now proven. Remaining validation work includes:

- direct application/process validation of `edge-01` / cloudflared;
- final `sensor-01` capture-NIC installation and packet-engine activation;
- backup/restore architecture and recovery testing;
- remaining router/switch device-level audit and rebuild work;
- continued observability expansion where useful.

These are outstanding work items, not reasons to treat already validated hosts as undiscovered.
