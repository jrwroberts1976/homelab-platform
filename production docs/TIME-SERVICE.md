# Homelab Time Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Implementation:** Ansible / Chrony  
**Scope:** `192.168.2.0/24`  
**Status:** operational  
**Last current-state review:** 12 September 2026

## Purpose

Time is a core infrastructure dependency. Proxmox, DNSSEC, TLS, logging, monitoring, backup, automation and security tooling all depend on consistent clocks.

The homelab uses the two physical Proxmox hosts as independent NTP servers. There is deliberately no NTP VM/LXC, avoiding a circular dependency where a hypervisor would need a guest to obtain correct time.

## Architecture

| Service alias | Address | Physical host | Role |
|---|---:|---|---|
| `ntp-01.jameshouse` | `192.168.2.70` | `PROXMOX` | Primary local NTP endpoint |
| `ntp-02.jameshouse` | `192.168.2.71` | `Proxmox-2` | Secondary local NTP endpoint |

Both hosts:

- run Chrony directly on the physical Proxmox/Debian host;
- synchronise independently with upstream NTP sources;
- serve NTP to `192.168.2.0/24`;
- listen on UDP/123;
- remain independently usable if the other Proxmox host is offline.

Critical infrastructure should use the IP addresses directly where bootstrapping must not depend on DNS.

## Current validation

The 12 September 2026 audit confirmed on both Proxmox hosts:

- `chrony` active;
- normal synchronisation state;
- stratum 3 during the observed check;
- UDP/123 listening;
- direct NTP query from `admin-01` succeeds;
- DNS aliases resolve to the intended `.70` / `.71` addresses.

Observed upstream/reference information during the audit included `labs.netweaver.uk`; upstream selection may change normally over time and should not be treated as a fixed dependency.

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

No NTP guest is required for either hypervisor to boot.

## IaC ownership

```text
IaC/ansible/playbooks/proxmox-time.yml
IaC/ansible/roles/chrony_server/
IaC/ansible/inventory/hosts.yml
```

Do not hand-edit the managed Chrony configuration and then treat that drift as authoritative. Change/review/apply through IaC.

## Controller

Normal reconciliation is launched from:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired TestServer identity must not be used as the normal controller.

Typical validation/reconciliation entry point:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook --syntax-check playbooks/proxmox-time.yml
ansible-playbook playbooks/proxmox-time.yml
```

## Validation

On either Proxmox host:

```bash
chronyc tracking
chronyc -n sources
ss -lunp | grep ':123'
systemctl is-active chrony
```

Expected healthy state includes:

- `Leap status : Normal`;
- a selected upstream source;
- UDP/123 listening;
- `chrony` active.

Direct client-side validation without changing the client clock:

```bash
chronyd -Q -t 5 'server 192.168.2.70 iburst'
chronyd -Q -t 5 'server 192.168.2.71 iburst'
```

## Client policy

Managed infrastructure should use both servers where supported:

```text
192.168.2.70
192.168.2.71
```

Do not configure only one local server when the client supports multiple sources. Do not configure the Proxmox hosts to depend solely on each other; each must retain independent upstream synchronisation.

## Failure behaviour

If one Proxmox host is unavailable, clients should continue using the other local NTP endpoint.

If both local NTP servers are unavailable, restore at least one physical Proxmox host first and validate its upstream synchronisation before relying on it for time-dependent infrastructure.

## Security boundary

The intended LAN service scope is:

```text
allow 192.168.2.0/24
```

No public NTP service is intended.

## Definition of done

The time service is operational because:

- both Proxmox hosts run the Ansible-managed Chrony service;
- both report healthy synchronisation;
- both answer NTP on UDP/123 from the LAN;
- both service aliases resolve correctly;
- `admin-01` successfully queried both endpoints during the 12 September audit.
