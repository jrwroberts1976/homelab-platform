# Pi4 router-01 — PPPoE first, Kea DHCP next, existing Debian installation

**Operational runbook, 27 October 2026.** This supersedes the previous "reimage / networkd first" path. The user wants the broadband router built now, accepts BirdNET-Go and Komodo Periphery downtime and a planned internet interruption. Source-controlled Ansible is used for every software/config change.

## Known deployed state BEFORE steps

- Pi 4 still called `docker-01`, Debian 13, SSH `192.168.2.220` on onboard `eth0` (MAC `d8:3a:dd:5a:51:44`), DHCP via Netplan+NetworkManager `netplan-eth0`. **Do not reimage, rename, or change this interface/IP while preparing.**
- Extra ASIX AX88179 USB Ethernet `eth1` (MAC `00:24:9b:63:b3:8a`) will be raw PPPoE WAN. Current eth1 has no IP and no cable.
- ASUS WAN now handles PPPoE from external ONT, ASUS LAN/DHCP gateway `192.168.2.1`, HP switch and old LAN attached.
- Confirmed PPPoE: untagged, 1492 MTU/MRU, 6-second LCP echo and 10 failures, auto authentication. Actual credentials **already confirmed encrypted** in off-Git local `$HOME/.config/router-01/pppoe-vault.yml` on `admin-01`, and a local real-Vault rendering test passed. No secrets in repository.
- Future Pi LAN `192.168.3.1/24`, Kea pool `192.168.3.100`–`192.168.3.199`, Unbound recursive DNS at `.3.1`. ASUS future **WAN DHCP client** (not a fixed .3.2 address), ASUS remains router-mode/DHCP/AiMesh initially; temporary double NAT acceptable.

## LIVE progress — 27 October 2026, 11:22 GMT

**PPPoE installation on the actual existing Pi4 SUCCEEDED**: `docker-01 ok=14 changed=4 unreachable=0 failed=0`. The user's encrypted Ansible Vault provided both actual credentials, the PPP peer/PAP/CHAP secret files and dedicated service unit were installed, and PPPoE remains **STOPPED/DISABLED**. Original SSH 192.168.2.220/24 remains accessible via NetworkManager netplan-eth0; no ISP WAN connection attempted or ONT cabling modified. Follow section 2 next (Kea/Unbound installation MASKED), then section 3 (physical ONT/PPPoE auth test). Do not repeat section 1 unless intentionally repairing config.

## 1. NOW, while ASUS broadband is still working: install PPPoE but DO NOT connect

From `admin-01`:

```bash
cd ~/projects/homelab-platform
git fetch origin
git switch feature/pi-router-iac-birdnet-poc-migration-20261027
git pull --ff-only origin feature/pi-router-iac-birdnet-poc-migration-20261027
cd IaC/ansible

ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-pppoe-install-inplace.yml \
  --limit docker-01 --ask-become-pass --ask-vault-pass \
  -e @"$HOME/.config/router-01/pppoe-vault.yml" \
  -e router_pppoe_install_approved=true
```

This **installs `ppp` and root-private /etc/ppp secrets**, plus a dedicated `router-pppoe.service` in STOPPED/DISABLED state. It checks real eth0/eth1 MACs, Debian13, hostname `docker-01`, active `netplan-eth0` and old SSH IP, without readdressing any interface. It never starts a PPPoE session or changes ASUS broadband.

## 2. NOW, before losing ASUS WAN: install Kea + Unbound but KEEP MASKED

```bash
ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-dhcp-install-inplace.yml \
  --limit docker-01 --ask-become-pass \
  -e router_dhcp_install_approved=true
```

This installs and syntax-checks the `192.168.3.0/24` Kea scope and future `.3.1` Unbound resolver. It explicitly **MASKS and DISABLES both services**. Never unmask/start Kea while `eth0` is attached to the old ASUS LAN: DHCP broadcasts could otherwise get competing replies. Docker is not removed here.

## Live DNSSEC trust-anchor issue and Git-only repair (27 Oct 2026, 11:26 GMT)

User ran `router-01-dhcp-install-inplace.yml` on actual `docker-01`:

- **Recap: 12 OK, 4 changed, 1 failed** (and no unreachable hosts).
- Kea and Unbound packages installed; both service units STOPPED/DISABLED/MASKED.
- Future Kea scope `192.168.3.0/24` staged; `kea-dhcp4 -t` **PASS**.
- Future Unbound config staged, but `unbound-checkconf` **FAILED** because Debian's packaged `auto-trust-anchor-file` points to a missing `/var/lib/unbound/root.key`.
- Remaining final old LAN IP verification/report tasks did not execute due to the Unbound validation failure. There is **no evidence of PPPoE authentication, DNS/DHCP activation or LAN readdressing**.

**Remediation committed**: the playbook now explicitly installs Debian `dns-root-data`, requires non-empty `/usr/share/dns/root.key`, creates writable `/var/lib/unbound` for the `unbound` service user, initialises **only a missing** `/var/lib/unbound/root.key` from the Debian-maintained data, checks its size, then runs `unbound-checkconf`. A present runtime DNSSEC trust anchor is not overwritten, preserving RFC5011 trust-anchor tracking. Kea and Unbound remain masked throughout. Do NOT disable DNSSEC, hand-write root keys, unmask DNS/DHCP or move WAN cables to work around the failure.

**Rerun section 2 after pulling updated feature branch**. It is intended to be idempotent and should finish with the old LAN unchanged. If it fails again, inspect the *new* exact error before further change.

Debian packaged root data: https://packages.debian.org/trixie/all/dns-root-data/filelist and official Unbound trust-anchor setup: https://unbound.docs.nlnetlabs.nl/en/latest/getting-started/configuration.html .

## Live update — Kea and Unbound stage PASSED after DNSSEC repair

On 27 October 2026, user reran `router-01-dhcp-install-inplace.yml` on `docker-01`: **ok=22 changed=2 failed=0 unreachable=0**. Debian DNSSEC root data verified, missing `/var/lib/unbound/root.key` initialised, `unbound-checkconf` passed; Kea syntax passed. Both Kea and Unbound remain **stopped and masked**, protecting the existing ASUS DHCP network; original `eth0 192.168.2.220/24` and SSH validated unchanged. `ppp`, peer/authentication files and PPPoE systemd unit were already installed earlier and remain **stopped and disabled**.

**Stage 2 COMPLETE; proceed with Stage 3 ONT cable move and real ISP authentication test.** Keep Pi onboard `eth0` on the old HP switch for `admin-01` SSH. Do not move eth0, change IP, start DHCP/DNS or start router nftables yet. ONT to USB `eth1` takes ASUS internet offline temporarily; old ASUS LAN DHCP can still operate. The test can establish only WAN PPPoE, not working client traffic. If it fails, run PPPoE stop play and restore ONT to ASUS WAN.

## 3. Physical PPPoE authentication test — broadband interruption accepted

**Expect existing internet access through ASUS to go offline during this test.** Keep **Pi eth0 plugged into old HP switch** and SSH `192.168.2.220` reachable through the current LAN. ASUS LAN/DHCP continues to hand out `192.168.2.x` locally, even when its WAN disconnected.

1. Disconnect Ethernet from **ONT → ASUS WAN**.
2. Plug **ONT → Pi USB `eth1`**. Do **not** move Pi `eth0` yet.
3. On `admin-01` (same `.2.x` network), run:

```bash
ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-pppoe-connect-inplace.yml \
  --limit docker-01 --ask-become-pass \
  -e router_pppoe_connect_approved=true
```

It checks ONT carrier on `eth1`, marks **only eth1** unmanaged in NetworkManager, brings up the Ethernet link, starts pppd and verifies `ppp0` got an IPv4 address and a default route. The original eth0 LAN and SSH remain unchanged. A **PASS here proves only WAN authentication on Pi**, not yet client internet access/NAT/DHCP. It does not start Kea, Unbound or firewall forwarding.

**If ISP handshake fails:** confirm ONT/ISP session release and credentials outside logs, disconnect/reconnect ONT if appropriate; do not invent VLAN. To abort Pi PPPoE test:

```bash
ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-pppoe-stop-inplace.yml \
  --limit docker-01 --ask-become-pass \
  -e router_pppoe_stop_approved=true
```

Then **physically reconnect ONT → ASUS WAN**; give ASUS time to re-establish PPPoE. The Pi keeps SSH `.2.220` and both Kea/Unbound stay disabled.

## LIVE PPPoE PASS and immediate WAN-input protection stage

On 27 October 2026 user physically connected ONT to the Pi4 USB ASIX `eth1` and ran `router-01-pppoe-connect-inplace.yml` on actual `docker-01`: **14 OK, 3 changed, zero failures**. Link carrier passed; `router-pppoe.service` started and enabled; `ppp0` negotiated actual ISP IPv4 and installed default route; `eth0` kept old `192.168.2.220/24` SSH. Kea and Unbound remain STOPPED/MASKED, no NAT yet. ASUS WAN disconnected from ONT, so old ASUS LAN is local-only. The repeated `ifconfig` was run on `admin-01` (`192.168.2.48`), **not** the Pi; do not mistake admin-01's eth0 for the ISP WAN.

**WAN firewall concern:** earlier read-only Pi evidence showed host iptables `INPUT ACCEPT` and listening Nginx/SSH/metrics; the new ppp0 may expose them to ISP inbound traffic if assigned a routable address and no separate rule blocks them. Stage 0 for the remaining cutover is therefore a small, dedicated **PPP-only incoming firewall** managed by `router-01-wan-guard-inplace.yml`; it adds an independent nftables `inet router_wan_guard` INPUT base chain accepting established/related traffic and dropping unsolicited packets **arriving via ppp0 only**. Does **not** flush/rewrite Docker's filter/forward/NAT rules or the existing SSH LAN. The guard's separate `router-wan-guard.service` is enabled to start before PPPoE after reboot. Run on `admin-01`:

```bash
cd ~/projects/homelab-platform
git fetch origin
git switch feature/pi-router-iac-birdnet-poc-migration-20261027
git pull --ff-only origin feature/pi-router-iac-birdnet-poc-migration-20261027
cd IaC/ansible

ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-wan-guard-inplace.yml \
  --limit docker-01 --ask-become-pass \
  -e router_wan_guard_approved=true
```

After guard PASS, stage future ppp0 NAT and IPv4 forwarding files (syntax validated but **NOT ACTIVE**) on same existing host:

```bash
ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-firewall-stage-inplace.yml \
  --limit docker-01 --ask-become-pass \
  -e router_firewall_stage_approved=true
```

Files remain inside private `/var/lib/router-01-stage/forwarding/`; they are NOT loaded and forwarding is NOT enabled. On *later* isolated .3.1 LAN activation, after Docker is stopped/retired and its iptables FORWARD DROP is reconciled, the staged complete router firewall becomes owner (it uses `flush ruleset`, intentionally NOT permitted while Docker running). It then replaces the standalone ppp0 guard with complete default-deny WAN input, enables IPv4 forwarding and NAT. **Do NOT activate this merely after both stage playbooks pass; a physical eth0 separation and Netplan/NetworkManager cutover are still needed.**

Why Docker reconciliation matters: Docker's historical iptables `FORWARD DROP` can drop packets despite an `accept` in a different nftables forward chain. See Docker's firewall docs: https://docs.docker.com/engine/network/firewall-nftables/ .

## 4. NEXT — connect DHCP and routing AFTER PPPoE PASS

The final **LAN and client forwarding** step is separate, because the existing old `.2.x` LAN must NOT share a broadcast segment with the new Kea DHCP server. Changing `eth0` while logged in to `.2.220` can break the SSH session.

Required topology for the initial double-NAT phase:

```text
ISP ONT --- Pi eth1 (ppp0; PPPoE to ISP)
                Pi eth0 (192.168.3.1; Kea DHCP/Unbound)
                          |
                       ASUS WAN (automatic DHCP from Kea, .3.x)
                       ASUS LAN (192.168.2.1; existing DHCP + AiMesh)
                          |
                       HP switch --- existing 192.168.2.x clients
```

- First ensure an **actual working Netplan/NetworkManager native IP-change and timeout rollback** is implemented for the real `netplan-eth0` file. The legacy systemd-networkd rollback installer is HARD DISABLED and **must not be run**.
- Prepare firewall/NAT `eth0 .3.0/24 → ppp0`, enable IPv4 forwarding, validate no Docker-managed iptables chain blocks forwarding (retire Docker before router NAT activation), verify DNS/UDP 53 and DHCP UDP 67 (from source 0.0.0.0) allowed on the new LAN.
- During the explicit physical LAN handover: unplug Pi eth0 from old HP switch, connect it to **ASUS WAN**, activate Pi LAN `192.168.3.1/24` then unmask/start Kea and Unbound. **Never enable DHCP on eth0 while still connected to the HP switch/ASUS LAN**.
- Keep ASUS **router mode** and its LAN DHCP at `192.168.2.1`. ASUS WAN is **DHCP/automatic**; don't set a guessed fixed 192.168.3.2 IP. Verify an actual lease, DNS, client traffic/NAT and external browsing, then consider later separate ASUS AP-mode conversion.
- At IP cutover, a direct screen/keyboard or laptop on isolated Pi LAN and an tested rollback/recovery path are required to avoid stranding management. The old `192.168.2.220` won't persist after physically separating the networks.
- After verified in-place host conversion, update canonical `CURRENT-STATE.md`, inventory, Prometheus/Komodo/Trivy targets, DNS names and `gpt-handover.md`. Never update deployed truth ahead of actual changes.

## Scope boundaries

These new playbooks are intentional **real installs on live Debian**; they do not reimage and do not alter existing LAN IP. They do NOT automatically decommission BirdNET/Komodo or begin routing. Do not use the earlier `router-01-basics.yml` playbook which assumes a fresh systemd-networkd router with a fully isolated LAN. Docker retirement remains independently tracked in issue #206 and draft PR #207.

Debian 13 pppd PPPoE plugin accepts `plugin pppoe.so` and `nic-eth1`: https://dyn.manpages.debian.org/trixie/ppp/pppd.8. ISC Kea explicitly binds to named interfaces and must be isolated from the old DHCP broadcast domain: https://kea.readthedocs.io/en/stable/config-examples.html .
