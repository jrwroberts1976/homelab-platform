# dns-02 — Proxmox LXC

Status: **DNS cutover is complete. CT 100 (`dns-02`) is running on `PROXMOX` at `192.168.2.50/24`; Debian 13/systemd is healthy; Pi-hole + Unbound are deployed through Ansible; direct, client-only, and DHCP cutover validation have passed. Proxmox protection is now enabled in desired Terraform state and requires a final plan/apply on the runner.**

## Goal

Create a small, reproducible Debian LXC on the primary Proxmox host to become the secondary Pi-hole + Unbound resolver.

Target design:

```text
dns-01
  Raspberry Pi 3
  192.168.2.48
  Pi-hole + Unbound
  independent physical DNS path

dns-02
  Proxmox LXC on PROXMOX
  static/reserved IPv4: `192.168.2.50/24`
  Pi-hole + Unbound
  managed through Terraform + Ansible
```

The previous `dns-02` at `192.168.2.242` has been removed. ASUS DHCP now advertises `192.168.2.48` (`dns-01`) and `192.168.2.50` (replacement `dns-02`). A Windows Wi-Fi client and a freshly renewed TestServer lease both received `.48 + .50`.

## Planned LXC resources

- Target node: `PROXMOX`
- Debian 13 official Proxmox LXC template already present on `local` (`debian-13-standard_13.6-1_amd64.tar.zst`)
- 1 vCPU
- 512 MiB RAM
- 256 MiB swap
- 8 GiB root disk
- `vm-ssd` root filesystem storage
- `vmbr0` LAN bridge
- unprivileged LXC
- start on boot
- no plaintext root password; SSH key bootstrap only

Pi-hole itself documents 512 MB RAM and 4 GB recommended free space as sufficient baseline capacity, so this allocation leaves modest headroom while remaining lightweight.

## Safety gates before apply

Run these on `PROXMOX` and record the output:

```bash
pvesh get /cluster/nextid
pct list
pvesm status
pvesm list local --content vztmpl
```

Live preflight selected and approved `192.168.2.50/24` for `dns-02`. It did not answer ICMP and no MAC resolved for it from `PROXMOX` before allocation. The address was then approved for this workload.

Do **not** advertise the new resolver to DHCP clients yet.

## Authentication

The Terraform provider uses a Proxmox API token.

Never commit the token. Supply it only to the Terraform process:

```bash
export TF_VAR_proxmox_api_token='user@realm!token=secret'
```

The current runner reuses the scoped `iac@pve!opentofu` API token. Its ACLs cover the target node, `vmbr0`, `/vms`, and the required datastores. The existing Debian template is referenced directly; Terraform does not download or own it.

## Local values

Copy:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Then replace the example CT ID, IP address and public SSH key with verified values.

## Proven runner

Terraform is executed from `TestServer` (`192.168.2.220`). The validated toolchain is Terraform 1.16.0 on `linux_arm64` with `bpg/proxmox` 0.111.1 pinned by `.terraform.lock.hcl`.

## Plan gate

From this directory:

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
```

Review the complete plan before any apply.

Do not run `terraform apply` until:

- CT ID `100` is still unused immediately before apply
- IPv4 `192.168.2.50/24` remains reserved for `dns-02`
- the SSH key is correct
- the target storage names are confirmed
- the plan contains only the expected template/LXC operations

## Template handling

Live preflight on 7 September 2026 confirmed the official Proxmox Debian 13 template is already present:

`local:vztmpl/debian-13-standard_13.6-1_amd64.tar.zst`

The stack references that existing template directly rather than trying to download or take ownership of an unmanaged template file. Template lifecycle can be brought under IaC separately later if desired.

## Configuration phase

Terraform stops at the operating-system boundary. Pi-hole + Unbound are configured with Ansible under `IaC/ansible/`; the live `dns-01` configuration was captured and reconciled before the first apply.

That capture must include:

- current Pi-hole versions
- current block/ad lists
- local DNS records and CNAMEs
- important Pi-hole v6 settings
- current Unbound configuration
- current Nebula Sync intent
- any monitoring/exporter integration

Passwords/API tokens are not copied into plaintext Git.

## Cutover

After Ansible configuration:

1. query `dns-02` directly over UDP and TCP/53
2. verify Pi-hole blocking
3. verify Unbound recursion/DNSSEC
4. compare expected local records with `dns-01`
5. stop `dns-02` and prove `dns-01` still serves clients
6. start `dns-02`, temporarily stop the existing secondary path and prove resolution
7. only then update ASUS DHCP/DNS advertisement
8. replace stale client/router references to `192.168.2.242` only after the new path has been stable and rollback to `dns-01` is proven

Service validation and client/router cutover proof are complete. `protect_after_build` now defaults to `true`; run a final reviewed Terraform plan/apply so Proxmox protects CT 100 from accidental removal.


## Debian 13 / systemd 257 runtime

The first live boot of CT 100 on Proxmox VE 9.2 showed systemd 257 with `dev-mqueue.mount`, `run-lock.mount`, and `tmp.mount` failed, leaving the guest in a degraded state. Enabling LXC nesting resolved all three failures and returned `systemctl is-system-running` to `running`.

The desired Terraform state therefore includes:

```hcl
features {
  nesting = true
}
```

### Proxmox API limitation observed

When the scoped `iac@pve!opentofu` token attempted to add the feature block to the already-created container, the provider submitted the full feature structure (`fuse=false`, `keyctl=false`, `mknod=false`, `nesting=true`). Proxmox rejected that API update because changing feature flags other than nesting is restricted to `root@pam`.

The one-time live bootstrap used on `PROXMOX` was:

```bash
pct set 100 -features nesting=1
pct shutdown 100 --timeout 30 || pct stop 100
pct start 100
```

After the container restarted, systemd was healthy, Terraform refreshed the manually-set nesting state, and the final `terraform plan` reported **No changes**.

This root-only bootstrap requirement must be considered if CT 100 is ever recreated from scratch with the current scoped API identity. Do not widen the IaC service-account permissions to `Administrator` merely to bypass this Proxmox restriction.

The guest network interface is named `eth0` and is live at `192.168.2.50/24`, so Debian and subsequent Ansible configuration use the conventional interface name.

## Provisioning completion evidence

Live validation on 7 September 2026 confirmed:

- CT 100 exists and is running
- `eth0` has `192.168.2.50/24`
- SSH key bootstrap works with `proxmox-automation`
- systemd state is `running`
- zero failed systemd units
- final Terraform plan: **No changes. Your infrastructure matches the configuration.**


## DHCP cutover evidence — 8 September 2026

ASUS DHCP was changed from the retired resolver pair `192.168.2.48 + 192.168.2.242` to `192.168.2.48 + 192.168.2.50`.

Validation confirmed:

- a Windows Wi-Fi client received DNS servers `192.168.2.48` and `192.168.2.50` from `192.168.2.1`
- TestServer renewed its NetworkManager DHCP lease
- TestServer `/etc/resolv.conf` contains `192.168.2.48` followed by `192.168.2.50`
- NetworkManager reports `IP4.DNS[1]=192.168.2.48` and `IP4.DNS[2]=192.168.2.50`

The stale `.242` DHCP reference is therefore removed from the proven client path.
