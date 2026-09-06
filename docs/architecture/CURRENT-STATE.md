# Current-State Architecture

This document is intentionally incomplete until discovery is performed on each host.

## Hosts to audit

| Host | Known role | Audit state |
|---|---|---|
| Proxmox | Primary x86 virtualization candidate | NOT AUDITED |
| TestServer | Current main Docker host | PARTIAL |
| ids-01 | Security / IDS host | NOT AUDITED |
| k3s-node-01 | Raspberry Pi / k3s node | NOT AUDITED |
| DietPi / Pi-hole | DNS appliance | NOT AUDITED |
| Secondary Pi-hole | DNS resilience | NOT AUDITED |
| BirdNET Pi | Garden-room BirdNET workload | NOT AUDITED |

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

No target placement decision is final until the audit is complete.
