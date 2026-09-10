# Ansible Service Configuration

This directory contains operating-system and service configuration for the rebuilt homelab.

## Controller

Run normal Ansible work from:

```text
admin-01.jameshouse
192.168.2.48
~/projects/homelab-platform/IaC/ansible
```

`TestServer` is no longer the preferred Ansible controller.

## Inventory

Authoritative inventory:

```text
inventory/hosts.yml
```

Current managed groups include DNS resolvers, Proxmox hosts, monitoring, administration, edge, sensor, media, mail relay and cloud hosts.

Important identities:

```text
admin-01     192.168.2.48   physical Pi 3 admin/jump host
dns-02       192.168.2.50   CT100 on PROXMOX
dns-01       192.168.2.51   CT101 on Proxmox-2
monitor-01   192.168.2.52   VM200 on Proxmox-2
cloud-01     192.168.2.53   VM200 on PROXMOX
mail-relay-01 192.168.2.54  CT102 on PROXMOX
sensor-01    192.168.2.55   VM201 on PROXMOX
edge-01      192.168.2.56   CT103 on Proxmox-2
PROXMOX       192.168.2.70   standalone PVE host
Proxmox-2     192.168.2.71   standalone PVE host
media-01     192.168.2.195  physical Raspberry Pi 5
```

`ids-01` is decommissioned and must not be restored to active inventory by copying historical files.

## Proxmox time service

`playbooks/proxmox-time.yml` configures the two standalone Proxmox hosts as redundant LAN NTP servers using the `chrony_server` role:

- `ntp-01.jameshouse` -> `PROXMOX` / `192.168.2.70`
- `ntp-02.jameshouse` -> `Proxmox-2` / `192.168.2.71`

Chrony runs directly on the physical hypervisors so LAN time does not depend on a VM/LXC.

Typical validation from `admin-01`:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook --syntax-check playbooks/proxmox-time.yml
ansible-playbook playbooks/proxmox-time.yml --list-tasks
ansible-playbook playbooks/proxmox-time.yml
```

## DNS service

The active resolver pair is now fully virtualized across the two Proxmox failure domains:

- `dns-01` — `192.168.2.51`, CT101 on `Proxmox-2`, Pi-hole + Unbound
- `dns-02` — `192.168.2.50`, CT100 on `PROXMOX`, Pi-hole + Unbound

The previous physical `.48` resolver role is retired. `192.168.2.48` is now `admin-01`.

`playbooks/dns-local-records.yml` is the focused playbook for reconciling Pi-hole local host records without re-running unrelated resolver configuration.

Current local records include `admin-01.jameshouse -> 192.168.2.48` and `edge-01.jameshouse -> 192.168.2.56`.

## Proxmox resolver management

`playbooks/proxmox-resolver.yml` manages resolver configuration on both standalone Proxmox nodes.

Approved state:

```text
search jameshouse
nameserver 192.168.2.51
nameserver 192.168.2.50
```

The role validates host identity and `vmbr0` before changing resolver state, keeps backups for changed files, and validates public/local DNS afterwards.

## Monitoring

`playbooks/monitoring.yml` manages the monitoring application layer on `monitor-01`.

Current operational core:

- Prometheus
- Grafana
- Alertmanager
- Blackbox Exporter

Fresh Loki/Alloy central logging is the next monitoring-platform phase. Do not copy the old TestServer logging stack as desired state.

## Edge

`edge-01` is already represented in inventory at `192.168.2.56` using root SSH with the `proxmox-automation` identity.

The LXC base is operational; a dedicated `cloudflared` role/playbook should be added for idempotent package/service/configuration management. Tunnel credentials must remain outside Git.

## Media

`media-01` is a **physical Raspberry Pi 5** at `192.168.2.195`, not a VM/LXC and not a k3s node.

Relevant playbooks:

- `playbooks/media-01-preflight.yml`
- `playbooks/media-01.yml`

## Safety model

- Use syntax/check/plan modes where they accurately represent the task.
- Do not rely on check mode for a pristine build where later validation depends on installation earlier in the same real run.
- Keep secrets outside Git and use `no_log` for secret-bearing tasks.
- Validate identity before applying host-specific configuration.
- Back up mutable production configuration before replacement when rollback matters.
- Follow real applies with health checks and an idempotence/no-drift run.
- Do not target decommissioned `ids-01` or treat TestServer as the normal controller.

See `../../runbooks/README.md` for the operational runbook catalogue.
