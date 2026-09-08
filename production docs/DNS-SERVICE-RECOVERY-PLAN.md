# DNS Service Recovery Plan

**Repository:** `jrwroberts1976/homelab-platform`  
**Authority:** `main` branch  
**Runbook location:** `production docs/DNS-SERVICE-RECOVERY-PLAN.md`  
**Last validated against live build:** 8 September 2026

## Purpose

This runbook defines how to recover the homelab DNS service when Pi-hole/Unbound, an LXC container, a Proxmox node, or the IaC controller is lost.

The recovery objective is:

1. restore **one validated DNS resolver** as quickly and safely as possible;
2. restore **dual-resolver redundancy**;
3. only advertise a resolver through DHCP after it has passed direct validation;
4. keep Git/IaC as the service configuration source of truth;
5. preserve or deliberately reconcile Terraform state rather than creating unmanaged duplicates.

The preferred recovery model is **rebuild from IaC**, not manual reconstruction of Pi-hole or Unbound.

---

## 1. Production DNS topology

Known state when this runbook was written:

| Component | Address | Platform | Guest | Role |
|---|---:|---|---:|---|
| `dns-01` | `192.168.2.51` | `pve2` / `192.168.2.71` | CT `101` | IaC-built Pi-hole + Unbound |
| `dns-02` | `192.168.2.50` | `PROXMOX` / `192.168.2.70` | CT `100` | IaC-managed Pi-hole + Unbound |
| physical fallback | `192.168.2.48` | Raspberry Pi / DietPi | n/a | Legacy Pi-hole + Unbound fallback |
| ASUS router | `192.168.2.1` | RT-AC86U | n/a | DHCP and DNS advertisement |
| TestServer | `192.168.2.220` | Debian / ARM64 | n/a | IaC controller / recovery workstation |

At the time of the first `dns-01` build, ASUS DHCP still advertised `.48 + .50`. The planned steady-state pair is `.51 + .50`. **Always verify the router's current DHCP DNS values before making incident changes; do not assume this table is still the advertised pair.**

The physical `.48` resolver is a rollback path while it remains in service. If it is retired later, update this runbook.

---

## 2. Authoritative recovery sources

The DNS service is reconstructed from these repository paths:

```text
IaC/scripts/deploy-dns-resolver.sh
IaC/scripts/bootstrap-proxmox-node.sh
IaC/terraform/proxmox/dns-resolver/
IaC/ansible/playbooks/dns-resolver.yml
IaC/ansible/roles/dns_resolver/
.github/workflows/build-dns-resolver.yml
```

The Ansible role is the source of truth for:

- Pi-hole installation and FTL configuration;
- Unbound configuration;
- local DNS records;
- managed adlists;
- DNSSEC behaviour;
- service validation.

Do not treat a hand-edited Pi-hole configuration as authoritative. If a required production setting is missing from the role, update Git through review first, then apply it.

Terraform state is deliberately outside Git:

```text
~/.local/state/homelab-iac/dns-resolver/<hostname>/terraform.tfstate
```

That state is part of the recovery data set and must be protected.

---

## 3. Recovery prerequisites

### 3.1 Minimum service prerequisite

Whenever possible, keep at least one resolver working while recovering the other.

Before rebuilding a failed resolver, test the other known resolvers directly:

```bash
dig @192.168.2.51 example.com A +short
dig @192.168.2.50 example.com A +short
dig @192.168.2.48 example.com A +short
```

A successful result from one resolver means the household can remain on that resolver while the failed server is repaired.

Do **not** change DHCP merely because one resolver has failed if the remaining advertised resolver is working.

### 3.2 Recovery workstation

Preferred controller:

```text
TestServer
192.168.2.220
user: james
repository: ~/projects/homelab-platform
```

Required commands:

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

The current repository checkout must be able to reach GitHub and must be updated to reviewed `main` before recovery:

```bash
cd ~/projects/homelab-platform
git status --short
git fetch origin
git switch main
git pull --ff-only
```

If `git status --short` is not empty, do not discard work as part of an incident. Use a separate clean worktree or reconcile the changes first.

### 3.3 Required SSH keys

TestServer must have:

```text
~/.ssh/proxmox-automation
~/.ssh/proxmox-automation.pub
~/.ssh/proxmox-root
```

Purpose:

- `proxmox-automation` — root SSH into the resolver LXC;
- `proxmox-root` — root SSH into the target Proxmox node for guarded bootstrap actions such as LXC nesting.

Permissions should prevent other local users reading private keys.

Verify root access to the selected PVE before any rebuild:

```bash
ssh -i ~/.ssh/proxmox-root -o BatchMode=yes root@<PVE_IP> 'hostname; pveversion'
```

### 3.4 Protected local secrets

Required local files:

```text
~/.config/homelab-iac/proxmox.env
~/.config/homelab-iac/proxmox-pve2.env
~/.config/homelab-iac/pihole.env
```

Expected variables:

```text
TF_VAR_proxmox_api_token
PIHOLE_WEB_PASSWORD
```

Files must be protected:

```bash
chmod 700 ~/.config/homelab-iac
chmod 600 ~/.config/homelab-iac/proxmox*.env
chmod 600 ~/.config/homelab-iac/pihole.env
```

Never `cat` these files into incident notes or terminal transcripts.

The Pi-hole password must be at least 16 characters because the Ansible role enforces that minimum.

### 3.5 Proxmox API identity

Each usable target PVE needs:

- user `iac@pve`;
- token `iac@pve!opentofu` with `privsep=0`;
- roles `HomelabIaCNode`, `HomelabIaCStorage`, `HomelabIaCVM`;
- node, VM, storage, and vmbr0 SDN ACLs created by the node bootstrap process.

Verify the stored token without exposing it:

```bash
(
  source ~/.config/homelab-iac/proxmox-pve2.env
  export TF_VAR_proxmox_api_token

  curl -fsSk \
    -H "Authorization: PVEAPIToken=${TF_VAR_proxmox_api_token}" \
    https://192.168.2.71:8006/api2/json/version \
    | jq -r '"PASS - Proxmox API version " + .data.version'
)
```

Use the corresponding `proxmox.env` and endpoint `192.168.2.70` for `PROXMOX`.

### 3.6 Proxmox node prerequisites

A recovery target must have:

- healthy `pve-cluster`;
- `/etc/pve` mounted;
- bridge `vmbr0`;
- a usable rootfs datastore;
- the Debian 13 template;
- sufficient CPU, RAM and disk;
- no conflicting CT ID;
- no conflicting IP address.

Known target defaults:

| PVE | API / SSH address | Default rootfs datastore | Template |
|---|---:|---|---|
| `PROXMOX` | `192.168.2.70` | `vm-ssd` | `local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst` |
| `pve2` | `192.168.2.71` | `local-lvm` | `local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst` |

Verify a target before recovery:

```bash
ssh -i ~/.ssh/proxmox-root root@<PVE_IP> '
systemctl is-active pve-cluster
mountpoint /etc/pve
pvesm status
pveam list local
ip -br addr show vmbr0
'
```

### 3.7 Network prerequisites

Before recreating a resolver with its production IP:

- the failed instance must be stopped, destroyed, disconnected, or its old host must be fenced;
- the IP must not answer;
- ARP/neighbor state must not show another active device using the address;
- the CT ID must not already belong to another guest;
- the router must not be changed to advertise the recovering resolver until validation succeeds.

Example:

```bash
ping -c 2 -W 1 <RESOLVER_IP> || true
ip neigh show <RESOLVER_IP>

ssh -i ~/.ssh/proxmox-root root@<PVE_IP> \
  'pct config <CT_ID> 2>&1 || true'
```

**A failed ping alone is not proof that an IP is free.** Confirm the old workload cannot return later and create a duplicate address.

### 3.8 Internet/bootstrap dependency

A fresh build needs access to:

- Debian/Proxmox package and template repositories;
- the official Pi-hole installer;
- public root DNS servers for the Unbound validation;
- the configured adlist sources.

If both local resolvers are down, preserve a temporary path to working DNS for TestServer before starting a fresh build. Prefer the physical `.48` resolver while it exists. Any temporary public/ISP DNS override is emergency-only and must be removed after local DNS is restored.

### 3.9 Terraform state protection

The persistent state directory is a prerequisite for clean same-resource recovery:

```text
~/.local/state/homelab-iac/dns-resolver/
```

Treat this directory as protected operational data.

**DR requirement:** maintain an off-host protected backup of this directory. Git does not contain Terraform state.

If TestServer and its local state are lost, the service can still be rebuilt from Git, keys and secrets, but Terraform state must then be reconstructed or intentionally replaced with fresh isolated state.

---

## 4. Resolver identity variables

Set the identity for the resolver being recovered.

### dns-01

```bash
RESOLVER="dns-01"
RESOLVER_IP="192.168.2.51"
PVE_NAME="pve2"
PVE_IP="192.168.2.71"
PVE_ENDPOINT="https://192.168.2.71:8006/"
PVE_ENV="$HOME/.config/homelab-iac/proxmox-pve2.env"
ROOTFS_DATASTORE="local-lvm"
CT_ID="101"
```

### dns-02

```bash
RESOLVER="dns-02"
RESOLVER_IP="192.168.2.50"
PVE_NAME="PROXMOX"
PVE_IP="192.168.2.70"
PVE_ENDPOINT="https://192.168.2.70:8006/"
PVE_ENV="$HOME/.config/homelab-iac/proxmox.env"
ROOTFS_DATASTORE="vm-ssd"
CT_ID="100"
```

Shared values:

```bash
REPO="$HOME/projects/homelab-platform"
TEMPLATE="local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst"
STATE_ROOT="$HOME/.local/state/homelab-iac/dns-resolver"
DEPLOY_DIR="$STATE_ROOT/$RESOLVER"
```

Confirm the variables before any modifying command:

```bash
printf 'resolver=%s\nip=%s\npve=%s\npve_ip=%s\nct=%s\nrootfs=%s\n' \
  "$RESOLVER" "$RESOLVER_IP" "$PVE_NAME" "$PVE_IP" "$CT_ID" "$ROOTFS_DATASTORE"
```

---

## 5. Incident triage — choose the correct recovery path

Do not immediately rebuild.

Run:

```bash
echo "===== DNS RESPONSE ====="
dig @"$RESOLVER_IP" example.com A +time=3 +tries=1

echo
echo "===== NETWORK ====="
ping -c 2 -W 1 "$RESOLVER_IP" || true
ip neigh show "$RESOLVER_IP"

echo
echo "===== PVE GUEST STATE ====="
ssh -i ~/.ssh/proxmox-root root@"$PVE_IP" "
pct status '$CT_ID' 2>&1 || true
pct config '$CT_ID' 2>&1 || true
"
```

Choose one path:

| Condition | Recovery path |
|---|---|
| CT exists and SSH works, but DNS is broken | **Path A — service repair with Ansible** |
| CT exists but is stopped | Start CT, validate, then use Path A if needed |
| CT exists but OS/filesystem is unusable | **Path B — controlled CT replacement** |
| CT is absent and Terraform state exists | **Path C — recreate from existing Terraform state** |
| CT is absent and Terraform state does not exist | **Path D — fresh one-click rebuild** |
| Entire PVE host is unavailable | **Path E — recover on alternate/new PVE** |
| Both household resolvers are unavailable | **Path F — emergency continuity first** |

---

## 6. Path A — repair an existing resolver with Ansible

Use this when the CT exists, has the expected IP, and accepts SSH.

Do **not** run `deploy-dns-resolver.sh`; it is a creation workflow and intentionally refuses an existing CT/state.

### 6.1 Verify identity

```bash
ssh -i ~/.ssh/proxmox-automation \
  -o BatchMode=yes \
  root@"$RESOLVER_IP" '
hostname
ip -br addr
systemctl --failed --no-legend --plain
systemctl is-active pihole-FTL || true
systemctl is-active unbound || true
'
```

Do not continue if the host/IP is not the resolver you intend to repair.

### 6.2 Build a temporary recovery inventory

```bash
RECOVERY_DIR="/tmp/dns-recovery-$RESOLVER"
mkdir -p "$RECOVERY_DIR"

cat > "$RECOVERY_DIR/inventory.yml" <<EOF
---
all:
  children:
    dns_resolvers:
      hosts:
        $RESOLVER:
          ansible_host: $RESOLVER_IP
          ansible_user: root
          ansible_ssh_private_key_file: $HOME/.ssh/proxmox-automation
          dns_resolver_expected_ipv4: $RESOLVER_IP
          dns_resolver_hostname: $RESOLVER
EOF
```

### 6.3 Load the protected Pi-hole password

```bash
source ~/.config/homelab-iac/pihole.env
export PIHOLE_WEB_PASSWORD

if [ "${#PIHOLE_WEB_PASSWORD}" -lt 16 ]; then
  echo "FAIL - protected Pi-hole password is missing or too short"
else
  echo "PASS - protected Pi-hole password is loaded"
fi
```

Do not print the password.

### 6.4 Apply the authoritative resolver role

```bash
cd "$REPO/IaC/ansible"

ANSIBLE_HOST_KEY_CHECKING=False \
ANSIBLE_ROLES_PATH="$PWD/roles" \
ansible-playbook \
  -i "$RECOVERY_DIR/inventory.yml" \
  playbooks/dns-resolver.yml

unset PIHOLE_WEB_PASSWORD
```

Expected end state:

```text
unreachable=0
failed=0
```

The role itself validates Unbound recursion, valid/broken DNSSEC behaviour, Pi-hole resolution, local self-resolution, and failed systemd units.

Continue to **Section 11 — final validation**.

---

## 7. Path B — controlled replacement of a present-but-corrupt CT

Use this only when the guest exists but cannot be safely repaired.

### 7.1 Prove another resolver works

Before removing the corrupt CT:

```bash
dig @192.168.2.51 example.com A +short
dig @192.168.2.50 example.com A +short
dig @192.168.2.48 example.com A +short
```

At least one alternative path should be working unless this is a total DNS outage.

### 7.2 Preserve evidence/configuration

On the affected PVE:

```bash
ssh -i ~/.ssh/proxmox-root root@"$PVE_IP" "
echo '===== STATUS ====='
pct status '$CT_ID' || true
echo
echo '===== CONFIG ====='
pct config '$CT_ID' || true
"
```

If the guest data may be useful, take a Proxmox backup before destructive action when storage health allows it.

### 7.3 Understand protection

IaC-built resolvers are expected to end with Proxmox protection enabled.

Check:

```bash
ssh -i ~/.ssh/proxmox-root root@"$PVE_IP" \
  "pct config '$CT_ID' | grep '^protection:' || true"
```

Disabling protection and destroying the guest is a deliberate destructive recovery decision. Do not automate it as part of triage.

Before removal, confirm all four facts:

1. the selected resolver/CT ID is correct;
2. an alternate DNS path exists, or emergency continuity is already established;
3. the old guest will not be needed for forensic/backup purposes;
4. its Terraform state is preserved.

After the corrupt CT has been deliberately removed, use **Path C** if state exists, otherwise **Path D**.

---

## 8. Path C — CT missing, Terraform state exists

This is the preferred full rebuild for a destroyed guest on the **same logical target** because it preserves Terraform state continuity.

### 8.1 Prove the old guest is absent and the IP is safe

```bash
ssh -i ~/.ssh/proxmox-root root@"$PVE_IP" \
  "pct config '$CT_ID' 2>&1 || true"

ping -c 2 -W 1 "$RESOLVER_IP" || true
ip neigh show "$RESOLVER_IP"

ls -l "$DEPLOY_DIR/terraform.tfstate"
```

Do not continue if the old CT still exists or if another device is using the production IP.

### 8.2 Refresh Terraform source in the persistent state directory

```bash
mkdir -p "$DEPLOY_DIR"
cp "$REPO/IaC/terraform/proxmox/dns-resolver/"*.tf "$DEPLOY_DIR/"
```

This refreshes code only; it does not replace `terraform.tfstate`.

### 8.3 Export Terraform inputs

```bash
source "$PVE_ENV"
export TF_VAR_proxmox_api_token

export TF_VAR_proxmox_endpoint="$PVE_ENDPOINT"
export TF_VAR_proxmox_node_name="$PVE_NAME"
export TF_VAR_vm_id="$CT_ID"
export TF_VAR_hostname="$RESOLVER"
export TF_VAR_ipv4_cidr="$RESOLVER_IP/24"
export TF_VAR_rootfs_datastore_id="$ROOTFS_DATASTORE"
export TF_VAR_template_file_id="$TEMPLATE"
export TF_VAR_protect_after_build="false"

export TF_VAR_ssh_public_keys
TF_VAR_ssh_public_keys="$(
  jq -n --arg key "$(cat ~/.ssh/proxmox-automation.pub)" '[$key]'
)"
```

### 8.4 Plan exactly one recreate

```bash
RECOVERY_PLAN="/tmp/$RESOLVER-recovery-create.tfplan"

terraform -chdir="$DEPLOY_DIR" init -input=false
terraform -chdir="$DEPLOY_DIR" validate
terraform -chdir="$DEPLOY_DIR" plan -input=false -out="$RECOVERY_PLAN"
```

Gate the plan:

```bash
terraform -chdir="$DEPLOY_DIR" show -json "$RECOVERY_PLAN" |
jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
    and $changes[0].address == "proxmox_virtual_environment_container.resolver"
    and $changes[0].change.actions == ["create"]
' && echo "PASS - exactly one resolver create"
```

**Do not apply** if the gate fails or Terraform proposes deletion/replacement of anything else.

### 8.5 Apply the recreate

```bash
terraform -chdir="$DEPLOY_DIR" apply -input=false "$RECOVERY_PLAN"
```

### 8.6 Reapply Debian 13 LXC nesting

The scoped API identity does not manage the complete Proxmox LXC feature structure. Apply the required root-only bootstrap:

```bash
ssh -i ~/.ssh/proxmox-root root@"$PVE_IP" "
pct set '$CT_ID' -features nesting=1 &&
(pct shutdown '$CT_ID' --timeout 30 || pct stop '$CT_ID') &&
pct start '$CT_ID'
"
```

### 8.7 Wait for SSH

```bash
ssh-keygen -R "$RESOLVER_IP" >/dev/null 2>&1 || true

for attempt in $(seq 1 30); do
  if ssh -i ~/.ssh/proxmox-automation \
      -o BatchMode=yes \
      -o StrictHostKeyChecking=accept-new \
      -o ConnectTimeout=3 \
      root@"$RESOLVER_IP" true >/dev/null 2>&1; then
    echo "PASS - resolver SSH ready"
    break
  fi
  sleep 4
done
```

Then run **Path A, Sections 6.2–6.4** to apply Pi-hole + Unbound, followed by **Section 11** and **Section 12**.

---

## 9. Path D — CT missing and no Terraform state exists

Use this for a fresh rebuild when:

- the CT ID is free;
- the production IP is free;
- there is no usable state for that resolver;
- the selected PVE is already supported by the deployment wrapper.

Run from a clean checkout of `main`:

```bash
cd "$REPO"

DNS_HOSTNAME="$RESOLVER" \
DNS_IPV4="$RESOLVER_IP" \
DNS_PVE="$PVE_NAME" \
DNS_CT_ID="$CT_ID" \
bash IaC/scripts/deploy-dns-resolver.sh
```

The deployment workflow performs:

1. command/input checks;
2. root SSH preflight;
3. CT ID collision check;
4. IP response check;
5. storage/template check;
6. isolated Terraform plan;
7. exactly-one-create gate;
8. Terraform apply;
9. LXC nesting bootstrap;
10. SSH readiness;
11. Ansible Pi-hole + Unbound;
12. public/local/DNSSEC/blocking validation;
13. protection-only Terraform plan;
14. final protection apply.

If it fails **after Terraform has created the CT**, do not blindly rerun the creation wrapper. Inspect the exact stopping point and resume the remaining phase, as demonstrated during the first live `dns-01` build.

---

## 10. Path E — recover on an alternate or replacement PVE

Use this when the original PVE host has failed.

### 10.1 Fence the original host first

Before reusing the same resolver IP/hostname on another node, the original host must be unable to bring the old CT back online.

Acceptable fencing includes:

- physically powered off;
- network disconnected;
- storage/guest proven destroyed;
- otherwise positively isolated.

This is mandatory. A recovered old CT starting later with the same `192.168.2.x` address would create an IP conflict and can break DNS.

### 10.2 Select the recovery target

The current deployment wrapper supports:

```text
PROXMOX
pve2
```

A future `pve3` or other node must be added to Git/IaC and reviewed before it can be used by the one-click wrapper. Do not make an uncommitted incident-only edit to the production deployment mapping unless there is no safer option.

### 10.3 Inspect a new/unprepared PVE

Before running the bootstrap script on a new host:

```bash
ssh -i ~/.ssh/proxmox-root root@<NEW_PVE_IP> '
hostname
pveversion
systemctl is-active pve-cluster
mountpoint /etc/pve
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
pvs
vgs
lvs
pvesh get /storage --output-format yaml
pveam list local
ip -br addr
'
```

The bootstrap does **not** create an LVM thin pool. It verifies the VG/thinpool supplied to it already exists.

### 10.4 Bootstrap the target PVE

For a normal Proxmox install with `pve/data`:

```bash
cd "$REPO"

PVE_NAME="<NEW_PVE_NAME>" \
PVE_HOST="<NEW_PVE_IP>" \
PVE_ROOTFS_STORAGE="local-lvm" \
PVE_VG_NAME="pve" \
PVE_THINPOOL_NAME="data" \
PVE_TEMPLATE_STORAGE="local" \
PVE_TEMPLATE_NAME="debian-13-standard_13.6-1_amd64.tar.zst" \
bash IaC/scripts/bootstrap-proxmox-node.sh
```

The bootstrap:

- validates `pve-cluster` and `/etc/pve`;
- verifies the LVM-thin pool;
- registers Proxmox storage if needed;
- downloads/verifies the Debian 13 template if absent;
- reconciles the IaC roles/user/ACLs;
- reports whether an API token still needs to be created.

### 10.5 Create/recreate the API token if needed

If `iac@pve!opentofu` does not exist, create it and capture the secret directly to a protected local file.

If a token object exists but the secret is lost, remove only that token and recreate it; Proxmox does not reveal the token secret again.

Use the same guarded pattern proven on `pve2`. Keep the `!` inside single quotes to avoid Bash history expansion.

Example, adapting the PVE address and destination filename:

```bash
mkdir -p ~/.config/homelab-iac
chmod 700 ~/.config/homelab-iac

TOKEN_JSON="$(
  ssh -i ~/.ssh/proxmox-root root@<NEW_PVE_IP> \
    'pveum user token add iac@pve opentofu --privsep 0 --expire 0 --output-format json'
)"

TOKEN_VALUE="$(printf '%s\n' "$TOKEN_JSON" | jq -er '.value')"
FULL_TOKEN='iac@pve!opentofu='"$TOKEN_VALUE"

umask 077
printf 'TF_VAR_proxmox_api_token=%q\n' "$FULL_TOKEN" \
  > ~/.config/homelab-iac/<NEW_PVE_ENV_FILE>

unset TOKEN_JSON TOKEN_VALUE FULL_TOKEN
chmod 600 ~/.config/homelab-iac/<NEW_PVE_ENV_FILE>
```

Do not print the resulting file.

### 10.6 Preserve old state before moving the logical resolver

If the failed host is permanently unavailable and the resolver must be recreated on another PVE, do not silently overwrite the old state.

Archive it:

```bash
mkdir -p "$STATE_ROOT/archive"

if [ -d "$STATE_ROOT/$RESOLVER" ]; then
  mv "$STATE_ROOT/$RESOLVER" \
    "$STATE_ROOT/archive/$RESOLVER-$(date +%Y%m%d-%H%M%S)-old-pve"
fi
```

This is appropriate only after the original host is fenced and the old resource can no longer return.

Then use **Path D** for a fresh build on the supported alternate PVE.

---

## 11. Final resolver validation

A resolver is **not recovered** merely because the CT is running.

Run all validation before advertising it to clients.

### 11.1 Public DNS

```bash
dig @"$RESOLVER_IP" example.com A +short
```

Expected: one or more public addresses.

### 11.2 Local DNS

```bash
dig @"$RESOLVER_IP" "$RESOLVER.jameshouse" A +short
```

Expected: the resolver's own production address.

### 11.3 Broken DNSSEC

```bash
dig @"$RESOLVER_IP" fail01.dnssec.works A +time=5 +tries=2 |
grep 'status:'
```

Expected:

```text
status: SERVFAIL
```

### 11.4 Valid DNSSEC

```bash
dig @"$RESOLVER_IP" +ad dnssec.works A +time=5 +tries=2 |
grep -E 'status: NOERROR|flags:'
```

The resolver should return `NOERROR` and the authenticated-data (`ad`) flag.

### 11.5 Pi-hole blocking

```bash
BLOCKED_DOMAIN="$(
  ssh -i ~/.ssh/proxmox-automation \
    -o BatchMode=yes \
    root@"$RESOLVER_IP" \
    "sqlite3 /etc/pihole/gravity.db 'SELECT domain FROM gravity LIMIT 1;'"
)"

printf 'test_domain=%s\n' "$BLOCKED_DOMAIN"
dig @"$RESOLVER_IP" "$BLOCKED_DOMAIN" A +short
```

Expected:

```text
0.0.0.0
```

### 11.6 UDP and TCP DNS

```bash
dig @"$RESOLVER_IP" example.com A +time=5 +tries=1
dig @"$RESOLVER_IP" example.com A +tcp +time=5 +tries=1
```

Both must succeed.

### 11.7 Service health

```bash
ssh -i ~/.ssh/proxmox-automation root@"$RESOLVER_IP" '
systemctl is-active pihole-FTL
systemctl is-active unbound
systemctl --failed --no-legend --plain
ss -lntup | grep -E "(:53|:5335)"
'
```

Expected:

- `pihole-FTL`: active;
- `unbound`: active;
- no failed systemd units;
- Pi-hole listening on DNS port 53;
- Unbound listening on local port 5335.

---

## 12. Restore Proxmox protection

A rebuilt resolver should end protected.

If the normal one-click deployment completed, protection is applied automatically.

For a manual state-preserving recovery, perform a protection-only Terraform plan.

```bash
source "$PVE_ENV"
export TF_VAR_proxmox_api_token

export TF_VAR_proxmox_endpoint="$PVE_ENDPOINT"
export TF_VAR_proxmox_node_name="$PVE_NAME"
export TF_VAR_vm_id="$CT_ID"
export TF_VAR_hostname="$RESOLVER"
export TF_VAR_ipv4_cidr="$RESOLVER_IP/24"
export TF_VAR_rootfs_datastore_id="$ROOTFS_DATASTORE"
export TF_VAR_template_file_id="$TEMPLATE"
export TF_VAR_protect_after_build="true"

export TF_VAR_ssh_public_keys
TF_VAR_ssh_public_keys="$(
  jq -n --arg key "$(cat ~/.ssh/proxmox-automation.pub)" '[$key]'
)"

PROTECT_PLAN="/tmp/$RESOLVER-protect.tfplan"

terraform -chdir="$DEPLOY_DIR" plan -input=false -out="$PROTECT_PLAN"
```

Gate it:

```bash
terraform -chdir="$DEPLOY_DIR" show -json "$PROTECT_PLAN" |
jq -e '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  | ($changes | length) == 1
    and $changes[0].address == "proxmox_virtual_environment_container.resolver"
    and $changes[0].change.actions == ["update"]
    and $changes[0].change.before.protection == false
    and $changes[0].change.after.protection == true
' && echo "PASS - exactly one protection update"
```

Only after the gate passes:

```bash
terraform -chdir="$DEPLOY_DIR" apply -input=false "$PROTECT_PLAN"
```

Verify:

```bash
ssh -i ~/.ssh/proxmox-root root@"$PVE_IP" "
pct status '$CT_ID'
pct config '$CT_ID' | grep -E '^(hostname|features|protection):'
"
```

Expected:

```text
status: running
features: nesting=1
protection: 1
```

Then clear sensitive exported values:

```bash
unset TF_VAR_proxmox_api_token
unset TF_VAR_ssh_public_keys
```

---

## 13. Router/DHCP recovery and cutover

The IaC resolver deployment intentionally does **not** modify ASUS DHCP/DNS advertisement.

### 13.1 Same-IP recovery

If the resolver was rebuilt with the same production IP and the router was still advertising that address, no router configuration change is required.

After direct validation, renew a client lease and verify the expected DNS pair.

On TestServer:

```bash
cat /etc/resolv.conf
nmcli -f IP4.DNS device show
```

The exact pair depends on the current approved router state.

### 13.2 Alternate-IP recovery

If recovery required a different IP, do not advertise it until Section 11 has fully passed.

Then:

1. update ASUS DHCP DNS values;
2. save/apply router configuration;
3. renew TestServer DHCP;
4. prove the new DNS pair is received;
5. test public and local resolution through normal client APIs;
6. renew at least one additional client;
7. leave the old resolver address out of DHCP only after the new one is proven.

Client proof on TestServer should include:

```bash
getent hosts example.com
getent hosts "$RESOLVER.jameshouse"
curl -I https://example.com
```

A direct `dig @server` test proves the resolver. `getent` and `curl` prove the normal client path.

---

## 14. Path F — both DNS resolvers unavailable

If both advertised resolvers are down, first restore a working management DNS path so recovery tooling can reach package repositories and GitHub.

Preferred emergency order:

1. use physical `192.168.2.48` while it remains operational;
2. if it has been retired, use a temporary known-good upstream DNS path for the recovery workstation;
3. recover one IaC resolver;
4. validate it directly;
5. point the router/clients back to local DNS;
6. remove the temporary upstream override;
7. recover the second IaC resolver.

During this state, do not attempt to recover both virtual resolvers simultaneously unless there is a specific reason. Restore one known-good resolver first, then restore redundancy.

Temporary public DNS bypasses Pi-hole policy and local `jameshouse` records and is therefore **emergency-only**, not a production configuration.

---

## 15. If TestServer is lost

A TestServer failure must not make DNS unrecoverable.

Required recovery assets outside TestServer:

- access to this private GitHub repository;
- Proxmox root SSH private key or another approved root recovery path;
- resolver SSH private key;
- Proxmox API token secret(s), or root access capable of recreating them;
- Pi-hole password secret;
- protected backup of Terraform resolver state;
- knowledge of the current resolver identities/IPs/CT IDs;
- router administrative access.

On a replacement Linux controller:

1. clone `homelab-platform`;
2. install Terraform, Ansible, jq, dig, ssh, curl and ping;
3. restore the SSH keys with correct permissions;
4. restore protected `~/.config/homelab-iac/*.env` files;
5. restore `~/.local/state/homelab-iac/dns-resolver/` if available;
6. prove PVE root SSH;
7. prove API token authentication;
8. follow the correct Path A–E from this runbook.

If Terraform state is not available but the CT still exists, restore service with Ansible first. Do not create a duplicate guest merely to rebuild state.

---

## 16. New/third Proxmox node prerequisite

A third PVE node is not automatically usable by the current one-click form.

Before production recovery can target a new node:

1. install and validate Proxmox;
2. assign its final hostname/IP;
3. establish root key-based SSH;
4. inspect its real storage layout;
5. run `bootstrap-proxmox-node.sh` with correct VG/thinpool/storage values;
6. create/capture its scoped API token;
7. create a protected local PVE environment file;
8. add the node mapping to `IaC/scripts/deploy-dns-resolver.sh`;
9. add it to the GitHub workflow choice list if the workflow is to be used;
10. review and merge those changes;
11. run static validation;
12. only then use it for DNS recovery.

Do not assume every Proxmox host uses `pve/data` or `local-lvm`. Inspect first.

---

## 17. Recovery completion checklist

A DNS recovery is complete only when all of the following are true:

- [ ] at least one alternative resolver remained available during recovery, or emergency continuity was established;
- [ ] recovered CT has the intended hostname, IP and CT ID;
- [ ] no duplicate old CT/IP can return;
- [ ] Terraform state is present and corresponds to the live resource, or its replacement state has been deliberately established;
- [ ] LXC `nesting=1` is present;
- [ ] Pi-hole FTL is active;
- [ ] Unbound is active;
- [ ] public DNS works;
- [ ] local `jameshouse` DNS works;
- [ ] deliberately broken DNSSEC returns `SERVFAIL`;
- [ ] valid DNSSEC authenticates;
- [ ] Pi-hole gravity blocking returns `0.0.0.0`;
- [ ] UDP and TCP DNS both work;
- [ ] zero failed systemd units;
- [ ] Proxmox protection is enabled;
- [ ] router DHCP advertises only validated resolvers;
- [ ] a normal client resolves local/public names and reaches HTTPS;
- [ ] the second resolver is restored/validated so redundancy exists again;
- [ ] Terraform state has an off-host protected backup;
- [ ] temporary emergency DNS overrides have been removed;
- [ ] incident notes and any changed IaC have been committed/reviewed.

---

## 18. Known limitations / recovery gaps

1. **Terraform state is local to the controller.** Git intentionally does not contain it. Off-host protected state backup is therefore required for strong DR.
2. **The creation wrapper intentionally refuses an existing CT or existing resolver state.** This prevents accidental duplication, but means an interrupted post-create run must be resumed at the correct stage rather than blindly rerun.
3. **The GitHub Actions one-click path depends on a compatible self-hosted runner.** CLI recovery from TestServer remains the reliable fallback even if the Actions runner is unavailable.
4. **Only `PROXMOX` and `pve2` are currently mapped in the deployment wrapper.** A future node must be added through IaC first.
5. **Router/DHCP cutover is intentionally outside the resolver build.** This is a safety boundary, not an omission.
6. **The physical `.48` fallback is temporary.** When retired, the total-outage continuity section must be updated with the approved replacement emergency DNS path.

---

## 19. Recovery principle

The safest order is always:

```text
prove surviving DNS
    -> identify the failure layer
    -> fence duplicate identity risk
    -> repair/rebuild from Git/IaC
    -> validate directly
    -> enable protection
    -> advertise through DHCP
    -> validate normal clients
    -> restore second-resolver redundancy
    -> back up state and document the incident
```

Never advertise an unvalidated resolver, never destroy a protected guest during triage, and never reuse a production DNS IP while the old instance could still return.
