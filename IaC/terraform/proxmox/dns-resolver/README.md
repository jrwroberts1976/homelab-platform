# Reusable DNS resolver build

This stack is the reusable build path behind the **Build DNS Resolver** GitHub Actions workflow.

## User inputs

The workflow intentionally exposes only:

- hostname
- IPv4 address
- target PVE host (`pve2` or `PROXMOX`)
- CT ID

For the first replacement-primary test:

```text
hostname: dns-01
IPv4:    192.168.2.51
PVE:     pve2
CT ID:   101
```

The subnet, gateway, bridge, CPU, RAM, swap and disk size remain approved defaults.

## What one click does

The workflow runs on the ARM64 self-hosted runner on TestServer and:

1. validates the input format
2. maps the selected PVE to its API endpoint and local credential file
3. proves root key-based SSH to the selected PVE works
4. refuses to continue if the requested CT ID already exists
5. refuses to continue if the requested IP answers ICMP
6. proves the selected rootfs storage and Debian template exist
7. creates exactly one unprivileged LXC through Terraform
8. applies the required Debian 13/systemd LXC nesting bootstrap through a narrowly-scoped root SSH command
9. configures Pi-hole + Unbound through the shared Ansible role
10. validates public resolution, local self-resolution, broken DNSSEC handling and Pi-hole blocking
11. enables the Proxmox protection flag through Terraform
12. reports PASS

It deliberately does **not** change ASUS DHCP/DNS advertisement. Cutover remains a separate guarded action until router automation is designed and proven.

## State isolation

Each resolver has its own persistent Terraform state outside the Git checkout:

```text
~/.local/state/homelab-iac/dns-resolver/<hostname>/terraform.tfstate
```

This prevents a new build from reusing or mutating the existing `dns-02` Terraform state.

## One-time runner prerequisites

TestServer must have a GitHub Actions self-hosted runner registered with the default labels:

```text
self-hosted
Linux
ARM64
```

The runner account must already have Terraform, Ansible, jq, dig and SSH available.

Required local secret/key files:

```text
~/.config/homelab-iac/proxmox.env
~/.config/homelab-iac/proxmox-pve2.env
~/.config/homelab-iac/pihole.env
~/.ssh/proxmox-automation
~/.ssh/proxmox-automation.pub
~/.ssh/proxmox-root
```

The PVE environment file must provide:

```bash
TF_VAR_proxmox_api_token='user@realm!token=secret'
```

It may override the host defaults with:

```bash
PVE_ROOTFS_DATASTORE='local-lvm'
PVE_TEMPLATE_FILE_ID='local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst'
```

The Pi-hole secret file must provide:

```bash
PIHOLE_WEB_PASSWORD='...'
```

Keep these files out of Git and mode `0600`.

## Proxmox nesting limitation

The scoped Proxmox API identity cannot safely submit the provider's full feature structure because Proxmox restricts non-nesting feature changes to `root@pam`. The reusable Terraform stack therefore does not manage LXC features directly. The deployment script proves root key-based SSH is available **before Terraform creates anything**, then applies only:

```bash
pct set <ct_id> -features nesting=1
```

and restarts the new container before Ansible runs.


## New Proxmox node onboarding

A separate idempotent host-preparation script lives at:

`IaC/scripts/bootstrap-proxmox-node.sh`

This is intentionally separate from workload deployment. A new PVE node should be bootstrapped once before any one-click workload build.

Inputs include:

```text
PVE_NAME
PVE_HOST
PVE_ROOTFS_STORAGE
PVE_VG_NAME
PVE_THINPOOL_NAME
PVE_TEMPLATE_STORAGE
PVE_TEMPLATE_NAME
```

The bootstrap validates `pve-cluster`/`/etc/pve`, verifies the existing LVM-thin pool before registering it, ensures the required LXC template is present, and reconciles the scoped Homelab IaC roles/user/ACLs.

API-token secret creation remains a separate guarded step because Proxmox displays the token secret only once; the bootstrap must never print or accidentally discard that credential.


## First live node-bootstrap proof — pve2

On 8 September 2026 the reusable node bootstrap was run against standalone `pve2` (`192.168.2.71`) with:

- rootfs storage: `local-lvm`
- VG: `pve`
- thinpool: `data`
- template storage: `local`
- template: `debian-13-standard_13.6-1_amd64.tar.zst`

The run completed successfully. It:

- validated node health and the existing LVM-thin pool
- registered `local-lvm`
- downloaded and checksum-verified the Debian 13.6 LXC template
- reconciled the scoped Homelab IaC roles
- created/reconciled `iac@pve` and its ACLs
- stopped short of creating the `iac@pve!opentofu` token secret, as designed

No workload container was created by this bootstrap run.


## pve2 credential readiness proof

On 8 September 2026 the scoped `iac@pve!opentofu` token was created on standalone `pve2`, stored locally on TestServer in the protected `~/.config/homelab-iac/proxmox-pve2.env` file, and authenticated successfully against the Proxmox API.

A protected local `~/.config/homelab-iac/pihole.env` file was also created for the resolver build. Secret values are intentionally not recorded in Git.
