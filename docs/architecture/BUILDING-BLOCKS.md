# Homelab Building Blocks

This is the technical home for the JRW Roberts homelab building blocks. It describes the platform's components and points to the authoritative configuration and operational documentation.

> **Deployment truth:** Always check [CURRENT-STATE.md](CURRENT-STATE.md) and [IaC/inventory/estate.json](../../IaC/inventory/estate.json) before treating a component as deployed. This page is a navigation guide, not a second inventory.

## Core building blocks

| Building block | Purpose | Authoritative reference |
|---|---|---|
| Proxmox VE cluster | Virtual machines, LXC containers, cluster quorum and workload hosting | [Current-state architecture](CURRENT-STATE.md), [cluster implementation](PROXMOX-CLUSTER-REBUILD-PLAN.md) |
| DNS: Pi-hole and Unbound | Redundant internal DNS, recursive resolution and domain filtering | [Current-state architecture](CURRENT-STATE.md), [installed solutions](INSTALLED-SOLUTIONS-CATALOGUE.md) |
| Monitoring and logs | Prometheus, Grafana, Alertmanager, Loki, Alloy and Zabbix | [Installed solutions](INSTALLED-SOLUTIONS-CATALOGUE.md) |
| Network visibility | Suricata and Zeek passive monitoring via switch SPAN | [Current-state architecture](CURRENT-STATE.md) |
| Vulnerability management | Greenbone Community scanning and evidence reporting | [Current-state architecture](CURRENT-STATE.md) |
| Containers | Docker workloads and Komodo management | [Installed solutions](INSTALLED-SOLUTIONS-CATALOGUE.md) |
| Backups and recovery | Scheduled Proxmox backups, restore validation and recovery planning | [Backup strategy](BACKUP-STRATEGY.md) |
| Remote access | ASUS router OpenVPN service | [VPN implementation record](../network/VPN-REMOTE-ACCESS-DESIGN.md) |
| Automation and GitOps | IaC, Ansible, inventories and version-controlled change | [Repository root](../../README.md), [migration tracker](../migrations/MIGRATION-TRACKER.md) |
| Runbooks | Repeatable administration and recovery procedures | [Runbook catalogue](../../runbooks/README.md) |

## Deployed versus planned

The current-state document and IaC inventory determine which components are live. Design proposals and future building blocks belong in [TARGET-STATE.md](TARGET-STATE.md) until deployment and validation are complete. A repository-only design must never be described as an installed service.

## Ownership

This repository owns technical architecture, deployment decisions, IaC and operational runbooks. The public professional portfolio should only provide a short project overview and a link to the appropriate repository material, not maintain a separate copy of these building blocks.
