# DNS Service Recovery Plan

**Repository:** `jrwroberts1976/homelab-platform`  
**Authority:** reviewed `main` branch
**Runbook:** `production docs/DNS-SERVICE-RECOVERY-PLAN.md`
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`
**Current resolver pair validated:** 10 September 2026

## Purpose

This runbook restores local DNS when Pi-hole/Unbound, an LXC resolver, a Proxmox host, or the normal administration controller is unavailable.

Recovery objectives, in order:

1. keep or restore at least one validated resolver;
2. keep the ASUS router advertising only working resolvers;
3. restore the failed resolver from Git/IaC rather than hand-building unmanaged configuration;
4. restore dual-resolver redundancy across the two physical Proxmox failure domains;
5. validate public DNS, local `jameshouse` records and DNSSEC behaviour before declaring recovery complete.

## Production topology

| Component | Address | Placement | Role |
|---|---:|---|---|
| `dns-01` | `192.168.2.51` | LXC CT101 on `Proxmox-2` / `.71` | Primary Pi-hole + Unbound |
| `dns-02` | `192.168.2.50` | LXC CT100 on `PROXMOX` / `.70` | Secondary Pi-hole + Unbound |
| ASUS RT-AC86U | `192.168.2.1` | Physical router | DHCP authority / advertises DNS pair |
| `admin-01` | `192.168.2.48` | Physical Raspberry Pi 3 | Normal recovery/IaC controller |

There is **no active physical DNS fallback at `.48`**. `192.168.2.48` is now `admin-01` and must never be configured as a resolver because an older DietPi deployment once used that address.

The two Proxmox hosts are standalone. Resolver redundancy therefore comes from one DNS LXC on each physical host, not from Proxmox HA.

## Authoritative sources

Primary repository paths include:

```text
IaC/ansible/inventory/hosts.yml
IaC/ansible/playbooks/dns-resolver.yml
IaC/ansible/playbooks/dns-local-records.yml
IaC/ansible/roles/dns_resolver/
IaC/terraform/proxmox/dns-resolver/
IaC/terraform/proxmox/dns-02/
.github/workflows/build-dns-resolver.yml
```

The Ansible role/local-record data is authoritative for Pi-hole/Unbound configuration and managed local DNS records. Infrastructure state must be reconciled with the relevant Terraform/OpenTofu definition before creating replacement guests.

Manual Pi-hole GUI changes are not authoritative unless reconciled into Git.

## Secrets and access

From `admin-01`, resolver/root automation normally uses the protected SSH identities referenced by `IaC/ansible/inventory/hosts.yml`.

Required secret material such as Pi-hole administrative credentials or Proxmox API tokens must remain outside Git. Never print private keys, SOPS/age identities, API tokens or password-bearing environment files into incident transcripts.

If normal secret material is unavailable during an incident, recover it from the protected recovery source before creating unmanaged substitute credentials.

## First response: identify what actually failed

From `admin-01`:

```bash
for DNS in 192.168.2.51 192.168.2.50; do
  echo "===== $DNS ====="
  dig +time=2 +tries=1 @"$DNS" example.com A +short
  dig +time=2 +tries=1 @"$DNS" admin-01.jameshouse A +short
  nc -zvw2 "$DNS" 53 || true
done
```

Check the Proxmox guests without changing them:

```bash
ssh Proxmox-2 'pct status 101'
ssh PROXMOX   'pct status 100'
```

Check the router's current DNS advertisement before changing it. Do not assume a DHCP setting from an old document is still live.

## Healthy-resolver rule

If one resolver is working, **do not disturb it while repairing the other**.

A resolver is a viable temporary single service only after direct checks show:

- public A/AAAA resolution works;
- expected `jameshouse` local records resolve;
- UDP and TCP DNS work;
- Pi-hole FTL and Unbound are active;
- deliberately broken DNSSEC still fails as expected if using the standard validation test.

The household can operate temporarily on one resolver. Loss of redundancy is degraded service, not a reason to make risky changes to the healthy resolver.

## Resolver service failure with LXC still running

On the affected resolver, inspect first:

```bash
systemctl --failed --no-pager
systemctl status pihole-FTL --no-pager --full || true
systemctl status unbound --no-pager --full || true
ss -lntup | grep -E '(:53|:5335)' || true
journalctl -u pihole-FTL -u unbound -n 100 --no-pager
```

Validate Unbound directly:

```bash
dig @127.0.0.1 -p 5335 example.com A +short
```

Validate Pi-hole through the host address after Unbound succeeds.

Prefer reconciling configuration through Ansible instead of manually editing Pi-hole/Unbound files. If the failure is clearly transient and configuration is known-good, restart only the failing service and re-run the validation gates.

## LXC failure with Proxmox host healthy

Expected identities:

```text
CT101 dns-01 on Proxmox-2 (.71)
CT100 dns-02 on PROXMOX (.70)
```

Read-only triage:

```bash
ssh Proxmox-2 'pct status 101; pct config 101'
ssh PROXMOX   'pct status 100; pct config 100'
```

If the container is merely stopped and no storage/configuration fault is indicated, a controlled start is lower risk than rebuilding it.

If rebuild is required:

1. confirm the other resolver remains healthy;
2. confirm the expected CT ID and IP are not already occupied by another guest/device;
3. inspect the relevant Git/IaC definition and infrastructure state;
4. rebuild the failed resolver using the approved Terraform/OpenTofu/Ansible path;
5. apply the managed local records;
6. validate directly before changing DHCP;
7. only then restore normal dual-resolver advertisement.

Do not create a second unmanaged container with the production IP while stale infrastructure state still refers to the original.

## Proxmox host failure

Failure-domain mapping:

```text
PROXMOX .70 loss      -> dns-02 .50 unavailable, dns-01 .51 should remain
Proxmox-2 .71 loss    -> dns-01 .51 unavailable, dns-02 .50 should remain
```

If the surviving resolver is healthy, use it as the temporary single DNS service while recovering the failed hypervisor.

Do not move the surviving resolver onto the failed host merely to preserve labels such as primary/secondary. Availability is more important than naming during the incident.

After the hypervisor returns, verify the expected LXC state before starting/rebuilding anything that might duplicate an IP.

## Router DHCP/DNS advertisement during a single-resolver outage

Do not edit DHCP automatically just because one resolver is unavailable. Existing clients often continue using the healthy resolver from the advertised pair.

Change router DNS advertisement only when the failed resolver causes a material client problem or the outage is expected to be prolonged.

Before any router change:

1. read the current setting;
2. record/backup the current value;
3. prove the surviving resolver directly;
4. change only the DNS server list;
5. renew a test client lease and verify the resulting DNS configuration;
6. restore the pair after the failed resolver is healthy.

Do not modify ASUS SSH authorized-key persistence as part of DNS recovery.

## Total DNS outage

If both resolvers fail, recovery does not require functioning local DNS if IP addresses are used deliberately.

Work from `admin-01` using IPs:

```text
router       192.168.2.1
PROXMOX      192.168.2.70
Proxmox-2    192.168.2.71
dns-02       192.168.2.50
dns-01       192.168.2.51
```

Recovery order:

1. verify router/LAN reachability by IP;
2. verify both Proxmox hosts by IP;
3. inspect CT100 and CT101 state;
4. recover whichever resolver has the simpler/safer fault first;
5. validate that resolver directly by IP;
6. use it to restore normal local/public name resolution;
7. recover the second resolver;
8. confirm router DHCP advertises both `.51` and `.50`.

Do not point clients at `.48`; that address is the administration host.

If GitHub access is needed while local DNS is down, temporarily use an explicitly documented resolver only on the administration host if necessary and restore the normal configuration immediately after one homelab resolver is working. Do not make an emergency public resolver a permanent DHCP change without review.

## Controller failure

DNS service does not depend on `admin-01` at runtime. If `admin-01` is unavailable and DNS itself is healthy, leave DNS untouched while rebuilding the controller.

If DNS recovery and controller recovery are both required, use another trusted workstation with:

- a clean checkout of `homelab-platform`;
- protected Proxmox/resolver SSH access;
- Ansible/Terraform/OpenTofu tooling required for the chosen recovery path;
- protected secret material recovered outside Git.

Do not fall back to TestServer as an assumed controller merely because old runbooks referenced it. TestServer is a retirement target and should be used only if explicitly verified and required as an emergency path.

## Local DNS record recovery

Managed records are reconciled by:

```text
IaC/ansible/roles/dns_resolver/defaults/main.yml
IaC/ansible/playbooks/dns-local-records.yml
```

From `admin-01`:

```bash
cd ~/projects/homelab-platform
export ANSIBLE_ROLES_PATH="$PWD/IaC/ansible/roles"
ansible-playbook -i IaC/ansible/inventory/hosts.yml \
  IaC/ansible/playbooks/dns-local-records.yml --check
ansible-playbook -i IaC/ansible/inventory/hosts.yml \
  IaC/ansible/playbooks/dns-local-records.yml
```

The focused local-record playbook is preferred when only managed host records changed; do not rerun a full resolver build unnecessarily.

## Post-recovery validation

Validate both resolvers separately rather than relying on the host's normal resolver order:

```bash
for DNS in 192.168.2.51 192.168.2.50; do
  echo "===== $DNS ====="
  dig +time=2 +tries=1 @"$DNS" example.com A +short
  dig +time=2 +tries=1 @"$DNS" admin-01.jameshouse A +short
  dig +time=2 +tries=1 @"$DNS" edge-01.jameshouse A +short
  dig +tcp +time=2 +tries=1 @"$DNS" example.com A +short
done
```

Expected local records include at least:

```text
admin-01.jameshouse -> 192.168.2.48
monitor-01.jameshouse -> 192.168.2.52
edge-01.jameshouse -> 192.168.2.56
```

On each resolver:

```bash
systemctl is-active pihole-FTL
systemctl is-active unbound
systemctl --failed --no-pager
```

Also verify:

- router DHCP DNS list is `.51 + .50`;
- a renewed representative client receives the expected pair;
- monitoring sees both resolver targets healthy;
- no stale `.48` or `.242` resolver dependency has been reintroduced.

## Backup and rebuild policy

Resolver operating systems are rebuildable. Protect/reproduce:

- Git/IaC configuration;
- Terraform/OpenTofu state where required;
- Pi-hole credentials outside Git;
- any intentional local policy that is not already represented in Git;
- the administration SSH/SOPS/age recovery material required to perform a rebuild.

A complete guest image backup can accelerate recovery, but it must not become the only documented recovery method.

## Incident completion criteria

DNS recovery is complete when:

- `dns-01 .51` and `dns-02 .50` both answer directly;
- Pi-hole + Unbound are healthy on each resolver;
- local managed records agree with Git;
- public DNS and TCP/UDP queries work;
- DNSSEC validation behaviour is correct;
- the ASUS router advertises `.51 + .50`;
- monitoring reports the resolver service healthy;
- no active dependency points to retired `.242` or the old `.48` DietPi role;
- any emergency/manual changes have been reconciled back into Git or reverted.

## Current failure-domain summary

```text
ASUS router / DHCP .1
        |
        +--> dns-01 .51 / CT101 / Proxmox-2 .71
        |
        +--> dns-02 .50 / CT100 / PROXMOX .70

admin-01 .48 = controller only, not DNS
ids-01 .242 = decommissioned
```
