# Infrastructure as Code

This directory is the **authoritative location for new homelab Infrastructure-as-Code** in `jrwroberts1976/homelab-platform`.

## Rules

- New Terraform, Ansible and related deployment code belongs under `IaC/`.
- Terraform provisions infrastructure; Ansible configures operating systems and services.
- Git contains desired state, not plaintext secrets.
- Terraform state and local `.tfvars` files must not be committed.
- Secret values are supplied through protected environment variables/SOPS or another approved secret mechanism.
- Production changes require a reviewed plan and a validation/rollback path.
- Host/workload ownership must remain explicit.

## Layout

```text
IaC/
├── terraform/
│   └── proxmox/
│       └── dns-02/
└── ansible/
    ├── inventory/
    ├── playbooks/
    └── roles/
        └── dns_resolver/
```

The existing top-level `terraform/` directory predates this convention. Do not add new IaC there. It can be migrated into `IaC/` later as a separate non-functional cleanup once references and state handling are checked.

## Current build

The first workload being built under this structure is `dns-02`: a small Debian LXC on the primary Proxmox host for secondary Pi-hole + Unbound service.

Provisioning and service migration are deliberately separated:

1. Terraform creates and validates the LXC.
2. Current Pi-hole/Unbound configuration is captured from the existing DNS estate.
3. Ansible expresses that configuration as code. The first `dns_resolver` role now captures the live `dns-01` Pi-hole/Unbound baseline for `dns-02`.
4. Direct DNS tests are performed against `dns-02`.
5. Router DNS advertisement is changed only after failover testing succeeds.
6. The previous `dns-02` at `192.168.2.242` has already been removed. `dns-01` remains the working resolver while the replacement `dns-02` at `192.168.2.50` is built and validated; ASUS DHCP is still advertising the stale `.242` address until cutover.


## One-click DNS resolver builds

Reusable DNS resolver creation lives under `IaC/terraform/proxmox/dns-resolver/` and is orchestrated by `.github/workflows/build-dns-resolver.yml`.

The workflow form accepts hostname, IPv4 address, PVE target and CT ID. It uses isolated per-resolver Terraform state, then runs the shared Ansible role and validation. ASUS DHCP/DNS cutover remains deliberately separate.
