# Infrastructure as Code

`IaC/` is the authoritative location for homelab infrastructure and service configuration managed through Git.

The normal control point is `admin-01` (`192.168.2.48`). Terraform describes supported Proxmox guests and Ansible reconciles operating systems, services and shared platform configuration. Production state is discovered and validated before changes are applied.

Machine identity, addressing and lifecycle state are authoritative in `IaC/inventory/estate.json`. The Ansible inventory describes management/configuration scope and must agree with that canonical estate.

## Operating rules

- New Terraform, Ansible and deployment automation belongs under `IaC/`.
- Terraform provisions supported infrastructure; Ansible configures operating systems and services.
- Git contains desired state, never plaintext production secrets or Terraform state.
- Local `.tfvars`, `.env`, state files and protected credentials stay outside the repository.
- Production changes require an explicit target, reviewed plan/check, validation and a rollback/recovery path.
- Destructive operations must have an identity gate and explicit approval.
- Reconciliation should be idempotent; a second real Ansible run is expected to report `changed=0` for a stable service.
- Existing production resources must be imported/reconciled rather than recreated simply to make them match code.
- Host and workload ownership must remain explicit.
- New hostnames, IPs and VMIDs are allocated only after canonical/live collision checks.

## Layout

```text
IaC/
├── ansible/
│   ├── inventory/
│   ├── playbooks/
│   └── roles/
├── inventory/
│   └── estate.json
├── scripts/
└── terraform/
    └── proxmox/
        ├── cloud-01/
        ├── dns-02/
        ├── dns-resolver/
        ├── greenbone-01/
        ├── home-01/
        ├── komodo-01/
        ├── mail-relay/
        ├── monitor-01/
        ├── sensor-01/
        └── zabbix-01/
```

The older top-level `terraform/` directory predates this convention. Do not add new IaC there. It can be migrated separately after its references and state handling are verified.

## Current managed estate

As of 17 September 2026 the production Ansible inventory covers the following 15 Linux systems:

| Host / service | Address | Platform / role |
|---|---:|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / IaC controller / QNetd |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound CT100 on `PROXMOX` |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound CT101 on `Proxmox-2` |
| `monitor-01` | `192.168.2.52` | Prometheus/Grafana/Alertmanager/Blackbox/Loki VM202 on `Proxmox-2` |
| `cloud-01` | `192.168.2.53` | Production Nextcloud/PostgreSQL/Redis VM200 on `PROXMOX` |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix relay CT102 on `PROXMOX` |
| `sensor-01` | `192.168.2.55` | Operational Suricata/Zeek sensor VM201 on `PROXMOX` |
| `edge-01` | `192.168.2.56` | Reserved edge CT103 on `Proxmox-2`; Cloudflare Tunnel not deployed |
| `greenbone-01` | `192.168.2.57` | Greenbone vulnerability scanner VM203 on `Proxmox-2` |
| `komodo-01` | `192.168.2.58` | Komodo control plane CT104 on `PROXMOX` |
| `zabbix-01` | `192.168.2.59` | Zabbix monitoring platform CT105 on `PROXMOX` |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` cluster node 1 / NTP |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` cluster node 2 / NTP / Network Host Collector |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint / primary Proxmox NFS backup target |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host |

The `zabbix_agents` group contains all 15 systems. Zabbix Agent 2 is deployed across that group and the matching 15 Zabbix host objects are reporting through the active-agent template.

`home-01` is also an active production asset but is **not** part of the normal Ansible-managed Linux estate because HAOS is an appliance platform.

`ids-01`, `TestServer`, `DietPi` and the former `k3s-node-01` identity are not active platform targets. Historical references should remain historical rather than being reused as current-state authority.

## Active Home Assistant infrastructure

`home-01` is commissioned and active:

```text
hostname: home-01
address:  192.168.2.60
VMID:     204
node:     PROXMOX
platform: Home Assistant OS 18.2
Core:     2026.9.2
```

Its Terraform source is under `IaC/terraform/proxmox/home-01/`, and `IaC/scripts/deploy-home-01.sh` is the guarded build entry point.

Validated live state includes 2 vCPU, 4096 MiB RAM, 32 GiB `vm-ssd`, OVMF/q35, VirtIO network, QEMU guest agent, on-boot and Proxmox protection. The application endpoint is the proven port-80 URL `http://192.168.2.60/`; both managed DNS resolvers return the correct `home-01.jameshouse` record.

Native Home Assistant backup and manual Proxmox VM backup/integrity proof exist. VM204 is included in the `PROXMOX` 02:15 nightly schedule. The first unattended VM204 run, external monitoring and deeper restore proof remain separate evidence gates.

## Important current-state distinctions

### `edge-01`

The LXC host exists and is healthy, but no `cloudflared` workload is currently deployed. Do not treat membership in the `edge_hosts` inventory group as proof that the Cloudflare Tunnel application layer is operational.

### `sensor-01`

The dedicated capture path is operational. Suricata and Zeek are active on VM201 and consume the approved passive/SPAN traffic path. Older notes that describe capture as pending are historical and must not be used as current state.

### `cloud-01`

`cloud-01` is production, not staging. It uses a dedicated 200 GiB VM data disk mounted at `/srv/cloud-01-data`. The former 4 TB WD USB disk is not its production data disk.

The 17 September application audit confirmed Nextcloud/PostgreSQL/Redis health but also identified a live/IaC configuration-path difference for Redis authentication: live uses a mounted `redis.conf` while current IaC models the `.env`/`REDIS_PASSWORD` pattern. Treat this as configuration reconciliation work, not evidence that Redis is unhealthy.

### `komodo-01`

CT104 is an unprivileged Debian 13 LXC with Docker, MongoDB and Komodo Core commissioned. Application backup and isolated database-restore validation are proven. CT104 is included in the IaC backup job; first unattended scheduled proof remains open from the displayed 17 September audit evidence and Proxmox protection remains a separate decision.

### `zabbix-01`

CT105 is the dedicated Zabbix 7.0 platform using PostgreSQL/TimescaleDB, Zabbix Server, Agent 2 and Nginx. Application logical restore and manual whole-container backup integrity are proven. CT105 is included in the IaC backup job and an unattended 02:15 CT105 backup was observed on 17 September.

### `media-01`

The Kodi, Samba and NFS-backup workloads are operational. The 17 September audit found three IaC-managed Kodi add-ons absent: `weather.openmeteo`, `service.subtitles.opensubtitles-com` and `plugin.program.autocompletion`. Reconcile those separately after review; do not treat the healthy Kodi service itself as failed.

## Production cloud state

Current production design:

- Debian 13 VM, VMID 200, on `PROXMOX`;
- dedicated 200 GiB `scsi1` data disk;
- ext4 filesystem mounted at `/srv/cloud-01-data`;
- Nextcloud + PostgreSQL + Redis + cron;
- Nextcloud data at `/srv/cloud-01-data/data`;
- HTTP bound to `192.168.2.53:8080`;
- SMTP through `mail-relay-01` at `192.168.2.54:25`;
- explicit storage-identity and deployment-approval gates;
- protected application secrets supplied outside Git.

VM-level backup is proven. Application-consistent Nextcloud/PostgreSQL recovery remains a separate delivery requirement.

## Terraform state

Repository Terraform directories contain source configuration and lock files only. Durable runtime state is kept outside Git under the controller's protected state directory, for example:

```text
~/.local/state/homelab-iac/<service>/terraform/
```

Never copy a live `terraform.tfstate`, secret-bearing `.tfvars` file or provider credential into this repository.

## Ansible workflow

From `admin-01`:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-inventory --graph
ansible-playbook --syntax-check playbooks/<playbook>.yml
```

Use check mode when the playbook supports it, review the result, then perform the explicitly approved real reconciliation. Validate service health and run the playbook again to prove idempotence before merging the change.

See [`ansible/README.md`](ansible/README.md) for current inventory groups, playbooks, protected configuration paths and service-specific notes.

## Bootstrap versus reconciliation scripts

Scripts under `IaC/scripts/` fall into two categories:

- **bootstrap/build scripts** create a missing guest and deliberately refuse an existing production target/state;
- **reconciliation scripts** operate against an existing service and must preserve the safety gates in the underlying Terraform/Ansible code.

Do not use an initial-build script as an ad-hoc rebuild mechanism for an existing production guest.
