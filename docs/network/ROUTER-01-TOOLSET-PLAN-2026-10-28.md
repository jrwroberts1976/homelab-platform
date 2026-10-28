<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 toolset baseline — 28 October 2026

**Status:** design and read-only audit **staged in GitHub**. No software installed and no running Pi services, routes, nftables or addresses modified by this branch.

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
