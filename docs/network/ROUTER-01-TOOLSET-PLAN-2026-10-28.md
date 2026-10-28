<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 toolset baseline — 28 October 2026

**Status (28 Oct): STAGE A COMPLETE — VERIFIED LIVE.** Ansible's corrected installer re-ran in normal mode at ~15:23 UK time and **PASSED** (`ok=28 changed=0 unreachable=0 failed=0 skipped=0`). All five real diagnostic packages returned `dpkg-query rc=0 / install ok installed`, and PPPoE routing, `nftables`, `router-pppoe`, `dnsmasq`, `unbound`, persistent MSS 1452, original firewall/NAT postflight passed. Earlier APT installation had already installed the packages; rerun was idempotent. Monitoring Loki/Zabbix connections from router remain unresolved; no agents installed. No router services/network/firewall were restarted or modified in this final run.

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

## 28 October ~15:23 GMT — Stage A diagnostics installation FINAL SUCCESS

After source fix to query real `bind9-dnsutils` rather than virtual `dnsutils`, operator on `admin-01` fast-forwarded the isolated branch and ran: `router-01-diagnostics-install.yml --syntax-check` **PASS**, `--check --diff` **PASS** `ok=26 changed=0 unreachable=0 failed=0 skipped=2` (only non-check-mode package assertions skipped), then real `ansible-playbook ... -e router_diagnostics_install_approved=true` **PASS `ok=28 changed=0 unreachable=0 failed=0 skipped=0`**.

In the real run, all five concrete package verification items individually reported `rc=0` and `stdout='install ok installed'`: **mtr-tiny, traceroute, bind9-dnsutils, conntrack and jq**. The APT task returned `ok` (no new installation on rerun), proving the prior installation step had already completed and the failure was in the old virtual-package assertion, now corrected. Preflight and postflight of `default dev ppp0`, active `nftables`, `router-pppoe`, `dnsmasq` and `unbound`, both persistent 1452 MSS clamp rules, original firewall `inet filter_router` and NAT `ip nat_router` **passed**. No service restart, network reconfiguration, firewall reload, or reboot performed.

**Stage A is accepted as software-installed and gateway-operational.** This evidence validates router core functionality **on the router only**; the separate post-install client BBC/browser test has not been reported. Stage C/D/E observability agents remain absent. Historical failed assertion and dry-run notes above are chronological evidence, now superseded by this final pass.

### Next stage — monitoring connectivity design, READ-ONLY

`router-01` (`192.168.3.1/24`) could not reach Loki HTTP `192.168.2.52:3100` nor Zabbix TCP `192.168.2.59:10051` in corrected prior audit. Both central services live in ASUS downstream `192.168.2.0/24` (router-mode + NAT), so an upstream Pi is not necessarily able to initiate traffic into that LAN. **Do not infer backend outage without testing from inside the ASUS LAN.** From `admin-01` on `192.168.2.0/24` test reachability to Loki and Zabbix and inspect local route; from Pi read route to downstream addresses without changing it. Choose push vs pull with least privilege: Prometheus and passive Zabbix may be accessed *from* downstream monitoring server *to* Pi `192.168.3.1` if Pi's input firewall and ASUS NAT permit, whereas Alloy pushing logs and active Zabbix to downstream services will need a separate, explicitly approved connectivity solution. **No port-forward/firewall changes or AP-mode cutover as part of this test.** Verify IP/host resolution and service state before agent install. Track in issue #209.

### Read-only two-vantage monitoring path probe (staged, NOT YET RUN)

New source-only `IaC/ansible/playbooks/router-01-monitoring-path-readonly.yml` compares `admin-01` (inside ASUS downstream `.2.x`) and router Pi (upstream `.3.1`), from the same Ansible invocation. It reads each origin's route to Loki/Zabbix, tests HTTP 200 for `192.168.2.52:3100/ready` and TCP connect to `192.168.2.59:10051`. Uses `check_mode:false` on read-only network requests to ensure these run in `--check`. Guards operator opt-in, controller hostname `admin-01`, router target `192.168.3.1` and actual Pi onboard MAC `d8:3a:dd:5a:51:44`. No host configuration, APT, service, firewall or routing changes.

Run from `admin-01` existing detached worktree (after safe `fetch` and fast-forward):

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-monitoring-path-readonly.yml --syntax-check
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-monitoring-path-readonly.yml --check \
  -e router_monitoring_path_audit_approved=true
```

**No monitoring agent packages have yet been installed; this playbook has not been executed on the controller and syntax is not yet tested there.** Interpret results: if admin-01 reaches the services but the router cannot, focus on directionality/routing through the ASUS (NAT) rather than asserting monitoring outage; if both fail, check the server/endpoint state from inside the ASUS LAN before any router-side changes. Any later changes to export traffic or access controls require separate reviewed IaC and narrow allowances; never WAN-expose Zabbix/Prometheus/Alloy.

## 28 October — actual two-vantage network evidence (PASS; no changes)

Operator ran `router-01-monitoring-path-readonly.yml --syntax-check` and `--check -e router_monitoring_path_audit_approved=true` on `admin-01`; **recap `router-01 ok=14 changed=0 unreachable=0 failed=0 skipped=0`**. All probes were read-only and actually executed (no check-mode skips).

| Origin | IPv4 path to 192.168.2.52/.59 | Loki TCP/3100 HTTP /ready | Zabbix TCP/10051 |
| --- | --- | --- | --- |
| `admin-01` on ASUS LAN `192.168.2.48/24` | Direct `eth0` (no gateway) | **HTTP 503**: reachable but not ready | **CONNECTED** |
| `router-01` upstream Pi `192.168.3.1/24` | **default `ppp0` ISP uplink** (not via ASUS) | Connection failed (status -1) | FAILED |

**Conclusions grounded in live evidence:** Both central endpoints are in the ASUS downstream `192.168.2.0/24` subnet. The upstream Pi has no specific route toward it and attempts to send this private traffic via the ISP default PPPoE path. Blindly adding a `192.168.2.0/24` static route is **not a complete solution**: ASUS's WAN NAT/firewall normally blocks unsolicited upstream connections to LAN servers. `admin-01` does reach Zabbix locally and reaches Loki but gets HTTP 503, so Loki has an **independent local health/readiness problem**. Do not use "Ansible task ok" as HTTP 200: readiness 503 is currently a failure signal. Client internet from ASUS post-tool install remains unreported.

### Staged next — monitor-01 local Loki audit, READ-ONLY only

New `IaC/ansible/playbooks/monitor-01-loki-readiness-readonly.yml` (source-only; NOT yet syntax-checked or executed on controller) targets existing canonical `monitoring_hosts` inventory host and refuses wrong hostname/IP, requiring an explicit opt-in. Collects Docker active state, local `127.0.0.1:3100/ready` HTTP status, buildinfo API, `docker compose ps --all`, 35 recent Loki compose log lines, local 3100 TCP listen state, and free space in `/opt/monitoring`. **No Docker service/container restart, no compose up/down, no config/iptables/routing/IP changes.** On `admin-01`:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-loki-readiness-readonly.yml --syntax-check

ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-loki-readiness-readonly.yml \
  --limit monitor-01 --ask-become-pass --check \
  -e monitor_loki_readonly_approved=true
```

**Do not run generic `playbooks/monitoring.yml`** to correct the 503 without reading this audit; it may pull and recreate monitoring containers. Avoid deploying `alloy` and `zabbix-agent2` from router-01 while it cannot route to their private server IPs.

**Later topology options to design (not applied):** retrieve verified ASUS WAN `192.168.3.x` IP, then design least-privilege controlled LAN-to-Pi telemetry pull (e.g., Proxmox/monitor-01 uses the ASUS NATed path to a Pi Node Exporter endpoint on `192.168.3.1`; Pi firewall must narrowly permit this from a verified WAN-side ASUS source). If push of journald/active Zabbix is desired, consider explicit ASUS mode changes or tunnel/route+NAT rules only with independent console rollback, staged IaC and impact assessment. Keep Pi `ppp0` firewall default-deny and never expose 9100/10050 on ISP WAN.
