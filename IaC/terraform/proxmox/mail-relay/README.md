# mail-relay-01

IaC for the internal SMTP relay.

Target design:

- Debian 13 unprivileged LXC
- placement: `PROXMOX`
- 1 vCPU
- 512 MiB RAM
- 8 GiB root disk
- Postfix relay-only service
- outbound smart host: Gmail SMTP on TCP/587
- no public MX or inbound Internet mail
- only approved homelab sources may relay
- Gmail App Password is supplied from protected local configuration and is never committed

Default build candidates are intentionally selected by the deployment wrapper and
must pass live preflight before Terraform is allowed to create anything.

Proxmox metadata:

- tags: `homelab`, `iac`, `core`, `mail`, `smtp`
- comment: internal SMTP relay for homelab notifications via Gmail
