# router-01 — PPPoE configuration first (no live change)

**Git-only as of 27 October 2026.** Tracks issue #206 / draft PR #207.

## What is configured

Debian 13 `pppd` loads the PPPoE plugin `pppoe.so` on the **ASIX AX88179 USB Ethernet** adapter `eth1` (MAC `00:24:9b:63:b3:8a`). The broadband connection appears as logical `ppp0` **only after a successful authenticated ISP session**. Current `docker-01` `eth0` at `192.168.2.220` remains untouched.

Ansible templates:
- `roles/router_basics/templates/ppp-homelab-wan.j2`: `pppd` peer options, `nic-eth1`, default route, persist/retry and initial MTU/MRU 1492.
- `roles/router_basics/templates/ppp-secrets.j2`: secrets are deployed root-only, through external encrypted Vault input, never stored plaintext in Git.
- `roles/router_basics/templates/router-pppoe.service.j2`: systemd unit, not enabled until separately approved final handover.
- `roles/router_basics/templates/20-router-wan.network.j2`: future raw `eth1` has no DHCP/IPv4; `ppp0` gets the ISP-assigned address.

**Only PPPoE preparation is in scope here.** DHCP, temporary DNS, nftables and LAN address switch are separately staged and must not be activated yet.

## Measured pre-cutover broadband baseline

User-supplied speed-test screenshot received 27 October 2026, while current ASUS remains the broadband router:

| Metric | Baseline |
|---|---:|
| Download | **36.43 Mbps** |
| Upload | **12.05 Mbps** |
| Ping / latency | **10 ms** |

This is a **single speed test**, not a guaranteed ISP line rate or proof of new Pi performance. At the approved cutover, take comparable repeated tests on the same client / server, with and without any subsequent IPS/proxy features, and record observed PPPoE reconnect time, stability, WAN errors and CPU load. Basic PPPoE+NAT should comfortably fit within Pi 4 hardware at this measured throughput, subject to actual testing. This screenshot does **not** show PPPoE credentials or VLAN tagging.

## ASUS WAN settings — read-only screenshots received 27 October 2026

The user supplied ASUS RT-AC86U WAN configuration screenshots. **No WAN or ISP settings were modified.**

| ASUS item | Verified value | Router-01 handling |
|---|---|---|
| WAN connection type | **PPPoE** | `pppd` with `pppoe.so` on USB `eth1` |
| Enable WAN | Yes | PPPoE systemd service enabled only at approved handover |
| Get WAN IP automatically | Yes | WAN IPv4 obtained through PPP negotiation on `ppp0`, **not DHCP on raw `eth1`** |
| PPP authentication | Auto | Leave PPPoE authentication method negotiable, protected PAP/CHAP secrets |
| Disconnect after inactivity | 0 | No idle disconnect, persistent session |
| MTU / MRU | 1492 / 1492 | `pppd` profile 1492 |
| Service Name | Blank | Do not specify one |
| Access Concentrator Name | Blank | Do not specify one |
| Host-Uniq / additional pppd options | Blank | No overrides requested |
| Internet detection | PPP Echo | LCP echo monitoring on Pi |
| PPP Echo Interval | **6 seconds** | `router_pppoe_lcp_echo_interval: 6` |
| PPP Echo Max Failures | **10** | `router_pppoe_lcp_echo_failure: 10` |
| ASUS NAT | Enabled, **Symmetric** | Basic Pi nftables masquerade planned; not claimed identical to ASUS symmetric NAT |
| UPnP | Enabled (secure mode enabled) | **Not automatically enabled** on Pi; assess inbound use/port forwards separately |

**PPPoE credentials are sensitive:** a previously shared screenshot displayed the current login and password. **Do not commit, quote, send again, or paste these values into any issue/PR or terminal transcript.** Treat the exposed password as needing rotation via the ISP at a planned non-disruptive point; rotate stored Vault values then. The PPPoE username should also remain outside public Git. Do not attempt an uncoordinated password rotation while ASUS is connected.

**Latest user confirmation:** the ASUS has **no WAN VLAN configured and no IPTV settings/menu**. For the initial `router-01` build, use **untagged PPPoE directly on physical USB `eth1`**, with no `8021q` VLAN subinterface and no invented VLAN ID. This reflects the observed ASUS setup; a missing ASUS IPTV menu alone is not definitive ISP documentation. At the approved handover, if PPPoE discovery does not complete, verify actual ISP/ONT requirements before considering a tagged WAN. IPv6 support remains a separate open item.

## ISP settings to capture read-only

From current ASUS WAN > Internet Connection and the ISP agreement:
- Connection protocol: **PPPoE** (already confirmed)
- PPPoE login **username and password**; enter these only into *your own encrypted Ansible Vault*, do **not** paste the password in Git/PR/chat or console logs
- **No VLAN setting is present on current ASUS (user-confirmed)**. Deploy untagged physical `eth1` for initial PPPoE; only revisit VLAN tagging if supported ISP/ONT evidence or connection testing requires it.
- Special ISP access concentrator/PPPoE service name if configured (default: none)
- MTU and any IPv6 requirements. Initial expected PPPoE MTU is **1492** on standard Ethernet, to be tested at cutover.
- ISP modem/ONT remains connected to ASUS throughout preparation; no second PPPoE session now.

### Create protected credentials — on admin-01 (user action, NOT performed by this PR)

Use a secure location **outside** `~/projects/homelab-platform`; ideally an encrypted backed-up secrets folder:

```bash
# This creates an ENCRYPTED file; the editor input is local, not a chat message.
mkdir -p "$HOME/.config/router-01"
chmod 700 "$HOME/.config/router-01"
ansible-vault create "$HOME/.config/router-01/pppoe-vault.yml"
```

In the editor that opens, enter the following using real credentials locally:

```yaml
router_pppoe_username: "YOUR_ISP_LOGIN"
router_pppoe_password: "YOUR_ISP_PASSWORD"
```

Store and back up the Vault password separately. Do not share this secrets file or run commands that print it. **Creating the Vault file does not contact or change any network device.**

## Safe config validation now, on admin-01 only

```bash
cd ~/projects/homelab-platform
git fetch origin
git switch feature/pi-router-iac-birdnet-poc-migration-20261027
cd IaC/ansible
ansible-playbook -i inventory/router-01-prestage.yml \
  playbooks/router-01-pppoe-prestage.yml --syntax-check
```

This only validates syntax on the controller; no SSH or PPPoE connection is attempted.

## Latest completed local secret check — 27 October 2026

The user ran `ansible-vault view` on `admin-01`, piping decrypted YAML into a validator which **only printed** `PASS: PPPoE credentials present`. The required keys are populated; file mode is `0600` and the Vault header is `$ANSIBLE_VAULT;1.1;AES256`. Neither actual ISP credential nor the Vault password was shared or recorded.

### Next: controller-only PPPoE rendering with the REAL Vault, no SSH

The new playbook `playbooks/router-01-pppoe-local-validate.yml` runs on **localhost only**, loads defaults, decrypts the off-repository Vault passed with `-e @`, renders PPPoE peer and authentication templates **in memory**, and reports a generic PASS without revealing credentials. It does **not** connect to `192.168.2.220`, `router-01`, the ASUS router or ISP. No PPPoE session, file installation or network changes.

On `admin-01`, after pulling the approved draft branch:

```bash
cd ~/projects/homelab-platform
git fetch origin
git switch feature/pi-router-iac-birdnet-poc-migration-20261027
git pull --ff-only origin feature/pi-router-iac-birdnet-poc-migration-20261027

cd IaC/ansible
ansible-playbook -i localhost, -c local \
  playbooks/router-01-pppoe-local-validate.yml \
  --ask-vault-pass \
  -e @"$HOME/.config/router-01/pppoe-vault.yml"
```

**Important:** Never use `-v/-vvv` troubleshooting with real credentials unless confirmed that outputs are redacted. No `ansible-vault view` without piping to a private validator and never paste decrypted content in chat. The playbook is intentionally marked `no_log: true` for sensitive tasks.

## Later: approved reimaged router-01 only

Only after an explicitly approved handover, physical console arrangement and successful reimage of `docker-01` to **`router-01`**, the guarded `router-01-pppoe-prestage.yml` may be invoked with an off-Git Vault and `router_pppoe_prestage_approved=true`. It requires Debian 13, exact `eth0` and `eth1` MACs, reimage marker and preserved `192.168.2.220` SSH address.

It **only renders prospective PPPoE files** under `/var/lib/router-01-stage/pppoe`. It does not install packages, overwrite active `/etc/ppp` files, start `pppd`, connect the ONT, change LAN IP, change DNS, change DHCP, or disconnect SSH.

**Actual PPPoE login tests, external IP, reconnection and performance tests must wait for the separately approved ISP handover.** Start untagged as per the existing ASUS settings, without adding any VLAN device. Successful authentication and default route do not automatically prove DHCP/DNS/firewall forwarding works.

## Sources

- Debian 13 `pppd(8)` documents `plugin pppoe.so` and the `nic-<ethernet-interface>` option: https://dyn.manpages.debian.org/trixie/ppp/pppd.8
