# dns-02 — Proxmox LXC

Status: **IaC prepared; live infrastructure preflight complete for CT ID, storage, template and IPv4 allocation. Terraform authentication/plan validation remains before apply.**

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

The existing containerized secondary DNS service on `ids-01` (`192.168.2.242`) stays in service until `dns-02` is built, validated and included in a successful failover test.

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

The token must have the permissions required to allocate/configure the LXC and to manage the LXC template download. The provider's download resource also requires Proxmox datastore/template and system audit/modify privileges.

## Local values

Copy:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Then replace the example CT ID, IP address and public SSH key with verified values.

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

Terraform stops at the operating-system boundary. Pi-hole + Unbound will be configured with Ansible under `IaC/ansible/` after the current DNS configuration has been captured and reconciled.

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
8. retain the old `ids-01` secondary until the new path has been stable and rollback is proven

After validation, set `protect_after_build = true` and apply again so Proxmox protects the container from accidental removal.
