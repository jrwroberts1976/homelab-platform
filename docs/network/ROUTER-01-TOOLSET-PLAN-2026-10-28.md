<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 toolset baseline — 28 October 2026

**Status (28 Oct): STAGES A AND C1 COMPLETE — VERIFIED LIVE.**

**Node Exporter Stage C1 LIVE PASS:** operator's approved normal-mode Ansible run completed **`router-01 ok=37 changed=4 unreachable=0 failed=0 skipped=2`**. Debian `prometheus-node-exporter` installed, a systemd override written to bind `127.0.0.1:9100`, only exporter service started/restarted. HTTP local metrics and required metric names passed; postflight confirmed localhost-only TCP 9100, original PPPoE default route, 4 critical gateway services, nft filter/NAT and MSS clamp unchanged. **No LAN/WAN monitoring ingress or Prometheus target is configured.** A client-side household internet test has not yet been reported.

 Ansible's corrected installer re-ran in normal mode at ~15:23 UK time and **PASSED** (`ok=28 changed=0 unreachable=0 failed=0 skipped=0`). All five real diagnostic packages returned `dpkg-query rc=0 / install ok installed`, and PPPoE routing, `nftables`, `router-pppoe`, `dnsmasq`, `unbound`, persistent MSS 1452, original firewall/NAT postflight passed. Earlier APT installation had already installed the packages; rerun was idempotent. Monitoring Loki/Zabbix connections from router remain unresolved; no agents installed. No router services/network/firewall were restarted or modified in this final run.

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

## 28 October — monitor-01 read-only preflight YAML parse failure, source corrected

Operator fetched branch through `0fa641e3`, attempted `monitor-01-loki-readiness-readonly.yml --syntax-check` and then `--check`. **Both failed during YAML parsing before any Ansible task/remote connection**, pinpointing line 105 `argv: [ss, -ltn, sport, =, :3100]`. The `ss` socket-filter argument `:3100` was unquoted in a YAML flow sequence and the parser rejected it. This error has **no bearing on Loki container health**, and neither command inspected or altered `monitor-01`.

The source playbook now uses a YAML block sequence with safely quoted `"="` and `":3100"` as independent `ss -ltn sport = :3100` arguments (GitHub commit `620d697d`). This is a **Git-only repair**. The revised playbook has **not yet** been checked or run by the user, so the Loki 503 root cause is still unknown. Follow exactly the read-only invocation already documented above after fetching this branch. **Always confirm `--syntax-check` passes before executing `--check`**. Never run `playbooks/monitoring.yml` or restart containers as a workaround for a YAML parser error.

## 28 October 2026 ~15:38 GMT — monitor-01 local Loki audit PASS; prior 503 not currently reproduced locally

Operator fast-forwarded draft PR #210 branch through `065748dc`, ran `monitor-01-loki-readiness-readonly.yml --syntax-check` and `--check -e monitor_loki_readonly_approved=true` using canonical `inventory/hosts.yml --limit monitor-01`; both **PASS**, real recap **`monitor-01 ok=13 changed=0 unreachable=0 failed=0 skipped=0`**. The playbook **made no changes**.

Verified from the local `monitor-01` itself: `docker.service active`, `monitoring-loki-1` image `grafana/loki:3.7.7` **Up 2 hours** and published TCP `0.0.0.0:3100` and `[::]:3100`; **`http://127.0.0.1:3100/ready` HTTP 200**, Loki buildinfo HTTP 200; TCP 3100 LISTEN; filesystem 79G total, 23G used, **53G free (31% used)**. Other compose services running: Prometheus v3.14.0, Alertmanager v0.34.0, Blackbox Exporter v0.29.0, Grafana container observed **13.2.1**, while repository defaults `monitoring_grafana_image` currently say **13.2.4** (possible deployment drift; do not deploy blindly).

Recent Loki logs show successful HTTP 200 queries and TSDB indexing, plus `deletion is not available for this tenant` warnings/errors in the compactor cache-generation path; these messages **do not establish a current unready service**, but may warrant a separate low-risk configuration review if recurrent. Local HTTP 200 does **not prove** the earlier `admin-01 -> 192.168.2.52:3100/ready` HTTP 503 is resolved from a second vantage or identify its historical cause. Do not claim the 503 root cause fixed, and do not restart or redeploy Loki.

**Next safe monitoring path checks, no package/firewall/service changes**: from `admin-01` verify `http://192.168.2.52:3100/ready` is now HTTP 200; from `monitor-01` verify `ip route get 192.168.3.1` and TCP connectivity to `192.168.3.1:22`. These establish an inside-LAN-to-upstream-router path suitable for designing a *restricted pull* Node Exporter scrape. They do **not** grant or test port 9100; exporter is not yet installed and the Pi INPUT firewall currently has no monitored-exporter exception. Any later Node Exporter/agent installation or Pi nftables allowlist must be separately safety-gated, with proven ASUS WAN IP/source, localhost and from-monitor scrape evidence, and no ISP WAN exposure. Active Zabbix or outbound Alloy from Pi to `.2.x` remain blocked by the distinct Pi `ppp0` routing/ASUS NAT boundary.

## 28 October ~15:57 BST/GMT — monitor-01 outbound path to router verified

Operator on `admin-01` ran the last three **read-only** checks from the live monitoring estate:

- `curl http://192.168.2.52:3100/ready` returned **HTTP 200** from `admin-01`. Prior HTTP 503 is no longer reproduced either locally on `monitor-01` or from `admin-01`; **cause remains unknown**, so no service restart or deployment warranted.
- From `monitor-01`, `ip -4 route get 192.168.3.1` showed **`192.168.3.1 via 192.168.2.1 dev eth0 src 192.168.2.52`**, i.e. across ASUS to upstream Pi.
- From `monitor-01`, `ansible.builtin.wait_for host=192.168.3.1 port=22` **SUCCESS** `state=started`, `changed=false`, confirming TCP connectivity in the **downstream-to-upstream** direction (only port 22 demonstrated). Ad hoc `ansible.builtin.command` route read was labelled CHANGED by Ansible's default even though `ip route get` does not change the routing table; no actual router/network modification occurred.

This supports designing a **pull-based Node Exporter** for `monitor-01` to scrape Pi `192.168.3.1:9100` via ASUS, rather than forcing Pi-originating traffic into private downstream `.2.x`. It does **not** prove 9100 is allowed/open, because exporter is not installed and Pi's input policy is default-deny. Explicit minimal ingress allowance, source NAT awareness, bind address and boot recovery need review first. Forwarding on `ppp0` must NEVER expose metrics to the ISP.

### Stage C preflight prepared — source-only, no agent deployment

Added `IaC/ansible/playbooks/router-01-exporter-ingress-readonly.yml` to the isolated audit branch, requiring controller `admin-01`, exact router IP `192.168.3.1`, physical `eth0` MAC and opt-in `router_exporter_ingress_audit_approved=true`. Reads **live `nft -a list table inet filter_router`**, current main routes, LAN IPv4 neighbors, Pi's dnsmasq leases (if readable), currently bound TCP sockets, Node Exporter package status, and confirms all four critical services active. Logs changes as READ ONLY; no network or package mutation. This playbook has **not been syntax-checked or run on admin-01 yet**.

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-exporter-ingress-readonly.yml --syntax-check && \
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-exporter-ingress-readonly.yml --check --ask-become-pass \
  -e router_exporter_ingress_audit_approved=true
```

**Design gate:** Identify real ASUS WAN IP on Pi `.3.x`, any stable DHCP reservation, trusted source semantics after ASUS NAT, current nft input-chain order and default-deny, and whether `9100` is already used. If source is SNATed to ASUS WAN IP, a Pi firewall rule restricted to ASUS WAN IP permits *downstream LAN hosts behind ASUS*, not just `monitor-01` specifically; avoid falsely representing it as host-specific protection. Do not apply a firewall rule, modify ASUS mode, restart router services or install/export Node Exporter until that evidence is reviewed. After a safely authorized exporter rollout, add exact scrape target in Prometheus via separate reviewed IaC; do not redeploy entire monitoring stack blindly. Zabbix/Alloy outbound paths remain unresolved.

## 28 October ~16:11 — Live exporter ingress audit PASS, repeated; Stage C1 localhost-only prepared

Operator executed `router-01-exporter-ingress-readonly.yml` **twice** from `admin-01` using `--syntax-check` and `--check`. Both PASS `router-01 ok=14 changed=0 unreachable=0 failed=0 skipped=0`. No router or ASUS services/config changed.

**Live Pi firewall and routing:**
- `inet filter_router input`: **policy drop**, loopback accept, `ct state established,related` accept, invalid drop; on `eth0` TCP allows **22 and 53 only**, UDP **53 and 67**, ICMP. **No TCP 9100 allow**.
- `forward`: policy drop with established/related and `eth0 -> ppp0 ip saddr 192.168.3.0/24 accept`. Output policy accept.
- Routes `default dev ppp0`, `192.168.3.0/24 dev eth0 src 192.168.3.1`; PPPoE WAN source is a public address (do **not** put monitoring on `ppp0`).
- TCP listeners are SSH `0.0.0.0:22` and `[::]:22`; DNS `127.0.0.1:53` and `192.168.3.1:53`. **No TCP 9100 listener; `prometheus-node-exporter` package absent.**
- DNSMASQ leases include `192.168.3.142` / MAC `04:d4:c4:b8:52:28` / **hostname `*`**, and `192.168.3.187` / MAC `04:d4:c4:c1:62:38` / **hostname `RT-AC86U-6238`**. The neighbour table listed `.142` with matching MAC as `REACHABLE`, but **neither DHCP hostname nor the neighbour listing conclusively proves which address performs source NAT for `monitor-01`**. Do not invent a source-IP firewall allowlist until verifying WAN-side ASUS IP and translated source during monitor traffic.
- All four critical units (nftables, router-pppoe, dnsmasq, unbound) active.

### Stage C1 — source-only LOCALHOST Node Exporter pilot (NOT INSTALLED)

New `IaC/ansible/playbooks/router-01-node-exporter-local.yml` is staged in draft PR #210 and requires `-e router_node_exporter_local_install_approved=true`. It targets only isolated `router_toolset_audit` inventory `router-01` `192.168.3.1`, and checks admin-01 controller, Pi MAC, Debian 13/aarch64, LAN IP, PPPoE MTU/default route, four active router services, existing nft filter/NAT and MSS 1452, no externally bound TCP 9100, free space, existing override safety, and APT simulation for no removals/upgrades.

It plans **only `prometheus-node-exporter`**, `install_recommends: false`, `policy_rc_d: 101` (suppress Debian package auto-start). Then Ansible configures a root-owned systemd `override.conf` with `ExecStart=/usr/bin/prometheus-node-exporter --web.listen-address=127.0.0.1:9100`, daemon-reloads and starts/enables only the exporter. `--web.listen-address` is supported by Debian 13 Node Exporter (Debian manual `https://manpages.debian.org/trixie/prometheus-node-exporter/prometheus-node-exporter.1.en.html`). On live run it verifies local HTTP 200 `127.0.0.1:9100/metrics`, expected node metrics, **only localhost listener**, gateway units, route, and unchanged original nftables filter/NAT/MSS. **No Pi INPUT rule or WAN port, ASUS config, Prometheus target, Zabbix, Alloy, or VPN change.**

The stage C1 installer is **source-only and has not been controller syntax-tested, dry-run, or deployed**. In check mode, it previews the APT task; file/drop-in/systemd tasks are intentionally skipped because the package/unit is not yet present and cannot be safely verified in check mode. Stage C1 produces **local metrics only**, not remotely scraped until a separately staged solution is designed.

First retrieve branch updates and perform *syntax-check and preview only*:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-node-exporter-local.yml --syntax-check && \
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-node-exporter-local.yml --check --diff \
  --ask-become-pass -e router_node_exporter_local_install_approved=true
```

**Stop after `--check --diff` and review APT simulation / proposed changes first.** Do not remove `--check` until the source has passed live syntax and dry-run and the operator approves. Post-deployment household browser check is still advised. Later service access may be solved using restricted source-aware Pi INPUT allow rule, SSH tunnel, or another reviewed architecture; access from downstream via ASUS NAT needs a firm source IP verification, and a WAN-IP allow from ASUS might grant *all downstream clients*, not just monitor-01. Avoid automatic proxy-wide monitoring-stack redeploys.

## 28 October ~16:19 — Stage C1 Node Exporter preflight passed; no install yet

User fetched draft PR #210 branch through `1302fb48`, `router-01-node-exporter-local.yml --syntax-check` **PASS**, and ran `--check --diff -e router_node_exporter_local_install_approved=true` from `admin-01`; recap **`router-01 ok=31 changed=1(predicted) unreachable=0 failed=0 skipped=8`**. All exact Pi MAC/IP/Debian13, PPPoE MTU1492/default route, critical services, default-deny filter/NAT, persisted MSS, no pre-existing 9100 external socket, free-space and APT simulation checks **PASS**.

APT proposed only **`prometheus-node-exporter` (1 new package)**, **0 upgraded, 0 removed, 20 not upgraded**. Optional `prometheus-node-exporter-collectors` appeared only as a RECOMMENDATION and is disabled by `install_recommends:false`. Skipped check-mode tasks included override, local service startup and metrics checks, by design because package/unit do not yet exist; the fact that they skipped does not prove binding or endpoint until real run. **No packages or configurations were actually changed.**

**Final source-only safety improvement after this dry run:** Debian APT `policy_rc_d:101` should suppress maintainer service start, but if a package auto-started the unmodified vendor unit anyway, merely asking systemd `state: started` might leave it running without the new loopback-only flag. The playbook now uses **conditional `state: restarted` for only `prometheus-node-exporter` if either package or drop-in changes**, otherwise `started`, and conditionally daemon-reloads. This ensures any transient default listener is replaced by `127.0.0.1:9100` when first installed; existing Pi nft INPUT default-deny continues to protect from WAN and LAN. It never restarts PPPoE, Unbound, dnsmasq, nftables, or Docker. This change has **not yet been syntax-checked/dry-run on admin-01** and was not part of the previous preview.

**Next gate:** fetch current audit branch, syntax-check `router-01-node-exporter-local.yml` and repeat `--check --diff`; only after clean results execute the live playbook without `--check` using explicit approval. Live postflight must show 127.0.0.1:9100 HTTP 200 and node metric family, no eth0/ppp0/IPv6 wildcard listener, original nft filter/NAT, PPPoE default route and four core services unchanged; obtain operator browser check. **No Prometheus job, upstream firewall ingress or Zabbix/Alloy change is part of Stage C1.**

## 28 October ~16:24 — final safety-polished Stage C1 dry run PASS (NO LIVE INSTALL YET)

User on `admin-01` fast-forwarded the isolated branch to `cfa5691b`, including the exporter-only restart-if-necessary source refinement, then ran `router-01-node-exporter-local.yml --syntax-check` **PASS** and `--check --diff -e router_node_exporter_local_install_approved=true` **PASS**, recap `router-01 ok=31 changed=1 (predicted) unreachable=0 failed=0 skipped=8`.

APT preview: **one new `prometheus-node-exporter` package only**, `0 upgraded, 0 removed, 20 not upgraded`; `prometheus-node-exporter-collectors` only **recommended**, excluded by playbook. Exact router MAC/IP, Debian 13, PPPoE/default route/MTU, all four essential services, original nft filter/NAT/MSS, free space and no pre-existing exposed 9100 passed. Eight skips are expected for the absent package's override/systemd/HTTP-local-metrics post-deployment checks in check mode.

**The final revised playbook is now accepted for a bounded operator-approved live execution, but the actual run has NOT occurred in this evidence.** In existing `~/projects/homelab-router-toolset-audit/IaC/ansible` directory:
```bash
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-node-exporter-local.yml \
  --ask-become-pass -e router_node_exporter_local_install_approved=true
```

Monitor the full live recap and **require HTTP 200 localhost `127.0.0.1:9100/metrics`, node metrics, exclusively localhost TCP 9100, unchanged nftables/MSS/NAT/PPPoE route and four core services** before closing C1. Do not mistake dry-run `changed=1` for actual installation. No inbound TCP 9100 exception, Prometheus scrape, ASUS change, Loki/Alloy or Zabbix change is authorized in this stage. Verify household internet from a client after the live run.

## 28 October ~16:24+ — C1 real Node Exporter installation SUCCESS, not just preview

User executed the guarded `ansible-playbook -i inventory/router-01-toolset-audit.yml playbooks/router-01-node-exporter-local.yml --ask-become-pass -e router_node_exporter_local_install_approved=true` (normal mode, **not** `--check`). **Actual `PLAY RECAP`: `router-01 ok=37 changed=4 unreachable=0 failed=0 skipped=2 rescued=0 ignored=0`.** Reported four changes: APT install `prometheus-node-exporter`, create systemd override directory, write loopback-only systemd override, and enable/start/restart only `prometheus-node-exporter`.

Normal live postflight passed: local `http://127.0.0.1:9100/metrics` returned HTTP 200 and included `node_uname_info` and `node_network_receive_bytes_total`; only 127.0.0.1 TCP9100 listener present (explicitly no `192.168.3.1:9100`, `0.0.0.0:9100`, `[::]:9100`); `nftables`, `router-pppoe`, `dnsmasq`, `unbound` all active; original `inet filter_router`, `ip nat_router`, ppp0 default route and persistent two MSS1452 rules intact. The two skipped tasks were conditional checks for a pre-existing override; this was a new installation. **NO changes to nftables/ISP WAN, ASUS, Prometheus job, Loki, Zabbix, Alloy or unrelated gateway services were made.**

**Stage C1 is complete and accepted as localhost-only metrics; remote scraping is NOT configured or tested.** Obtain a client-side browser internet validation as an operational follow-up; no evidence of client check in the submitted excerpt.

**C2 safety gate:** Before configuring a Prometheus scrape, choose and review a restricted transport from `monitor-01` (ASUS downstream `192.168.2.52`) to Pi `192.168.3.1`. SSH22 via ASUS works, but direct TCP9100 is intentionally absent and Pi `input` default drop. Do not arbitrarily open 9100 or loosen default-deny; earlier Pi leases showed `.3.142` (neighbour reachable, no hostname) and `.3.187` (ASUS-named), but did NOT establish actual NAT source for `monitor-01`. If choosing TCP9100, strict `eth0` + expected ASUS WAN source and end-to-end packet-capture/test are needed, and note ASUS SNAT obscures individual downstream hosts. Alternatively explicitly design a loopback-preserving authenticated SSH transport without exposing 9100; either is a separate reviewed IaC change. Consider scrape-target config update without blind full monitoring stack cutover, and ensure boot/restart persistence.

