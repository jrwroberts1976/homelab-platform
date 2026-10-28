<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 toolset baseline — 28 October 2026

**Status (28 Oct):** live read-only Ansible audit **PASSED** (`ok=14`, `changed=0`, `failed=0`, `unreachable=0`, `skipped=2`). Phase-A five-package diagnostic installer is **staged, not deployed**. No router software, services, routes or firewall modified.

## Confirmed router state

The Pi4 still identifies as `raspberrypi` with LAN `eth0=192.168.3.1/24`, PPPoE `ppp0 MTU 1492`, and ASUS upstream-WAN client on the Pi LAN. Following a real reboot, nftables, PPPoE, dnsmasq DHCP, Unbound DNS, IPv4 forwarding, default `ppp0` route, default-deny original filter/NAT and both MSS 1452 forward directions all passed. The permanent nftables table `ip router_pppoe_mss` is active with packet counters. ASUS household LAN was subsequently restored to `192.168.2.0/24` (revalidate exact downstream host IPs). Old `docker-01` BirdNET/Komodo assumptions in production `hosts.yml` are stale, not authority for the live Pi.

## Baseline tools

| Stage | Packages/services | Intent | Deployment policy |
| --- | --- | --- | --- |
| A: diagnostics | tcpdump (already used), ethtool, mtr-tiny, traceroute, dnsutils, conntrack, jq | PPPoE/MTU/DNS/connection troubleshooting | Install missing packages only, no background daemon |
| B: measured diagnostics | nmap, iperf3, vnstat | LAN testing and traffic accounting | Optional; check resource and listening-port impact |
| C: metrics | prometheus-node-exporter | Export CPU, RAM, filesystem, interface and service status | Restricted LAN scrape only; no new WAN-open port |
| D: log shipping | Grafana Alloy (systemd journal, possibly PPPoE/dnsmasq/Unbound) | Outbound transport to Loki | Verify central `monitor-01:3100`, avoid DNS query privacy leakage |
| E: alerting | Zabbix Agent 2 | Service + agent monitoring | Prefer active outbound to known Zabbix server; passive port 10050 remains closed unless scoped |
| F: patching | unattended-upgrades with no automatic reboot | Security-only maintenance and telemetry | No unattended reboot of household WAN router |
| G: clock and security | Check chrony/time source, existing ssh/firewall, Greenbone external scan | Reliable logs and vulnerability baseline | Do not overwrite working time/network policy with generic role |
| Later project | WireGuard VPN; optional Suricata IPS / content filtering | Remote access, advanced inspection | Separate performance/recovery design, not installed here |

The repository already has reusable `node_exporter`, `zabbix_agent`, `alloy`, `automated_patching`, and `chrony_client` roles, but none is approved for blind application to the live router. Important issues: existing Alloy asserts target hostname == inventory hostname (`raspberrypi` vs `router-01`); its default package version may be older than current fleet; its hard-coded Loki URL is `192.168.2.52`. Zabbix currently points at historical `192.168.2.59`; verify backend reachability first. The current Pi INPUT policy only allows LAN SSH/DNS/DHCP/ICMP, so remote scraping on TCP 9100/10050 would not work without an explicitly scoped rule. Never expose monitoring ports via `ppp0`.

## Read-only audit

Run from `admin-01` in a **separate worktree**, preserving local `main` or previous router review branches:

```bash
cd ~/projects/homelab-platform
git fetch origin feature/router-01-toolset-audit-20261028
git worktree add --detach ../homelab-router-toolset-audit FETCH_HEAD
cd ../homelab-router-toolset-audit/IaC/ansible

ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-toolset-audit.yml --syntax-check

ansible -i inventory/router-01-toolset-audit.yml \
  router-01 -m ansible.builtin.ping

ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-toolset-audit.yml --ask-become-pass \
  --check -e router_toolset_audit_approved=true
```

**This playbook is read-only even in normal Ansible mode**, and should report `changed=0`. It requires exact host `router-01 / 192.168.3.1`, Pi eth0 MAC `d8:3a:dd:5a:51:44`, Debian, current LAN/PPPoE MTU and healthy core services before showing installed packages and listeners. It probes current configured Loki and Zabbix servers without making any change or claiming those endpoints are current.

After reviewing audit output, author separate explicitly approved router-only Ansible install steps, then validate changes with `--check --diff`, capture backups, deploy one stage at a time, verify gateway health, SSH and internet from a downstream client.

## Non-goals and safeguards

Do not install Docker, Komodo Periphery, Kea, inline IPS, new default-DROP chains, a new DHCP/DNS service or the generic estate-wide `automated-patching.yml` as part of the audit. Do not reload/restart nftables, pppd or NetworkManager. Keep the original firewall backup `/etc/nftables.conf.2112.2026-10-28@13:09:59~`, and update actual operational truth `docs/architecture/CURRENT-STATE.md` only after verified deployment. Related tickets: [Router conversion #206](https://github.com/jrwroberts1976/homelab-platform/issues/206), [MSS persistence PR #208](https://github.com/jrwroberts1976/homelab-platform/pull/208), [Toolset issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209).

## 28 October — actual admin-01 read-only audit (operator evidence)

The user recovered SSH to `admin-01` at **192.168.2.48** (password login), fetched this branch to a separate detached worktree and ran the read-only toolset audit in `--check` mode with `-e router_toolset_audit_approved=true`. Syntax check passed. Real Ansible recap:

```text
router-01 : ok=14 changed=0 unreachable=0 failed=0 skipped=2
```

- Host authenticated/verified: `raspberrypi`, Debian 13 `aarch64`, eth0 MAC/IP and ppp0 1492 checks PASS.
- Essential `nftables`, `router-pppoe`, `dnsmasq`, `unbound` passed both active and enabled checks.
- Persistent nftables TCP MSS 1452 bidirectional rules present.
- **Installed:** `tcpdump=4.99.5-2` and `ethtool=1:6.14.2-1`.
- **Missing/uninstalled in package audit:** `prometheus-node-exporter`, `alloy`, `zabbix-agent2`, `unattended-upgrades`, `mtr-tiny`, `traceroute`, `dnsutils`, `conntrack`, `jq`, `nmap`, `iperf3`, `vnstat`, `chrony`, `auditd`, `wireguard-tools`, `suricata`. Missing optional unit `is-active` printed `inactive`; absence is established by package query, not by service state alone.
- Listeners observed: SSH TCP 22 on all IPv4/IPv6, Unbound DNS TCP/UDP 53 at LAN and loopback, dnsmasq DHCP UDP 67, Avahi UDP 5353; no exporter/Zabbix listener.
- Loki and Zabbix connectivity probes were **SKIPPED by Ansible check mode**, not proven unreachable. Audit playbook amended after this run: only these two read-only probes now set `check_mode: false`. Re-run the updated playbook to obtain actual network evidence.

### Approved-tools candidate: Phase A diagnostics-only (NOT DEPLOYED)

`playbooks/router-01-diagnostics-install.yml` uses the same isolated inventory and an additional opt-in variable `router_diagnostics_install_approved=true`. It checks exact router identity, LAN, PPPoE, four critical services, persistent MSS, original filter/NAT, free space and simulated APT removals before installing only **mtr-tiny, traceroute, dnsutils, conntrack, jq**. `tcpdump` and `ethtool` already exist and are left untouched. APT package installation uses `install_recommends: false` and a temporary `policy_rc_d: 101` to suppress service auto-start; no service/network/firewall restart task exists. Post-install verifications re-check PPPoE, four services, MSS and firewall/NAT.

The new installer has **not yet passed an on-controller syntax check, check-mode preview or real run**. Follow this order from `admin-01`:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/router-01-toolset-audit.yml playbooks/router-01-toolset-audit.yml --syntax-check
ansible-playbook -i inventory/router-01-toolset-audit.yml playbooks/router-01-diagnostics-install.yml --syntax-check

# No live changes: reads Loki/Zabbix even under --check after fix
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-toolset-audit.yml --ask-become-pass --check \
  -e router_toolset_audit_approved=true

# Preview diagnostic apt changes, no install:
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-diagnostics-install.yml --ask-become-pass \
  --check --diff -e router_diagnostics_install_approved=true
```

**Do not run the installer without `--check` until this dry run passes and the APT simulation is inspected.** A later separately authorised live run uses the same command *without* `--check`, then requires post-install router and household browser checks. Agent rollout is an independent next stage. Legacy `docker-01` production inventory and base roles remain out of scope until reconciled.
