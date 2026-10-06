<!-- estate-authority: IaC/inventory/estate.json -->
# DNS Service Recovery Plan

**Repository:** `jrwroberts1976/homelab-platform`  
**Authority:** `IaC/` for migrated DNS configuration  
**Runbook location:** `production docs/DNS-SERVICE-RECOVERY-PLAN.md`  
**Current-state review:** 6 October 2026

## Purpose

Recover Pi-hole/Unbound service while preserving at least one working resolver, avoiding duplicate CT/IP identities, and restoring the Git/IaC-managed dual-resolver design.

Recovery objectives:

1. keep one validated resolver available whenever possible;
2. repair the smallest failed layer first;
3. do not recreate a guest until IP/CT/state collision checks pass;
4. restore dual-resolver redundancy;
5. advertise only validated resolvers through DHCP;
6. preserve Terraform state, secrets and recovery identities outside Git.

`admin-01` (`192.168.2.48`) is the IaC/recovery controller and is **not** a DNS resolver.

## Production topology

| Component | Address | Placement | Guest | Role |
|---|---:|---|---:|---|
| `dns-01` | `192.168.2.51` | `Proxmox-2` | CT101 | Pi-hole + Unbound |
| `dns-02` | `192.168.2.50` | `PROXMOX` | CT100 | Pi-hole + Unbound |
| ASUS RT-AC86U | `192.168.2.1` | router | n/a | DHCP / resolver advertisement |
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 | n/a | recovery/IaC controller |

Approved resolver pair:

```text
192.168.2.51
192.168.2.50
```

There is no physical third local resolver.

## Local DNS parity

The older cross-resolver local-record parity defect is **resolved** in current DNS IaC. The managed local-host set contains both:

```text
dns-01.jameshouse
dns-02.jameshouse
```

During recovery, validate both records on both resolvers. If parity fails again, treat it as configuration drift and reconcile through the managed local-record playbook rather than accepting GUI-only state.

## Authoritative recovery sources

```text
IaC/scripts/deploy-dns-resolver.sh
IaC/terraform/proxmox/dns-resolver/
IaC/ansible/playbooks/dns-resolver.yml
IaC/ansible/playbooks/dns-local-records.yml
IaC/ansible/roles/dns_resolver/
```

Terraform state remains outside Git under the controller's protected state tree. Pi-hole/Proxmox credentials and SSH keys remain protected runtime/controller material.

## Normal recovery controller

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

Before recovery:

```bash
cd ~/projects/homelab-platform
hostname
hostname -I
git status --short
git fetch origin
git switch main
git pull --ff-only
```

Do not discard unrelated local work during an incident; use a clean worktree if required.

## First response: prove what still works

Test both resolvers directly before changing anything:

```bash
dig @192.168.2.51 example.com A +short
dig @192.168.2.50 example.com A +short

dig @192.168.2.51 dns-01.jameshouse A +short
dig @192.168.2.51 dns-02.jameshouse A +short
dig @192.168.2.50 dns-01.jameshouse A +short
dig @192.168.2.50 dns-02.jameshouse A +short
```

Check TCP DNS and DNSSEC validation as appropriate. If one resolver works, preserve it; do **not** change DHCP merely because the other resolver is down.

## Identify the failure layer

Check the expected guest on its hypervisor first.

`dns-01`:

```bash
ssh -i ~/.ssh/proxmox-root root@192.168.2.71 '
hostname
pct status 101
pct config 101
'
```

`dns-02`:

```bash
ssh -i ~/.ssh/proxmox-root root@192.168.2.70 '
hostname
pct status 100
pct config 100
'
```

If the CT is reachable, inspect services before considering rebuild:

```bash
ssh -i ~/.ssh/proxmox-automation root@<RESOLVER_IP> '
hostname
systemctl --failed --no-pager
systemctl is-active pihole-FTL
systemctl is-active unbound
ss -lntup | grep -E "(:53|:5335)"
'
```

Classify the fault as service/configuration, stopped/damaged CT, missing CT, hypervisor failure, controller/state loss, or total DNS outage.

## Repair an existing CT

Prefer reconciliation over rebuild when the guest exists:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook --syntax-check playbooks/dns-resolver.yml
ansible-playbook -i inventory/hosts.yml playbooks/dns-resolver.yml --limit <dns-host>
```

Run the reconciliation again after repair and expect no unintended changes.

## Safety gate before recreating a resolver

Never recreate a resolver merely because DNS does not answer.

Prove:

- old guest is destroyed/fenced and cannot return;
- production IP is not in use;
- CT ID is unused;
- protected Terraform state has been reviewed;
- new creation will not duplicate a live resource.

A failed ping is not proof an IP is free.

## Resolver identities

`dns-01`:

```text
hostname: dns-01
IPv4:    192.168.2.51
node:    Proxmox-2
CTID:    101
storage: local-lvm
```

`dns-02`:

```text
hostname: dns-02
IPv4:    192.168.2.50
node:    PROXMOX
CTID:    100
storage: vm-ssd
```

## Missing CT rebuild

Only after the safety gate passes, use the guarded build entry point:

```text
IaC/scripts/deploy-dns-resolver.sh
```

The wrapper is expected to reject existing identities/state and missing prerequisites rather than blindly create duplicates.

It deliberately does **not** change ASUS DHCP DNS advertisement.

## Missing Terraform state with a live CT

Do not run the initial-build wrapper against an existing production resolver.

Priority order:

1. preserve the working service;
2. repair with Ansible if needed;
3. recover protected Terraform state if available;
4. otherwise perform a separately reviewed import/state-reconstruction change.

Missing state is a control-plane problem, not permission to duplicate the resolver.

## One hypervisor unavailable

If one PVE node is down and the resolver on the other node works:

1. keep the working resolver in service;
2. avoid emergency relocation merely for symmetry;
3. recover the failed node or deliberately design a temporary placement;
4. validate any temporary resolver before advertising it;
5. restore the intended split placement when practical.

## Both resolvers unavailable

There is no `.48` DNS fallback.

For controller recovery only, temporarily configure a known-good upstream resolver on `admin-01`, recover one local resolver, validate it, return `admin-01` to the approved local pair, then recover the second resolver.

Do not leave public DNS configured after the incident; that bypasses local policy/naming.

## Final resolver validation

For each resolver, validate:

```bash
dig @<RESOLVER_IP> example.com A +short
dig +tcp @<RESOLVER_IP> example.com A +short
dig @<RESOLVER_IP> dns-01.jameshouse A +short
dig @<RESOLVER_IP> dns-02.jameshouse A +short
```

Validate DNSSEC with a known-good signed domain and a deliberately broken DNSSEC test that should return `SERVFAIL`.

Service checks:

```bash
ssh -i ~/.ssh/proxmox-automation root@<RESOLVER_IP> '
systemctl is-active pihole-FTL
systemctl is-active unbound
systemctl --failed --no-pager
ss -lntup | grep -E "(:53|:5335)"
'
```

Validate blocking with an existing managed gravity domain rather than inventing an unsupported test case.

## Proxmox protection

After rebuild/recovery, confirm the CT is running and protected:

```bash
ssh -i ~/.ssh/proxmox-root root@<PVE_IP> \
  "pct status <CT_ID>; pct config <CT_ID> | grep -E '^(hostname|net0|features|protection):'"
```

Expected production state includes `protection: 1`.

## DHCP/router recovery

DNS IaC does not automatically mutate ASUS DHCP resolver advertisement.

For same-IP recovery, no router change is required if the router still advertises `.51` and `.50`.

For any deliberate alternate-IP recovery, validate the alternate resolver first, then perform a separately approved router/DHCP change and later restore the canonical pair.

## Backup relationship

Both DNS CTs are included in the production Proxmox backup schedules:

```text
CT100 dns-02 -> PROXMOX 02:15 job
CT101 dns-01 -> Proxmox-2 03:15 job
```

Backup recovery is useful, but DNS service repair/reconciliation should still use the smallest safe recovery layer. Do not restore a whole CT solely to fix a manageable Pi-hole/Unbound configuration problem.

## Incident closeout

Before closing a DNS incident:

- both resolvers answer UDP and TCP DNS;
- both local cross-records resolve on both resolvers;
- DNSSEC validation behaves correctly;
- blocking policy is effective;
- Pi-hole FTL and Unbound are active;
- no unexpected failed units remain;
- Proxmox protection/state are correct;
- DHCP advertises only approved resolvers;
- temporary public-DNS/controller workarounds are removed;
- Git/IaC reflects any intentional configuration change.

## Security notes

Never print private keys, API tokens or Pi-hole credentials into chat, shell transcripts, CI logs or incident reports. Preserve host-key verification and approved SSH identities during recovery.
