# Raspberry Pi router — IaC build, controlled handover and BirdNET-Go POC relocation

**Updated 27 October 2026. Status: DESIGN / GIT ONLY.**
Tracking: [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206), [draft PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207).

## Non-negotiable user requirements

1. **No interruption whatsoever to the current production network before the expressly agreed handover.** The ASUS RT-AC86U remains default gateway `192.168.2.1`, DHCP provider, AiMesh controller and OpenVPN endpoint until then. Do not introduce duplicate DHCP or duplicate gateway IP, change switch ports, remove SPAN, change DNS, reimage an in-service Pi, disable BirdNET, alter VLANs, or make live network-policy changes before handover.
2. **BirdNET microphone testing happens only AFTER the router project has been completed.** Do not run microphone audio capture, USB audio enumeration, `arecord` tests or BirdNET detection/recording acceptance before that milestone. It is not a router-handover dependency.
3. **Entire router build is reproducible from Git/Ansible**, including recovery onto replacement Pi 5 hardware with secure backups of non-Git secrets and device-specific configuration.
4. No VLANs, existing flat `192.168.2.0/24`; preserve existing Pi-hole+Unbound, ASUS AiMesh Wi-Fi, monitoring and Proxmox availability.
5. **Do not introduce `192.168.3.0/24` or a second ASUS routed subnet, including as a migration stage.** Final and transitional network addressing remains `192.168.2.0/24`; Pi becomes sole gateway/DHCP at approved handover, with ASUS converted to AiMesh AP mode.

The previously proposed **"move BirdNET to Pi 5, verify microphone and then free Pi 4" sequence is superseded** by this instruction. The physical Pi 4 is still needed for its present BirdNET POC and **cannot serve as a pre-handover test router**.

## Current source of truth (do not modify until actual cutovers)

- `docs/architecture/CURRENT-STATE.md`; `IaC/inventory/estate.json`; `IaC/ansible/inventory/hosts.yml` are **deployed-state authority**.
- `docker-01` (`192.168.2.220` Ethernet, `.221` secondary Wi-Fi): active Pi 4, BirdNET-Go Docker, Komodo Periphery and Garden Room USB microphone.
- `media-01` (`192.168.2.195`): active Pi 5, Kodi, qBittorrent HTTPS/Nginx, SMB, and **production Proxmox NFS backup exports**. Do not reimage, broadly upgrade, reset nftables, overwrite Nginx virtual hosts or reboot casually.
- `admin-01` Pi 3: Ansible controller and Proxmox QNetd; leave unchanged.
- DNS: `dns-01` `192.168.2.51`, `dns-02` `192.168.2.50`; core switch HP ProCurve 2510G-24. SPAN source ports 1–23 and destination 24 serve passive `sensor-01`.
- BirdNET-Go POC **recordings, audio clips, historical detections and database do NOT need copying or retention**. Existing audio hardware location is a post-project question.

## Confirmed broadband WAN: PPPoE (27 October 2026)

The user confirmed that the existing ISP modem/ONT connects to the ASUS over Ethernet and **the new router must authenticate using PPPoE**. This is a hard implementation requirement, not a discovery hypothesis. Do not change the live ASUS WAN or PPPoE session before handover.

- Proposed physically isolated Pi router network: **USB 3.0 Ethernet = PPPoE WAN**, built-in `eth0` = LAN. Identify interfaces by permanent hardware/MAC facts; do **not** assume an `enx...` name without read-only hardware inventory. Do not connect USB Ethernet to the live ONT now.
- Debian 13: pin `ppp` and use `pppd` with its documented `pppoe.so` plugin and managed peer profile, plus network bring-up/systemd supervision. No interactive `pppoeconf` wizard in normal IaC reconciliation. PPPoE interface `ppp0` is the logical WAN after successful authentication. Avoid a competing IP/DHCP client on the raw WAN Ethernet link.
- PPPoE user/password must be entered through protected secret handling (Ansible Vault or equivalent), deployed as root-readable-only PAP/CHAP secret material, redacted from logs with `no_log`. Never commit credentials, reveal them in PR output or send screenshots showing the password.
- ISP-specific settings to **discover read-only on the existing ASUS**: username (redacted if sharing), authentication type, WAN interface VLAN ID/priority or no tag, PPPoE service/access concentrator name if needed, MTU, public IPv4/CGNAT, IPv6 support and login retry/reconnection behaviour. Do not assume ISP VLAN ID merely from UK broadband technology.
- **Initial MTU/MRU 1492** for normal 1500-byte Ethernet PPPoE (RFC 2516); implement path-MTU discovery/MSS management and test relevant websites and VPN. PPP MTU 1500 is optional *only if* the end-to-end transport supports RFC 4638 and is independently verified.
- Bring up default route **only** over authenticated PPPoE after cutover; nftables WAN/NAT and Suricata forwarding rules bind to the logical PPP interface, including reconnections and interface lifecycle. Ensure no leak/bypass over the bare USB WAN Ethernet, and prohibit router DNS/client routing changes on the existing Pi 4 while BirdNET remains live.
- Fail-open Suricata does not apply to the PPPoE link: if authentication, modem, USB NIC, or router itself fails, internet connectivity is unavailable. Health check and reconnect, alert on PPP down/auth failure (without credentials), and keep a proven **ASUS restore/cutback** path.
- Test with an **isolated PPPoE access concentrator or separate permitted test link**; no dual production PPPoE sessions or live modem/ONT connection during pre-handover development. Acceptance gate at handover: PADI/PADO, authentication, `ppp0` IP, default route, NAT, IPv4 MTU, IPv6 as supported, DNS/Pi-hole, WireGuard, Suricata and dashboard/alerts, then controlled rollback.

## Build architecture

- Debian 13 ARM64 dedicated router, `nftables` NAT/firewall, interface identities and board parameters in inventory-host variables; hardware-neutral Ansible roles.
- Suricata on NFQUEUE, nft `queue bypass` and application `nfq.fail-open`, watchdog, failure and packet-drop telemetry. **Fail-open means IPS service failure does not block forwarded traffic; it does NOT mean router hardware failure is non-disruptive.**
- E2Guardian + Squid web filtering, branded HTTP block page. Managed HTTPS proxy/certificate pilot needed for reliable branded HTTPS block pages; no unconditional interception of all device traffic.
- WireGuard VPN split-tunnel/full-tunnel options; private keys and CA materials protected off plaintext Git.
- Kea DHCP and Stork where supported; preserve existing ASUS reservations/dynamic range exactly after a real read-only export. At no point allow simultaneous uncontrolled ASUS and Pi DHCP responders on production LAN.
- Pi-hole DNS remains authoritative for client DHCP options. Grafana/Loki/Prometheus/Alertmanager/Zabbix receive security and availability alerts.
- Cockpit and/or approved IaC-backed router admin controls, management reachable only on trusted LAN/VPN.
- ASUS AiMesh retained for Wi-Fi and converted to supported AP mesh topology at handover; unsupported ASUS firmware remains a separately tracked residual wireless risk. ASUS documentation permits its **WAN or LAN port as upstream uplink in AP mode** (https://www.asus.com/uk/support/faq/1015009/). Connecting Pi LAN/core-switch LAN to ASUS WAN is supported **after AP-mode conversion**, but not as a router-mode WAN and LAN both on `192.168.2.0/24`: that overlaps the routed subnets. Give ASUS an unused unique `192.168.2.x` management IP via verified DHCP lease/reservation or approved static config; it must not retain gateway `192.168.2.1`.

## Phase 1 — PRE-HANDOVER: Git-only and off-network preparation

**Permitted without changing production:** GitHub source review, repository/IaC authoring, unit tests, Ansible syntax/static checks, offline image preparation on spare boot media, plan/rollback rehearsal on paper. Collect PPPoE-specific WAN settings (credentials stored securely, possible VLAN tags), DHCP reservations, WAN access keys and ASUS export through read-only admin interaction **only if separately authorised and non-disruptive**.

**Not permitted:** touching network cabling/switch mirrors, applying any playbook that changes live hosts, running a second DHCP server/gateway on production Ethernet, reimaging `docker-01`, moving or testing its microphone, redeploying `media-01`, installing Docker on Pi 5, any changes to current ASUS routing/AiMesh.

The draft playbook `IaC/ansible/playbooks/pi-router-birdnet-readonly.yml` is a **read-only non-audio readiness tool**, but **DO NOT execute against production until separately approved**. The code must contain **no ALSA / microphone checks**, even if read-only. Syntax checks are permitted.

**Isolated pilot when spare hardware is available:** physically isolated Pi (not the in-production Pi 4), isolated switch/laptop or direct cable, simulated WAN connection and distinct test addressing. Validate image bootstrap, Ansible idempotence, nftables, Suricata fail-open, Kea, DNS, WireGuard, E2Guardian/Squid block page, alert pipelines and Pi 5 substitution against a clean environment. Never connect test DHCP/WAN/LAN interfaces to live production switch.

**If no spare test Pi exists:** write/CI-test IaC and pre-stage supported storage/image; document that full performance/hardware tests must happen during the handover maintenance window, before router becomes production gateway. No claims of zero-downtime Pi 4 hardware testing.

## Phase 2 — HANDOVER PREREQUISITES AND GO/NO-GO

Require an explicit approved date/window and rollback authority before **any production switch**:
- Tested ASUS configuration backup and instructions to restore its routing/DHCP/OpenVPN modes.
- Physical diagram identifying exact ONT Ethernet, Pi 4 WAN NIC, Pi 4 LAN NIC and core switch connection. PPPoE credentials and tagging settings captured securely.
- DHCP lease/reservation/DNS/default-gateway details verified; no double default gateway `.1`.
- Secure offline copy of WireGuard keys, TLS or interception CA (if explicitly used), configuration backups, Ansible Vault keys, runtime secrets; no secrets committed.
- Approved risk note: BirdNET POC may be **unavailable temporarily** after source Pi 4 retirement and until Pi 5 audio can be tested **AFTER completion**. A fresh app without microphone tests cannot be signed off as functional bird detection. POC shutdown requires separate express approval.
- No change to current NFS backup schedules, Kodi/qBittorrent HTTPS or the switch SPAN unless a separate scoped action is approved.

## Phase 3 — APPROVED HANDOVER WINDOW ONLY

1. Ensure fallback ASUS still routes live traffic while remaining tasks happen on **isolated** hardware. User specifically forbids *pre*-handover network interruption.
2. With approval, stop BirdNET POC on `docker-01` at the planned window and reimage Pi 4 to dedicated router; preserve source-system recovery option as feasible. Do not claim continued BirdNET detection on Pi 5 while microphone testing is deferred.
3. Optionally stage a clean BirdNET container on `media-01` **at/after handover** with independent safety checks for Docker/nftables, existing qBittorrent Nginx/443, NFS exports and Kodi; **do not run microphone tests**. BirdNET history/recordings intentionally omitted. No target live-recognition acceptance yet.
4. Apply router Ansible bootstrap and functional checks **on an isolated test link**; verify two NICs, routing, DHCP, port filtering, Suricata failure mode, VPN, web proxy health, DNS, and monitoring before any live switch. Abort to ASUS if incomplete.
5. At the approved moment, coordinate WAN and LAN gateway ownership so the Pi alone owns `192.168.2.1` and Kea is the **only** DHCP responder. Save existing ASUS configuration; switch ASUS AiMesh controller to **AP mode** (not a second router), disable its old NAT/DHCP through that mode, reconnect Pi LAN/core switch to the ASUS WAN uplink supported in AP mode, and locate the ASUS new unique `192.168.2.x` management IP. Validate AiMesh nodes, wired switch devices, DHCP and internet. Avoid both ASUS and Pi simultaneously owning `.1`. Restore ASUS router/PPPoE/DHCP roles and original cabling immediately if the controlled handover fails. Temporary outage is possible **inside approved handover only**, never before.
6. Test wired/wireless clients, DNS resolvers, internet, client renewal, roaming, firewall/IPS fail-open, proxy page as supported, WireGuard from external mobile data, Grafana/alerts, and remote access to Proxmox. Keep ASUS restore plan ready until accepted.

**Hardware feasibility constraint:** A Pi 4 carrying BirdNET cannot simultaneously be rebuilt for routing without POC interruption. If zero **handover-window** downtime and uninterrupted BirdNET both become requirements, additional separate hardware is mandatory. A Pi 5 upgrade similarly requires hardware-specific NIC and recovery validation.

## Phase 4 — AFTER ROUTER PROJECT COMPLETE: BirdNET audio

Only now arrange physical transfer of the Garden Room USB microphone to Pi 5 or implement an independently proven network stream. Verify USB/ALSA or streaming input, permissions, audio capture, recent classifications and actual intended listening location. Tune location/config as necessary. If audio cannot be made available, document BirdNET as **deferred/POC inactive**, not as migrated and functioning. Maintain NFS and Kodi service safety.

## Required Ansible/IaC modules and recovery acceptance

| Role | Scope |
|---|---|
| `router_bootstrap` | Debian image, user/SSH bootstrap, trust paths, NIC discovery, rescue access |
| `router_network` | WAN and LAN with explicit gates, optional PPPoE, static rescue address, IPv4 forwarding |
| `router_firewall` | nftables validation and reversible WAN/LAN NAT; explicit WireGuard exposure |
| `router_ips` | Suricata NFQUEUE fail-open and health watchdog; preserve firewall when IPS bypassed |
| `router_web_filter` | E2Guardian/Squid filtering and opt-in managed proxy/HTTPS policy; graceful failure |
| `router_vpn` | WireGuard peer config, split/full routing, secure key restore/revoke |
| `router_dhcp` | Kea DHCP, Stork visibility, reservations, lease integrity and rogue DHCP detection |
| `router_observability` | Prometheus, Alloy/Loki, Zabbix, alert routes and dashboards |
| `router_management` | LAN/VPN-only web management; Git is configuration authority |

Recovery target: flash Pi 4 or Pi 5 supported Debian image; use rescue network not dependent on failed gateway; restore versioned encrypted inputs (WireGuard, WAN secrets, DHCP reservations, certificates and role vars); execute Ansible; validate network routing/firewall/DNS/DHCP/VPN/IPS/filtering; ensure second idempotent reconciliation has no unintended drift; rollback controlled cutover if possible. Document minimum external peripherals (USB/PCIe NIC and storage) and change-safe interfaces for Pi 5.

## Documentation discipline

`CURRENT-STATE.md` and canonical inventory must report **verified live state only**, not plans. Update `gpt-handover.md` after Git changes and again after each live approved cutover. Retired identities remain history-only. SPAN mirror removal requires separately approved scope because same-subnet east–west visibility would be lost.

**No pre-handover production changes, no microphone testing before router-project completion.**
