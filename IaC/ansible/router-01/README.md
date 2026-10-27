# router-01 — initial PPPoE/DHCP/Unbound IaC (NOT DEPLOYED)

Tracked in [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206) and draft PR #207.

**Do NOT run any router role on the existing production `docker-01`.** It currently provides BirdNET POC on `192.168.2.220`. The ASUS router currently owns PPPoE/DHCP for the complete home network.

The router playbook uses a **separate staging inventory**, so it cannot resolve or contact production `docker-01` through `inventory/hosts.yml`. First obtain an *approved handover*, retire/reimage the Pi 4 as Debian 13 **router-01**, configure `eth0 = 192.168.3.1/24` over a physically isolated link under **systemd-networkd** with console access, and keep USB `eth1` unplugged from the live ONT. Verify Pi board/NIC MAC addresses, route absence, firewall restore and isolation before any deployment.

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

## Security and bootstrap safeguards

- `inventory/router-01-staging.yml` names ONLY future `router-01` at `192.168.3.1`; do not add it to canonical production inventory before verified handover.
- Ansible roles assert hostname, Debian 13, current router IP, **both Ethernet MACs** and lack of legacy `.2.220`/ASUS default route.
- No router service starts without explicit `router_activate_services=true`; no role runs without `router_deploy_approved=true`.
- Password is passed only via **encrypted external Ansible Vault file** (`router_pppoe_username`, `router_pppoe_password`). No credentials in repository, command-line extra-vars, terminal output or screenshots. File ownership/mode 0600.
- PPPoE login and VLAN tagging details still require read-only confirmation from ASUS; this role does not configure VLAN tagging. IPv6 is deferred.
- **Important:** the first bootstrap is not yet fully automated: install Debian image, initialize SSH/keys and isolated `eth0` networkd interface with offline media/console. `router_basics` only writes the lasting networkd definitions; it does NOT restart networkd or change live interfaces. Capture this dependency before claiming fully automated disaster recovery.
- Running `apt` may start package services briefly; that is why the role is allowed **only on physically isolated reimaged hardware**, never on the live Pi or production LAN.
- Some installer images use NetworkManager/ifupdown rather than networkd. Establish `systemd-networkd` ownership in the isolated image/console before role runs, with no competing Ethernet manager; the role aborts if networkd inactive.
- `router_activate_services=true` is intended only after full boot/network/firewall readiness. It enables nftables, Unbound, Kea and PPPoE; always keep console access and a proven ASUS rollback. On initial isolated tests with no ISP ONT, PPPoE service may retry; this is expected.
- `/etc/nftables.conf` is fully managed and includes `flush ruleset`: **never** apply to a shared Docker/Kodi/Proxmox host. Target MUST be fresh dedicated router-01.
- Templates are not yet verified with `nft -c`, `kea-dhcp4 -t` and `unbound-checkconf` on Debian. Run those validations and the Ansible syntax checks before deployment. No claim of tested production readiness.

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
