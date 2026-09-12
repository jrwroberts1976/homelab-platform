# Infrastructure as Code

`IaC/` is the authoritative location for homelab infrastructure and service configuration managed through Git.

The normal control point is `admin-01` (`192.168.2.48`). Terraform describes supported Proxmox guests and Ansible reconciles operating systems, services and shared platform configuration. Production state is discovered and validated before changes are applied.

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

## Layout

```text
IaC/
├── ansible/
│   ├── inventory/
│   ├── playbooks/
│   └── roles/
├── scripts/
└── terraform/
    └── proxmox/
        ├── cloud-01/
        ├── dns-02/
        ├── dns-resolver/
        ├── mail-relay/
        ├── monitor-01/
        └── sensor-01/
```

The older top-level `terraform/` directory predates this convention. Do not add new IaC there. It can be migrated separately after its references and state handling are verified.

## Current managed estate

The Ansible inventory is the machine-readable authority for host addresses and service groups. As of 12 September 2026 the active estate represented by this IaC includes:

| Host / service | Address | Platform / role |
|---|---:|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / IaC controller |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound LXC on `PROXMOX` |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound LXC on `Proxmox-2` |
| `monitor-01` | `192.168.2.52` | Monitoring VM on `Proxmox-2` |
| `cloud-01` | `192.168.2.53` | Nextcloud VM on `PROXMOX` |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix relay LXC on `PROXMOX` |
| `sensor-01` | `192.168.2.55` | Network/security sensor VM on `PROXMOX`; Phase 1 complete |
| `edge-01` | `192.168.2.56` | Reserved edge LXC on `Proxmox-2`; Cloudflare Tunnel workload not deployed |
| `PROXMOX` | `192.168.2.70` | Primary standalone Proxmox VE host / NTP server |
| `Proxmox-2` | `192.168.2.71` | Secondary standalone Proxmox VE host / NTP server |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi media endpoint |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 Docker / BirdNET-Go host |

`ids-01`, `TestServer`, `DietPi` and the former `k3s-node-01` identity are not active platform targets. Historical references should remain historical rather than being reused as current-state authority.

## Important current-state distinctions

### `edge-01`

The LXC host exists and is healthy, but no `cloudflared` package/binary/service/process is currently deployed. Do not treat membership in the `edge_hosts` inventory group as proof that the Cloudflare Tunnel application layer is operational.

### `sensor-01`

The VM/toolchain are live and validated. The dedicated capture NIC and SPAN path are not present yet, so Suricata/Zeek remain deliberately stopped.

### `cloud-01`

`cloud-01` is production, not staging. It uses a dedicated 200 GiB VM data disk mounted at `/srv/cloud-01-data`. The former 4 TB WD USB disk is not its production data disk.

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

Backups, restore testing and full observability integration remain separate delivery workstreams; they are not reasons to treat the live Nextcloud deployment as staging.

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
