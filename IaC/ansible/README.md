# Ansible service configuration

This directory contains operating-system and service configuration for guests provisioned from `IaC/terraform/`.

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

The retired `ids-01` / `192.168.2.242` local-DNS record is intentionally not reproduced. A canonical `dns-02.jameshouse` record for `192.168.2.50` is added.

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
ansible-playbook playbooks/dns-02.yml --check
```

A real apply must be reviewed separately. During apply the role:

1. verifies the target is Debian at `192.168.2.50` on `eth0`
2. verifies direct authoritative access to `a.root-servers.net`
3. installs/configures Unbound and validates recursion + DNSSEC
4. installs/configures Pi-hole
5. reconciles the five captured adlists
6. validates public and local DNS responses
7. fails if any systemd unit is left failed

The role intentionally preserves the current Unbound cache/security policy from `dns-01`, including the 4 MiB socket-buffer request. If the LXC kernel refuses that buffer size, validate the warning before changing host-level sysctls.
