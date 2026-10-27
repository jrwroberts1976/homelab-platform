# Raspberry Pi router — IaC build, controlled handover and BirdNET-Go POC relocation

**Updated 27 October 2026. Status: DESIGN / GIT ONLY.**
Tracking: [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206), [draft PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207).

## Non-negotiable user requirements

1. **No interruption whatsoever to the current production network before the expressly agreed handover.** The ASUS RT-AC86U remains default gateway `192.168.2.1`, DHCP provider, AiMesh controller and OpenVPN endpoint until then. Do not introduce duplicate DHCP or duplicate gateway IP, change switch ports, remove SPAN, change DNS, reimage an in-service Pi, disable BirdNET, alter VLANs, or make live network-policy changes before handover.
2. **BirdNET microphone testing happens only AFTER the router project has been completed.** Do not run microphone audio capture, USB audio enumeration, `arecord` tests or BirdNET detection/recording acceptance before that milestone. It is not a router-handover dependency.
3. **Entire router build is reproducible from Git/Ansible**, including recovery onto replacement Pi 5 hardware with secure backups of non-Git secrets and device-specific configuration.
4. No VLANs, existing flat `192.168.2.0/24`; preserve existing Pi-hole+Unbound, ASUS AiMesh Wi-Fi, monitoring and Proxmox availability.
5. **Use `192.168.3.0/24` solely for the temporary Pi-router-to-ASUS-WAN transit LAN during the approved handover.** Keep the ASUS LAN, AiMesh clients, homelab hosts and DHCP in `192.168.2.0/24` until a separately approved conversion of ASUS to AP mode. Do not permanently renumber the homelab.

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
- ASUS AiMesh retained for Wi-Fi. **During the first approved handover stage, ASUS stays in router/AiMesh-controller mode** with `192.168.3.2/24` (proposed) on its WAN, upstream Pi LAN `192.168.3.1/24`, ASUS LAN `192.168.2.1/24` and existing `192.168.2.x` DHCP. This is *temporary double NAT*. Only later, on a separately approved second cutover, place ASUS in AP mode (WAN port as upstream uplink supported by ASUS: https://www.asus.com/uk/support/faq/1015009/), give it a unique `.2.x` management IP, transfer `.2.1` and DHCP to Pi, and reconnect the switch to Pi LAN. **Never** have ASUS router-mode WAN and LAN both on `192.168.2.0/24`.

## Two-stage IP transition — APPROVED AS A DESIGN, NOT A LIVE CHANGE

**Reinstated at user request (27 October 2026).** A temporary `192.168.3.0/24` link is the chosen migration approach. It is **not** a new permanent network or a VLAN.

**Existing production before handover (unchanged):**
```text
ONT -- PPPoE -- ASUS RT-AC86U (LAN 192.168.2.1, DHCP, AiMesh)
                       |
                  HP ProCurve + entire 192.168.2.0/24 estate
```

**First approved handover / temporary state:**
```text
ONT -- PPPoE -- Pi 4 router
                 USB-WAN: physical PPPoE NIC, logical ppp0
                 LAN: 192.168.3.1/24 (temporary)
                       |
                 ASUS WAN: 192.168.3.2/24 (static or reserved)
                 ASUS LAN: 192.168.2.1/24
                 ASUS DHCP and AiMesh remain active, ASUS router/NAT mode
                       |
                  HP ProCurve + existing 192.168.2.0/24 LAN and Wi-Fi
```
- Pi is the PPPoE terminator, default gateway for transit link, upstream NAT/firewall; ASUS NATs `.2.x` clients toward its `.3.2` WAN. **Temporary double NAT is intentional**.
- The Pi's DHCP scope on this transit link is unnecessary if ASUS WAN uses static `.3.2`. Never enable Pi DHCP on `.2.x` during stage one. ASUS alone continues serving `.2.x` clients.
- Assign the Pi LAN `.3.1`, ASUS WAN `.3.2`; check these addresses do not conflict before handover. ASUS must still have WAN and LAN on **different** subnets in router mode.
- Keep the **entire existing switch and static `.2.x` server estate behind ASUS LAN**, not directly on the Pi `.3.x` LAN. The network remains in place without renumbering.
- Double NAT can affect existing ASUS OpenVPN port forwards, inbound hosting, UPnP, game connectivity, IP attribution and WireGuard. Test explicit temporary inbound port forwarding and return paths before accepting remote access. On Pi the source from LAN appears primarily as ASUS WAN `.3.2`; per-device attribution is reduced; retain SPAN while needed.
- For split VPN access into downstream `.2.x`, plan route `192.168.2.0/24 via 192.168.3.2` on Pi **and allow relevant incoming forwarded connections through ASUS security rules** (or validate policy-directed port forwards). Routing alone does not remove ASUS WAN firewall restrictions. Do not assume it works.
- Before stage one starts, record ASUS PPPoE settings, backup the configuration, physically label ONT-to-Pi and Pi-to-ASUS connections, prove revert-to-ASUS PPPoE, and secure maintenance approval. Expect a brief controlled internet interruption **at** handover.

**Second, separately approved cutover / permanent state:**
```text
ONT -- PPPoE -- Pi 4 router
                 LAN: 192.168.2.1/24
                       |
                  HP ProCurve + 192.168.2.0/24 estate
                       |
                  ASUS AiMesh in AP mode, unique management IP on .2.x
```
- Export and reconcile ASUS DHCP reservations, lease pool and DNS. Prepare Pi Kea for `.2.x` but do not enable it until ASUS DHCP is disabled.
- Convert ASUS controller/nodes to AP-mode-supported AiMesh topology and attach its WAN uplink (if supported in AP mode) to the Pi/core switch; preserve SSIDs and verify client association and roaming.
- Switch Pi LAN and Kea to `.2.1` **in coordinated sequence with** removal of ASUS gateway/DHCP ownership to prevent collisions.
- Confirm no permanent `.3.x` dependence before retiring the temporary subnet; preserve rollback plans for both phases.

All preparations remain **Git-only/offline** until the user approves a handover window. No staged address is to be added to a production NIC during design.

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
5. **First approved handover:** keep the HP switch and all existing `192.168.2.x` wired/wireless devices behind the ASUS **LAN**. Stop ASUS PPPoE and connect its **WAN** to the Pi LAN (`192.168.3.2` to Pi `192.168.3.1`), while Pi USB WAN authenticates PPPoE to ONT. Preserve ASUS LAN `.2.1`, DHCP, AiMesh and NAT. Validate internet, DNS, switch, Wi-Fi and monitored infrastructure, acknowledging double NAT and possible VPN/port-forward side effects. Roll back to direct ONT→ASUS PPPoE if any critical check fails.
6. **Separate final AP conversion:** only after first-stage stability and explicit approval, migrate Pi LAN from `.3.1` to `192.168.2.1` and enable Kea with original DHCP reservations, convert ASUS to AP-mode and new unique `.2.x` management IP, and connect Pi LAN/core switch and ASUS AP uplink. Ensure no duplicate `.2.1` gateway or competing DHCP service. Validate internal services and Wi-Fi roaming; retain a documented ASUS restore path. Any temporary outage is confined to approved cutover windows.
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
