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

## OFFLINE RECOVERY / DHCP-FIRST DIAGNOSTIC WHEN CHAT OR SSH IS UNAVAILABLE (27 Oct 2026)

**User report:** after the delayed physical cutover was ARMED (7 OK/1 changed), confirming Pi `192.168.3.1` from admin-01 failed with `Network is unreachable`; admin-01 remained `192.168.2.48/24`, ASUS LAN `192.168.2.1` responded, and old Pi `192.168.2.220` did not respond. The ASUS reportedly **did not receive a WAN DHCP lease**. The user will not be able to use this chat once they unplug cables, so instructions must work WITHOUT internet, GitHub or assistant connectivity. **No validated proof yet of actual local switch success or rollback.**

**Before another attempt, save these instructions locally** (printed or terminal). Do not re-arm a timer while the old one may still be pending. Keep the Pi eth0 and ASUS WAN as a *direct, isolated link*, never Pi eth0 connected to the HP switch if Kea may be running. The ASUS LAN remains on the HP switch.

At the **Pi's direct local console (keyboard/screen)** after ONT→USB eth1 and Pi eth0→ASUS WAN are physically plugged:

```bash
sudo /usr/local/sbin/router-01-nm-cutover status
ip -4 -br addr show eth0
sudo systemctl is-active kea-dhcp4-server.service
sudo systemctl is-enabled kea-dhcp4-server.service
sudo systemctl status router-lan-switch.service router-lan-rollback.timer --no-pager
sudo journalctl -u router-lan-switch.service -u router-lan-rollback.service -u kea-dhcp4-server.service -n 80 --no-pager
```

**Only if Pi eth0 actually shows `192.168.3.1/24` AND is physically isolated directly on ASUS WAN** (NOT HP switch), then turn on Kea for a DHCP-only diagnostic without changing Pi LAN addressing or resetting PPPoE:

```bash
sudo /usr/sbin/kea-dhcp4 -t /etc/kea/kea-dhcp4.conf
sudo systemctl unmask kea-dhcp4-server.service
sudo systemctl enable --now kea-dhcp4-server.service
sudo systemctl status kea-dhcp4-server.service --no-pager
sudo journalctl -u kea-dhcp4-server.service -n 60 --no-pager
sudo cat /var/lib/kea/kea-leases4.csv | tail -n 8
```

At the ASUS UI (still local on `192.168.2.1`, internet not required), WAN must be **Automatic IP**. Click WAN DHCP renewal/reconnect. Expect a **`192.168.3.100–199` lease with gateway `192.168.3.1`**. A Kea DHCP lease proves Pi→ASUS WAN Layer2+DHCP only; PPPoE/NAT and client internet are separate. If `192.168.3.1` is missing on Pi eth0, merely unmasking Kea is not a valid test: the previous Netplan cutover didn't finish (or timed rollback reverted it). **Do not enable Kea in that state**. Inspect the last `router-lan-switch.service` and `router-lan-rollback.service` logs. Only when the Pi's `eth0` is isolated can the local existing staged cutover be retried, and only after ensuring old timers inactive and script baseline checks pass. The script is at `/usr/local/sbin/router-01-nm-cutover`.

**Do NOT run `confirm` just because ASUS has a lease.** Verify PPP0 IPv4, NAT table, Unbound and actual client browsing before disabling the local rollback timer. Conversely the rollback timer may revert an unconfirmed but otherwise working DHCP trial after ten minutes. If console is unavailable, return to a known old management state (Pi eth0 on HP switch ONLY after confirming Kea is stopped/masked) before using Ansible over `192.168.2.220`; running arbitrary local commands from `admin-01` DOES NOT configure the Pi.

## CURRENT NEXT STEP — SINGLE-ONT PI ROUTER + ASUS WAN DHCP (27 Oct 2026)

**Physical network desired by user**: only Pi USB `eth1` connects to the Vodafone ONT; the Pi onboard `eth0` connects DIRECTLY to the **ASUS WAN**; ASUS **LAN** still connects to the HP switch and continues DHCP `192.168.2.1/24` to current clients. The ASUS **WAN must be configured to Automatic IP/DHCP** (it will receive a lease in `192.168.3.100–199` from Pi Kea). Temporary double NAT is intentional; ASUS AP mode is a separate future change.

**Live last-known**: user successfully authenticated PPPoE, then `router-01-wan-guard-inplace.yml` failed on **missing `ppp0`**, 3 OK/0 changed/1 failed at 11:56, proving no WAN guard actually installed. ISP ONT may have been moved back to ASUS; PPP can be disconnected without invalidating the pre-stage. `router-01-wan-guard-inplace.yml` has since been corrected to install a protective nft INPUT rule for `ppp0` even when the interface is temporarily absent. Existing Kea/Unbound are MASKED. **Do not rerun the old `router-01-firewall-stage-inplace.yml` requiring PPP up**; the NEW full cutover stage below replaces it.

### Stage router with old SSH available, no network change

**Do this while `admin-01` still has internet and can pull GitHub**, before changing ASUS WAN mode or unplugging the working ONT connection. Run:

```bash
cd ~/projects/homelab-platform
git switch feature/pi-router-iac-birdnet-poc-migration-20261027
git pull --ff-only origin feature/pi-router-iac-birdnet-poc-migration-20261027
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-lan-stage-inplace.yml \
  --limit docker-01 --ask-become-pass \
  -e router_lan_stage_approved=true
```

This stages `99-router-01-lan.yaml` for Netplan+NetworkManager, persistent unmanaged USB eth1 (PPPoE), `192.168.3.1/24`, full nftables PPP NAT/firewall, forwarding sysctl and **local 120-second deferred cutover + 10-minute automatic rollback**. It specifically runs `netplan generate --root-dir` with a temporary copy of the Pi's actual Netplan YAML: **validates the merge without changing active networking**. Confirms Kea/Unbound remain masked; Docker still untouched. PPPoE **does not need to be active** for staging. **STOP if staging fails; do not physically cut over.**

### Physical activation: one WAN, ASUS downstream

1. In ASUS web interface `192.168.2.1`, set Internet/WAN type **Automatic IP** (not PPPoE); leave ASUS operating mode **Wireless Router**, LAN `192.168.2.1/24` and DHCP/AiMesh unchanged. Its internet will stop until the Pi takes over.
2. Ensure the new stage Ansible above reported PASS. Keep Pi `eth0` on HP switch for the next ARM command (SSH is `192.168.2.220`). `admin-01` stays ASUS LAN `192.168.2.48`.
3. **ARM a detached local switch**, which starts **120 seconds AFTER** the command returns. This is the last Ansible call to the old IP:
   ```bash
   ansible-playbook -i inventory/hosts.yml \
     playbooks/router-01-lan-arm-inplace.yml \
     --limit docker-01 --ask-become-pass \
     -e router_lan_cutover_approved=true \
     -e router_asus_wan_automatic_ip_confirmed=true \
     -e router_operator_ready_to_rewire=true
   ```
4. **IMMEDIATELY AFTER ARM returns**, within the 120-second grace period: connect **ONT → Pi USB eth1**, unplug **Pi eth0 from HP switch** and connect **Pi eth0 → ASUS WAN**. Keep **ASUS LAN → HP switch**, other devices unchanged. There is now no electrical connection between the new Pi `192.168.3.0/24` segment and the old ASUS `192.168.2.0/24` switch segment except through ASUS routing.
5. The Pi's scheduled local program refuses to act if old ASUS `192.168.2.1` is still responding on `eth0`, or if the cable carrier is absent; it arms the **10-min rollback timer before readdressing**. It stops Docker's two approved workloads, disables Docker/socket/runtime (without package purge or volume/key deletion), installs the validated Netplan `.3.1` override, loads complete nft PPP WAN/NAT rules, enables IPv4 forwarding, starts Unbound/Kea on `.3`, and restarts/reenables PPPoE to reconnect to ONT. SSH `.2.220` intentionally ceases; Pi is reachable at `192.168.3.1` **through the ASUS WAN when its DHCP lease succeeds**.
6. In ASUS WAN status, verify it receives `192.168.3.100–199` with gateway/DNS `192.168.3.1`. Test internet on a device connected to ASUS LAN.
7. **ONLY IF** an ASUS LAN device browses successfully and the ASUS WAN lease is valid, DISARM rollback from `admin-01` using the new inventory and existing Ansible credentials:
   ```bash
   ansible-playbook -i inventory/router-01-cutover-new.yml \
     playbooks/router-01-lan-confirm-inplace.yml \
     --limit router-01 --ask-become-pass \
     -e router_lan_confirm_approved=true \
     -e router_asus_wan_dhcp_lease_verified=true \
     -e router_client_internet_verified=true
   ```
   The confirmation play requires real `ppp0` IPv4+default, active Kea/Unbound and nft NAT, then stops the rollback timer. Do NOT falsely attest success.

### If new network does not come up

- Do not turn on Kea manually on the old HP switch. If unconfirmed, local `router-lan-rollback.timer` restores previous Netplan DHCP and stops Kea/Unbound/PPPoE after ten minutes from activation. If the switch preflight aborts before changing networks, the rollback should not be needed.
- **Physically reconnect Pi eth0 to HP switch** and **ONT to ASUS WAN**. Restore ASUS WAN PPPoE settings (it was changed to Automatic IP during cutover) to return old internet. The old Pi `192.168.2.220` management DHCP becomes available again when cables are back.
- The legacy systemd-networkd rollback helpers are **not compatible** and remain disabled. Do NOT run them.
- Check Pi locally using monitor/keyboard or via reachable IP: `sudo /usr/local/sbin/router-01-nm-cutover status`, and journal `sudo journalctl -u router-lan-switch.service -u router-lan-rollback.service -n 100 --no-pager` (no PPP passwords). When the Pi is online at new `.3.1`, SSH may be reached from ASUS LAN `.2.x` via its WAN routing.

**KNOWN LIMITATIONS:** Stage/play syntax and Netplan offline generation cannot prove the ASUS WAN config or physical cabling; actual operation needs physical change. The hostname remains `docker-01` until separate IaC inventory/doc migration, and Komodo/BirdNET run their last cycles until cutover stops Docker. The previous observed `ppp0` dropout could indicate ONT moved back or a separate PPP stability issue; the cutover program retries PPP, but connection success still requires the actual ONT carrier and ISP session. If this fails it will not pretend success.

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
