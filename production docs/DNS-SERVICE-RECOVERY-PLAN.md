# DNS Service Recovery Plan

**Repository:** `jrwroberts1976/homelab-platform`  
**Authority:** reviewed repository state / `IaC/` for migrated DNS configuration  
**Runbook location:** `production docs/DNS-SERVICE-RECOVERY-PLAN.md`  
**Recovery workflow last fully validated:** 8 September 2026  
**Current service state reviewed:** 12 September 2026

## Purpose

This runbook defines how to recover the homelab DNS service when Pi-hole/Unbound, an LXC container, a Proxmox node, or the normal IaC controller is unavailable.

The recovery objective is:

1. keep at least one validated resolver available whenever possible;
2. recover a failed resolver without creating duplicate IPs, CT IDs or unmanaged Terraform resources;
3. restore dual-resolver redundancy;
4. advertise only validated resolvers through DHCP;
5. rebuild from Git/IaC rather than manually reconstructing Pi-hole or Unbound;
6. preserve Terraform state, secrets and recovery identities outside Git.

> **Important current-state correction:** `192.168.2.48` is `admin-01`. It is not a DNS resolver and must not be used as a fallback resolver. The retired `DietPi` and `TestServer` identities must not be used as active recovery targets.

---

## 1. Production DNS topology

| Component | Address | Platform | Guest | Role |
|---|---:|---|---:|---|
| `dns-01` | `192.168.2.51` | `Proxmox-2` / `192.168.2.71` | CT `101` | Pi-hole + Unbound |
| `dns-02` | `192.168.2.50` | `PROXMOX` / `192.168.2.70` | CT `100` | Pi-hole + Unbound |
| ASUS router | `192.168.2.1` | RT-AC86U | n/a | DHCP and DNS advertisement |
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 / Debian 13 | n/a | IaC controller / recovery workstation |

Approved resolver pair:

```text
192.168.2.51
192.168.2.50
```

The current design has **no physical third DNS fallback**.

### Known local-record parity defect

The 12 September 2026 audit found:

- `dns-01` resolves both `dns-01.jameshouse` and `dns-02.jameshouse`;
- `dns-02` resolves `dns-02.jameshouse` but currently does not resolve `dns-01.jameshouse`.

This matches a known IaC parity defect in the managed local-host list. It is not evidence that `dns-02` recursion, DNSSEC or general DNS service is unhealthy. Do not make an emergency recovery depend on cross-resolver local-name parity until that separate defect is deliberately corrected.

---

## 2. Authoritative recovery sources

Current DNS IaC paths:

```text
IaC/scripts/deploy-dns-resolver.sh
IaC/scripts/bootstrap-proxmox-node.sh
IaC/terraform/proxmox/dns-resolver/
IaC/ansible/playbooks/dns-resolver.yml
IaC/ansible/roles/dns_resolver/
.github/workflows/build-dns-resolver.yml
```

The Ansible role is authoritative for managed Pi-hole/Unbound configuration including:

- Pi-hole installation and FTL configuration;
- Unbound configuration;
- managed local DNS records;
- managed adlists;
- DNSSEC behaviour;
- service validation.

Do not treat a manual Pi-hole GUI edit as authoritative unless it is deliberately reconciled back into Git-managed configuration.

Terraform state is intentionally outside Git:

```text
~/.local/state/homelab-iac/dns-resolver/<hostname>/terraform.tfstate
```

Protected state is part of the recovery data set.

---

## 3. Normal recovery controller

Preferred controller:

```text
admin-01
192.168.2.48
user: james
repository: ~/projects/homelab-platform
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

Expected controller identity is `admin-01` with `192.168.2.48` present.

If the working tree is not clean, do not discard unrelated work during an incident. Use a clean worktree or reconcile the local changes first.

Required command-line tooling includes:

```bash
command -v terraform
command -v ansible-playbook
command -v jq
command -v ssh
command -v ssh-keygen
command -v dig
command -v ping
command -v curl
```

---

## 4. Protected controller state

Expected recovery material includes, as applicable:

```text
~/.ssh/proxmox-automation
~/.ssh/proxmox-automation.pub
~/.ssh/proxmox-root
~/.config/homelab-iac/proxmox.env
~/.config/homelab-iac/proxmox-pve2.env
~/.config/homelab-iac/pihole.env
~/.local/state/homelab-iac/dns-resolver/
```

Never print private keys, API tokens or the Pi-hole password into terminal transcripts, chat, CI logs or incident notes.

Verify permissions without displaying secret contents:

```bash
ls -ld ~/.ssh ~/.config/homelab-iac ~/.local/state/homelab-iac/dns-resolver
ls -l ~/.ssh/proxmox-automation ~/.ssh/proxmox-root
ls -l ~/.config/homelab-iac/proxmox*.env ~/.config/homelab-iac/pihole.env
```

---

## 5. First response: prove what still works

Test each resolver directly before changing anything:

```bash
dig @192.168.2.51 example.com A +short
dig @192.168.2.50 example.com A +short
```

Check DNSSEC behaviour:

```bash
dig @192.168.2.51 dnssec.works A +dnssec
dig @192.168.2.50 dnssec.works A +dnssec

dig @192.168.2.51 fail01.dnssec.works A +time=5 +tries=2
dig @192.168.2.50 fail01.dnssec.works A +time=5 +tries=2
```

The deliberately broken DNSSEC domain should return `SERVFAIL` from a healthy validating resolver.

Check service reachability:

```bash
nc -vz 192.168.2.51 53
nc -vz 192.168.2.50 53
```

If one resolver works, preserve it. Do **not** change DHCP simply because the other resolver failed.

---

## 6. Identify the failure layer

Check the expected hypervisor and CT first.

### `dns-01`

```bash
ssh -i ~/.ssh/proxmox-root root@192.168.2.71 '
hostname
pct status 101
pct config 101
'
```

### `dns-02`

```bash
ssh -i ~/.ssh/proxmox-root root@192.168.2.70 '
hostname
pct status 100
pct config 100
'
```

If the CT is running, inspect the guest before considering a rebuild:

```bash
ssh -i ~/.ssh/proxmox-automation root@<RESOLVER_IP> '
hostname
systemctl --failed --no-pager
systemctl is-active pihole-FTL
systemctl is-active unbound
ss -lntup | grep -E "(:53|:5335)"
'
```

Classify the incident as one of:

- service/configuration failure inside an existing CT;
- stopped or damaged CT;
- missing CT;
- Proxmox host failure;
- controller/state loss;
- total DNS outage.

Repair the smallest failed layer first.

---

## 7. Safety gate before recreating a resolver

Never recreate a resolver merely because it does not answer DNS.

Before creating a production resolver identity, prove all of the following:

- the old guest is destroyed, permanently disconnected, or fenced so it cannot return;
- the production IP is not in use;
- the CT ID is not in use on the intended hypervisor;
- the existing Terraform state has been reviewed;
- creating a new resource will not duplicate an existing live CT.

Example checks:

```bash
ping -c 2 -W 1 <RESOLVER_IP> || true
ip neigh show <RESOLVER_IP>

ssh -i ~/.ssh/proxmox-root root@<PVE_IP> \
  'pct config <CT_ID> 2>&1 || true'

ls -l ~/.local/state/homelab-iac/dns-resolver/<RESOLVER>/ 2>/dev/null || true
```

**A failed ping is not proof that an IP is free.**

---

## 8. Resolver identity values

### `dns-01`

```bash
RESOLVER="dns-01"
RESOLVER_IP="192.168.2.51"
PVE_NAME="Proxmox-2"
PVE_IP="192.168.2.71"
CT_ID="101"
ROOTFS_DATASTORE="local-lvm"
```

The current deployment wrapper also accepts the compatibility selector `pve2`, but `Proxmox-2` is the current human-facing host identity.

### `dns-02`

```bash
RESOLVER="dns-02"
RESOLVER_IP="192.168.2.50"
PVE_NAME="PROXMOX"
PVE_IP="192.168.2.70"
CT_ID="100"
ROOTFS_DATASTORE="vm-ssd"
```

---

## 9. Path A — repair an existing CT

Use this path when the CT exists and the operating system is reachable.

From `admin-01`:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook --syntax-check playbooks/dns-resolver.yml
```

Then target only the affected resolver through the approved inventory/limit mechanism and reconcile the managed DNS role.

Do not destroy a recoverable CT merely to use the initial-build wrapper.

After repair, perform the validation in Section 14.

---

## 10. Path B — missing resolver CT

Use this only after the recreation safety gate in Section 7 is satisfied.

The supported build entry point is:

```text
IaC/scripts/deploy-dns-resolver.sh
```

The wrapper deliberately refuses:

- an existing CT ID;
- an IP that answers ICMP;
- an existing resolver Terraform state file;
- missing PVE storage/template prerequisites;
- missing protected credentials/SSH keys.

Typical invocation pattern:

```bash
cd ~/projects/homelab-platform

DNS_HOSTNAME="$RESOLVER" \
DNS_IPV4="$RESOLVER_IP" \
DNS_PVE="$PVE_NAME" \
DNS_CT_ID="$CT_ID" \
PVE_ROOTFS_DATASTORE="$ROOTFS_DATASTORE" \
bash IaC/scripts/deploy-dns-resolver.sh
```

The wrapper creates exactly one resolver CT, enables required LXC nesting, runs the DNS Ansible configuration, validates DNS behaviour, and enables Proxmox protection.

It intentionally does **not** change ASUS DHCP/DNS advertisement.

---

## 11. Path C — CT exists but Terraform state is missing

Do **not** run the initial-build wrapper against an existing production CT.

Priority order:

1. preserve the existing working DNS service;
2. repair/configure the guest with Ansible if needed;
3. recover the protected Terraform state backup if available;
4. otherwise deliberately reconstruct/import/replace state using a reviewed Terraform recovery change.

The absence of Terraform state is a control-plane recovery problem, not permission to create a duplicate resolver.

---

## 12. Path D — one Proxmox node unavailable

If one hypervisor is unavailable but the resolver on the other host works:

1. leave the working resolver in service;
2. do not perform an emergency relocation simply for symmetry;
3. recover the failed Proxmox node or deliberately design a temporary resolver placement;
4. validate any temporary placement before advertising it;
5. restore the intended dual-host resolver design when practical.

Current normal placements remain:

```text
dns-01 -> Proxmox-2 .71 / CT101
dns-02 -> PROXMOX .70 / CT100
```

---

## 13. Path E — both local resolvers unavailable

There is no longer a physical `.48` DNS fallback.

If both `.51` and `.50` are unavailable, restore a temporary management DNS path on `admin-01` so Git/package/bootstrap dependencies can resolve.

Emergency sequence:

1. record the current resolver configuration on `admin-01`;
2. configure a temporary known-good upstream resolver using the active Debian network-management mechanism;
3. prove public DNS from `admin-01`;
4. recover **one** local resolver;
5. validate it directly;
6. restore `admin-01` to the approved local resolver pair;
7. remove the temporary public/upstream override;
8. recover the second local resolver;
9. revalidate redundancy.

Before making the temporary change, capture:

```bash
cat /etc/resolv.conf
command -v resolvectl >/dev/null && resolvectl status || true
command -v nmcli >/dev/null && nmcli device show || true
```

Do not leave public DNS configured after the incident. It bypasses Pi-hole policy and local `jameshouse` records.

---

## 14. Final resolver validation

For the recovered resolver:

```bash
dig @"$RESOLVER_IP" example.com A +short
dig @"$RESOLVER_IP" "$RESOLVER.jameshouse" A +short
dig @"$RESOLVER_IP" fail01.dnssec.works A +time=5 +tries=2
```

Validate valid DNSSEC with a signed domain and confirm the broken test returns `SERVFAIL`.

Prove TCP as well as UDP DNS:

```bash
dig +tcp @"$RESOLVER_IP" example.com A +short
```

Check services and failed units:

```bash
ssh -i ~/.ssh/proxmox-automation root@"$RESOLVER_IP" '
systemctl is-active pihole-FTL
systemctl is-active unbound
systemctl --failed --no-pager
ss -lntup | grep -E "(:53|:5335)"
'
```

Validate blocking using an existing managed gravity domain rather than inventing a test domain:

```bash
BLOCKED_DOMAIN="$(ssh -i ~/.ssh/proxmox-automation root@"$RESOLVER_IP" \
  "sqlite3 /etc/pihole/gravity.db 'SELECT domain FROM gravity LIMIT 1;'")"

printf 'test_domain=%s\n' "$BLOCKED_DOMAIN"
dig @"$RESOLVER_IP" "$BLOCKED_DOMAIN" A +short
```

Expected blocking result is the configured Pi-hole blocking response, currently `0.0.0.0` for the managed build.

Do not use cross-resolver `dns-01.jameshouse` resolution from `dns-02` as a completion gate until the known local-record parity defect is separately fixed.

---

## 15. Proxmox protection validation

After a rebuild, verify the CT is running and protected:

```bash
ssh -i ~/.ssh/proxmox-root root@"$PVE_IP" \
  "pct status '$CT_ID'; pct config '$CT_ID' | grep -E '^(hostname|net0|features|protection):'"
```

Expected protection state includes:

```text
protection: 1
```

The resolver build also requires LXC nesting for its current managed implementation.

---

## 16. Router/DHCP recovery and cutover

DNS IaC intentionally does not modify ASUS DHCP DNS advertisement.

### Same-IP recovery

If a resolver returns on its existing production address and the router still advertises that address, no DHCP change is required.

After direct validation, prove a normal client path.

On `admin-01`:

```bash
getent hosts example.com
getent hosts dns-01.jameshouse
getent hosts dns-02.jameshouse
curl -I https://example.com
```

Be aware of the known `dns-02` local-record parity defect described earlier.

### Alternate-IP recovery

Do not advertise an alternate resolver address until it has passed the direct validation gates.

If an alternate address is deliberately approved:

1. update ASUS DHCP DNS values;
2. save/apply the router configuration;
3. renew a client lease;
4. prove the expected DNS pair was received;
5. test public and local resolution through normal client APIs;
6. test at least one additional client;
7. remove obsolete resolver advertisement only after the replacement is proven.

---

## 17. If `admin-01` is lost

Loss of the normal controller must not make DNS unrecoverable.

Required recovery assets outside `admin-01` include:

- access to the private GitHub repository;
- approved Proxmox root recovery access;
- resolver SSH recovery access;
- Proxmox API token material or an approved way to recreate it;
- Pi-hole secret material;
- protected backup of resolver Terraform state;
- current resolver identities/IPs/CT IDs;
- ASUS router administrative access.

On a replacement Linux controller:

1. clone `homelab-platform`;
2. install the required Terraform/Ansible/DNS/SSH tooling;
3. restore protected SSH keys and controller configuration;
4. restore `~/.local/state/homelab-iac/dns-resolver/` if available;
5. prove root SSH to the target Proxmox node;
6. prove API-token authentication;
7. follow the appropriate recovery path in this document.

If Terraform state is absent but a resolver CT still exists, preserve the service and repair with Ansible first. Do not create a duplicate guest.

---

## 18. New Proxmox node prerequisite

A new Proxmox node is not automatically a supported DNS build target.

Before using a new node for production DNS recovery:

1. install and validate Proxmox;
2. assign final hostname/IP;
3. establish approved root recovery access;
4. inspect real storage layout;
5. bootstrap required IaC roles/tokens deliberately;
6. create protected local environment configuration;
7. add the node mapping to `IaC/scripts/deploy-dns-resolver.sh`;
8. update any GitHub workflow choice list if required;
9. review and merge the IaC change;
10. run static validation;
11. only then use it for DNS recovery.

Do not assume storage names such as `local-lvm` on an unfamiliar node.

---

## 19. Recovery completion checklist

A DNS recovery is complete only when all applicable items are true:

- [ ] a surviving resolver remained available, or temporary emergency continuity was established;
- [ ] recovered CT has the intended hostname, IP and CT ID;
- [ ] no duplicate old CT/IP can return;
- [ ] Terraform state corresponds to the live resource or has been deliberately reconstructed;
- [ ] required LXC nesting is present;
- [ ] Pi-hole FTL is active;
- [ ] Unbound is active;
- [ ] public DNS works;
- [ ] local self-resolution works;
- [ ] deliberately broken DNSSEC returns `SERVFAIL`;
- [ ] valid DNSSEC validates;
- [ ] Pi-hole blocking works;
- [ ] UDP and TCP DNS both work;
- [ ] zero unexpected failed systemd units;
- [ ] Proxmox protection is enabled;
- [ ] ASUS DHCP advertises only validated resolvers;
- [ ] a normal client resolves public/local names and reaches HTTPS;
- [ ] the second resolver is restored/validated so redundancy exists again;
- [ ] temporary emergency upstream DNS overrides have been removed;
- [ ] changed IaC and incident notes have been reviewed.

---

## 20. Known recovery gaps

1. Terraform state remains controller-side protected operational data and requires an off-host recovery copy.
2. The initial-build wrapper deliberately refuses existing CT/state identities; interrupted builds must be resumed deliberately rather than blindly rerun.
3. GitHub Actions recovery depends on a compatible self-hosted runner; the CLI path from an approved Linux controller remains the fallback.
4. Only the mapped Proxmox targets are supported by the current deployment wrapper.
5. Router/DHCP cutover remains intentionally outside resolver deployment.
6. There is no physical third DNS resolver. Total-outage continuity therefore requires temporary upstream DNS on the recovery controller until one local resolver is restored.
7. `dns-02` currently lacks the `dns-01.jameshouse` local record because of a known IaC parity defect. Correct that separately through reviewed IaC; do not improvise a manual emergency fix unless it is required by the incident.

---

## Recovery principle

The safest order is:

```text
prove surviving DNS
    -> identify the failed layer
    -> preserve/fence identity
    -> repair before rebuild
    -> rebuild from Git/IaC only when absence is proven
    -> validate directly
    -> validate normal client path
    -> restore redundancy
    -> remove temporary emergency changes
```

Do not trade a recoverable single failure for duplicate IPs, duplicate CTs, lost state or undocumented emergency configuration.
