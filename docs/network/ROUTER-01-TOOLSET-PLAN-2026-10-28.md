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


## 28 October ~16:25+ — post-install ASUS browsing confirmed; Stage C2 SSH tunnel discovery staged

Operator confirmed **"browsing all ok"** from their setup after the live Stage C1 Node Exporter install. Together with live Ansible `router-01 ok=37 changed=4 failed=0 skipped=2`, verified local metrics and gateway postflight, this **closes Stage C1 end-to-end operational safety acceptance**. No current internet disruption reported.

**Stage C2 remains research/source-only, NOT deployed.** Secure monitoring architecture must account for existing Prometheus **inside Docker** on `monitor-01`: a normal SSH `-L 127.0.0.1:19100:127.0.0.1:9100` on the monitor host is **not directly reachable from a Prometheus container's loopback**. Do not assume a host-local tunnel can be scraped by Prometheus without a purpose-built container access path. Binding a tunnel to `0.0.0.0` to get around this is **not permitted**; any non-loopback listener would need explicit interface/source protection and risk review. We also have not proven passwordless SSH authentication or SSH server forwarding permissions.

New source-only `IaC/ansible/playbooks/monitor-01-router-exporter-tunnel-readonly.yml` in draft PR #210 (not yet tested on admin-01) uses explicit approval `router_c2_tunnel_audit_approved=true`, strict `admin-01` controller and `monitor-01=192.168.2.52` identity guards. It reads `monitor-01` route to Pi, locally listening ports including proposed `19100`, Prometheus Docker container network topology **without printing container secrets**, and Prometheus HTTP readiness. It performs a safe, **non-interactive SSH authentication test** from monitor's `james` user to Pi `james@192.168.3.1` using `BatchMode=yes`, `StrictHostKeyChecking=yes`, no password prompts, and a read-only `true` command. Failure is **expected if keys or host trust have not been provisioned**; the audit does not create keys, alter `known_hosts` or start any SSH tunnel.

Run after safe fetch/fast-forward of existing worktree:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-exporter-tunnel-readonly.yml \
  --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-exporter-tunnel-readonly.yml \
  --limit monitor-01 --ask-become-pass --check \
  -e router_c2_tunnel_audit_approved=true
```

**This is only architecture discovery, not a tunnel, not a Prometheus scrape.** Inspect results before deciding between a locked-down persistent SSH transport, a Docker-aware tunnel sidecar or a tightly restricted LAN-only exporter interface. Do not alter live ASUS/WAN, Pi `nftables`, SSH host trust, monitoring Compose services or Prometheus config until a separate IaC plan with validation and rollback has been approved.

## 28 October ~16:38 — C2 secure SSH / Prometheus topology discovery LIVE PASS (no changes)

User on `admin-01` fetched the C2 tunnel discovery playbook and ran `--syntax-check` PASS followed by `--check --limit monitor-01 -e router_c2_tunnel_audit_approved=true` PASS, **`monitor-01 ok=11 changed=0 unreachable=0 failed=0 skipped=0`**. It was *read-only* and executed all probes.

- Prometheus **HTTP 200 ready** on monitor-01 localhost 9090; Docker inspect of `monitoring-prometheus-1` succeeded.
- Prometheus runs in **Docker bridge `monitoring_default`**, container IPv4 `172.18.0.4`, network mode `monitoring_default`. Host TCP `19100` currently **unused**. Thus a hypothetical host-only SSH local forward `127.0.0.1:19100` is *not reachable as container-localhost* from the Prometheus Docker container. Do not expose it with an unsafeguarded `0.0.0.0:19100` binding.
- `monitor-01` still routes `192.168.3.1 via 192.168.2.1 dev eth0 src 192.168.2.52` (via ASUS).
- `monitor-01` user `james` SSH to `james@192.168.3.1` with `StrictHostKeyChecking=yes`, `BatchMode=yes`, `PasswordAuthentication=no` **did not authenticate**. Explicit error: **"No ED25519 host key is known for 192.168.3.1 ... Host key verification failed."** This demonstrates a **missing trusted host-key record** and does *not* yet test whether an eligible noninteractive private key exists or is authorized. It is not proof of a credential problem. No key was accepted or added, no SSH tunnel was established.

### Next C2 security gate — verify actual Pi host fingerprint and existing trust (source-only)

A read-only Ansible playbook `IaC/ansible/playbooks/router-01-ssh-trust-readonly.yml` is staged on draft PR #210, **NOT yet syntax-checked/executed on admin-01**. It must use **both inventories** because the isolated router audit inventory intentionally lacks monitor-01 and production hosts.yml lacks this exact Pi entry:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/hosts.yml \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-ssh-trust-readonly.yml \
  --limit router-01,monitor-01 --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-ssh-trust-readonly.yml \
  --limit router-01,monitor-01 --ask-become-pass --check \
  -e router_c2_ssh_trust_audit_approved=true
```

This verifies the **actual** physical router eth0 MAC, reads its `/etc/ssh/ssh_host_ed25519_key.pub` SHA256 fingerprint **directly on Pi** and effective `sshd -T` forwarding policies; validates monitor-01 hostname and IPv4, tests if `james` has an existing known_hosts record for `192.168.3.1` and presence of public key files (**does not print or read any private key**). No `ssh-keyscan`, TOFU acceptance, copy of private keys, key generation, `known_hosts` mutation, SSH daemon change, tunnel, Docker modification or firewall change is performed. **Compare fingerprints before any future explicit IaC-pinned known_hosts deployment.**

C2 design remains pending: decide how a strictly restricted authenticated tunnel can be reached from the **Prometheus container** without an unsafe all-interface listener, using a dedicated nonprivileged identity/key with only `PermitOpen=127.0.0.1:9100` and no interactive privileges where practical. Future changes require a separate IaC proposal, dry-run and rollback. The live Pi exporter stays **only 127.0.0.1:9100**, and user-confirmed ASUS internet browsing remains OK.

## 28 October ~16:45+ — genuine Pi SSH fingerprint and monitor identity audit PASS (read-only)

Operator ran **new** `router-01-ssh-trust-readonly.yml` from `admin-01` using both `-i inventory/hosts.yml` and `-i inventory/router-01-toolset-audit.yml`, `--limit router-01,monitor-01`, syntax check PASS then `--check -e router_c2_ssh_trust_audit_approved=true` PASS. **Real recaps: `router-01 ok=7 changed=0 unreachable=0 failed=0 skipped=0`; `monitor-01 ok=9 changed=0 unreachable=0 failed=0 skipped=0`.** No SSH service restart/host trust/key/file changes.

Verified **on physical Pi** using `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256`:

```text
256 SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI root@raspberrypi (ED25519)
```

This fingerprint belongs to verified onboard eth0 MAC `d8:3a:dd:5a:51:44` / router alias `router-01`. Current general `sshd -T` output reports `pubkeyauthentication yes`, `passwordauthentication yes`, `gatewayports no`, `allowtcpforwarding yes`, `disableforwarding no`, `permitopen any`. This is **not a purpose-restricted metrics account**. It is general effective policy and may differ for specific Match conditions; validate actual effective policy for a future monitoring identity before deploying.

On `monitor-01` for `james`: `/home/james/.ssh/known_hosts` exists but **has no entry for `192.168.3.1`**. Standard public-key files `/home/james/.ssh/id_ed25519.pub` and `id_rsa.pub` both **absent**. The audit did **not** inspect arbitrary alternate key paths or private keys, so do not assert no possible credentials anywhere. Prior strict BatchMode SSH probe failed on **host-key trust** before testing authentication. Do not disable strict checking and do not treat a network-returned key as trusted unless it matches this verified fingerprint.

### Stage C2 design decision and security acceptance gates

Preferred design for review, **not approved/deployed**:

1. Provision an **independent, least-privilege SSH identity** just for monitoring, instead of `james` or existing fleet-wide private keys. Keep new private key restricted to monitor-01 (later a tunnel sidecar gets only the necessary read-only key material); never commit it to GitHub or Ansible output.
2. Retrieve Pi's actual **ED25519 public host key** through the already-verified Ansible connection, compare the SHA256 fingerprint to the independently captured `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`, and pin that exact key in a dedicated SSH known-hosts file on monitor-01; preserve `StrictHostKeyChecking=yes` and fail closed on mismatch.
3. Restrict a dedicated Pi account's authorized public key to **local TCP forwarding to `127.0.0.1:9100` only**. For any service account ensure no password login, no PTY, no agent/X11 forwarding, no remote command and no access to other Pi services. Check `sshd` effective `Match User` policy and validate SSH syntax before reload; do **not** modify global `sshd` settings or restart the router's networking.
4. Prometheus resides inside container `monitoring-prometheus-1` on Docker network `monitoring_default` (`172.18.0.4`). Prefer an **isolated tunnel sidecar that shares only the Prometheus container's network namespace** and binds its forwarding listener to container `127.0.0.1`, subject to image provenance, key restrictions, monitoring stack impact and rollback review. A host-local 127.0.0.1 tunnel is not accessible as Prometheus container's localhost; do not bind 19100 on all host interfaces as a shortcut.
5. Configure `monitoring_node_exporter_targets` through reviewed IaC, and update/reload *only* Prometheus configuration when tunnel has been proven working. Existing `playbooks/monitoring.yml` performs Docker Compose pull/up and must **not** be used as the quick way to add a scrape target. Require independent `up{target_name="router-01"} == 1` and related node metric checks after change, plus rollback.
6. Verify no TCP9100 on Pi LAN/ppp0 before and after, internet browsing behind ASUS, static monitoring host identity, router services/PPPoE/NAT/MSS intact, and SSH tunnel reconnection and system startup behavior. C2 remains **NOT INSTALLED** until separate branch-reviewed implementation and normal deployment approval.

Do not expose the Pi host's live SSH public-key contents or any generated private key in user-facing notes or repository commits. The SHA256 public fingerprint alone is suitable as a documented security pin.

### C2a implementation candidate: independently pinned host trust ONLY (NOT RUN)

Staged source-only `IaC/ansible/playbooks/router-01-ssh-host-pin.yml` on draft PR #210. Before any trust write, the playbook:
- Requires explicit `router_c2_host_pin_approved=true`, `admin-01` controller, exact Pi `192.168.3.1` + hardware MAC and monitor `192.168.2.52` + hostname guards.
- Reads the **physical Pi's own** `/etc/ssh/ssh_host_ed25519_key.pub` using the existing authenticated Ansible link; validates exact `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI` fingerprint against independently observed evidence, refusing mismatch.
- Refuses to overwrite any existing differing dedicated pin. Planned target **on monitor only**: `/etc/homelab/router-metrics-ssh/known_hosts`, line `192.168.3.1 ssh-ed25519 <actual Pi public key>`. Root-owned directory `0755` and root-owned pin file `0644` allow future unprivileged SSH client to read the **public** key but not edit it. Does **not** modify `/home/james/.ssh/known_hosts`.
- In check mode predicts creation of the directory but does not try to copy into a nonexistent directory; the actual host-key verification is gated to normal mode. This means check mode **does not claim** to have established trust. On real execution `ssh-keygen -lf <dedicated known_hosts>` must exactly match the pinned SHA256.
- Does not generate any monitoring **private** key, create Pi user/authorized_keys, touch Pi sshd settings, launch SSH, open firewall ports, or change Prometheus/Docker. Stage C2a alone will **not** make remote login or metrics scraping work.

**No live or check-mode execution yet. First run only this source check and preview:**

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-ssh-host-pin.yml \
  --limit router-01,monitor-01 --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-ssh-host-pin.yml \
  --limit router-01,monitor-01 --ask-become-pass --check --diff \
  -e router_c2_host_pin_approved=true
```

If the preview passes without discrepancy, approve a **separate normal-mode** invocation to write *only the dedicated monitor host public-key pin*. Provisioning a dedicated limited-privilege SSH key pair and Pi account is **another distinct review/deploy gate**. No broad SSH daemon configuration change, no changes to existing `james` credentials and no ISP port exposure should occur.

### 28 October ~16:50 — Stage C2a host-key pin **check-mode PASS**; live write pending

User on `admin-01` fetched draft PR #210 branch to `f1c5bc88`, then ran `router-01-ssh-host-pin.yml` with both inventories, `--limit router-01,monitor-01`, syntax-check **PASS** and `--check --diff -e router_c2_host_pin_approved=true` **PASS**.

Actual recaps: **`router-01 ok=8 changed=0 unreachable=0 failed=0 skipped=0`; `monitor-01 ok=8 changed=1 (predicted) unreachable=0 failed=0 skipped=5`.** The Pi's onboard hardware MAC, ED25519 public-key format and its independently pinned fingerprint **`SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`** were all revalidated; both monitor name/address guards passed.

Only anticipated check-mode change is creating **`/etc/homelab/router-metrics-ssh/`** on `monitor-01`. Pre-existing dedicated trust file did **not** exist; so pre-existing-content checks skipped. Actual `known_hosts` copy and installed fingerprint checks were **intentionally skipped** in check mode because the predicted parent directory does not exist yet. **No real file was created**, no Pi/router operation changed and no SSH trust established during preview.

**Review status: safe to run the exact bounded C2a playbook in normal mode after explicit operator approval.** This writes only the root-owned directory and root-owned `0644` **public** Pi host key to `/etc/homelab/router-metrics-ssh/known_hosts` on `monitor-01`; the playbook verifies the SHA256 of that installed trust file after writing. It does not write to Pi, restart SSH, generate client key, start tunnel, open TCP9100 or change Docker/Prometheus.

From existing `~/projects/homelab-router-toolset-audit/IaC/ansible` worktree:

```bash
ansible-playbook \
  -i inventory/hosts.yml \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-ssh-host-pin.yml \
  --limit router-01,monitor-01 \
  --ask-become-pass \
  -e router_c2_host_pin_approved=true
```

**Do not mark C2a installed until a successful normal Ansible recap and installed fingerprint verification.** Even after trust is pinned, dedicated SSH client authentication and Prometheus Docker-aware tunnel design remain future, separately gated stages.

### 28 October ~16:59 — Stage C2a public SSH host-key pin LIVE SUCCESS

Operator executed `router-01-ssh-host-pin.yml` in **normal mode** (no `--check`), with exact two inventories, `--limit router-01,monitor-01` and explicit opt-in `router_c2_host_pin_approved=true`. **Actual recaps:** `router-01 ok=8 changed=0 unreachable=0 failed=0 skipped=0`; `monitor-01 ok=11 changed=2 unreachable=0 failed=0 skipped=2`. Only actual changes were creation of root-owned `/etc/homelab/router-metrics-ssh/` and `/etc/homelab/router-metrics-ssh/known_hosts` **on monitor-01**. The installed known_hosts public Pi SSH server key was independently verified **on monitor-01** after writing; the required SHA256 fingerprint matched **`SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`**. The real Pi remained read-only. No SSH client private keys or account, no tunnel, no SSH daemon/network/firewall/ASUS, and no Prometheus/Docker changes were made.

**Stage C2a is COMPLETE and the host public-key trust is deployed**, not just previewed. This purpose-built file is separate from `/home/james/.ssh/known_hosts` and would need an explicit `UserKnownHostsFile=/etc/homelab/router-metrics-ssh/known_hosts` in a later restricted SSH tunnel; current unrelated `james` SSH sessions are unchanged. Stage C1 local metrics and confirmed downstream internet browsing remain intact. **Stage C2 overall is NOT DONE: no authenticated monitoring principal or reachable remote scrape exists yet.**

### Stage C2b — new dedicated SSH tunnel identity, read-only preflight STAGED (NOT EXECUTED)

New IaC `IaC/ansible/playbooks/router-01-ssh-metrics-identity-readonly.yml` on draft PR #210 checks **without modifying** either target: exact `admin-01` controller and Pi/monitor inventory identities, router physical MAC, planned `router-metrics` Pi service account/group availability, real `sshd -t` validity and global effective SSH permissions, isolated `127.0.0.1:9100` metrics socket, default-deny firewall and all critical router services. On monitor-01, it confirms the newly installed dedicated `known_hosts` path remains a normal root-owned file with the precise verified ED25519 SHA256 fingerprint, checks proposed nonprivileged `router-metrics-tunnel` local identity and dedicated private key path for potential conflicts (does not read keys), port 19100 availability, Prometheus HTTP readiness, and route to Pi SSH. `getent passwd` command output and account attributes are suppressed to avoid unnecessary disclosure, and only boolean availability is reported. **The preflight source is not yet syntax-checked on admin-01 or run**.

From the existing isolated feature worktree, run only the syntax and **read-only check**:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/hosts.yml \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-ssh-metrics-identity-readonly.yml \
  --limit router-01,monitor-01 --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-ssh-metrics-identity-readonly.yml \
  --limit router-01,monitor-01 --ask-become-pass --check \
  -e router_c2_identity_audit_approved=true
```

Only after seeing account/service conflicts and reviewing transport policy should we author **separate** tightly gated and rollback-capable identity/key/account installation, SSH policy restrictions, and Docker-side Prometheus tunnel. **No auto-generated private keys should be committed to the repository or printed by Ansible.** Protect client host trust using the pinned dedicated file with StrictHostKeyChecking=yes. Keep Pi node exporter bound to localhost and leave existing firewall and PPPoE untouched. Do not blindly run generic monitoring stack playbook or restart Prometheus stack.

### 28 October ~17:03 — Stage C2b identity feasibility read-only PASS; local client key source staged

User fetched the isolated audit branch through `a851b964` and ran `router-01-ssh-metrics-identity-readonly.yml` **syntax-check PASS**, then `--check -e router_c2_identity_audit_approved=true` with both inventories. Real recap: **`router-01 ok=13 changed=0 unreachable=0 failed=0 skipped=0`**, **`monitor-01 ok=15 changed=0 unreachable=0 failed=0 skipped=0`**.

Observed on actual Pi: `router-metrics` **user absent**, group **absent**; existing `/usr/sbin/sshd -t` PASS; global sshd policy allows public-key authentication and TCP forwarding but has broad `allowtcpforwarding yes; permitopen any; permittty yes`. Pi **metrics remain localhost-only `127.0.0.1:9100`**, default deny input firewall active, and all `nftables`, `router-pppoe`, `dnsmasq`, `unbound` units active. On monitor-01: `router-metrics-tunnel` user **absent**, intended dedicated `/etc/homelab/router-metrics-ssh/id_ed25519` private key **absent**; dedicated pinned Pi SSH host-key file exists and matches independent fingerprint `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`. Host port **19100 unused**, route from monitor to Pi goes via ASUS `192.168.2.1`; Prometheus ready HTTP **200**. **Absolutely no modifications on either host from this diagnostic.**

**Stage C2b design is split into small change gates.** First, generate dedicated client identity/key on `monitor-01` only (no access granted on Pi), then separately review Pi-side authorization/permissions (and only later a Docker-aware SSH tunnel). No changes to the Pi or router during key generation.

Staged **SOURCE ONLY** `IaC/ansible/playbooks/monitor-01-router-metrics-key-provision.yml`, requiring `-e router_c2_key_provision_approved=true` and strict `admin-01`/monitor identity guard. The playbook re-verifies installed dedicated Pi fingerprint and Prometheus readiness, checks for account/key conflicts, and previews a new system group/user `router-metrics-tunnel` with `/usr/sbin/nologin`, dedicated home, password locked. In **normal mode only**, it generates a fresh ED25519 key **directly on monitor-01** at `/etc/homelab/router-metrics-ssh/id_ed25519`, applies `0600` and service-account ownership to the private key, root-owned `0644` public key, verifies ED25519 fingerprint, Prometheus readiness and no TCP19100 listener. **Private key content is never printed, slurped, copied to controller or committed to GitHub; it is deliberately unencrypted for future unattended SSH and must be restricted through key authorization/permissions.** It does **not** create Pi `router-metrics`, `authorized_keys`, SSH tunnel, Compose job, or any firewall change. In check mode it predicts creation of the system group only; service-user creation and all key operations are skipped, because the newly proposed group does not yet exist for a dependent user task. Its deployment/rollback process will be reviewed after syntax check and dry-run on admin-01; no runtime results exist yet.

Run **syntax and preview ONLY**:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-provision.yml \
  --limit monitor-01 --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-provision.yml \
  --limit monitor-01 --ask-become-pass --check --diff \
  -e router_c2_key_provision_approved=true
```

No live normal-mode action until reviewing syntax and proposed changes; no Pi account, tunnel or Prometheus scrape will be configured by this pilot.

### 28 October ~17:07 — C2b1 dedicated monitor-01 SSH identity preview PASS, live still pending

User on `admin-01` fast-forwarded isolated worktree to branch `60759298`, then ran `monitor-01-router-metrics-key-provision.yml --syntax-check` **PASS** followed by `--check --diff -e router_c2_key_provision_approved=true` **PASS** with `--limit monitor-01`: **`monitor-01 ok=24 changed=1 (predicted) unreachable=0 failed=0 skipped=7 rescued=0 ignored=0`**.

All controller/monitor identity, SSH host-key pin and safe parent directory checks passed; no pre-existing `router-metrics-tunnel` account/group or colliding private/public key was encountered, Prometheus remains HTTP 200 ready, filesystem space is sufficient, port 19100 unoccupied both before and after, and no router access/change occurred. The **only check-mode difference** was predicted creation of `router-metrics-tunnel` **system group**. Dependent user creation and `ssh-keygen`/key ownership/fingerprint checks skipped in check mode since the group is not actually present. **NO SSH user or key created in this preview.**

**C2b1 may advance to bounded operator-approved live execution, without `--check`, using the existing vetted `monitor-01`-only Ansible playbook**. This creates a locked-password unprivileged system user `router-metrics-tunnel` with `/usr/sbin/nologin`, and generates locally on monitor-01 only a new ED25519 keypair `/etc/homelab/router-metrics-ssh/id_ed25519[.pub]`; private file `0600` owned by that account and public file root-owned `0644`. Normal-mode postflight verifies generated public key ED25519, Prometheus ready 200, and still no TCP19100 forwarder. No Pi account/authorized_keys yet, no SSH connection/tunnel, no firewall, no Docker or Prometheus modifications. **Do not display/commit the private key.** The key is unencrypted to enable unattended future forwarding and must remain restricted to the local monitoring account.

Exact next invocation from existing `~/projects/homelab-router-toolset-audit/IaC/ansible`:

```bash
ansible-playbook \
  -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-provision.yml \
  --limit monitor-01 \
  --ask-become-pass \
  -e router_c2_key_provision_approved=true
```

**Do not claim C2b1 installed until normal-mode recap shows success and generated ED25519 public fingerprint passes.** If live mode fails after creating an account/group or key, pause to inspect the partial state rather than blindly rerunning with credentials changed. Then separately scope C2b2 Pi-side restricted authorized-key account, SSH host trust use, source restrictions and a Docker-aware tunnel.

### 28 October ~17:10 — C2b1 normal-mode Ansible returns OK with ZERO changes; reconcile existing identity

User executed the previously approved `monitor-01-router-metrics-key-provision.yml` **WITHOUT** `--check` on live `monitor-01` with explicit `router_c2_key_provision_approved=true`. Actual recap **`monitor-01 ok=31 changed=0 unreachable=0 failed=0 skipped=0`**. All group, account, ED25519 key generation, key mode/ownership, key public-key fingerprint, Pi pinned host-key trust, Prometheus HTTP200 and no TCP19100 listener tasks returned **OK**, none reported CHANGED. Debug claimed `LIVE: isolated local SSH client identity and key provisioned`, but critically **zero CHANGED means this particular invocation did not actually create or modify the group/user/key files**. The earlier dry-run `--check --diff` predicted a missing group and skipped all account and key creation. Therefore the identity/key state must have appeared between executions, or changed in a separate unreported invocation. Do **not** infer who/what created the credentials, or assume that the private/public files pair and account locking have been independently verified merely from their existence and the key-type fingerprint check. Do not alter Pi SSH trust or authorised keys until reconciling this state.

**C2b1 runtime state is present and original playbook completed successfully; credential *provenance is unknown***. Subsequent source-only `IaC/ansible/playbooks/monitor-01-router-metrics-key-postflight-readonly.yml` now staged on draft PR #210. It **does not mutate any host**. It guards exact controller and monitoring identity, verifies dedicated system user/group, locked password, nologin shell, user home, root-owned trust directory and pinned Pi ED25519 fingerprint, private mode `0600` owned by service identity, public mode `0644`, validates the *actual private key is readable by the service identity* using `runuser -u router-metrics-tunnel -- ssh-keygen -y -f ...`, compares its derived public key against the stored `.pub` without printing key material, and reads file modification timestamps to help determine when those key files appeared. It also rechecks Prometheus readiness and no TCP19100 listener. Only the public-key SHA256 fingerprint and redacted status are emitted; no private-key material goes into GitHub, Ansible output or the controller.

**Next command, read-only syntax and --check ONLY:**

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-postflight-readonly.yml \
  --limit monitor-01 --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-postflight-readonly.yml \
  --limit monitor-01 --ask-become-pass --check \
  -e router_c2_key_postflight_approved=true
```

This **only audits monitor-01**, not Pi; no trust, key, account or tunnel changes. If passes, treat account/key as existing and secure and proceed to **separately reviewed C2b2 Pi service account and restricted key authorisation**. No remote metrics scrape has yet been configured; Pi exporter still localhost-only. Do not print the actual private SSH key.

### 28 October ~17:15 — C2b1 private-key postflight FAILED read-only; investigate without key disclosure

The operator ran `monitor-01-router-metrics-key-postflight-readonly.yml`, syntax-check PASS, then gated read-only `--check`. **Actual recap `monitor-01 ok=17 changed=0 unreachable=0 failed=1 skipped=0`**. The task `Derive public key from PRIVATE key as the nonprivileged service user` failed with nonzero return code. That task deliberately uses `no_log: true`; the raw error is concealed and **the cause has NOT been diagnosed**. Earlier checked facts before failure: dedicated `router-metrics-tunnel` user and group present with home `/var/lib/router-metrics-tunnel`, nologin shell and locked password; key path exists as regular nonsymlink file owned by identity, mode `0600`; root-owned `/etc/homelab/router-metrics-ssh` mode 0755 and public key root-owned mode0644; known_hosts pinned trust file and metadata appropriate. **The check did not complete private/public key equivalence, SSH login eligibility, Prometheus postflight or the no-tunnel assertion.** Do not mark credential as functional or deploy Pi `authorized_keys`.

Very plausible but **unverified** reason: an ancestor of the key path (`/etc/homelab`) might be inaccessible to non-root even though the final trust directory is mode0755 and private key belongs to service user. Other possible causes are key format, passphrase, or runuser execution. Do **not** broadly change `/etc/homelab` permissions or weaken protection, regenerate key, run `StrictHostKeyChecking=no`, or print private bytes until evidence identifies the fault.

**Source-only** `IaC/ansible/playbooks/monitor-01-router-metrics-key-access-readonly.yml` added to draft PR #210 for targeted diagnosis. It runs only on `monitor-01`, requires exact `admin-01` controller and `router_c2_key_access_audit_approved=true`. It checks modes and ownership of every path segment (/etc, /etc/homelab, dedicated dir, private/public files); probes service-user runuser identity, `test -f` and `test -r` as service user; derives public key separately as root and as service user with `ssh-keygen -y -P "" -f`, all raw key outputs fully redacted with `no_log: true`, then reports only pass/fail booleans, matching against the stored public key, and coarse error category. **No keys, user accounts, directory modes, sshd, network or monitoring are modified.** The `ssh-keygen -y` outputs are public material but not printed to avoid leaking details into logs.

**Next operator task is only to fetch latest branch, syntax-check, and execute this source as a read-only check**:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-access-readonly.yml \
  --limit monitor-01 --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-access-readonly.yml \
  --limit monitor-01 --ask-become-pass --check \
  -e router_c2_key_access_audit_approved=true
```

Inspect output flags and path metadata. If service-user read fails but root parse succeeds, next reviewed IaC fix should arrange a safe private-key path that the service can traverse, without altering shared parent directory permissions. If root parse also fails, inspect format/passphrase without copying secret into console. No change/deploy authorised in this diagnostic stage.

### 28 October ~17:20 — root cause identified for C2b1 service-key failure; safe remediation staged SOURCE ONLY

Operator ran `monitor-01-router-metrics-key-access-readonly.yml` from `admin-01`, syntax-check **PASS**, `--check` **`monitor-01 ok=14 changed=0 failed=0 skipped=0`**. It isolated an **access-control, not a key-corruption, problem**:

- `/etc`: **`0755 root`**; `/etc/homelab`: **`0750 root`**; `/etc/homelab/router-metrics-ssh`: **`0755 root`**; `id_ed25519` **`0600 router-metrics-tunnel`**.
- `runuser` for `router-metrics-tunnel` **works**, but the service user **cannot see or read the private-key pathname** and the SSH key derivation failed with **permission-denied**.
- Root **can parse the private ED25519 key**, and root's derived public key **MATCHES** the stored `id_ed25519.pub`. Thus the original keypair is valid, and filesystem traversal through the shared `/etc/homelab` directory is blocked as designed.
- **No files, users, SSH services, Pi router, monitoring services or network were changed by this diagnostic.**

**Security decision:** Do **NOT** `chmod 755 /etc/homelab` or weaken the shared root-only configuration directory; do not grant blanket directory access. Avoid storing private client SSH credentials beneath this protected shared parent for an unprivileged tunnel process.

Staged IaC candidate **`IaC/ansible/playbooks/monitor-01-router-metrics-key-relocate.yml`** in draft PR #210, **not syntax-checked or executed on admin-01**. Design: exact `admin-01`->`monitor-01` and opt-in `router_c2_key_relocate_approved=true`; require existing locked/nonlogin `router-metrics-tunnel` account and verified source keypair + independently pinned Pi ED25519 host SHA256; refuse existing conflicting target files and symlinks. In real mode only, create **`/var/lib/router-metrics-tunnel/.ssh` owned by that user, mode `0700`**, then securely copy the *existing validated private key* to `/var/lib/router-metrics-tunnel/.ssh/id_ed25519` as service-user `0600`, copy matching public key and pinned `known_hosts` into that private directory; copies are **remote-to-remote on monitor-01**, with private-key task `no_log: true` and no secret to admin-01 or GitHub. Check actual usability with `runuser -u router-metrics-tunnel -- ssh-keygen -y -P '' -f /var/lib/router-metrics-tunnel/.ssh/id_ed25519` (no_log, match against source public), verify copied host trust SHA256 as the service user, then Prometheus HTTP200 and TCP19100 still unused. The original valid keypair and original root-owned host pin at `/etc/homelab/router-metrics-ssh` are **retained** pending a distinct, approved cleanup after a secure tunnel is working. Shared `/etc/homelab` mode0750 is untouched; no key is regenerated, no Pi modifications, no SSH tunnel, no Docker/Prometheus changes. Future tunnel SSH client must use **new canonical key and known_hosts paths** in `/var/lib/router-metrics-tunnel/.ssh` rather than old inaccessible paths.

**Next gate: syntax check and dry run ONLY** (the preview predicts just creation of the private `.ssh` directory, dependent credential copies/postflight intentionally skipped):

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-relocate.yml \
  --limit monitor-01 --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-relocate.yml \
  --limit monitor-01 --ask-become-pass --check --diff \
  -e router_c2_key_relocate_approved=true
```

**Do not run without `--check` until the full preview has been reviewed.** No further Pi-side `router-metrics` account or `authorized_keys` installation is authorised until the service can actually derive its own public key from its own safe private-key path. This fix is more secure than modifying the shared config directory and keeps the original key available for rollback.

### 28 October ~18:02 — SSH key relocation dry-run caught missing-stat-field bug; source corrected, NOT deployed

Operator on `admin-01` fetched isolated branch through `79f09778`, syntax-checked `monitor-01-router-metrics-key-relocate.yml` **PASS**, then tried `--check --diff -e router_c2_key_relocate_approved=true` against `monitor-01`. Actual recap **`monitor-01 ok=18 changed=0 unreachable=0 failed=1 skipped=0`**. The root/home/actual monitor identity checks, source keypair private-derived/public equivalence and independently pinned Pi host ED25519 fingerprint all passed again. Failure was at **`Refuse existing nonregular, linked or wrong-owner destinations`** *before any copy or directory creation*:
```text
Error while evaluating conditional: object of type 'dict' has no attribute 'islnk'
```
**Root cause is the Ansible playbook's filtering logic**, not a bad SSH key: `ansible.builtin.stat` does not necessarily return `islnk`, `isreg`, ownership or mode for nonexistent destination files. The previous `selectattr('stat.islnk', 'equalto', true)` failed to handle missing attributes. The live router, SSH, shared `/etc/homelab`, Prometheus and Docker remain unchanged. No private keys copied and no credential staging done.

**GitHub IaC patch** to `IaC/ansible/playbooks/monitor-01-router-metrics-key-relocate.yml` replaces those `selectattr`/`rejectattr` filters with **one assertion per destination file**, looped over the existing `stat` results, applying `default(false)` to absent `exists/islnk/isreg`, `default('')` to absent `pw_name/mode`. A missing destination now passes the existence gate without relaxing anything: for *any existing file*, it still rejects symlinks, nonregular files, wrong owner and wrong mode (private 0600, public/known_hosts 0644) before copy. This source is now staged but **has not been re-syntax-checked or re-executed on admin-01**. Protected parent `/etc/homelab=0750` will not change.

**Retry syntax and dry run ONLY** from the existing isolated worktree:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-relocate.yml \
  --limit monitor-01 --syntax-check && \
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-relocate.yml \
  --limit monitor-01 --ask-become-pass --check --diff \
  -e router_c2_key_relocate_approved=true
```

Expected dry-run if destinations are still absent: identity/source/host-key assertions PASS, three absent destination file assertions PASS, and **only a predicted** `/var/lib/router-metrics-tunnel/.ssh` creation (mode0700). Actual private/public/known_hosts copies and service-account key usability verification intentionally skip during --check. **No live run until operator supplies and we review the full corrected dry-run output.** No Pi C2b2 authorized_keys until C2b1 fully proven functional.

### 28 October ~18:05 — C2b1 corrected SSH key relocation CHECK MODE PASS, live still pending

The operator reran the corrected `monitor-01-router-metrics-key-relocate.yml` dry-run on `monitor-01` with `--check --diff -e router_c2_key_relocate_approved=true`. Full tail and recap provided: **`monitor-01 ok=25 changed=1 (PREDICTED) unreachable=0 failed=0 skipped=13 rescued=0 ignored=0`**.

Critical newly fixed guard `Refuse unexpected existing destination files without assuming absent stat fields` ran successfully for all three intended destinations; actual `ansible.builtin.stat` showed **`exists: false`** for each:
- `/var/lib/router-metrics-tunnel/.ssh/id_ed25519`
- `/var/lib/router-metrics-tunnel/.ssh/id_ed25519.pub`
- `/var/lib/router-metrics-tunnel/.ssh/known_hosts`

The preflight private/public source keypair equivalence and Pi independently pinned ED25519 host-key fingerprint checks returned OK. The preview predicted **only directory creation** `/var/lib/router-metrics-tunnel/.ssh`; actual private/public/host pin copies, service-user derivation and fingerprint postflight deliberately skipped in check mode. Prometheus readiness and absent TCP19100 listener postflight passed. **No credentials copied, no directory created, no Pi SSH account, no tunnel, no Docker/Prometheus or router changes**.

**Next accepted narrowly bounded normal-mode step** (operator approval required by playbook): from the existing `~/projects/homelab-router-toolset-audit/IaC/ansible` directory run the exact `monitor-01` scoped IaC playbook without `--check`:

```bash
ansible-playbook \
  -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-key-relocate.yml \
  --limit monitor-01 \
  --ask-become-pass \
  -e router_c2_key_relocate_approved=true
```

In normal mode, the playbook will create a `0700` service-owned directory, copy the existing validated ED25519 private key to the service home as `0600`, copy the matching public key and verified Pi public host-key pin, then **test key derivation as `router-metrics-tunnel`** and verify the copied pin SHA256. Copy is remote source to remote destination **on monitor-01 only**, no private key material to controller or GitHub and sensitive task `no_log`. Existing protected `/etc/homelab` remains `0750 root` and original keypair/public host pin **remain untouched for rollback**. The playbook does not create Pi users or router authorized_keys, open ports, start a tunnel, change Docker or alter Prometheus. Do **not** mark relocation done until after receiving a normal-mode success recap with service-key equality and Pi SHA256 postflight. If the live play fails partway through, inspect the partial state instead of applying manual permission changes or blindly rerunning.

### 28 October ~18:10 — Stage C2b1 SSH credential relocation LIVE SUCCESS; restricted Pi SSH authorization is next

Operator ran `monitor-01-router-metrics-key-relocate.yml` **normal mode** with `--limit monitor-01 -e router_c2_key_relocate_approved=true`. Actual recap **`monitor-01 ok=33 changed=4 unreachable=0 failed=0 skipped=5`**. All preflight identity, source ED25519 keypair equivalence and genuine Pi server host-key fingerprint assertions passed.

The four changes **only on monitor-01**:
1. Created `/var/lib/router-metrics-tunnel/.ssh/` owned by dedicated locked/non-login service identity, mode0700.
2. Securely copied valid private ED25519 key to `/var/lib/router-metrics-tunnel/.ssh/id_ed25519` with service ownership and mode0600 (no_log, remote-local copy; never exposed private bytes or sent them to admin-01).
3. Copied matching client **public** key to `/var/lib/router-metrics-tunnel/.ssh/id_ed25519.pub`.
4. Copied independently pinned Pi SSH **server public** host key to `/var/lib/router-metrics-tunnel/.ssh/known_hosts`.

**Critical LIVE verification PASSED:** `runuser -u router-metrics-tunnel -- ssh-keygen -y -P '' -f /var/lib/router-metrics-tunnel/.ssh/id_ed25519` returned successfully and produced a public key **matching the original**, confirming actual service-user key readability and cryptographic validity. `router-metrics-tunnel` could read its new known_hosts and obtain exact Pi ED25519 server host fingerprint **`SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`**. Prometheus readiness postflight passed, host TCP19100 remains unbound. No SSH tunnel, no router/ASUS/firewall/PPPoE or sshd changes, no Docker/Prometheus modification. **Stage C2b1 now COMPLETE**. Original credentials **RETAINED** under root-protected `/etc/homelab/router-metrics-ssh`; shared `/etc/homelab` remains 0750. A separate reviewed cleanup may remove duplicated old credentials only after successful full rollout; do not blindly delete them.

Next Stage C2b2 is a *distinct security gate*: decide how to authorize **only this dedicated monitor public key** to Pi `router-metrics` service account, with **local TCP forwarding limited to `127.0.0.1:9100`**, no password/session/PTY/agent/X11/remote forwarding, and no global SSH relaxation. This likely needs both `authorized_keys` key-level restrictions and a **user-specific sshd Match policy**. On Pi, current general `sshd -T` permits `allowtcpforwarding yes`, `permitopen any`, `passwordauthentication yes`, `permittty yes`, so **do not rely on the global policy as sufficient**. Before deploying any change, inspect actual sshd config structure, Include/Match ordering, effective policies and account homes to establish a safe gated `sshd -t` validation and reload/rollback plan; source tunnel key must come ONLY from the verified public key on monitor. **SSH client must use `IdentityFile=/var/lib/router-metrics-tunnel/.ssh/id_ed25519`, `UserKnownHostsFile=/var/lib/router-metrics-tunnel/.ssh/known_hosts`, `StrictHostKeyChecking=yes`** when eventually tested. Do not open Pi TCP9100 on LAN, do not edit PPPoE/NAT/nftables, do not launch a tunnel until a distinct transport and Docker Compose network namespace review. Containerized Prometheus still cannot access host-loopback local forward directly.

### 28 October ~18:10+ — Stage C2b2 SSH-only Pi policy preflight STAGED (source only, NOT RUN)

Having validated the dedicated monitoring private key works from its safe new home path, next inspect **the Pi's own SSH daemon policy and configuration ordering** before authorizing that key. New source-only, gated Ansible `IaC/ansible/playbooks/router-01-metrics-ssh-authorization-readonly.yml` in draft PR #210 checks original `admin-01` controller, `router-01=192.168.3.1` inventory, exact verified Pi onboard Ethernet MAC, whether proposed Pi `router-metrics` account already exists, `sshd -t` config syntax, general effective forwarding/password/public-key settings, main `sshd_config` Include/Match directive ordering, included fragment filenames, and still loopback-only `127.0.0.1:9100` export. Every probe is read-only, and there is **no account creation, no authorised key, no SSH daemon reload/restart, no firewall, no tunnel or Prometheus change**. This source has **not yet been syntax-checked or executed on `admin-01`**.

Run from the isolated worktree after fetching the current draft branch:
```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-ssh-authorization-readonly.yml \
  --limit router-01 --syntax-check && \
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-ssh-authorization-readonly.yml \
  --limit router-01 --ask-become-pass --check \
  -e router_c2_auth_audit_approved=true
```

Review actual include/match ordering BEFORE proposing a restrictive, user-specific sshd configuration. Future Pi-side `router-metrics` user must be locked-password/noninteractive, with exact public client key from `monitor-01:/var/lib/router-metrics-tunnel/.ssh/id_ed25519.pub`, an authorized_keys rule granting **only local TCP port-forwarding to `127.0.0.1:9100`**, and deny PTY/X11/agent/session/remote forwards where supported. An authorized-key `restrict,port-forwarding,permitopen=...` alone **is not sufficient to ensure no remote -R forwards**; use user-specific `AllowTcpForwarding local` and `PermitOpen 127.0.0.1:9100` enforced by sshd after understanding Include/Match behavior. Avoid a global SSH relaxation and any change to WAN/PPPoE/nftables/Node Exporter listener. Plan `sshd -t`, effective account-specific `sshd -T -C ...` verification and safe rollback before any daemon reload; don't deploy Pi auth during this preflight.

### 28 October ~18:15 — Pi Stage C2b2 SSH policy audit LIVE PASS; SSH Match ordering review STAGED only

Operator on `admin-01` fast-forwarded isolated feature branch through `3fe2bffe` and ran `router-01-metrics-ssh-authorization-readonly.yml` syntax-check PASS and `--check -e router_c2_auth_audit_approved=true` PASS. **Actual `router-01 ok=12 changed=0 unreachable=0 failed=0 skipped=0`**. Pi MAC matched, existing `sshd -t` passed, the proposed `router-metrics` service user is **absent**, and Node Exporter still binds exclusively to `127.0.0.1:9100`. No router or SSH files changed.

Actual globally effective Pi `sshd` includes: `pubkeyauthentication yes`, `passwordauthentication yes`, `kbdinteractiveauthentication no`, `x11forwarding yes`, `permittty yes`, `allowtcpforwarding yes`, `allowagentforwarding yes`, `disableforwarding no`, `authorizedkeysfile .ssh/authorized_keys .ssh/authorized_keys2`, `authenticationmethods any`, `permitopen any`, `permitlisten any`. Main `/etc/ssh/sshd_config` has **`Include /etc/ssh/sshd_config.d/*.conf` at LINE 12**, with **zero matching installed fragments**, and no existing main-file `Match` directive. Treat unrestricted settings as baseline only; do not alter those settings for existing admin users. No authenticated monitoring principal or tunnel is working on the Pi.

**New specific safeguard before writing any `Match User router-metrics` fragment:** the SSH Include is EARLY in the main sshd config. A `Match` block's scope, directive precedence and included-file ordering could affect the remainder of main config or invalid directives, potentially breaking existing SSH access. Authoring a Match fragment without inspecting the active main config lines **AFTER line 12** is not acceptable on this live PPPoE gateway. The restriction must be proven both for `router-metrics` and ordinary `james` via `sshd -t` and `sshd -T -C user=...,addr=...,host=...` before any daemon reload. Official Debian OpenSSH man page: https://manpages.debian.org/trixie/openssh-server/sshd_config.5.en.html (Match allows only a subset of directives; `AllowTcpForwarding local` and `PermitOpen 127.0.0.1:9100` are supported). Any future config must deny remote -R forwarding and agent/X11/pty/session use, without disabling intended local forwarding or weakening global policy.

Source-only **`IaC/ansible/playbooks/router-01-sshd-layout-readonly.yml`** added to draft PR #210. It requires exact `admin-01`, `router-01=192.168.3.1`, confirmed onboard MAC and `-e router_c2_sshd_layout_audit_approved=true`. It reads **only directive names with source line numbers**, tagged BEFORE versus AT_OR_AFTER line12 Include (does not disclose sshd config line values or private SSH keys); `sshd -t`, effective policy for globally and individually for existing `james` and proposed `router-metrics` (using current likely ASUS source address `192.168.2.1`), fragment filenames, proposed account/group name conflicts, localhost exporter and essential gateway service health. Nothing is written, reloaded or restarted. Staged source **NOT YET syntax-checked or run on admin-01**.

Next exact user commands — **syntax and read-only --check ONLY**:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-sshd-layout-readonly.yml \
  --limit router-01 --syntax-check && \
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-sshd-layout-readonly.yml \
  --limit router-01 --ask-become-pass --check \
  -e router_c2_sshd_layout_audit_approved=true
```

Do not create Pi service user, authorized_keys or sshd Match fragment, and do not touch Pi SSH services/nftables or Prometheus yet. Review ordering and compare ordinary user vs dedicated user effective policies before authoring a separate, rollback-safe, least-privilege Pi authorization deployment. The verified public monitor client key is at `monitor-01:/var/lib/router-metrics-tunnel/.ssh/id_ed25519.pub`, with its protected matching private key local to monitor, but **NO Pi-side grant** yet. Don't copy private key to GitHub/admin-01 or relax host-key checking.

### 28 October ~18:20 — Pi sshd layout read-only PASS; C2b2-a dormant Pi service identity SOURCE ONLY

Operator on `admin-01` fast-forwarded the isolated feature branch through `aa90930e`, ran `router-01-sshd-layout-readonly.yml --syntax-check` PASS and `--check -e router_c2_sshd_layout_audit_approved=true` PASS: **`router-01 ok=16 changed=0 unreachable=0 failed=0 skipped=0`**. All real physical Pi MAC and controller guards passed, `sshd -t` passed, and `router-metrics` proposed user and group both **ABSENT**. Essential `nftables`, `router-pppoe`, `dnsmasq`, `unbound` active, and exporter remains local `127.0.0.1:9100`; nothing changed.

The main `/etc/ssh/sshd_config` has `Include /etc/ssh/sshd_config.d/*.conf` **at line 12**, followed by active **`KbdInteractiveAuthentication` line64**, **`UsePAM` line87**, **`X11Forwarding` line92**, **`PrintMotd` line96**, **`AcceptEnv` line114**, **`Subsystem` line117**. No installed include fragments, no Match in main config. `sshd -T -C` evaluated for existing `james` and proposed `router-metrics` currently yields the SAME broad general forwarding/password/PTY policy (`passwordauthentication yes`, `allowtcpforwarding yes`, `permitopen any`, `permitlisten any`, `permittty yes`, `forcecommand none`). No current selective restriction exists.

**Decision for later SSH policy design (NOT DEPLOYED):** Do NOT write a `Match User router-metrics` stanza in an early `sshd_config.d/*.conf`, where it can affect later non-Match-capable `UsePAM`/`Subsystem` directives in the main config or fail `sshd -t`. Append a tightly controlled `Match User router-metrics` block at the END of main config only after fully testing a candidate with `sshd -t`, account-context `sshd -T -C` for `james` and `router-metrics`, backup and immediate rollback plan; no Pi sshd reload until independently approved. Candidate constraints: `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `AuthenticationMethods publickey`, `AllowTcpForwarding local`, `PermitOpen 127.0.0.1:9100`, `PermitTTY no`, `X11Forwarding no`, `AllowAgentForwarding no`, `AllowStreamLocalForwarding no`, `MaxSessions 0`, possibly `PermitUserRC no`. Authorized_keys should also restrict specific public monitor key and permit only local forwarding. `MaxSessions 0` explicitly prevents shell/login/subsystem sessions while allowing forwarding, per OpenSSH manual `https://man.openbsd.org/sshd_config`. Avoid setting `DisableForwarding yes` (would break required local forwarding). SSH known_hosts and client ED25519 keys remain securely resident on monitor-01 only.

**Next small, independent Pi-side step** is to create only an as-yet-UNAUTHORIZED service account, not install the key or change sshd. New **SOURCE-ONLY** gated IaC `IaC/ansible/playbooks/router-01-metrics-service-account.yml` in draft PR #210. It checks exact controller/admin Pi inventory and physical MAC, `sshd -t`, absent/no-collision proposed `router-metrics` user/group and home `/var/lib/router-metrics`, local exporter isolation, and essential router services. The only possible changes in **normal mode** are a dedicated system group and a new locked-password, `/usr/sbin/nologin` system user with a separate home; **no SSH keys, no `authorized_keys`, no SSH configuration/reload, no PPPoE/nftables, no tunnel or Prometheus modifications**. In `--check`, predict group creation only and skip dependent account creation, since the system group won't exist until normal mode. **This new source is not yet operator syntax-checked, previewed or deployed.**

Run **syntax and dry-run only** with the isolated Pi inventory from admin-01:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-service-account.yml \
  --limit router-01 --syntax-check && \
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-service-account.yml \
  --limit router-01 --ask-become-pass --check --diff \
  -e router_c2_pi_account_approved=true
```

Review actual check-mode recap before any normal-mode creation on the live Pi. Establish restricted sshd Match only via separate validated, rollback-capable change after the account is present, and **withhold authorized_keys installation until the restrictive sshd policy is independently verified**.

### 28 October ~18:25 — C2b2-a dormant Pi system-account PREVIEW PASS, not deployed

User fetched feature branch through `1ae298ba` into isolated `~/projects/homelab-router-toolset-audit`, executed `router-01-metrics-service-account.yml` **syntax-check PASS**, then `--check --diff -e router_c2_pi_account_approved=true --limit router-01` with the isolated router inventory. Actual recap: **`router-01 ok=18 changed=1 (PREDICTED) unreachable=0 failed=0 skipped=2 rescued=0 ignored=0`**. All Pi physical identity/MAC, valid `sshd -t`, proposed user/group collision, `/var/lib/router-metrics` home, Node Exporter bound to `127.0.0.1:9100` only, and gateway units (`nftables`, `router-pppoe`, `dnsmasq`, `unbound`) pre/postflight PASS. **Only predicted new system group `router-metrics`**; dependent user task deliberately skipped as new group does not exist during check mode. No physical Pi mutation, no user, no SSH authorized_keys, no SSH policy/reload, no tunnel or monitoring alteration.

**Next separately gated normal-mode step approved by passed preview** is only to create dormant local Pi system user/group with a password lock and `/usr/sbin/nologin`, home `/var/lib/router-metrics`. Account will have no authorized keys and no changes to existing SSH daemon; no network/PPPoE/nftables/Prometheus changes.

```bash
# From admin-01 ~/projects/homelab-router-toolset-audit/IaC/ansible
ansible-playbook \
  -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-service-account.yml \
  --limit router-01 \
  --ask-become-pass \
  -e router_c2_pi_account_approved=true
```

**Do not mark C2b2-a live complete until the normal-mode recap and postflight succeed.** Before allowing remote authentication, separately test a candidate end-of-main `Match User router-metrics` with `sshd -t` and effective `sshd -T -C` for `james` and `router-metrics`, explicit rollback and operator approval; only then consider authorized_keys of the verified monitor public key. Keep SSH key private only on monitor-01, Node Exporter localhost-only, and no tunnel started.

### 28 October ~18:30 — C2b2-a dormant Pi monitoring user LIVE PASS; check-only SSH policy preview staged

Operator ran `router-01-metrics-service-account.yml` in **normal mode** with `--limit router-01 -e router_c2_pi_account_approved=true`; final debug `LIVE: dormant local service identity and group present`. Actual recap **`router-01 ok=19 changed=2 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0`**. Two live changes are the new `router-metrics` system GROUP and new non-interactive `router-metrics` system USER, password locked, `/usr/sbin/nologin`, home `/var/lib/router-metrics`. Pi sshd config still valid; existing authenticated `james` login untouched; **no SSH public key installed, no `authorized_keys`, no sshd Match policy or reload, no new network listener/tunnel, no PPPoE/nftables/routing/Docker/Prometheus modifications**. Existing Node Exporter remains localhost-only. **Stage C2b2-a complete**.

Next **C2b2-b** is the **SYNTACTIC PREVIEW**, not the installation, of a monitoring-user-only SSH restriction. OpenSSH official documentation permits in `Match User`: `AuthenticationMethods publickey`, `PasswordAuthentication no`, `AllowTcpForwarding local`, `PermitOpen 127.0.0.1:9100`, `PermitListen none`, `PermitTTY no`, `MaxSessions 0` (disables shell, login and subsystem sessions while retaining forwarding), X11/agent/streamlocal disables. Reference: https://man.openbsd.org/sshd_config . Because `sshd_config` has Include at LINE12 and later `UsePAM`/`Subsystem` global directives, insert Match **only at EOF of main config**, never inside early included fragments.

Staged new **SOURCE-ONLY, CHECK-MODE-ENFORCED** Ansible `IaC/ansible/playbooks/router-01-metrics-sshd-match-preview.yml` in draft PR #210. It explicitly **fails if not running with `--check`**, checks exact controller/admin-01, router inventory/IP, physical Pi MAC, valid original `sshd -t`, the **actually existing** locked `router-metrics` user/group/nologin shell, no preexisting `authorized_keys`, safe root-owned main sshd config, exact main-file Include-only directive at line12 and zero installed sshd_config.d snippets, plus four gateway services and still isolated exporter. It invokes `ansible.builtin.blockinfile` **only to compute the `--check --diff` EOF insertion**, with `validate: /usr/sbin/sshd -t -f %s`, **never writes the real sshd_config** and never reloads SSH. The proposed block includes `Match User router-metrics`, `PubkeyAuthentication yes`, `AuthenticationMethods publickey`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitTTY no`, `X11Forwarding no`, `AllowAgentForwarding no`, `AllowStreamLocalForwarding no`, `AllowTcpForwarding local`, `PermitOpen 127.0.0.1:9100`, `PermitListen none`, `GatewayPorts no`, `PermitTunnel no`, `PermitUserRC no` and `MaxSessions 0`. This only proposes a diff; no `authorized_keys` at this stage. **The playbook has not been syntax-checked or executed by the operator yet.**

IMPORTANT: A clean `--check` and `sshd -t` preview does NOT alone prove effective `sshd -T -C` policy of an *installed* candidate. Before any actual sshd config edit or reload, separately plan/verify `sshd -T -C user=router-metrics,addr=<observed ASUS source>,host=monitor-01` against a candidate config and compare existing `james` effective policy. Protect existing SSH admin access, keep a tested rollback, and require independent operator approval before live deployment and subsequent public-key authorisation. **Never use `ForceCommand /usr/sbin/nologin` or `DisableForwarding yes` for this forwarding-only service account.**

Next operator commands (CHECK MODE ONLY):

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-sshd-match-preview.yml \
  --limit router-01 --syntax-check && \
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-sshd-match-preview.yml \
  --limit router-01 --ask-become-pass --check --diff \
  -e router_c2_sshd_preview_approved=true
```

Review exact proposed diff and recap. **Do not install Match, reload SSH, grant `authorized_keys`, start a forward or change Prometheus until a later separate approved gate.**

### 28 October ~18:33 — C2b2-b monitoring-user sshd EOF Match PREVIEW PASS; offline effective-policy candidate source STAGED (not run)

User fetched draft branch through `4144b36f` and ran `router-01-metrics-sshd-match-preview.yml --syntax-check` **PASS**, then gated `--check --diff -e router_c2_sshd_preview_approved=true` on `router-01` **PASS**. Actual recap **`router-01 ok=27 changed=1 (PREDICTED) unreachable=0 failed=0 skipped=0`**. Exact Pi controller/MAC, new user/group/home/locked password/nologin, no pre-existing `authorized_keys`, safe main sshd_config root-owner, Include at line12 only and empty snippets, `sshd -t` existing config, loopback Node Exporter and all gateway services passed. **Nothing written or reloaded.**

The proposed diff **appends at very end of main `/etc/ssh/sshd_config`**, after all global-only directives, exactly:

```text
# BEGIN ANSIBLE MANAGED: router-metrics forwarding-only (C2b2)
Match User router-metrics
    PubkeyAuthentication yes
    AuthenticationMethods publickey
    PasswordAuthentication no
    KbdInteractiveAuthentication no
    PermitTTY no
    X11Forwarding no
    AllowAgentForwarding no
    AllowStreamLocalForwarding no
    AllowTcpForwarding local
    PermitOpen 127.0.0.1:9100
    PermitListen none
    GatewayPorts no
    PermitTunnel no
    PermitUserRC no
    MaxSessions 0
# END ANSIBLE MANAGED: router-metrics forwarding-only (C2b2)
```

The only predicted change was this block; **NO installed SSH policy**, no sshd reload, no Pi key grant, no SSH tunnel. It is important that `--check --diff` does **not itself prove the staged candidate's actual `sshd -t -f` or effective `sshd -T -f -C` settings**; the postflight rechecked the still-installed original config, not the candidate. Per OpenSSH manual `MaxSessions 0` disallows shell/subsystem sessions while allowing forwarding; `AllowTcpForwarding local` + `PermitOpen 127.0.0.1:9100` limits forwarding. References: https://manpages.debian.org/trixie/openssh-server/sshd_config.5.en.html and https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html .

**New source-only staged offline tester**:
- `IaC/ansible/scripts/router-01-sshd-candidate-validate.py` reconstructs the exact candidate block above from the live read-only sshd_config, verifies no Include or Match drift, runs `/usr/sbin/sshd -t -f <candidate>` and `/usr/sbin/sshd -T -f <candidate> -C user=...,host=...,addr=...` for existing `james` and proposed `router-metrics` (both direct admin/monitor and ASUS-source address contexts). Checks complete global and admin effective policies are **unchanged** compared with the actual on-disk config, and that the monitoring account gets every stated forwarding/password/PTY/session/agent/X11 restriction exactly. Fails closed on mismatch.
- `IaC/ansible/playbooks/router-01-metrics-sshd-candidate-effective-readonly.yml` gates `--check` only, `admin-01` controller, exact `router-01=192.168.3.1` inventory and physical MAC, absent `authorized_keys`, original `sshd -t`, core service health and still loopback exporter. Invokes the script on Pi via Ansible `python3 -` stdin from Git-managed source, no deployed script file.

**File-system detail**: to test a real candidate, the validator creates a **temporary mode0600 sshd config file in a mode0700 temporary directory under `/run` on the Pi**, runs the installed sshd binary against it, and **deletes the temporary directory/file immediately, even if validation raises an exception**. This is an ephemeral local test-file write, but **NO mutation of `/etc/ssh/sshd_config`, no SSH daemon reload/restart, no account/authorized_keys changes, no network/PPPoE/firewall/Node Exporter/Prometheus configuration changes**. Both sources are currently **only committed**, not yet syntax-checked or run by the operator. This is a diagnostic staging step, **NOT** authorization to deploy a live SSH restriction.

**Next operator command from `admin-01` to test candidate offline**:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-sshd-candidate-effective-readonly.yml \
  --limit router-01 --syntax-check && \
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-sshd-candidate-effective-readonly.yml \
  --limit router-01 --ask-become-pass --check \
  -e router_c2_sshd_candidate_audit_approved=true
```

**No normal-mode execution allowed by this playbook.** Review candidate `sshd -t` and `-T -C` effective results and unchanged admin/global settings before authoring the separately gated, backup-and-rollback SSH configuration deployment. Do not install any monitoring public key or initiate tunnel yet. Existing household browsing and Pi gateway services remain unchanged.

### 28 October ~18:40 — C2b2-b2 OFFLINE SSH CANDIDATE POLICY VALIDATION PASS; guarded on-disk installation SOURCE-ONLY

User on `admin-01` fetched branch through `6d786ec8` and ran `router-01-metrics-sshd-candidate-effective-readonly.yml`, syntax-check **PASS**, `--check -e router_c2_sshd_candidate_audit_approved=true` **PASS**. Exact recap **`router-01 ok=17 changed=0 unreachable=0 failed=0 skipped=0`**. The ephemeral protected candidate under `/run` was securely removed after validation. No live `/etc/ssh/sshd_config` change/reload, no `authorized_keys`, no router/network/monitoring changes. All physical Pi/router/Node Exporter baseline guards and before/after unit health checks passed.

Crucial actual on-box evidence:
- `candidate_sshd_syntax_valid: true` via `/usr/sbin/sshd -t -f <candidate>`.
- `global_policy_unchanged: true`, `admin_policy_unchanged_both_contexts: true`; **full** effective `sshd -T` output matched installed baseline for global and `james` via direct source and ASUS NAT source.
- `monitoring_policy_restrictions_verified_both_contexts: true` for the proposed `router-metrics` user (direct and ASUS contexts): `pubkeyauthentication yes`, `authenticationmethods publickey`, `passwordauthentication no`, `kbdinteractiveauthentication no`, `permittty no`, `x11forwarding no`, `allowagentforwarding no`, `allowstreamlocalforwarding no`, `allowtcpforwarding local`, `permitopen 127.0.0.1:9100`, `permitlisten none`, `gatewayports no`, `permittunnel no`, `permituserrc no`, `maxsessions 0`, `forcecommand none`.
- `live_main_ssh_config_unchanged: true`, `temporary_candidate_cleaned_up: true`, `no_sshd_reload_or_network_changes: true`.
- Pi `router-metrics` local system account/group is present, password-locked and nonlogin. **No SSH key authorized and NO active tunnel.**

**New next stage source ONLY** `IaC/ansible/playbooks/router-01-metrics-sshd-install.yml` in draft PR #210. Despite its filename, **it has NOT been run, syntax-checked or deployed on the Pi**. Has explicit `router_c2_sshd_install_approved=true` gate, exact admin-01/physical Pi verified identity, locked monitoring account, no authorized_keys, safe `/etc/ssh/sshd_config` root ownership and known `Include` ordering/absent snippets, SSH syntax, gateway health and loopback-only exporter. In `--check --diff`, Ansible should predict the identical EOF `Match User router-metrics` block already validated offline. It uses `blockinfile` with `validate: /usr/sbin/sshd -t -f %s` and `backup: true` in future **separately approved** normal-mode operation. The real on-disk deployment, if later authorised, is explicitly **NO sshd reload or restart**; before/after effective global and both admin policies compared for exact equality, monitoring user restrictions asserted in both source contexts, and `block/rescue` attempts to restore generated Ansible backup and revalidate if checks fail. Original SSH daemon remains running on existing loaded config until a separate, reviewed reload gate; if system restarts, on-disk policy would be applied (validated candidate). **A normal run is NOT currently authorised.** No key deployment, no exposure of port9100, no PPPoE/firewall/Prometheus modifications.

**Next operator task is SYNTAX AND CHECK-MODE ONLY**:

```bash
cd ~/projects/homelab-router-toolset-audit
git fetch origin feature/router-01-toolset-audit-20261028
git merge --ff-only FETCH_HEAD
cd IaC/ansible

ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-sshd-install.yml \
  --limit router-01 --syntax-check && \
ansible-playbook -i inventory/router-01-toolset-audit.yml \
  playbooks/router-01-metrics-sshd-install.yml \
  --limit router-01 --ask-become-pass --check --diff \
  -e router_c2_sshd_install_approved=true
```

Review full diff and check-mode recap before approval of normal mode. Under no circumstances reload Pi sshd, install `authorized_keys` from unverified source, open exporter to LAN, or start SSH tunnel based only on these staged results. Record live outcome and handover after any actual deployment. The monitor client's working private key remains isolated in `/var/lib/router-metrics-tunnel/.ssh/id_ed25519`.
