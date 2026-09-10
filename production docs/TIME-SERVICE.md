# Homelab Time Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Implementation:** Ansible / Chrony  
**Scope:** `192.168.2.0/24`
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`

## Purpose

Time is a core infrastructure dependency. Proxmox, DNSSEC, TLS, logging, monitoring, backup, automation and security tooling all depend on consistent clocks.

The homelab uses the two physical Proxmox hosts as independent NTP servers. There is deliberately no NTP VM or LXC, avoiding a circular dependency where a hypervisor would need a guest to obtain correct time.

## Architecture

| Service alias | Address | Physical host | Role |
|---|---:|---|---|
| `ntp-01.jameshouse` | `192.168.2.70` | `PROXMOX` | Primary local NTP endpoint |
| `ntp-02.jameshouse` | `192.168.2.71` | `Proxmox-2` | Secondary local NTP endpoint |

Both hosts are standalone Proxmox VE systems. Time service does not depend on Proxmox clustering.

## Current core hosting context

`PROXMOX` currently hosts `dns-02`, `mail-relay-01`, `cloud-01` and `sensor-01`. `Proxmox-2` currently hosts `dns-01`, `monitor-01` and `edge-01`. Chrony runs directly on the physical hosts so guest availability does not determine NTP availability.

Both hosts:

- synchronise independently with external UK NTP pool sources;
- serve NTP only to `192.168.2.0/24`;
- listen on UDP/123;
- remain independently usable if the other Proxmox host is offline.

Critical infrastructure should use the IP addresses `192.168.2.70` and `192.168.2.71` so DNS is not required to obtain time. The `ntp-01.jameshouse` and `ntp-02.jameshouse` records are operator-friendly aliases.

## Dependency order

```text
physical hardware
    |
    v
switch / router / LAN
    |
    v
PROXMOX .70 -------- Proxmox-2 .71
 chrony                  chrony
    \                    /
     \                  /
      +---- local NTP ---+
               |
       +-------+--------+
       |       |        |
     DNS     VMs      monitoring
```

## IaC ownership

```text
IaC/ansible/playbooks/proxmox-time.yml
IaC/ansible/roles/chrony_server/
IaC/ansible/inventory/hosts.yml
```

Do not hand-edit `/etc/chrony/chrony.conf` on either Proxmox host. Change the role, review the diff, then apply through Ansible.

## Deployment

From `admin-01`:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook --syntax-check playbooks/proxmox-time.yml
ansible-playbook playbooks/proxmox-time.yml --list-tasks
ansible-playbook playbooks/proxmox-time.yml
```

The role should refuse to apply if the expected hostname, management IPv4 address or `vmbr0` identity does not match the target.

## Validation

On either Proxmox host:

```bash
chronyc tracking
chronyc -n sources
ss -lunp | grep ':123'
systemctl is-active chrony
```

Expected state:

- normal leap/synchronisation state;
- an upstream source selected;
- UDP/123 listening;
- `chrony` active.

External validation from a Linux client with Chrony available can be done without changing the client's clock:

```bash
chronyd -Q -t 5 'server 192.168.2.70 iburst'
chronyd -Q -t 5 'server 192.168.2.71 iburst'
```

## Client policy

Managed infrastructure should use both local servers:

```text
192.168.2.70
192.168.2.71
```

Do not configure only one local NTP server. Do not point the Proxmox hosts at each other as their sole upstream source; each host must retain independent external synchronisation.

## Failure behaviour

If one Proxmox host is unavailable, clients continue using the other local NTP server. If both are unavailable, restore at least one physical Proxmox host first and validate its external synchronisation before relying on it for dependent infrastructure.

## Security boundary

NTP service is intentionally limited to the homelab subnet:

```text
allow 192.168.2.0/24
```

No public NTP service is intended. Firewall policy should continue to block unsolicited WAN access to UDP/123.

## Definition of done

The time service is production-ready when:

- both Proxmox hosts have the Ansible-managed Chrony configuration;
- both report normal synchronisation;
- both answer NTP on UDP/123 from the LAN;
- `ntp-01.jameshouse` resolves to `192.168.2.70`;
- `ntp-02.jameshouse` resolves to `192.168.2.71`;
- a normal client can query both endpoints;
- configuration is committed and reviewed in Git.
