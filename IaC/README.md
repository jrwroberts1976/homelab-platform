# Infrastructure as Code

This directory is the authoritative location for new homelab Infrastructure-as-Code in `jrwroberts1976/homelab-platform`.

## Normal controller

Run day-to-day IaC from:

```text
admin-01.jameshouse
192.168.2.48
~/projects/homelab-platform
```

`TestServer` is now a legacy migration source and should not be used as the default controller for new work.

## Rules

- New Terraform/OpenTofu, Ansible and related deployment code belongs under `IaC/`.
- Terraform/OpenTofu provisions infrastructure; Ansible configures operating systems and services.
- Git contains desired state, not plaintext secrets.
- Terraform state and local `.tfvars` files must not be committed.
- Secret values are supplied through SOPS/age, protected environment files or another approved secret mechanism.
- Production changes require read-only discovery, a reviewed plan, validation and rollback/recovery consideration.
- Host/workload ownership must remain explicit.
- Hypervisors stay free of application Docker workloads; services belong in guests or approved physical hosts.

## Current infrastructure placement

### PROXMOX — 192.168.2.70

- CT100 `dns-02` — `192.168.2.50`
- CT102 `mail-relay-01` — `192.168.2.54`
- VM200 `cloud-01` — `192.168.2.53`
- VM201 `sensor-01` — `192.168.2.55`

### Proxmox-2 — 192.168.2.71

- CT101 `dns-01` — `192.168.2.51`
- CT103 `edge-01` — `192.168.2.56`
- VM200 `monitor-01` — `192.168.2.52`

The Proxmox hosts are standalone; no active two-node cluster is assumed by IaC.

## Current service state

- DNS: dual Pi-hole + Unbound resolvers operational at `.51` and `.50`.
- Monitoring: Prometheus/Grafana/Alertmanager/Blackbox operational on `monitor-01`.
- Central logging: fresh Loki/Alloy implementation pending on `monitor-01`.
- Edge: `edge-01` base LXC operational; `cloudflared`, tunnel and Access/MFA pending.
- Media: physical Raspberry Pi 5 `media-01` remains outside Proxmox and is managed through Ansible.
- TestServer: retirement source only; final target is a clean Raspberry Pi 4 BirdNET-Go build.

## Layout

```text
IaC/
├── terraform/
│   └── proxmox/
└── ansible/
    ├── inventory/
    ├── playbooks/
    └── roles/
```

The older top-level `terraform/` directory predates this convention. Do not add new IaC there; migrate references/state only as a separate reviewed cleanup.

## DNS management

The active DNS pair is:

```text
dns-01  192.168.2.51  CT101 on Proxmox-2
dns-02  192.168.2.50  CT100 on PROXMOX
```

`IaC/ansible/playbooks/dns-local-records.yml` reconciles managed local records without re-running the whole resolver build. `192.168.2.48` is `admin-01`; it is not a DNS resolver.

## Change flow

A normal change should follow this pattern:

1. discover current state read-only;
2. update IaC/documentation on a feature branch;
3. syntax/check/plan validation;
4. controlled live apply with backups where configuration files are changed;
5. post-change health validation;
6. prove idempotence/no drift where applicable;
7. update service/runbook evidence;
8. review/merge and clean the feature branch.

See `../runbooks/README.md` and `../docs/architecture/OUTSTANDING-WORK.md` for operational priorities.
