# Raspberry Pi router — IaC and BirdNET-Go POC migration plan (27 October 2026)

**Status:** DESIGN / GIT-ONLY. **No live deployment approved or performed.** Tracking: [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206).

## Source of truth and migration goal
- Canonical *deployed* inventory: `docs/architecture/CURRENT-STATE.md`, `IaC/ansible/inventory/hosts.yml` and `IaC/inventory/estate.json`. Do **not** present this plan as live state.
- `docker-01` (`192.168.2.220`, secondary Wi-Fi `.221`) is the active Pi 4 BirdNET-Go Docker/Komodo Periphery host; its USB microphone is currently in the Garden Room.
- `media-01` (`192.168.2.195`) is the active Pi 5 Kodi/qBittorrent, SMB and **primary Proxmox NFS backup** host. Avoid forced reboot, broad package dist-upgrade, destructive storage changes and resetting nftables.
- **BirdNET-Go is a proof of concept:** the user explicitly does **not** require its recordings, clip files, detection history or database. **Use a fresh BirdNET application state** on the destination. Preserve old host until new POC works; data backup is *not* a gate to this particular move.
- Once BirdNET is healthy on the Pi 5 and old dependencies are removed, rebuild the liberated Pi 4 as a **dedicated Debian router**. The router IaC must support rebuilding on equivalent Pi 5 hardware later.

## Critical migration gates
1. **Audio placement:** current role `birdnet_baseline` requires a **local USB sound device** `0c76:161e` and current `birdnet_go` requires stable ID `usb-id:0c76:161e:`, with `/dev/snd` mounted into the container. To free Pi 4, physically move microphone to Pi 5 (and verify sound from intended observation location), or separately design/test a persistent network-audio capture path. If the Garden Room audio must stay physically there, do not claim direct migration works merely by moving Compose files.
2. **Existing service safety:** Pi 5 already serves Nginx HTTPS on 443 for qBittorrent, Kodi and production NFS. BirdNET site must use separate SNI `birdnet.home.jrwroberts.co.uk` and coexist with existing Nginx vhosts; never delete default/other sites, overwrite /etc/nftables.conf or restart Nginx indiscriminately. Test Nginx config and perform guarded reload only.
3. **Docker and nftables interactions:** check current Pi 5 Docker/iptables/nftables state before installation. Docker changes firewall chains; prove LAN TLS, Proxmox NFS 2049, SMB 445, SSH, Kodi/DLNA, and exporter still work, with rollback and maintenance window.
4. **Persisted configuration ownership:** `birdnet_go` and `birdnet_baseline` presently assert `docker-01`/`.220`/Pi 4. Refactor to target-specific variables and skip Pi-4-only baseline on the Pi 5. Keep old source role uninfluenced during preflight.
5. **Version drift:** Ansible default image `ghcr.io/tphakala/birdnet-go:20260823` vs Komodo resource `20261010`. These are *source declarations*, not verified running image. Read current container image digest/version before picking an immutable destination image. One owner for container rollout/upgrade, no concurrent Komodo/Ansible drift.
6. **DNS and TLS:** retain existing BirdNET service hostname, but use staged host-local HTTPS tests and only repoint Pi-hole DNS after the target works; avoid hostname dual-active ambiguity. Preserve existing qBittorrent certificate/vhost. Verify authenticated app operations and live audio after DNS cutover.
7. **Network role boundary:** no new VLANs or router changes during the BirdNET migration. Pi 4 has a secondary Wi-Fi IP `.221` which must be handled before router image/cutover.

## Execution phases / rollback

### A — Read-only audit (safe to run after local syntax check)
```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/pi-router-birdnet-readonly.yml --syntax-check
ansible-playbook -i inventory/hosts.yml playbooks/pi-router-birdnet-readonly.yml --ask-become-pass
```
Read service/port use, disk/RAM, USB/ALSA, current paths, Docker availability, and model identity. No installs or edits. Confirm the actual physical USB microphone strategy. The playbook is **not** a production migration.

### B — Stage fresh BirdNET on Pi 5
Write a **separate, target-guarded** Ansible playbook; avoid running the existing `birdnet-01.yml` against `media-01`. Keep Docker volume paths away from NFS backup namespaces. Configure a media-01 BirdNET virtual host without disturbing qBittorrent. Add Pi-5-specific audio preflight and deterministic image pin. Add scoped firewall rule for trusted LAN HTTPS if needed (443 already serves qBittorrent). Do not modify the original Pi 4.

### C — Validate and cut over BirdNET
Require successful live audio and recent bird classification, functioning HTTPS/app sessions, resource/temperature headroom, NFS backups, Kodi and existing qBittorrent HTTPS, both monitoring stacks, zero newly failed systemd units, and a second Ansible reconciliation with no unintended drift. Only then stage and approve DNS transition. If problems arise, revert BirdNET DNS to `.220` and shut down *only* the new BirdNET container/site, not media services. Historic recordings intentionally stay behind and may later be discarded after approval.

### D — Free the Pi 4
Verify no application, external audio, DNS, Komodo, exporter, backup or recovery workload relies on the old BirdNET host. Retire BirdNET/Komodo Periphery with a dedicated guarded playbook **after separate approval**, update canonical inventory, and provision a new router hostname/role. Do not reimage `docker-01` while it still carries the canonical active workload.

### E — Fully reproducible router build
Use dedicated Ansible roles split by function; no magic one-off SSH edits:
- `router_bootstrap`: Debian 13 image/SSH baseline, network interface detection, rescue console and idempotent host configuration.
- `router_network`: physically isolated WAN/LAN, NAT, `192.168.2.1/24` at cutover, safe remote-apply with timed rollback.
- `router_firewall`: nftables with guarded validation, correct established/related handling, minimal external exposure and explicit rescue/rollback.
- `router_ips`: Suricata NFQUEUE, nft queue `bypass` and Suricata `nfq.fail-open`, watchdog and overloaded/hung-worker tests; IPS bypass must **not** disable the firewall.
- `router_web_filter`: E2Guardian/Squid + branded block page, explicit proxy pilot and managed browser trust if TLS inspection is ever approved. Plain HTTPS cannot reliably display a custom block page without client cooperation/TLS interception. Proxy outage policy is distinct from IPS fail-open.
- `router_vpn`: WireGuard with split/full tunnel options, persistent keys stored securely off plain Git, peer revocation, external mobile-data tests.
- `router_dhcp`: Kea, Stork observability as feasible; import actual existing ASUS leases/reservations. **Never** run two uncontrolled DHCP servers on the live LAN.
- `router_observability`: exporter, Alloy/Loki, Grafana/Alertmanager/Zabbix security alerts; alert on Suricata bypass/failure, VPN/DHCP outages, risky rule changes and web-filter problems.
- `router_management`: LAN/VPN-only authenticated Cockpit and approved IaC-backed controls; no dashboard-side unmanaged rules.

Keep board-agnostic roles and explicit host variables for Pi 4 vs Pi 5 (interface names, USB Ethernet chipset, mount/boot layout, NIC MAC and interface identity, CPU/memory budgets). Validate measured throughput under real rules, DNS, VPN and proxy load before router cutover.

### F — Recovery and replacement acceptance
Rebuild from a clean, pinned Debian image plus a Git checkout, encrypted secret restore, bootstrap SSH, Ansible, and verified service data. Make the restore possible **without DHCP/DNS/network services from the failed router** (local keyboard/console or preconfigured emergency address and offline packages). Preserve externally backed-up WireGuard private keys, TLS/CA keys, DHCP reservation configuration, WAN connection details and limited state required for continuity. Test (1) clean same-model restore and (2) Pi 4 -> Pi 5 host-variable substitution in a test network. Use a written gateway rollback and keep ASUS routing recoverable during pilot.

## Decisions and known caveats
- ISP uses a separate modem/ONT with Ethernet WAN. Actual DHCP/PPPoE/VLAN tag, public-IP/CGNAT situation, and credentials **not yet audited**.
- Keep ASUS AiMesh as Wi-Fi access points while acknowledging unsupported firmware remains a risk. No VLAN scope.
- Intended switch SPAN retirement must be **separate approval** after accepting loss of same-subnet visibility from passive `sensor-01`.
- Production/current-state docs and IP identity should only be updated after verified cutovers.
- Treat Komodo deployment declaration and certificate provisioning as explicit migration dependencies; do not assume Docker on media-01 is already installed.
- BirdNET recording/history/database preservation is deliberately **out of scope** for this POC.
