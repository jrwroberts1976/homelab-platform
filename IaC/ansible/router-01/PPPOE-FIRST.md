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

## ISP settings to capture read-only

From current ASUS WAN > Internet Connection and the ISP agreement:
- Connection protocol: **PPPoE** (already confirmed)
- PPPoE login **username and password**; enter these only into *your own encrypted Ansible Vault*, do **not** paste the password in Git/PR/chat or console logs
- Any VLAN tag/priority needed on WAN (or **no tag**); unknown until checked. Do not guess an ISP VLAN ID.
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

## Later: approved reimaged router-01 only

Only after an explicitly approved handover, physical console arrangement and successful reimage of `docker-01` to **`router-01`**, the guarded `router-01-pppoe-prestage.yml` may be invoked with an off-Git Vault and `router_pppoe_prestage_approved=true`. It requires Debian 13, exact `eth0` and `eth1` MACs, reimage marker and preserved `192.168.2.220` SSH address.

It **only renders prospective PPPoE files** under `/var/lib/router-01-stage/pppoe`. It does not install packages, overwrite active `/etc/ppp` files, start `pppd`, connect the ONT, change LAN IP, change DNS, change DHCP, or disconnect SSH.

**Actual PPPoE login tests, external IP, reconnection and performance tests must wait for the separately approved ISP handover.** Confirm whether a WAN VLAN is needed before attempting that connection. Successful authentication and default route do not automatically prove DHCP/DNS/firewall forwarding works.

## Sources

- Debian 13 `pppd(8)` documents `plugin pppoe.so` and the `nic-<ethernet-interface>` option: https://dyn.manpages.debian.org/trixie/ppp/pppd.8
