<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 toolset baseline — 28 October 2026

**Status (28 Oct):** toolset audit and installer dry-run previously passed. **Actual diagnostic APT installation ran and reported `changed`, but the subsequent package assertion failed** (`ok=21 changed=1 failed=1`) before post-install router health checks. Debian 13 resolves virtual `dnsutils` to real `bind9-dnsutils`; source assertion corrected, **awaiting operator's post-install validation/re-run**. Loki and Zabbix connections also remain unresolved. No intentional network/firewall service changes were made.

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

## 28 October — corrected audit and diagnostics preview evidence from admin-01

Operator fast-forwarded the isolated worktree to commit `317f271e` and ran the actual router diagnostics `--syntax-check`, updated read-only audit in `--check` and the diagnostic installer `--check --diff`. All completed without Ansible failures.

- **Corrected audit recap:** `ok=16 changed=0 unreachable=0 failed=0 skipped=0`. Expected Pi identity Debian 13 / aarch64, `eth0=192.168.3.1/24`, critical services enabled/active, and persistent MSS 1452 assertions all PASS. The network probes now genuinely ran.
- **Loki check:** reported `Loki readiness (HTTP 200 = ready): -1` — HTTP request unsuccessful, not a valid readiness response. **Zabbix check:** `failed to connect` to `192.168.2.59:10051`. Their root causes remain unverified, but router `192.168.3.0/24` and monitored services `192.168.2.0/24` are separated by the downstream ASUS gateway/NAT. Do not assume unrestricted bidirectional routing or alter the firewall to make probes pass. Before Alloy/Zabbix enrollment inspect downstream topology, service state, and suitable *outbound vs. inbound* telemetry direction.
- **Diagnostics installer preflight:** hardware/IP/PPP MTU/default route/forwarding, 4 active services, permanent MSS, original filter/NAT and 200MiB free-space gate all PASS. Simulated `apt-get -s` proposed no `Remv` lines.
- **Installer dry-run recap:** `ok=26 changed=1 unreachable=0 failed=0 skipped=2`. The only planned change is APT installation: 16 new packages (5 requested package names plus dependency packages), **0 upgraded, 0 to remove, 20 not upgraded**. Requested `mtr-tiny`, `traceroute`, `dnsutils` (Debian resolves to bind9-dnsutils), `conntrack`, and `jq`; dependencies `bind9-host, bind9-libs, libfstrm0, libjemalloc2, libjq1, liblmdb0, libmaxminddb0, libncurses6, libonig5, liburcu8t64, libuv1t64`.
- **No deployment yet:** dry-run correctly printed `CHECK MODE: no packages actually installed`. The two post-install package checks skipped in check mode by design; post-preflight route, critical services, MSS and original firewall/NAT checks passed. Do not report installed until real run and runtime checks.

**Next approved bounded action after reviewing this preview:** from the same `admin-01` worktree `IaC/ansible` directory, run:

```bash
ansible-playbook \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-diagnostics-install.yml \
  --ask-become-pass \
  -e router_diagnostics_install_approved=true
```

This installs diagnostics ONLY; it does not touch interfaces, firewall, nftables, PPPoE, DHCP, DNS or router hostname. Its preflight checks are re-run before APT and postflight checks repeat after installation. Verify full live recap, installed package versions, and Windows/ASUS client browsing after the run. If anything unexpected occurs, **stop**, do not force an apt change or restart/reload the router firewall.

Monitoring topology issue must remain open independent of successful diagnostic installation. Other monitoring and VPN products are not part of this live action.

## 28 October — live installation returned a verification assertion failure

Operator ran the approved `router-01-diagnostics-install.yml` **without** `--check` after a successful dry-run on `admin-01`. All identity, PPPoE, IPv4 forwarding, four service, persistent MSS, original nft filter/NAT, space and APT simulation gates passed. APT task `Install the five approved diagnostic utilities only` returned **`changed: [router-01]`**, and all 5 individual `dpkg-query` tasks returned `ok`. Next aggregate assertion `selectattr('stdout','equalto','install ok installed')` failed. Ansible recap: **`ok=21 changed=1 unreachable=0 failed=1 skipped=0`**.

**Important:** This is an **assertion failure after APT**, not evidence of an APT error. The play terminated before the `post_tasks` could verify route, four services, MSS and original filter/NAT. Do **not** claim those postflight checks passed. The user's subsequent browser outcome and exact `dpkg-query` values have not been supplied.

**Root cause analysis:** Debian 13 / trixie `dnsutils` is a **virtual package**, provided by concrete `bind9-dnsutils`. Previous dry-run already showed APT installing `bind9-dnsutils` instead of a package called `dnsutils`. Querying aggregate dpkg statuses under the virtual name cannot reliably match 5 installed concrete packages. Debian package source: `https://packages.debian.org/search?keywords=dnsutils&lang=en`. The branch installer now explicitly requests and checks `bind9-dnsutils` and asserts each actual package with `item.rc == 0` and `item.stdout | trim == 'install ok installed'`, printing the failing item if any; APT simulation also uses the real package name. This is a **source-only repair; the real install has not been rerun since the fix**.

**Recovery and verification path:** From `admin-01` separate worktree fetch and fast-forward `feature/router-01-toolset-audit-20261028`; syntax-check the modified installer; first run `--check --diff` again to confirm no pending package changes, then rerun the approved installation **without** `--check` so the per-package checks and postflight router service/MSS/NAT verification actually execute. If dry-run predicts an unexpected change, stop. After successful Ansible recap, confirm client-side internet. Do not reload/restart nftables or interfere with PPPoE/DHCP/DNS.
