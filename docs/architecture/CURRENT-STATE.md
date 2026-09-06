# Current-State Architecture

This document is intentionally incomplete until discovery is performed on each host.

## Hosts and infrastructure to audit

| Asset | Known address | Known role | Audit state |
|---|---|---|---|
| PROXMOX | 192.168.2.70 | Primary x86 virtualization candidate | AUDITED — RAM/backup remediation required |
| TestServer | 192.168.2.220 | Current main Docker host | DISCOVERED — local host, full audit next |
| ids-01 | 192.168.2.242 | Security / IDS plus monitoring and secondary DNS workloads | DISCOVERED — SSH open, full audit pending |
| k3s-node-01 | 192.168.2.195 | Raspberry Pi / k3s node | DISCOVERED — SSH open, full audit pending |
| DietPi / Pi-hole | 192.168.2.48 | Primary Pi-hole / Unbound DNS appliance | DISCOVERED — SSH open, full audit pending |
| BirdNET Pi | VERIFY | Garden-room BirdNET workload | NOT AUDITED |
| ASUS RT-AC86U main | 192.168.2.1 | Router / DHCP / AiMesh controller | DISCOVERED — reachable, device audit pending |
| ASUS AiMesh node | 192.168.2.181 | Wireless mesh node | DISCOVERED — reachable, device audit pending |
| ASUS AiMesh node | 192.168.2.218 | Wireless mesh node | DISCOVERED — reachable, device audit pending |
| HP ProCurve switch | 192.168.2.16 | Core managed switch | DISCOVERED — reachable, SSH closed, device audit pending |

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


## Fleet discovery

A TestServer jump-box discovery run on 2026-09-06 verified:

- TestServer: `192.168.2.220`, local Debian 13 arm64 host.
- PROXMOX: `192.168.2.70`, reachable with SSH open; hostname is not resolved by TestServer DNS.
- ids-01: `192.168.2.242`, resolves as `ids-01.jameshouse`, SSH open.
- k3s-node-01: `192.168.2.195`, resolves as `k3s-node-01.jameshouse`, SSH open.
- DietPi / Pi-hole: `192.168.2.48`, reachable with SSH open; name resolution returned the host's IPv6 name.
- ASUS infrastructure at `192.168.2.1`, `192.168.2.181`, and `192.168.2.218` is reachable.
- `192.168.2.16` is reachable but does not expose SSH and remains the switch audit target.
- BirdNET host identity/address is still to be verified from live evidence.

Discovery report on TestServer: `/var/tmp/homelab-fleet-discovery-20260906T071538Z.txt`
SHA256: `04d809dea1c8a3c72532909ddb9b116dee69c7aba576fd91ad666570481edd9f`
