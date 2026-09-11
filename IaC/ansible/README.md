# Ansible service configuration

This directory contains operating-system and service configuration for guests provisioned from `IaC/terraform/`.


## Proxmox time service

`playbooks/proxmox-time.yml` configures the two standalone Proxmox hosts as
redundant LAN NTP servers using the `chrony_server` role:

- `ntp-01.jameshouse` -> `PROXMOX` / `192.168.2.70`
- `ntp-02.jameshouse` -> `Proxmox-2` / `192.168.2.71`

Chrony runs directly on the physical hypervisors so time service does not
depend on a VM or LXC being available. Both servers synchronise independently
to the UK NTP pool and serve only `192.168.2.0/24`.

Deploy from TestServer with:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook --syntax-check playbooks/proxmox-time.yml
ansible-playbook playbooks/proxmox-time.yml --list-tasks
ansible-playbook playbooks/proxmox-time.yml
```

See `production docs/TIME-SERVICE.md` for architecture, validation and client
policy.

## dns-02

`playbooks/dns-02.yml` configures CT 100 (`192.168.2.50`) as the secondary Pi-hole + Unbound resolver.

The live source baseline was captured from `dns-01` (`192.168.2.48`) on 7 September 2026:

- Pi-hole Core v6.4.3
- Pi-hole Web v6.6
- Pi-hole FTL v6.7
- Unbound 1.26.0
- Pi-hole upstream: `127.0.0.1#5335`
- Pi-hole DNSSEC: disabled because Unbound performs validation
- listening mode: `LOCAL`
- reverse servers: none
- CNAME records: none
- domain allow/deny rules: none
- client-specific group mappings: none
- groups: Default only
- five enabled subscribed blocklists

The retired previous `dns-02` record at `192.168.2.242` is intentionally not reproduced. A canonical `dns-02.jameshouse` record for the replacement resolver at `192.168.2.50` is added.

## Safety model

The role deliberately does not alter router DHCP/DNS advertisement or TestServer's current resolver list. `dns-01` remains the live dependency until direct validation and failover testing of `dns-02` succeeds.

Before applying, supply the Pi-hole web/API password only through the runner environment:

```bash
export PIHOLE_WEB_PASSWORD='...'
```

Do not commit that value. The role sends the password to Pi-hole's interactive `setpassword` command over stdin and marks the Ansible task `no_log`.

The official Pi-hole installer currently requires an existing configuration file for a true non-interactive first installation. The role seeds a minimal Pi-hole v6 `pihole.toml`, runs the official installer with `--unattended`, and then re-applies the captured desired values using `pihole-FTL --config`.

## Validation gates

From `IaC/ansible/` on TestServer:

```bash
ansible-playbook --syntax-check playbooks/dns-02.yml
ansible-playbook playbooks/dns-02.yml --list-tasks
```

Do not use check mode as the initial dry run on the pristine container: later validation tasks intentionally depend on Pi-hole having been installed earlier in the same real run. A real apply must be reviewed separately. During apply the role:

1. verifies the target is Debian at `192.168.2.50` on `eth0`
2. verifies direct authoritative UDP and TCP access to `a.root-servers.net` and checks its CHAOS identity
3. installs/configures Unbound and validates recursion + DNSSEC
4. installs/configures Pi-hole
5. reconciles the five captured adlists
6. validates public and local DNS responses
7. fails if any systemd unit is left failed

The role intentionally preserves the current Unbound cache/security policy from `dns-01`, including the 4 MiB socket-buffer request. If the LXC kernel refuses that buffer size, validate the warning before changing host-level sysctls.


## Live deployment evidence — 7 September 2026

The first real apply from TestServer completed successfully:

```text
dns-02 : ok=37 changed=13 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

Post-apply validation from TestServer confirmed:

- public DNS resolution through `192.168.2.50` over UDP and TCP/53
- `dns-02.jameshouse -> 192.168.2.50`
- `docker-01.jameshouse -> 192.168.2.220` on both `dns-01` and `dns-02`
- valid DNSSEC data resolves normally through Pi-hole/Unbound
- deliberately broken DNSSEC returns `SERVFAIL`
- a domain selected directly from the local gravity database is blocked as `0.0.0.0`

This validates the service build itself. Client resolver settings and ASUS DHCP/DNS advertisement remain unchanged pending a controlled failover test.


## Controlled client failover proof

On 7 September 2026, TestServer temporarily ignored DHCP-provided DNS and used only `192.168.2.50` through NetworkManager. Validation showed:

- `/etc/resolv.conf` contained only `nameserver 192.168.2.50`
- libc/system resolution succeeded for `example.com`
- local DNS resolved `dns-02.jameshouse -> 192.168.2.50`
- local DNS resolved `docker-01.jameshouse -> 192.168.2.220`
- HTTPS using normal system DNS returned HTTP 200 from `https://example.com`

This client-level proof was completed before changing ASUS DHCP/DNS advertisement. TestServer was then restored to DHCP-derived DNS.


## Router/DHCP cutover proof — 8 September 2026

The ASUS DHCP resolver pair is now `192.168.2.48 + 192.168.2.50`, replacing the removed previous `dns-02` at `.242`.

A Windows Wi-Fi client received the new pair directly from the ASUS DHCP server. TestServer then renewed its Ethernet DHCP lease through NetworkManager and also received exactly `.48 + .50`. Its generated `/etc/resolv.conf` and NetworkManager `IP4.DNS` values agree.

This completes the planned client/router DNS cutover for replacement `dns-02`.


## Proxmox system resolver management

`playbooks/proxmox-resolver.yml` manages the host resolver configuration on both standalone Proxmox nodes.

Approved state:

- search domain: `jameshouse`
- primary DNS: `192.168.2.51` (`dns-01`)
- secondary DNS: `192.168.2.50` (`dns-02`)
- retired resolver `192.168.2.48` is forbidden

The role validates the Proxmox hostname, management IPv4 and `vmbr0` identity before changing `/etc/resolv.conf`, keeps an Ansible backup of a changed file, and validates both public and local DNS after reconciliation.

From TestServer:

```bash
cd IaC/ansible
ansible-playbook --syntax-check playbooks/proxmox-resolver.yml
ansible-playbook playbooks/proxmox-resolver.yml
```

A second run should be idempotent.
