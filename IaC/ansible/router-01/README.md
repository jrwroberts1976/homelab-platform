# router-01 — initial PPPoE/DHCP/Unbound IaC (NOT DEPLOYED)

Tracked in [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206) and draft PR #207.

**Do NOT run any router role on the existing production `docker-01`.** It currently provides BirdNET POC on `192.168.2.220`. The ASUS router currently owns PPPoE/DHCP for the complete home network.

The build now has **two separate inventories**, neither of which changes canonical live `inventory/hosts.yml`. Only after an *approved handover* and retirement/reimage of the Pi 4 as Debian 13 **router-01**, keep onboard `eth0` on the old SSH management address **`192.168.2.220`** while preparing configuration. This preserves your connection during configuration. Keep USB WAN `eth1` disconnected from the live ONT; do not enable a new DHCP server on the production LAN. Verify the Pi MAC addresses, new hostname, host-key fingerprint and full console/rollback access first. **Change `eth0` to `192.168.3.1/24` LAST**, inside the approved router handover when the ASUS is ready to take DHCP on its WAN.

## First-phase topology

```
ONT -- PPPoE -- router-01 eth1 (ASIX AX88179, MAC 00:24:9b:63:b3:8a)
                ppp0 = ISP WAN (initial PPP MTU 1492)
                eth0 = 192.168.3.1/24
                       Kea .3.100-.199; Unbound .3.1:53; nftables NAT/firewall
                     |
                     +---- ASUS WAN DHCP (no static/reservation yet)
                                 ASUS router, NAT, DHCP and AiMesh for 192.168.2.0/24
                                 HP switch, Proxmox and Pi-hole remain downstream
```

ASUS remains a router through the first broadband cutover and validation. Converting it to AiMesh AP mode is a **separate later approved change**. Double NAT acceptable. Existing `dns-01`/`dns-02` remain in downstream `.2.x`; the Pi uses its own temporary Unbound to resolve DNS for the new `.3.x` LAN. Follow-on WireGuard, Suricata IPS, E2Guardian, management dashboards and new host addressing are deliberately **not** installed in this phase. A later fresh BirdNET-Go install on Pi 5 is separate.

## Crucial sequencing: keep the SSH address until the very end

**Do not readdress the Pi as the first provisioning step.** Once the existing POC has been explicitly approved for retirement and the Pi reimaged, choose the old management address `192.168.2.220` on the new `router-01` image until the router configuration is ready. The currently active `docker-01` must not be touched before approved handover.

1. **Pre-stage over SSH at `192.168.2.220`, after reimage:** use `inventory/router-01-prestage.yml` and `playbooks/router-01-prestage.yml` (not `router-01-basics.yml`). This refuses ANY host contact before a local opt-in flag; on target it checks Debian13, `router-01` hostname, expected MACs, old management IP and a `/etc/router-01-reimage-complete` image-provenance marker.
2. That pre-stage playbook **only renders private, prospective config files under `/var/lib/router-01-stage/`**. It does **not** install packages, touch `/etc/systemd/network`, start PPPoE, enable DHCP/DNS/firewall, reconfigure interfaces or change the live IP. PPPoE secrets stay root-only and off Git. Reimage marker creation and an off-Git Vault path remain bootstrap prerequisites.
3. **Remaining engineering gate:** add an explicitly separate, verified phase to install packages and copy staged configs into final managed paths **while keeping the old address**, with package post-install autostarts suppressed and no network reload/reboot. The initial `router-01-basics.yml` playbook currently targets the `.3.1` final identity and must **not** be used as the pre-stage deployment tool. Do not claim all software is installed or ready after a mere pre-stage render.
4. **LAST: switch LAN IP** to `192.168.3.1/24`, with a local-console or direct-attached management laptop preconfigured on `192.168.3.x`, automated timed rollback if not acknowledged, and physically approved ASUS WAN DHCP connection. The SSH connection on `.2.220` is expected to drop. Ansible from `admin-01` may not be able to reach the upstream `.3.x` subnet through the ASUS WAN firewall afterward: validate a separate re-entry/console method in advance.
5. After the new address is proven reachable, activate the PPPoE, nftables NAT, Unbound and Kea services through a reviewed guarded cutover mechanism. Confirm DHCP lease, DNS, PPPoE, routes and broadband, then explicitly acknowledge success to cancel the automatic rollback. Restore the original ASUS WAN PPPoE cabling/session if cutover fails.

**Do not run a remote command to readdress `eth0` without first implementing and testing the recovery mechanism.** This plan changes the sequencing, not production.

### Stage-only example (never run before approval and actual reimage)

```bash
cd ~/projects/homelab-platform/IaC/ansible
# Syntax check only, no host connection:
ansible-playbook -i inventory/router-01-prestage.yml playbooks/router-01-prestage.yml --syntax-check

# LATER, only after approved reimage of docker-01 to router-01 and image marker:
# ansible-playbook -i inventory/router-01-prestage.yml playbooks/router-01-prestage.yml \
#   --ask-vault-pass -e @/secure/off-repo/router-01-vault.yml \
#   -e router_prestage_approved=true
```

## Security and bootstrap safeguards

- `inventory/router-01-prestage.yml` resolves ONLY future `router-01` at the original SSH management IP `192.168.2.220`, **after an approved reimage**. `inventory/router-01-staging.yml` names the final `router-01` at `192.168.3.1`. Neither is canonical production inventory.
- Ansible roles assert hostname, Debian 13, current router IP, **both Ethernet MACs** and lack of legacy `.2.220`/ASUS default route.
- No router service starts without explicit `router_activate_services=true`; no role runs without `router_deploy_approved=true`.
- Password is passed only via **encrypted external Ansible Vault file** (`router_pppoe_username`, `router_pppoe_password`). No credentials in repository, command-line extra-vars, terminal output or screenshots. File ownership/mode 0600.
- PPPoE login and VLAN tagging details still require read-only confirmation from ASUS; this role does not configure VLAN tagging. IPv6 is deferred.
- **Important:** the first bootstrap is not yet fully automated: install Debian image, initialize SSH/keys and isolated `eth0` networkd interface with offline media/console. `router_basics` only writes the lasting networkd definitions; it does NOT restart networkd or change live interfaces. Capture this dependency before claiming fully automated disaster recovery.
- Running `apt` may start package services briefly; that is why the role is allowed **only on physically isolated reimaged hardware**, never on the live Pi or production LAN.
- Some installer images use NetworkManager/ifupdown rather than networkd. Establish `systemd-networkd` ownership in the isolated image/console before role runs, with no competing Ethernet manager; the role aborts if networkd inactive.
- `router_activate_services=true` is intended only after full boot/network/firewall readiness. It enables nftables, Unbound, Kea and PPPoE; always keep console access and a proven ASUS rollback. On initial isolated tests with no ISP ONT, PPPoE service may retry; this is expected.
- `/etc/nftables.conf` is fully managed and includes `flush ruleset`: **never** apply to a shared Docker/Kodi/Proxmox host. Target MUST be fresh dedicated router-01.
- **Automated offline validation PASS (27 October 2026):** GitHub Actions `Validate router-01 offline IaC` rendered and syntax-tested Kea, Unbound and nftables on an isolated Ubuntu 24.04 CI runner, and ran Ansible `--syntax-check` on both router playbooks. The separate estate/documentation guard also PASS. **Debian 13 ARM64 on-hardware validation, PPPoE ISP session, DHCP broadcast/renewal and full recovery test are still outstanding.** Do not treat an Ubuntu CI pass as a production acceptance.

## Controller-only syntax checks (NO HOST CONTACT)

```bash
cd ~/projects/homelab-platform
git fetch origin
git switch feature/pi-router-iac-birdnet-poc-migration-20261027
cd IaC/ansible
ansible-playbook -i inventory/router-01-staging.yml playbooks/router-01-basics.yml --syntax-check
ansible-playbook -i inventory/router-01-staging.yml playbooks/router-01-readonly.yml --syntax-check
```

## Future isolated execution only AFTER handover permission

Obtain approved change and prepare a preconfigured reimaged `router-01` on isolated Ethernet with rescue console. Populate a secure vaulted file **outside Git** containing `router_pppoe_username` and `router_pppoe_password`. Do not execute any command below before this stage.

```bash
# Readonly target identity check FIRST, after rebuild:
ansible-playbook -i inventory/router-01-staging.yml playbooks/router-01-readonly.yml

# Then, separately approved, install but do NOT activate services:
ansible-playbook -i inventory/router-01-staging.yml playbooks/router-01-basics.yml \
  --ask-vault-pass -e @/secure/off-repo/router-01-vault.yml \
  -e router_deploy_approved=true

# Activate ONLY after change review with rescue path and safe isolation:
ansible-playbook -i inventory/router-01-staging.yml playbooks/router-01-basics.yml \
  --ask-vault-pass -e @/secure/off-repo/router-01-vault.yml \
  -e router_deploy_approved=true -e router_activate_services=true
```

No physical or network cutover has happened by introducing these files.
