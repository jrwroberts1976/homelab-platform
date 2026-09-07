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
    └── (service configuration added as workloads are migrated)
```

The existing top-level `terraform/` directory predates this convention. Do not add new IaC there. It can be migrated into `IaC/` later as a separate non-functional cleanup once references and state handling are checked.

## Current build

The first workload being built under this structure is `dns-02`: a small Debian LXC on the primary Proxmox host for secondary Pi-hole + Unbound service.

Provisioning and service migration are deliberately separated:

1. Terraform creates and validates the LXC.
2. Current Pi-hole/Unbound configuration is captured from the existing DNS estate.
3. Ansible expresses that configuration as code.
4. Direct DNS tests are performed against `dns-02`.
5. Router DNS advertisement is changed only after failover testing succeeds.
6. `ids-01` is no longer present, so there is no live secondary rollback resolver. `dns-01` remains the working resolver while `dns-02` is built and validated; the stale `192.168.2.242` client resolver entry is removed only after `dns-02` is proven.
