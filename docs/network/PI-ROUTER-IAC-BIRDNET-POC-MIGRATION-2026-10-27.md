<!-- estate-authority: IaC/inventory/estate.json -->
# Raspberry Pi 4 router — PPPoE, DHCP, Unbound DNS first (IaC)

**Design state: 27 October 2026. No production changes approved, installed or performed.**
[Tracking issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206) · [draft PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207).

## Latest decisions — authoritative for this project

1. **ZERO network interruption before expressly approved first router handover.** ASUS remains live PPPoE gateway, DHCP server and AiMesh controller for `192.168.2.0/24`; do not alter existing switch/SPAN, Pi 4 interfaces/routing, existing Pi-hole servers, Pi 5 or other production services. No second live PPPoE connection or DHCP server on production Ethernet during preparation.
2. **Implement only the basics first:** PPPoE WAN, Kea DHCP, temporary **Unbound recursive DNS** on Pi, minimal safe nftables firewall/NAT and IPv4 forwarding. WireGuard, Suricata fail-open IPS, E2Guardian/Squid blocked-page web filtering, Cockpit/Stork, Grafana security dashboard are follow-on stages, not first PPPoE/DHCP cutover blockers.
3. New Pi LAN `192.168.3.1/24` using onboard `eth0`; USB Ethernet `eth1` is PPPoE WAN. `192.168.3.0/24` may remain the permanent primary LAN. The user accepts later host-by-host new static addresses; update canonical docs after proven live changes, not from this plan.
4. **ASUS WAN uses Automatic IP (DHCP), NOT static.** Kea allocates its `192.168.3.x` WAN address and hands out gateway/DNS `192.168.3.1`. A future reserved WAN address (e.g. `192.168.3.2`) is OPTIONAL only when the real ASUS WAN MAC is verified; no reservation/static ASUS WAN requirement at first handover.
5. **ASUS remains in ROUTER MODE throughout the first cutover and its acceptance testing.** Its LAN remains `192.168.2.1/24` with existing ASUS DHCP/AiMesh; HP switch, Proxmox, Pi-hole and Wi-Fi clients remain on the existing `.2.x` side. **Double NAT is accepted.**
6. **Only AFTER successful/verified Pi router cutover** and in a separate approved later change, migrate static IPs and dependencies and convert ASUS/AiMesh to Access Point mode. The AP conversion is NEVER a step of initial router handover. During conversion coordinate DHCP, DNS, core switch/uplink, clients and management IPs to avoid conflicts/outage. No VLAN project.
7. BirdNET-Go on Pi 4 `docker-01` is currently POC and is NOT to be migrated during this router project. Its retirement/reimage at approved handover requires explicit authority; historical recording/database preservation not needed. A fully fresh BirdNET-Go deployment on Pi 5 `media-01`, including microphone tests, is **separate and after router project completion**.
8. Git/Ansible IaC owns builds, static network config, secrets deployment and rollback. Clean OS image, board-specific NIC facts, encrypted off-Git PPPoE and future VPN credentials, restore-to-Pi-5 procedure and offline rescue access are mandatory.

## IMPLEMENTATION STAGED IN DRAFT PR #207 — future hostname `router-01`

**New hostname choice:** at the *approved router reimage/handover*, retire the Pi 4 production identity `docker-01` and build a **new host named `router-01`**. Do not rename the currently running BirdNET host or change `IaC/inventory/estate.json`, canonical Ansible `inventory/hosts.yml`, DNS or `CURRENT-STATE.md` until live cutover confirms the new identity. There must be no simultaneous production `docker-01` and `router-01` entries referring to the same active machine.

**Actual IaC now in the draft branch (files added; no deployment):**
- `IaC/ansible/inventory/router-01-staging.yml` — separate, future-only staging inventory, `192.168.3.1`.
- `IaC/ansible/playbooks/router-01-readonly.yml` — future reimaged host identity read-only inspection; **do not execute against the existing Pi 4**.
- `IaC/ansible/playbooks/router-01-basics.yml` and `roles/router_basics/` — guarded host/MAC/OS validation, systemd-networkd LAN/PPPoE physical NIC definitions, `pppd` with vaulted PAP/CHAP secrets, Kea DHCP, Unbound DNS and nftables NAT/firewall, optional explicit separate activation.
- `IaC/ansible/router-01/README.md` — bootstrap prerequisites, safe command sequence and explicit remaining validation/rollback tasks.
- `scripts/validate-router-01-basics.py` and `.github/workflows/validate-router-01-basics.yml` — offline render/contract/native syntax checks and Ansible syntax, with **no SSH to a host**.

**Safety/quality status:** Code is proposed implementation, **NOT yet validated on real Debian 13 Pi hardware**. A fresh Debian networkd/bootstrap image and isolated LAN with SSH console access are prerequisites; role refuses to run unless `router_deploy_approved=true`, hostname `router-01`, Debian 13, expected `eth0`/`eth1` MACs, and `.3.1` on LAN. Service activation separately requires `router_activate_services=true`. No claim of complete automated bare-metal provisioning yet; improve bootstrap after syntax and test feedback. Do not run code on the existing `docker-01`.

## Current documented production inventory (unchanged)

Live-state truth is `docs/architecture/CURRENT-STATE.md`, `IaC/inventory/estate.json` and `IaC/ansible/inventory/hosts.yml`.

| Device | Existing state / verified evidence | Proposed first handover |
| --- | --- | --- |
| ASUS RT-AC86U | PPPoE; LAN `192.168.2.1`; DHCP; AiMesh | WAN **DHCP client** of Pi; router/DHCP/AiMesh on `.2.x` preserved |
| Pi 4 `docker-01` | `192.168.2.220`, Debian 13, BirdNET POC/Komodo | Reimage and repurpose **only during approved handover** |
| Pi 4 `eth0` | onboard MAC `d8:3a:dd:5a:51:44`; current IP `192.168.2.220` | LAN `192.168.3.1/24` after rebuild |
| Pi 4 `eth1` | ASIX AX88179 USB GbE, `0b95:1790`, MAC `00:24:9b:63:b3:8a`, DOWN/NO-CARRIER | Untouched before handover; PPPoE WAN once connected to ONT |
| Pi 5 `media-01` | `192.168.2.195`, Kodi, qBittorrent HTTPS, SMB, production Proxmox NFS backup | No changes in router project |
| Pi-hole hosts | `dns-01 192.168.2.51`; `dns-02 192.168.2.50` | Keep serving ASUS `.2.x` clients; no changes initially |
| HP ProCurve | Core switch; SPAN to `sensor-01` | Remains downstream of ASUS LAN initially |

User's latest interface evidence: Pi `eth0` default route via ASUS `192.168.2.1`, `eth1` present with **no cable, no IP**. A detected NIC does not establish ISP link readiness.

## First target topology (ONLY during approved handover)

```text
ISP modem / ONT
      |
      | Ethernet PPPoE
      v
Pi 4 USB eth1 ------> PPPoE logical ppp0, dynamic ISP address
Pi 4 onboard eth0 --> 192.168.3.1/24 (LAN)
      |                     |
      |              Kea DHCP on eth0 ONLY
      |              Unbound UDP/TCP 53 on 192.168.3.1
      |              nftables: LAN->ppp0 routing/NAT
      |
      +---> ASUS WAN: Automatic IP (DHCP from Pi on .3.x)
                  ASUS router mode/NAT stays enabled
                  ASUS LAN: 192.168.2.1/24
                  ASUS DHCP + AiMesh remain in service
                         |
                   HP core switch, Pi-hole, Proxmox,
                   wireless and other current .2.x hosts
```

This creates intentional **double NAT**. Existing devices do not need to change addresses for stage one. Some externally initiated VPN/port-forwards or source attribution may be disrupted by double NAT; identify essential inbound services, test them, and keep a cutback to ASUS PPPoE.

## First IaC scope and acceptance tests

### PPPoE
- Debian 13, `ppp`/`pppd` with `pppoe.so`, automatic reconnect, systemd/health diagnostics. Interface identity bound to known USB NIC (host vars support future Pi 5).
- ISP username/authentication, secret password, optional VLAN tag and IPv6 need **read-only discovery** from existing ASUS configuration. Use Ansible Vault or equivalent secret path, no plaintext passwords in Git or diagnostics, root-only PAP/CHAP file. Never assume ISP VLAN tagging.
- Standard initial PPP MTU/MRU 1492, path MTU/MSS tests; external `ppp0` default route established only when ISP authentication succeeds.

### Kea DHCP
- Bind DHCP exclusively to onboard `eth0`, Pi `192.168.3.1/24`.
- **Proposed dynamic pool** `192.168.3.100 - 192.168.3.199` (subject to final preflight). Router option `192.168.3.1`, DNS option `192.168.3.1`.
- ASUS WAN **Automatic IP** from this pool. **Do not preconfigure static ASUS WAN `.3.2`.** Optional later reserved `.3.2` requires actual ASUS WAN MAC and a Git-managed Kea reservation.
- ASUS continues offering DHCP on its physically distinct `.2.x` LAN. Pi Kea must not listen/serve this downstream network.

### Temporary Unbound DNS
- Install **Unbound as recursive validating DNS on Pi**, listening on localhost and `192.168.3.1` on UDP/TCP 53 only; clients on Pi `.3.x` obtain it via Kea.
- Restrict recursion access to loopback and `192.168.3.0/24`, firewall-block WAN port 53, validate DNSSEC recursion, upstream reachability and DNS failure reporting. No internet-accessible open resolver.
- Existing `dns-01`/`dns-02` Pi-hole+Unbound remain on `.2.50/.51` behind ASUS WAN firewall; do not assume Pi-side `.3.x` clients can reach them, and do not change their settings during first handover.
- For the downstream ASUS `.2.x` LAN, preserve currently effective Pi-hole DNS; its WAN may use Pi Unbound only for router-originated fallback resolution. Document and later explicitly choose whether to retain or retire temporary Unbound once DNS hosts migrate.

### Minimal firewall/NAT
- `nftables` WAN input default-deny, safe established/related handling, SSH/rescue restrictions on LAN, LAN-to-`ppp0` stateful forwarding, masquerading and IPv4 forwarding.
- Bind rules to logical PPP interface, not raw USB NIC, and prove no unintended direct ingress/bypass. Firewall rollback not coupled to Suricata fail-open (later stage).
- Test PPP session, default route, MTU, IPv4 external access, DHCP lease/gateway/DNS option, Unbound query/TCP+UDP+DNSSEC, double-NAT outbound access for an ASUS client and existing Pi-hole resolution for downstream `.2.x` clients.

## Two distinct handovers

**Handover 1 — PPPoE + DHCP + Unbound + NAT:** only after readiness review and approval; stop and retire Pi 4 BirdNET POC with separate authorisation, reimage Pi 4 off-network, verify hardware and base services in isolation, move ONT Ethernet from ASUS PPPoE to Pi USB WAN, Pi LAN to ASUS WAN, set ASUS WAN to *Automatic IP*. Keep ASUS as router/DHCP/AiMesh and HP switch downstream. Test all essentials and revert ONT→ASUS PPPoE if blocked. Any necessary outage only inside agreed handover window.

**Handover 2 — ASUS access point, only AFTER Handover 1 has been accepted:** enumerate .2.x static dependencies and prepare new .3.x addresses, DNS/DHCP changes, HP switch path, Wi-Fi management address and client roaming. Ensure Kea pool/reservations do not overlap and there is no double active gateway. When separately authorised, convert ASUS to AP-mode AiMesh and preserve SSID coverage, then verify. Update live authoritative estate only for completed readdressed devices. Do not promise zero cutover downtime.

## Other planned services and work explicitly deferred
Suricata NFQUEUE IPS with fail-open semantics; E2Guardian+Squid web filtering and branded blocked pages (HTTPS client trust/limitations); WireGuard VPN server; Kea/Stork and Cockpit UI; integrated Grafana/Loki/Alertmanager/Zabbix security alerts; optional future SPAN removal with accepted same-subnet visibility loss. All built through IaC as subsequent scoped changes. Pi 5 BirdNET-Go is a **separate future clean install**, no microphone testing now.

## Disaster recovery and docs
Rebuild Pi 4 or replacement Pi 5 from a pinned clean Debian 13 image and Git Ansible roles with segregated NIC host vars. Restore protected WAN/PPPoE/CA/VPN keys (if present), Kea reservations and network config from external storage, with console/temporary rescue addressing not dependent on the broken router. Run second Ansible reconciliation and require no unintended drift. Keep production `CURRENT-STATE.md`, `estate.json`, `hosts.yml`, DNS, host security exceptions, NFS, monitoring and `gpt-handover.md` aligned **only with verified live changes**, not proposed moves.

**No production changes made by this plan.**
