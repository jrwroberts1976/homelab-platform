# Raspberry Pi 4 router — PPPoE and DHCP first, full IaC and controlled handover

**27 October 2026 — GIT-ONLY DESIGN, NOTHING DEPLOYED.**
Tracks [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206) and [draft PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207).

## Latest decisions (override earlier discussions)

1. **Do not interrupt the current production network before explicit approved handover.** ASUS RT-AC86U remains PPPoE gateway, `192.168.2.1` DHCP server and AiMesh controller until then; all active Pi, Proxmox, DNS and switch services remain unchanged.
2. **Start with the basics: PPPoE + an independent DHCP scope + minimal firewall/NAT on the Pi router.** No Suricata, web proxy, WireGuard, management dashboard, or Wi-Fi cutover in the first functional gate. Later phases retain these desired features.
3. **Use `192.168.3.0/24` for the new Pi LAN**, initially to ASUS WAN; it may remain the eventual primary LAN. The user is happy to choose **new static IP addresses** and update host/inventory documentation as devices move; do **not** commit to restoring `192.168.2.x` permanently.
4. **Accept double NAT** during the first stage: ASUS WAN `192.168.3.2`, ASUS LAN still `192.168.2.1`; keep the existing HP switch, AiMesh and `192.168.2.x` homelab behind ASUS during first handover. Don't require AP mode in first gate.
5. **BirdNET-Go is OUT OF SCOPE for this router build.** Pi 4 `docker-01` currently hosts BirdNET POC; at a separately approved router handover it will cease when Pi 4 is repurposed. User does not want recordings/history/database preserved. **At a later date after the router project**, do a completely fresh BirdNET-Go installation on the existing Pi 5 `media-01` with microphone testing then, not now. Do not stage, copy, migrate or test BirdNET on media-01 as part of this router project.
6. **Ansible/Git is the authority for all builds**, with off-Git encrypted secrets, clean Debian-image recovery on Pi 4 or Pi 5, validation, documentation and rollback.
7. The formerly discussed removal of switch SPAN mirroring and conversion of ASUS to AiMesh AP mode require **separate future decisions**. No VLAN requirement.

## Currently deployed estate (reference only)

See `docs/architecture/CURRENT-STATE.md`, `IaC/inventory/estate.json`, `IaC/ansible/inventory/hosts.yml`.

| Component | Verified/documented current state | Planned change |
|---|---|---|
| ASUS RT-AC86U | PPPoE, `192.168.2.1`, DHCP, AiMesh | Router behind Pi after FIRST handover; AP later if chosen |
| `docker-01` Pi 4 | Debian 13 BirdNET POC and Komodo Periphery at `192.168.2.220`; Wi-Fi previously `.221` | Reimage/rebuild into router **ONLY** at approved handover |
| Pi 4 `eth0` | MAC `d8:3a:dd:5a:51:44`, `192.168.2.220` | Pi LAN `192.168.3.1/24` **after** rebuild |
| Pi 4 `eth1` | ASIX AX88179 USB 3.0 GbE, USB VID:PID `0b95:1790`, MAC `00:24:9b:63:b3:8a`, NO-CARRIER | Physical PPPoE WAN once cabled to ONT **at handover** |
| `media-01` Pi 5 | Kodi, qBittorrent, SMB, NFS backups | **No change** during router project; optional fresh BirdNET later |
| `admin-01` Pi 3 | Ansible controller / Proxmox QNetd | Remains unchanged |
| `dns-01`, `dns-02` | Pi-hole/Unbound `192.168.2.51` and `.50` | Remain unchanged in first stage |
| HP ProCurve 2510G-24 | Existing core switch and SPAN capture to `sensor-01` | Keep behind ASUS LAN in first stage |

**Observed Pi 4 status from user-provided command output:** existing default route via ASUS `192.168.2.1` on `eth0`. USB `eth1` has no link and no IP; do not plug its cable into ONT during the preparation stage.

## First target topology / approved handover stage

```text
ISP modem / ONT
     |
     | Ethernet carrying PPPoE
     v
Pi 4  eth1 (ASIX USB, PPPoE physical WAN)
     ppp0 (logical PPPoE WAN, dynamic ISP address)
     nftables: LAN -> ppp0 forwarding/NAT, WAN input default-deny
     eth0  192.168.3.1/24 (LAN)
     |      |  \-- OPTIONAL isolated/client .3.x DHCP lease testing
     |
     +---> ASUS WAN 192.168.3.2/24; default gateway 192.168.3.1
                |
                | ASUS router NAT + DHCP + AiMesh remains active
                v
           ASUS LAN 192.168.2.1/24
                |
                +-- HP ProCurve + existing wired and Wi-Fi .2.x clients
```

- ASUS maintains its `.2.x` DHCP scope and router-mode WAN firewall; new Kea DHCP listens **only on the Pi `.3.x` LAN** for any clients there. On the `.3.x` transit, ASUS WAN may be statically configured `.3.2` outside the dynamic pool.
- Proposed Kea initial DHCP pool **`192.168.3.100-192.168.3.199`**, router `.3.1`, `.3.2` reserved for ASUS WAN. Confirm exact scope before approving deployment. No overlapping second Kea scope on `.2.x`.
- **DNS caveat:** existing Pi-hole servers stay *behind ASUS* on `.2.50/.51`, and Pi-side `.3.x` clients are upstream of ASUS NAT. The Pi cannot simply advertise these resolvers to `.3.x` clients without explicitly tested downstream reachability/firewall/routing. For initial isolated `.3.x` testing, use a documented temporary DNS resolver policy (or deliberately provision a Pi-side forwarder); decide and validate before client acceptance. ASUS `.2.x` clients keep existing Pi-hole DNS.
- **Double NAT is explicitly acceptable.** Remote OpenVPN/WireGuard/port-forward ingress and source attribution could differ; evaluate when those services are migrated, but do not block the basic outbound-connectivity gate unless existing essential services depend on inbound connectivity.
- With new static addresses allowed, stage a **per-host IP/DNS/NFS/firewall/monitoring migration register**, not bulk rewriting every live `.2.x` host. Each later change updates inventory/estate/docs only after live verification. Readdressing infrastructure (Proxmox, Pi-hole, NFS, Kubernetes or monitored applications) requires explicit dependency checks and rollback.

## First IaC delivery gate — PPPoE, DHCP and base NAT/firewall

**PPPoE requirements**
- Debian 13 ARM64, `ppp`/`pppd` + PPPoE plugin `pppoe.so`, service lifecycle, automatic reconnect and monitoring of `ppp0`.
- Guard for `eth1` hardware MAC `00:24:9b:63:b3:8a` or configurable NIC hardware identity; `eth0` LAN. Keep Pi 4 vs Pi 5 board settings separable. Verify NO-CARRIER on USB NIC now is normal and does not represent internet readiness.
- Ansible Vault (or equivalent) for PPP credentials; `no_log`, root-only file permissions. ISP VLAN tag, username/auth method, MTU/MRU, IPv6 capabilities and ISP-specific options need read-only discovery from ASUS before connecting Pi to live ONT.
- Initial PPP MTU/MRU 1492; default route and firewall bind to `ppp0`; validate DNS/MTU/TCP PMTU/MSS/renewal and session reconnection at isolated bench or approved cutover.

**Kea DHCP requirements**
- A configuration file/templates and **separate `.3.x` scope** enabled only when isolated/handed over, never active on current `docker-01` network.
- Proposed default gateway `192.168.3.1`, dynamic pool `.100-.199`, ASUS WAN fixed at `.3.2`; scope-specific DNS validated as above. No initial automatic permanent reservation import or renumbering of active `.2.x` estate.
- Offer logs, pool utilisation/lease health and monitoring after basic client connectivity is confirmed.

**Base connectivity required even though focus is PPPoE and DHCP**
- `nftables` input default-deny on WAN, established/related, selected LAN admin access, safe stateful forwarding and masquerade from `192.168.3.0/24` to `ppp0`.
- Debian IPv4 forwarding, no unexpected Docker forwarding/iptables leftovers after reimage, SSH/console rescue, tested rollback to ASUS PPPoE.
- Prove WAN session, public route, NAT, LAN client DNS and DHCP, ASUS WAN DHCP/static configuration as approved, and network access for existing `.2.x` clients.

## Operational gates

**Before handover:** only read-only source review and Git/IaC/static CI, encrypted-secret preparation and *physically isolated* test with separate hardware if available. No changes to ASUS PPPoE, production DHCP, Pi 4 `eth0`, Pi 5, SPAN, BirdNET microphone, switch or other production services. The existing Pi 4 cannot simultaneously be reimaged/tested as production router while running BirdNET POC.

**Approved handover:** confirm ASUS backup, ISP WAN settings, physical cabling, rollback, alerting and maintenance approval. Separately approve retiring Pi 4 BirdNET POC, then reimage Pi 4 in isolation; validate PPPoE/DHCP/config and connect to the ONT/ASUS WAN as a planned cutover. ASUS should remain capable of being reconnected to ONT and resuming PPPoE if validation fails. Existing `.2.x` switch estate stays behind ASUS during stage one.

**After basic network stability:** follow-on work includes WireGuard VPN, inline Suricata fail-open, E2Guardian/Squid filtering with HTTPS block-page limitations, Grafana/Loki/Alertmanager/Cockpit, Kea/Stork DHCP management, and (only if later approved) ASUS AiMesh AP conversion and migrations of static hosts to `.3.x`. Do not claim these features are installed during basic router acceptance.

**At a later date outside this router project:** clean BirdNET-Go installation on `media-01` with a new microphone/audio setup and separate safe plan. No recording/history/database migration is required. No audio tests before the router project completes.

## Hardware portability / backup

Board-neutral roles with replaceable WAN NIC hardware ID, LAN NIC identity, OS image, Wi-Fi policy and persistent encrypted secrets. Router rebuild must be possible on Pi 5 from clean Debian image, Git/Ansible and independently backed-up PPPoE credentials, DHCP configuration/reservations and future VPN/TLS keys; restore network rescue access without assuming functioning router DNS/DHCP.

## Documentation policy

Keep `CURRENT-STATE.md` and canonical inventory as **verified live state** until successful cutovers. Track future `.3.x` static host assignments in an IP migration ledger and update relevant service templates/Ansible vars and `gpt-handover.md` after each verified move. Do not use historical retired device identities for new active roles. Project status remains **planning only**.
