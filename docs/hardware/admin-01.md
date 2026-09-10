# admin-01 Administration Host

**Updated:** 10 September 2026  
**Hostname:** `admin-01`  
**Address:** `192.168.2.48`  
**Hardware:** Raspberry Pi 3  
**Role:** dedicated homelab administration / SSH jump / IaC controller  
**Status:** operational

## Purpose

`admin-01` is the normal control point for infrastructure administration. It replaces TestServer as the preferred place to run Git, Ansible and estate SSH operations.

## Platform

- Raspberry Pi 3
- 64-bit Raspberry Pi OS / Debian 13 (trixie)
- ARM64/aarch64
- Ethernet `192.168.2.48/24`
- Wi-Fi retained as emergency fallback
- Ethernet preferred by route metric
- gateway `192.168.2.1`
- DNS `192.168.2.51`, `192.168.2.50`
- search domain `jameshouse`

## Network identity

Ethernet MAC:

```text
B8:27:EB:E8:36:CD
```

The ASUS router has `.48` reserved for that Ethernet identity. Local DNS resolves:

```text
admin-01.jameshouse -> 192.168.2.48
admin-01            -> 192.168.2.48
```

The local machine may resolve its own short hostname through `/etc/hosts`; use the FQDN when validating Pi-hole DNS explicitly.

## Administration toolchain

Validated tools include:

- Git
- Ansible Core
- SOPS
- age
- jq
- GitHub CLI
- curl/rsync/tmux/dnsutils and normal SSH tooling

SOPS/age private material is held outside Git. Never print or commit private keys, tokens or secret-bearing environment files.

## SSH model

The host has validated SSH access to the active estate including:

- `dns-01`
- `dns-02`
- `monitor-01`
- `sensor-01`
- `PROXMOX`
- `Proxmox-2`
- `media-01`
- `TestServer`
- ASUS router using the already-authorized administration identity
- `edge-01`

Use dedicated SSH identities defined in `~/.ssh/config`; do not weaken target security merely to simplify automation.

## Repository

Primary working tree:

```text
~/projects/homelab-platform
```

GitHub repository:

```text
jrwroberts1976/homelab-platform
```

Infrastructure changes should be made on feature branches, validated, reviewed/merged, then local branches cleaned up.

## Sudo

`james` uses normal password-based sudo. NOPASSWD sudo is not required for the administration role. When remote commands need an interactive sudo password, allocate a TTY deliberately rather than weakening sudo policy.

## Recovery

If `admin-01` fails, infrastructure services continue to run; this host is a management dependency, not a runtime dependency for DNS, monitoring, mail, cloud, edge or media.

Rebuild priority:

1. clean supported Raspberry Pi OS/Debian install;
2. restore `.48` network identity/reservation;
3. restore SSH access configuration/keys from protected recovery sources;
4. restore SOPS/age material from protected recovery sources;
5. clone `homelab-platform`;
6. validate DNS/GitHub/estate SSH/Ansible inventory before changing production.

## Definition of done

The admin host is healthy when:

- Ethernet `.48` is preferred and Wi-Fi fallback remains available;
- both DNS resolvers work;
- GitHub access works;
- active estate SSH aliases work;
- Ansible inventory parses and managed-host pings succeed;
- the repository is clean/current before production changes;
- no plaintext secrets are stored in Git.
