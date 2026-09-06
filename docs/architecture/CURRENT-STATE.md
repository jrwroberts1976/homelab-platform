# Current-State Architecture

This document is intentionally incomplete until discovery is performed on each host.

## Hosts and infrastructure to audit

| Asset | Known address | Known role | Audit state |
|---|---|---|---|
| PROXMOX | 192.168.2.70 | Primary x86 virtualization candidate | AUDITED — RAM/backup remediation required |
| TestServer | 192.168.2.220 | Current main Docker host | NEXT |
| ids-01 | 192.168.2.242 | Security / IDS plus monitoring and secondary DNS workloads | NOT AUDITED |
| k3s-node-01 | VERIFY | Raspberry Pi / k3s node | NOT AUDITED |
| DietPi / Pi-hole | 192.168.2.48 | Primary Pi-hole / Unbound DNS appliance | NOT AUDITED |
| BirdNET Pi | VERIFY | Garden-room BirdNET workload | NOT AUDITED |
| 192.168.2.195 | 192.168.2.195 | Host identity/role must be reconciled during discovery | NOT AUDITED |
| ASUS RT-AC86U main | 192.168.2.1 | Router / DHCP / AiMesh controller | NOT AUDITED |
| ASUS AiMesh node | 192.168.2.181 | Wireless mesh node | NOT AUDITED |
| ASUS AiMesh node | 192.168.2.218 | Wireless mesh node | NOT AUDITED |
| HP ProCurve switch | 192.168.2.16 | Core managed switch | NOT AUDITED |

The secondary Pi-hole currently associated with ids-01 is a workload, not a separate physical-host audit target. It will be captured during the ids-01 workload audit.

Addresses or identities marked VERIFY are deliberately not assumed; the discovery pass must reconcile them from live evidence.

## Required evidence per host

Record:

- hostname and IP
- manufacturer/model
- CPU and architecture
- RAM and swap
- disks, filesystems and free space
- NICs and link speed
- OS and kernel
- virtualization/container runtime
- running services
- Docker containers and Compose projects
- persistent volumes and bind mounts
- exposed/listening ports
- monitoring agents/exporters
- backup coverage
- power/location constraints
- intended future role

No target placement decision is final until the audit is complete.\n\n## Completed audits\n\n- [PROXMOX](../hardware/PROXMOX.md) — CPU and storage capacity are strong; RAM and guest-backup posture must be addressed before it becomes the primary compute platform.
