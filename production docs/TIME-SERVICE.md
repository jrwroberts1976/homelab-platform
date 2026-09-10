# Homelab Time Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Implementation:** Ansible / Chrony  
**Scope:** `192.168.2.0/24`

## Purpose

Time is a core infrastructure dependency. Proxmox, DNSSEC, TLS, logging,
monitoring, backup, automation and security tooling all depend on consistent
clocks.

The homelab uses the two physical Proxmox hosts as independent NTP servers.
There is deliberately no NTP VM or LXC, avoiding a circular dependency where
the hypervisor would need a guest to obtain correct time.

## Architecture

| Service alias | Address | Physical host | Role |
|---|---:|---|---|
| `ntp-01.jameshouse` | `192.168.2.70` | `PROXMOX` | Primary local NTP endpoint |
| `ntp-02.jameshouse` | `192.168.2.71` | `Proxmox-2` | Secondary local NTP endpoint |

## Core infrastructure host inventory

This table records the currently rebuilt core infrastructure from physical host
through service guest. Physical-NIC MAC addresses identify the Proxmox hosts;
the DNS rows record the LXC virtual Ethernet MAC addresses assigned by Proxmox.

| Hostname | IPv4 | Type | Interface / MAC | Services provided |
|---|---:|---|---|---|
| `PROXMOX` | `192.168.2.70` | Physical Proxmox VE host | `nic0` / `80:E8:2C:1C:55:D2` | Proxmox VE hypervisor; `ntp-01.jameshouse` Chrony/NTP; hosts `dns-02` CT 100 |
| `Proxmox-2` | `192.168.2.71` | Physical Proxmox VE host | `nic0` / `00:1A:9F:0C:30:3B` | Proxmox VE hypervisor; `ntp-02.jameshouse` Chrony/NTP; hosts `dns-01` CT 101 |
| `dns-01` | `192.168.2.51` | Debian LXC, CT 101 on `Proxmox-2` | `eth0` / `BC:24:11:C3:75:BA` | Pi-hole DNS filtering; Unbound recursive DNS; DNSSEC validation; local `jameshouse` records |
| `dns-02` | `192.168.2.50` | Debian LXC, CT 100 on `PROXMOX` | `eth0` / `BC:24:11:35:3B:11` | Pi-hole DNS filtering; Unbound recursive DNS; DNSSEC validation; local `jameshouse` records |

Both hosts:

- run Chrony directly on the Proxmox/Debian host;
- synchronise independently with the UK NTP pool;
- serve NTP only to `192.168.2.0/24`;
- listen on UDP/123;
- remain independently usable if the other Proxmox host is offline.

Critical infrastructure should be configured with the IP addresses
`192.168.2.70` and `192.168.2.71` so DNS is not required to obtain time.
The `ntp-01.jameshouse` and `ntp-02.jameshouse` records are operator-friendly
aliases, not a dependency for bootstrapping.

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

DNS resolvers may use the local NTP service, but the NTP service itself uses
external pool names only after the host has basic network/DNS connectivity.
No NTP guest is required for either hypervisor to boot.

## IaC ownership

The service is managed by:

```text
IaC/ansible/playbooks/proxmox-time.yml
IaC/ansible/roles/chrony_server/
IaC/ansible/inventory/hosts.yml
```

Do not hand-edit `/etc/chrony/chrony.conf` on either Proxmox host. Change the
role, review the diff, then apply through Ansible.

## Deployment

From TestServer:

```bash
cd ~/projects/homelab-platform/IaC/ansible

ansible-playbook --syntax-check playbooks/proxmox-time.yml
ansible-playbook playbooks/proxmox-time.yml --list-tasks
ansible-playbook playbooks/proxmox-time.yml
```

The role refuses to apply if the expected hostname, management IPv4 address or
`vmbr0` identity does not match the target.

## Validation

On either Proxmox host:

```bash
chronyc tracking
chronyc -n sources
ss -lunp | grep ':123'
systemctl is-active chrony
```

Expected state:

- `Leap status : Normal`;
- one upstream source marked `^*`;
- UDP/123 listening;
- `chrony` active.

External validation from a Linux client with Chrony available can be done
without changing the client's clock:

```bash
chronyd -Q -t 5 'server 192.168.2.70 iburst'
chronyd -Q -t 5 'server 192.168.2.71 iburst'
```

## Client policy

Managed infrastructure should use both servers:

```text
192.168.2.70
192.168.2.71
```

Do not configure only one local NTP server. Do not point the Proxmox hosts at
each other as their sole upstream source; each host must retain independent
external synchronisation.

## Failure behaviour

If one Proxmox host is unavailable, clients continue using the other local NTP
server. If Internet NTP is temporarily unavailable, Chrony continues to
discipline the local clock from its last measurements, but this design does
not deliberately advertise an unsynchronised local clock as authoritative.

If both local NTP servers are unavailable, restore at least one physical
Proxmox host first, then validate its external synchronisation before relying
on it for dependent infrastructure.

## Security boundary

NTP service is intentionally limited to the homelab subnet with:

```text
allow 192.168.2.0/24
```

No public NTP service is intended. Firewall policy should continue to block
unsolicited WAN access to UDP/123.

## Definition of done

The time service is production-ready when:

- both Proxmox hosts have the Ansible-managed Chrony configuration;
- both report normal synchronisation;
- both have a selected upstream source;
- both answer NTP on UDP/123 from the LAN;
- `ntp-01.jameshouse` resolves to `192.168.2.70`;
- `ntp-02.jameshouse` resolves to `192.168.2.71`;
- a normal client can query both endpoints;
- configuration is committed and reviewed in Git.
