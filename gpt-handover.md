# GPT Handover — Homelab Platform

**Last updated:** 19 October 2026

**Session focus:** Greenbone vulnerability validation and remediation

**Current status (19 October 2026):** The last completed authenticated Greenbone report recorded **0 Critical, 0 High, 2 actionable Medium, 15 accepted risks** (14 ICMP timestamp replies and one BirdNET-Go `csrf` cookie missing HttpOnly). Former two actionable Mediums have been mitigated at the live service/network level (trusted qBittorrent HTTPS with direct LAN HTTP/8081 blocked; BirdNET-Go `csrf` Secure cookie verified) and await full scanner confirmation. **Three of the original 14 ICMP timestamp hosts now have independently tested live mitigations:** media-01 (existing Git-managed nftables input type-13 drop), docker-01 (dedicated iptables-nft host INPUT type-13 drop) and **monitor-01** (dedicated iptables-nft host INPUT type-13 drop). Newest user-run `greenbone-icmp-timestamp-monitor01-cutover.yml` completed **monitor-01 `ok=25 changed=3 unreachable=0 failed=0`; greenbone-01 `ok=8 changed=0 unreachable=0 failed=0`**. Scanner-side check reported `MONITOR01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, `MONITOR01_ICMP_ECHO=PASS`, `MONITOR01_FIREWALL_SCOPE=HOST_INPUT_ONLY`. Preflight and post-checks preserved Grafana HTTPS, existing monitoring container identities and Docker forwarding, without restarting containers/Docker/Greenbone scan. Dedicated systemd persistence was staged and applied on monitor-01 but **not reboot-tested**. **11 remaining ICMP host findings and the BirdNET-Go csrf HttpOnly exception** still require review. No accepted-risk allowlist entries have been removed; independently observed no-reply is operational mitigation proof, **not a fresh completed Greenbone report**. Next read-only host review should be scoped by inventory and live firewall owner; before an eventual single authenticated managed scan, check scan activity and GMP readiness.

## Next live step — sensor-01 only, audited VM timestamp filter (Git STAGED)

The successful 11-host read-only sweep is documented below. The now-committed **three-VM reusable `icmp_timestamp_vm_input` role** uses a host-specific exact IP/comment-tagged `iptables-nft INPUT -p icmp --icmp-type 13 DROP`, an idempotent helper, and a separate one-shot persistent unit. Git files:
- `roles/icmp_timestamp_vm_input/templates/helper.sh.j2` and `homelab-icmp-timestamp-vm.service.j2`
- `roles/icmp_timestamp_vm_input/tasks/main.yml`
- `playbooks/greenbone-icmp-timestamp-vms-cutover.yml` and `greenbone-icmp-timestamp-vms-rollback.yml`
- `scripts/validate-icmp-timestamp-vm-wave.py`.

**None has been executed on a host or tested using Ansible yet.** Three eligible hosts are sensor-01 (.55, Suricata + Zeek, no Docker), cloud-01 (.53, Docker/Nextcloud) and greenbone-01 (.57, Docker/Greenbone). The playbook `serial: 1` requires a positive scanner-side timestamp baseline and ordinary ping, uses monitor-01 as the **external** probe source only when modifying greenbone-01, checks SSH access, checks Docker active/container identity or sensor capture service state, and preserves INPUT policy + full FORWARD/DOCKER rule structures. It does not restart Docker, databases, scanner or sensor. **Stage only sensor-01 first**; only progress to cloud-01 and greenbone-01 after reviewing its actual Ansible output and verifying rollback readiness.

**From admin-01: validate the new source and playbook syntax, then apply sensor-01 only:**

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-icmp-timestamp-vm-wave.py &&
python3 scripts/validate-icmp-timestamp-probe.py &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-vms-cutover.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-vms-rollback.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-vms-cutover.yml \
  --limit sensor-01 --forks 1 --ask-become-pass
```

On a failure or connectivity disruption after a rule is added, run **sensor-01 only** rollback; do not attempt to change all VM hosts automatically:

```bash
cd ~/projects/homelab-platform/IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-vms-rollback.yml \
  --limit sensor-01 --forks 1 --ask-become-pass
```

**Expected verified success:** `VM=sensor-01`, `VM_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, `VM_ICMP_ECHO=PASS`; unchanged SSH, Suricata/Zeek service state, FORWARD chains. After evidence, record live outcome, then test cloud-01 and greenbone-01 **one at a time** by changing only the `--limit` argument. Do not claim 4/14 until live output arrives. For LXC/Komodo/Admin/Proxmox-2, more owner-specific review is still mandatory; don't apply VM role to them. Accepted risks and fresh scan unchanged.

## Latest verified remaining-11 compatibility sweep — SUCCESS (19 October 2026)

**Complete user-uploaded Ansible log after `--ask-become-pass`:** The earlier admin-01 `Missing sudo password` issue was resolved. `greenbone-icmp-timestamp-remaining11-readonly.yml --forks 1 --ask-become-pass` completed **all 11 host audits and the independent scanner-side probe**, with `changed=0 unreachable=0 failed=0` on all hosts. 10 targets reported `ok=3`; greenbone-01 reported `ok=7`. **Every one of the 11 hosts replied to three out of three ICMPv4 timestamp requests** (33 matched replies total). The greenbone-01 self-target was correctly probed externally from monitor-01. Ping tests were executed but the playbook set `failed_when: false` and did not print their registered RCs, so do **not** assert ping PASS for all 11 from this log. No configuration, firewall, service, scan or accepted-risk change was made.

**Evidence-based firewall classes:**
- **Five LXC guests with nftables active, CAP_NET_ADMIN present, and one nft INPUT/FORWARD hook each:** dns-01 (.51), dns-02 (.50), mail-relay-01 (.54), edge-01 (.56), zabbix-01 (.59). iptables commands missing; need inspect the Git/managed nftables configuration and hook priorities before adding one type-13 drop. Preserve live DNS, SMTP, Zabbix.
- **Three VM hosts with `iptables v1.8.11 (nf_tables)`, INPUT ACCEPT / zero INPUT rules and CAP_NET_ADMIN:** cloud-01 (.53, Docker active, FORWARD DROP/four DOCKER chains); sensor-01 (.55, no Docker, FORWARD ACCEPT); greenbone-01 (.57, Docker active, FORWARD DROP/six DOCKER chains; nft INPUT hooks 0, FORWARD hooks 2). Good candidates for a reusable host-INPUT-only iptables-nft rule with per-host pre/post service/Docker checks. External source to greenbone-01 must be monitor-01.
- **komodo-01 (.58):** LXC with Docker active and nftables active, iptables-nft INPUT ACCEPT/zero INPUT rules, FORWARD DROP, six Docker filter chains, **one nft INPUT hook** and three FORWARD hooks. Inspect ordering / nft firewall first; do not blindly reuse host-input rule.
- **admin-01 (.48):** Raspberry Pi admin and Corosync QNetd; iptables absent, nft available and readable with 0 INPUT/FORWARD hooks, nftables service not active, CAP_NET_ADMIN present. Standalone host policy could be designed but requires an explicit local-access/SSH/quorum-safe rollback.
- **Proxmox-2 (.71):** Both `pve-firewall` and `proxmox-firewall` services active, `iptables v1.8.11 (legacy)`, INPUT ACCEPT/0 rules, nft readable with 0 INPUT/FORWARD hooks and `/etc/pve` present. **Do not install nftables service, overwrite Proxmox policy or treat guest firewall as authoritative.** Inspect live Proxmox-native firewall configuration and active chains first.

**Progress stays at three live mitigations out of 14** (media-01, docker-01, monitor-01); 11 remain exposed, plus separate BirdNET-Go csrf HttpOnly acceptance. Last completed authenticated Greenbone report remains old; accepted-risk register unchanged.

**Next:** stage the three VM host-input compatibility cutovers (one at a time, preserving Docker/Nextcloud, Suricata+Zeek and scanner services) and separately inspect existing nftables rule ownership on five LXC guests/Komodo; treat admin-01 and Proxmox-2 as special. Do not attempt a blind all-11 firewall rollout. See `docs/security/GREENBONE-ICMP-REMAINING-ROLLOUT-2026-10-19.md`.

### Historical failed first attempt (resolved by successful sudo-authenticated sweep)

User ran the checked-in `greenbone-icmp-timestamp-remaining11-readonly.yml`, which starts serially with admin-01. Inventory connects to admin-01 as `james`. The identity assertion passed (`admin-01 ok=1`), then the first elevated packet-filter read failed: **`Missing sudo password`** at `Collect non-secret packet filter ownership and permissions`. Recap: `admin-01 ok=1 changed=0 unreachable=0 failed=1`; **no other hosts examined, no scanner-side probes, and no host/network/firewall changes occurred**. This is an authentication issue, not evidence of a firewall problem.

**Immediate retry from `admin-01:~/projects/homelab-platform/IaC/ansible`:**

```bash
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-remaining11-readonly.yml \
  --forks 1 --ask-become-pass
```

Supply the interactive `james` sudo password for admin-01 at the `BECOME password:` prompt; **do not place any password in shell arguments, inventory, Git, handover, or chat**. The task remains read-only. Since Ansible prompts once for one shared become password, if subsequent hosts have different sudo credentials, scope them separately rather than weakening sudo or saving secrets. Do not claim that the other 10 have been audited or that any of the 11 findings have been remediated.

## New user decision — remediate the remaining 11 ICMP timestamp hosts (19 October 2026)

**User authorised continued work on all 11 remaining reported ICMP timestamp findings**, beyond already verified media-01, docker-01 and monitor-01. The 11 are **six LXC guests** (dns-01, dns-02, mail-relay-01, edge-01, komodo-01, zabbix-01), **three VMs** (cloud-01, sensor-01, greenbone-01), **two physical nodes** (admin-01 Pi controller/QNetd, Proxmox-2 cluster hypervisor). The user has not supplied effective firewall ownership/netfilter capability evidence for these 11 and **nothing on these 11 has been modified yet**. It is unsafe to bulk-install the same INPUT rule onto LXCs or a Proxmox node without knowing which firewall owns packets, preserving DNS/SMTP/cluster/guest traffic, or checking CAP_NET_ADMIN.

**Git-only preparation now committed:** `playbooks/greenbone-icmp-timestamp-remaining11-readonly.yml` interrogates exactly those 11 inventory names/addresses sequentially, reporting only service/iptables/nft/backend/container/CAP_NET_ADMIN/Proxmox indicators (never raw secret-containing rules). The second play runs the existing self-tested 3-request ICMP timestamp probe and ordinary ping from greenbone-01; for **greenbone-01 itself**, probes are delegated to monitor-01 for an independent vantage. `scripts/validate-icmp-timestamp-remaining11-audit.py` statically validates the exact 11 hosts, safety properties and Python source. Detailed staged progression and host table: `docs/security/GREENBONE-ICMP-REMAINING-ROLLOUT-2026-10-19.md`. **No Ansible sweep has run and no new firewall configuration, scan, kernel, reboot, Proxmox policy or accepted-risk change was performed by the Git commit.** Current proof remains 3/14 mitigated, 11 pending. Greenbone's earlier two Mediums and BirdNET csrf HttpOnly remain separate, awaiting fresh completed scan/functional review.

**Next from admin-01, read-only full compatibility survey:**

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-icmp-timestamp-remaining11-audit.py &&
python3 scripts/validate-icmp-timestamp-probe.py &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-remaining11-readonly.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-remaining11-readonly.yml --forks 1
```

After reviewing each host's audit and scanner result, design target-specific managed cutover(s) and precise rollback **only for compatible cases**; separate guest/Proxmox host controls and the controller QNetd node, serialise deployment and verify normal ping, essential service paths and absence of timestamp replies before moving on. Do not publish claimed fixes or remove accepted risk records based solely on staged code.

**Owner:** User-led, ChatGPT-assisted infrastructure work

## Latest monitor-01 evidence and next read-only diagnostic — 19 October 2026
## Latest verified monitor-01 ICMP timestamp mitigation — LIVE (19 October 2026)

**Live user-supplied result:** Scoped `greenbone-icmp-timestamp-monitor01-cutover.yml --limit 'monitor-01:greenbone-01' --forks 1` finished: **monitor-01 `ok=25 changed=3 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`**, **greenbone-01 `ok=8 changed=0 unreachable=0 failed=0`**. The final independently checked result was:
- `MONITOR01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`
- `MONITOR01_ICMP_ECHO=PASS`
- `MONITOR01_FIREWALL_SCOPE=HOST_INPUT_ONLY`
- `Grafana HTTPS, running containers, Docker forwarding unchanged.`
- `No monitoring container, Docker service or Greenbone scan restarted.`

Preflight from greenbone-01 had previously reproduced 3 of 3 timestamp replies; the active, uniquely tagged IPv4 type-13 host INPUT-only iptables-nft rule now yields zero matching replies while ordinary ping works. Existing Docker Compose monitoring containers, Grafana TLS and Docker forwarding were checked unchanged. Dedicated persistence unit is configured but has not been verified by a reboot. **This is host 3 of 14 operationally mitigated; 11 ICMP host findings remain unverified/untreated.** No accepted-risk record updated, and a new authenticated Greenbone scan is still pending. Manual rollback is `playbooks/greenbone-icmp-timestamp-monitor01-rollback.yml`, **not executed**.

**Next candidate for one-host read-only reconnaissance:** cloud-01 (production Nextcloud VM), using the existing `playbooks/greenbone-accepted-icmp-firewall-readonly.yml --limit cloud-01 --forks 1`. Do not change Nextcloud, PostgreSQL, Redis, networking, firewall or guest connectivity until the result is reviewed. Other hosts such as Proxmox-2, LXC/DNS/SMTP, and admin-01 need particular care; no multi-host blanket rollout. Greenbone scan readiness and accepted-risk reconciliation are separate future steps.

### Historical plan — monitor-01 staged ICMP cutover (now deployed)

Live **read-only** monitor-01 evidence: `ok=3 changed=0 failed=0`, `iptables v1.8.11 (nf_tables)`, INPUT ACCEPT/0 rules, FORWARD DROP, 4 custom chains; `nft` utility missing. The user confirmed earlier monitor-01 sent 3 valid ICMP timestamp replies from 3 requests; ordinary ping PASS. Native systemd checks for Prometheus/Grafana/Loki/Alertmanager returned `not-active-or-unknown`, **as expected for the Git-managed Docker Compose monitoring stack**, and must not be misread as an outage. Repo service definition: `roles/monitoring_stack/templates/docker-compose.yml.j2` under `/opt/monitoring`.

**Git staged, not deployed:** New `roles/monitor_icmp_timestamp/` installs only idempotent comment-tagged `iptables -w -I INPUT 1 -d 192.168.2.52/32 -p icmp --icmp-type 13 -j DROP` with dedicated systemd oneshot persistence; no Docker service restart, chain flush, NAT or FORWARD alteration. `playbooks/greenbone-icmp-timestamp-monitor01-cutover.yml` checks scan-side baseline, >=5 running monitoring containers, Grafana trusted HTTPS, Docker FORWARD/DOCKER invariant before/after, then ping and three-request timestamp suppression from greenbone-01. `playbooks/greenbone-icmp-timestamp-monitor01-rollback.yml` stops the dedicated unit, deletes only the matching rule and checks ping/Grafana/Docker. `scripts/validate-monitor01-icmp-timestamp-firewall.py` is an offline gate. None of the newly staged source has been validated by the user or run live; Greenbone scan and accepted-risk register unchanged. Verified ICMP mitigations remain **2/14**.

**Next commands (admin-01; syntax/source checks gate scoped deployment):**

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-monitor01-icmp-timestamp-firewall.py &&
python3 scripts/validate-icmp-timestamp-probe.py &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml playbooks/greenbone-icmp-timestamp-monitor01-cutover.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml playbooks/greenbone-icmp-timestamp-monitor01-rollback.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml playbooks/greenbone-icmp-timestamp-monitor01-cutover.yml --limit 'monitor-01:greenbone-01' --forks 1
```

If network checks or monitoring break, manual scoped rollback:
```bash
cd ~/projects/homelab-platform/IaC/ansible &&
ansible-playbook -i inventory/hosts.yml playbooks/greenbone-icmp-timestamp-monitor01-rollback.yml --limit 'monitor-01:greenbone-01' --forks 1
```

User must provide Ansible output before claiming live success. Do not remove any accepted-risk entry before a new completed Greenbone scan.

## Latest verified monitor-01 result — ICMP timestamps reproducible (19 October 2026)

**User-provided live output:** Scoped `greenbone-icmp-timestamp-monitor01-readonly.yml --limit 'monitor-01:greenbone-01' --forks 1` completed `monitor-01 ok=3 changed=0 unreachable=0 failed=0` and `greenbone-01 ok=5 changed=0 unreachable=0 failed=0`. From greenbone-01, ordinary ping to `192.168.2.52` passed, and **3 of 3 ICMP type-13 timestamp requests elicited matching type-14 replies** (`ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED`, `MONITOR01_TIMESTAMP_INTERPRETATION=REPLY_CONFIRMED`). This reproduces the accepted ICMP timestamp finding; no firewall/sysctl/service configuration or Greenbone scans were changed.

**Missing output:** User pasted the second play and recap only, **not** the first play's `TASK [Report monitoring service and host firewall indicators only]`. Do not assume iptables backend/INPUT policy or why nft was unreadable. To retrieve without resending scanner probes, run only the first play on monitor-01:

```bash
cd ~/projects/homelab-platform/IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-monitor01-readonly.yml \
  --limit monitor-01 --forks 1
```

Review `IPTABLES_VERSION`, `IPTABLES_FILTER_STATUS`, `INPUT_POLICY`, `INPUT_RULE_COUNT`, `NFT_READ_FAILURE_CATEGORY` and service indicators before staging host-specific mitigation. Avoid copying media-01 or docker-01 firewall implementations to monitor-01. **Operational mitigation remains 2 of 14** (media-01 and docker-01); no accepted-risk records altered. Fresh completed authenticated Greenbone scan still pending.



**User's uploaded terminal log:** After the successful docker-01 ICMP timestamp remediation (already recorded), the user ran `ansible-playbook -i inventory/hosts.yml playbooks/greenbone-accepted-icmp-firewall-readonly.yml --limit monitor-01 --forks 1`. It finished `monitor-01 ok=2 changed=0 unreachable=0 failed=0`. Reported Debian GNU/Linux 13 (Trixie), no detected active nftables/UFW/firewalld/Proxmox firewall systemd services; `NFT_RULESET=not-readable`; `IPTABLES_RULESET=readable`; `IPTABLES_TIMESTAMP_REQUEST_REFERENCES=0`; `AUDIT=READ_ONLY`. This does **not** establish the effective iptables backend/policy or whether monitor-01 responds to timestamp requests. No host change made. User's log also contained benign `-bash: command not found` errors after accidentally pasting previous Ansible report output back into the shell; the actual cutover play had already passed and no SSH failure was evidenced.

**New Git-staged read-only diagnostic, NOT YET RUN:** `IaC/ansible/playbooks/greenbone-icmp-timestamp-monitor01-readonly.yml` targets only `monitor-01` (`192.168.2.52`) and `greenbone-01` (`192.168.2.57`). On monitor-01 it reports the iptables backend, filter INPUT/FORWARD/OUTPUT policy/rule counts, whether `nft` is missing/unavailable or permission denied, and brief Prometheus/Grafana/Loki/Alertmanager service indicators. On greenbone-01 it checks ordinary ping and sends three bounded ICMP timestamp requests via the existing self-tested shared packet probe. No firewall, network, kernel, monitoring service, risk acceptance or Greenbone scan changes. This playbook is committed only; source syntax and live behaviour have not yet been verified.

**Next commands on admin-01:**

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-monitor01-readonly.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-monitor01-readonly.yml \
  --limit 'monitor-01:greenbone-01' --forks 1
```

Review both plays before designing any narrowly scoped host-specific ICMP mitigation. **Two hosts operationally mitigated (media-01/docker-01); 12 still outstanding, including monitor-01; no fresh authenticated Greenbone scan or allowlist change yet.**

## Latest live deployment — docker-01 ICMP timestamps suppressed (19 October 2026)

**Verified user-provided Ansible output:** The scoped `greenbone-icmp-timestamp-docker01-cutover.yml --limit 'docker-01:greenbone-01' --forks 1` completed on docker-01 **`ok=22 changed=3 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`**, and on greenbone-01 **`ok=8 changed=0 unreachable=0 failed=0`**. After installing the Git-managed `docker_icmp_timestamp` host INPUT type-13-only rule, the scanner-side probe's `Require zero matching timestamp replies` assertion passed and reported `DOCKER01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, `DOCKER01_ICMP_ECHO=PASS`, `DOCKER01_FIREWALL_SCOPE=HOST_INPUT_ONLY`. Before this cutover, the separately captured scanner probe had observed three matching timestamp replies from three requests, while normal ping worked. No new Greenbone scan has run.

**Service/traffic preservation confirmed by run:** Docker service remained active, two running container identities remained unchanged, Docker FORWARD and DOCKER chain definitions/policy assertions passed, and trusted BirdNET HTTPS still worked. Docker was not restarted. The standalone systemd one-shot persistence unit and exact comment-tagged iptables-nft rule were installed; persistence over a real reboot has not yet been tested. The exact rollback playbook remains available: `IaC/ansible/playbooks/greenbone-icmp-timestamp-docker01-rollback.yml` (not used). This is **second operationally mitigated ICMP host out of 14**, not yet Greenbone-scan-cleared. Keep all accepted-risk policy entries unchanged pending a fresh completed scan.

**Next:** Choose **one** of the 12 other reported ICMP hosts for the already committed *read-only* firewall ownership audit, e.g. `monitor-01`, before deciding whether an existing packet-filter owner can safely be reused. No assumption that Docker's host INPUT approach or media-01's nftables role applies to other hosts. Greenbone authenticated rescan of both earlier Mediums and all accepted findings is deferred until readiness/evidence checks and a single managed scan. The independent BirdNET csrf HttpOnly acceptance remains open to functional review.

### Previous work plan — staged docker-01 ICMP timestamp INPUT cutover

**19 October 2026 newest live read-only evidence:** User reran `greenbone-icmp-timestamp-docker01-readonly.yml --limit docker-01 --forks 1`, `ok=3 changed=0 failed=0`. Observed Docker active (2 running containers), `iptables v1.8.11 (nf_tables)`, `INPUT_POLICY=ACCEPT`, **`INPUT_RULE_COUNT=0`**, `FORWARD_POLICY=DROP`, four Docker filter chains, no existing timestamp/INPUT ICMP rules, nftables INPUT hooks 0 and FORWARD hook 1. Earlier read-only Greenbone-side probe confirmed `docker-01` responds to 3/3 ICMP timestamp requests and ordinary ping succeeds. This confirms it is host INPUT traffic, unlike Docker container FORWARD traffic. **No live remediation applied on docker-01 yet.**

**Git-staged source only, not yet checked on admin-01 or deployed:** New `roles/docker_icmp_timestamp/` includes a small idempotent `iptables -w -I INPUT 1 -d 192.168.2.220/32 -p icmp --icmp-type 13 -m comment --comment homelab-docker01-icmp-timestamp -j DROP` policy helper, with `-C` guard and `-D` removal, refuses non-nft iptables backend. A small independent `homelab-docker01-icmp-timestamp.service` oneshot systemd unit makes the **single host INPUT rule** persistent across reboot; `Before=docker.service` for boot ordering. It does not start/restart Docker, alter Docker's existing FORWARD, DOCKER-* or NAT chains, flush iptables/nftables, install packages or replace another firewall ruleset. Playbooks `greenbone-icmp-timestamp-docker01-cutover.yml` and `greenbone-icmp-timestamp-docker01-rollback.yml` explicitly scope to docker-01 and greenbone-01, with scanner-side 3-request pre/post checks, Docker running-container identity checks, trusted BirdNET HTTPS health and filter FORWARD/DOCKER chain equivalence. `scripts/validate-docker01-icmp-timestamp-firewall.py` is an offline contract validator. **Actual validation and Ansible syntax checks are pending.** Do not claim mitigation or change Greenbone accepted risks until successful live evidence and a later fresh completed Greenbone report.

**Next command from admin-01 (offline validation then live scoped cutover, stop on failure):**

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-docker01-icmp-timestamp-firewall.py &&
python3 scripts/validate-icmp-timestamp-probe.py &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-docker01-cutover.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-docker01-rollback.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-docker01-cutover.yml \
  --limit 'docker-01:greenbone-01' --forks 1
```

If the postflight fails or unexpected service effects occur, run the scoped manual rollback (this disables the dedicated unit and deletes **only** the exact comment-tagged rule, leaving Docker intact):

```bash
cd ~/projects/homelab-platform/IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-docker01-rollback.yml \
  --limit 'docker-01:greenbone-01' --forks 1
```

The cutover should confirm `DOCKER01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED` and `DOCKER01_ICMP_ECHO=PASS` while BirdNET HTTPS/Docker containers remain available. No live work is asserted by staging the source; the user's next Ansible output is required. Keep the established media-01 ICMP filter and all accepted risks unchanged.

## Latest verified docker-01 ICMP timestamp result — 19 October 2026

**User supplied the scanner portion of scoped read-only Ansible output:** `greenbone-icmp-timestamp-docker01-readonly.yml` completed `docker-01 ok=3 changed=0 unreachable=0 failed=0`; `greenbone-01 ok=5 changed=0 unreachable=0 failed=0`. From greenbone-01 (192.168.2.57), ordinary ping to docker-01 (192.168.2.220) passed and **3 of 3 matching ICMPv4 timestamp replies** were observed (`ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED`, `DOCKER01_TIMESTAMP_INTERPRETATION=REPLY_CONFIRMED`). This confirms the accepted ICMP timestamp finding is still reproducible on docker-01. **No host, kernel, firewall, sysctl, service, scan or risk-acceptance changes.**

**Missing output:** User pasted only the latter scanner-side tasks and the play recap, **not** `TASK [Report non-secret Docker firewall indicators]` from the earlier docker-01 play. Do not infer the actual iptables backend or INPUT/FORWARD/OUTPUT policies from success alone. Before designing a Docker-safe fix, rerun **only** the first play:

```bash
cd ~/projects/homelab-platform/IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-docker01-readonly.yml \
  --limit docker-01 --forks 1
```

Request the `TASK [Report non-secret Docker firewall indicators]` message and recap. This limited read-only run does **not** resend timestamp probes from greenbone-01. Do not copy the media-01 nftables firewall onto docker-01 or alter Docker's forwarding/chains. As previously, the successful media-01 ICMP mitigation is verified independently, but still pending a completed Greenbone rescan.

## Latest work: docker-01 ICMP timestamp reconnaissance (19 October 2026)

User's read-only docker-01 audit: ok=2 changed=0 failed=0. Debian 13, nftables service inactive, nft rules readable but zero input hooks; iptables-save readable; no existing timestamp-specific rules. Docker host's actual packet filtering owner is **not established**. No host configuration changed.

A further scoped read-only playbook is staged in Git at IaC/ansible/playbooks/greenbone-icmp-timestamp-docker01-readonly.yml; it has **not been run**. It reports iptables backend and filter-chain structure on docker-01 without full rules, and tests normal ping plus three ICMP timestamp requests from greenbone-01. It does not install nftables or change Docker, firewall, kernel, services or scans. Next run its syntax check and limit execution to docker-01:greenbone-01 with forks=1. Do not apply media-01's firewall role on Docker hosts. Existing media-01 mitigation remains verified; all other accepted risks unchanged.

## Read this first in every new chat

1. Read this file **before** proposing new work.
2. Read `IaC/inventory/estate.json`, `docs/architecture/CURRENT-STATE.md`, `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md`, and the relevant Ansible configuration. These remain the source of truth; this handover is a **working pointer**, not an independent authority.
3. Read `AGENTS.md` and follow its preflight and validation rules.
4. Check Git status and the latest commits before editing; do not overwrite work from another session or blindly trust this handover if it is older than current changes.
5. Distinguish **implemented/committed**, **validated live**, **pending validation**, and **accepted risk**. Never interpret missing or stale evidence as zero vulnerabilities.
6. **Every user/assistant-driven change** to the repository, IaC, operational configuration, architecture, runbooks, security findings or project priorities requires a contemporaneous update to this file, preferably in the **same commit/PR**. Update the current status, evidence/commands, decision, next action and change log. Update canonical docs too if architecture or backlog status changed. Routine automated telemetry-only commits do not by themselves change the handover unless they alter a decision or status.
7. **Use Ansible for every host-level operation**, including inspection and read-only checks, from `admin-01` using the Git-managed inventory. **All persistent changes go into Git-managed IaC first**, validated and applied by Ansible; do not propose direct SSH/manual edits except an explicitly approved emergency exception subsequently reconciled into IaC.
8. Do not store passwords, keys, API tokens or raw confidential scan evidence here. Do not claim that local-only commands, tests, deployment or live verification ran unless they actually did.

## Current task — finish the Greenbone remediation gate

As of the repository review on **18 October 2026**, the last documented Greenbone managed scan is **14 October 2026**:

| Finding type | Last documented count |
| --- | ---: |
| Critical | 0 |
| High | 0 |
| Medium actionable | 1 |
| Low | 0 |
| Accepted risks | 30 |

The Medium finding was **cleartext Zabbix management HTTP**. Trusted HTTPS/reverse-proxy and secure cookie remediation is recorded as implemented, but **the final scan has not yet been reviewed**. Do not close it prematurely.

Other remediation already recorded:
- `docker-01`: Raspberry Pi 4 Trusted Firmware-A v2.15.0 speculative-execution hardening, codified and validated idempotently with Ansible; commit `b3047742`. Confirm scan findings after remediation.
- Grafana: port 3000 bound to localhost behind nginx HTTPS; seven public certificate renewal/deploy paths dry-run tested on 16 October.
- 16 October: new `tcp_timestamp_hardening` Ansible playbook/role to disable `net.ipv4.tcp_timestamps` across the 15 Greenbone-flagged Linux hosts; commit `e27b864f4d`. **Git commit confirmed; live rollout/Greenbone clearance not independently checked in this 18 October review.**
- 16 October: automated Suricata threat-rule refresh with validation and rollback; commit `827e7c9e85`. This is separate preventative security work, not proof that Greenbone findings cleared.
- Accepted-risk details are integrated with management reporting and Grafana; verify their consistency against Greenbone evidence.

**Decision:** Finish vulnerability validation before changing priority to Raspberry Pi overclocking, Docker lifecycle, or disaster recovery.

**Outage update — 18 October 2026:** The user reports **`Proxmox-2` is down**; on `admin-01`, Ansible's `greenbone-scan-evidence-readonly.yml` failed at the first remote command with `ssh: connect to host 192.168.2.57 port 22: Connection timed out`. The initial `assert` ran locally (it did **not** establish SSH connectivity). This **does not** mean there are zero vulnerabilities. Greenbone VM203, monitoring VM202, `dns-01` CT101, and `edge-01` CT103 are assigned to `Proxmox-2`; guest disks are node-local, and these workloads may be unavailable while their host is down. Actual Proxmox-2 power/cluster health has not been independently verified, nor has `PROXMOX` quorum been checked after the outage. Restore/repair is **not** approved by this note; avoid rebooting/migrating guests without evidence and authorisation.

**Instrumented GMP preflight live result — 18 October 2026:** User pulled `1b549376` to `admin-01`, syntax-checked `greenbone-gmp-preflight.yml` (PASS), and executed it on `greenbone-01`. The preflight passed its existing-credentials safeguard and reached `GMP_CHECK_STAGE=loading_credentials`, `GMP_CHECK_STAGE=creating_temporary_config`, `GMP_CHECK_STAGE=querying_managed_task`, then GNU timeout returned `rc=124` after 150s. Runner stderr reported `ERROR: GMP preflight interrupted by signal 15`. The post-run stat returned `Temporary GMP config absent: True`; SIGTERM cleanup worked. The final application assertion **failed correctly**: `ok=9 changed=0 unreachable=0 failed=1`. `GMP_CHECK_STAGE=querying_managed_task` precedes the Compose helper invocation and cannot distinguish helper startup, socket connection or GMP response. **Authentication/task lookup not verified, no new scan, and no credentials leaked on this attempt.**

**New Git-managed passive diagnostic, not yet executed:** `IaC/ansible/playbooks/greenbone-gmp-request-path-readonly.yml` examines helper-container remnants, the existing gvmd Unix socket and socket-volume mount, server/Docker logs and transient-credential absence. It does not invoke GMP, launch a temporary helper or read credentials. The playbook has not been syntax-checked or run on the controller. Read its output before any further GMP test or scan.

**GMP latency diagnostic — 18 October 2026:** User ran `greenbone-gmp-latency-readonly.yml` from `admin-01`, syntax check PASS and live `greenbone-01 ok=7 changed=0 unreachable=0 failed=0`. Docker events API returned no historical records (not conclusive); Docker journal logged helper endpoint join at 16:45:46 BST (`greenbone-community-edition-gvm-tools-run-e5ecef008d1a`) and a containerd task-delete at 16:45:47 BST (whether the same task is not proven). No relevant error in bounded gvmd/PostgreSQL logs; one 16:47 BST PostgreSQL checkpoint entry. Available RAM ~5,619 MB, disk ~61 GB free at 47% usage. The orphan credentials file remained **absent**. The helper is known to have been launched, but **the stage causing the 150-second timeout is still unknown**.

**Staged IaC diagnostics/fix (not deployed as of this note):** The `greenbone_scanning` Python runner template now logs safe stage markers only for `--check`, bounds the GMP task lookup subprocess to 75s instead of 120s for that mode, and converts SIGTERM into an exception to permit `finally` cleanup. The separate Ansible preflight refuses pre-existing orphan GMP credentials, imposes a TERM→KILL deadline, shows post-check file metadata, and **fails the playbook if the GMP check or cleanup fails**, rather than reporting a misleading green recap. Full production scan mode retains its existing default 120s per GMP command; **boot readiness guard and durable process-group cleanup have not yet been implemented**. The existing SIGTERM handler improves but does not guarantee cleanup if forcibly killed (SIGKILL or a subprocess that fails to terminate). **No host code/service modified by this Git commit**, and no new scan started.

**Confirmed safe credential cleanup — 18 October 2026:** The user executed `greenbone-gmp-orphan-cleanup.yml` on `admin-01`. Git fast-forward to commit `1f3fbde4` succeeded; local untracked Kodi metadata directories remained untouched. Ansible syntax check **PASS**; live run recap `greenbone-01 ok=12 changed=1 unreachable=0 failed=0`. Scan/service/lock/helper/file safety assertions passed. The cleanup reported `REMOVED_ORPHANED_GMP_CONFIG`, then verified `Temporary GMP credential file absent: True`. No scan, restart or helper container was launched by this playbook. The `changed=1` reflects the intended removal of the transient protected config; it does not represent persistent deployment change.

**Next diagnostic:** The exact source of the previous `managed --check` 150-second hang is still unknown. A new **read-only** Ansible playbook, `IaC/ansible/playbooks/greenbone-gmp-latency-readonly.yml`, inspects bounded historical Docker events for `gvm-tools` around 16:43–16:51 BST, Docker service journal, `gvmd`/PostgreSQL logs, system memory and disk, and verifies the orphan file remains absent. It makes **no authenticated GMP call**, starts no scan/helper or container, and doesn't inspect secrets. Historical Docker events may have rolled over; empty events are inconclusive. The new playbook is committed but **not yet syntax-checked or run on the controller**.

**Read-only orphan diagnostic — 18 October 2026:** User ran `greenbone-gmp-timeout-readonly.yml`; controller Ansible syntax **PASS**, live recap `greenbone-01 ok=9 changed=0 unreachable=0 failed=0`. The file `/run/greenbone-scanning/runner-gvm-tools.conf` was confirmed **present**, root-owned `0640` (mtime 2026-10-18 15:45:46 UTC). The shared scan lock file exists but `fuser` returned rc=1 (no detected lock owner), `ps` found no relevant `python3`/`docker`/`flock`/`timeout`/`gvm-cli` processes, and no recent GMP helper containers remained; only a four-week-old exited gvm-tools container was listed. `gvmd` and `pg-gvm` were both `Up (healthy)` for approximately 37 minutes. The managed scan systemd unit still reported the earlier 16:18 failure. This **confirms stale transient credentials remained after external timeout**, but does **not** establish where Docker/GMP hung.

**Staged safe remediation, not yet deployed:** `IaC/ansible/playbooks/greenbone-gmp-orphan-cleanup.yml` provides one-time controlled removal of this exact temporary GMP file only, after confirming no active managed scan, no active gvm-tools container, no relevant process/file/lock owner, root-owned regular file with expected mode, and acquisition of the same exclusive flock lock as the runner. It avoids printing credentials, refuses unexpected conditions, and checks for absence afterward. **The playbook has not yet been syntax-checked or run live.** User must review/execute it from `admin-01` before any further GMP preflight. Do not run a scan during this step.

**Preflight failure — 18 October 2026:** User ran `greenbone-gmp-preflight.yml` after a successful Ansible syntax check. The playbook reached `greenbone-01` (`ok=6 changed=0 unreachable=0 failed=0`) but the **actual GMP test did NOT pass**: `GMP check exit code: 124`, `GMP output: []`, `GMP error: []`, `GMP readiness: NOT VERIFIED`. Exit 124 is GNU `timeout 150s`, **not** an authentication-failure code. The playbook deliberately used `failed_when: false` to emit diagnostics, so Ansible's `ok` recap is **not** a passing application test. No Greenbone scan was started by `--check`, and the prior failed unit state remains.

**Potential temporary-credentials residue:** The existing runner writes a protected GMP credentials file at `/run/greenbone-scanning/runner-gvm-tools.conf` and tries to remove it in a Python `finally` block. An external SIGTERM from `timeout` may terminate Python before that cleanup block executes. File presence, lock ownership and helper-container lifetime have **not** been verified. **Never print/slurp the file contents or repeat the preflight** until residual processes and credential metadata are checked.

**New read-only diagnostic:** `IaC/ansible/playbooks/greenbone-gmp-timeout-readonly.yml` checks temporary GMP file **metadata only**, runner lock owners, relevant process names **without arguments/environment**, remaining `gvm-tools` helper containers, core Greenbone container health and bounded logs. The code is in Git, but **syntax/live execution remain pending**. This diagnostic cannot delete or modify runtime data.

**Greenbone stack live health evidence — 18 October 2026 (approx. 16:38 BST):** The user executed `greenbone-stack-health-readonly.yml` after fetching the repository update. Ansible syntax check PASSED; recap `greenbone-01 ok=7 changed=0 unreachable=0 failed=0`. Docker `ActiveState=active`; `gvmd` and `pg-gvm` containers are `Up ... (healthy)`; `docker compose exec ... gvmd` confirmed `gvmd-socket-present`; historical managed scan service still `failed` from the earlier launch. Logs give a clear **startup race**: Docker active and managed scan launched at **16:17:47 BST**, scan failed at **16:18:01 BST**, gvmd recorded `ready to accept GMP connections` only at **16:19:29 BST**. A scanner/database VT hash mismatch triggered a rebuild; logs show **190,103 VTs updated at 16:36:50 BST** and `SecInfo feed sync finished` at approximately **16:37:11 BST**. PostgreSQL emitted repeated `checkpoints are occurring too frequently` / `max_wal_size` hints during the import (separate performance observation; no unreviewed DB tuning). `gvmd` also logged a missing `data-objects/gvmd` feed subdirectory during startup; its impact is not established.

The existing `homelab-greenbone-managed-scan.timer` uses `Persistent=true`, and its service only orders `After=docker.service network-online.target`, which does **not** guarantee GMP readiness. This explains the attempt during startup; a durable Ansible-managed GMP readiness gate is a candidate fix but has **not** been deployed or yet designed/validated. Before starting another scan, use `greenbone-gmp-preflight.yml` to run the existing scan runner's `managed --check` (authenticated GMP task lookup **without scanning**). This uses a temporary, cleaned-up GMP config and ephemeral Docker helper; not a completely side-effect-free operation. The dedicated preflight is committed but **not yet syntax-checked or executed live**.

**Live Ansible results — 18 October 2026, approximately 16:27–16:29 BST:** Controller probes show TCP/22 connected to `PROXMOX`, `Proxmox-2` and `greenbone-01`. QNetd service is active. `pvecm status` returned `Quorate: Yes`, `Total votes: 3`, `Flags: Quorate Qdevice`. Proxmox reports both nodes online and all documented active guests on Proxmox-2 (`dns-01` CT101, `edge-01` CT103, `monitor-01` VM202 and `greenbone-01` VM203) running. The diagnostic and scan inspection playbooks both completed with `changed=0` and no unreachable/failed hosts.

**Vulnerability evidence and failure — 18 October 2026:** Live Ansible read `/var/lib/homelab-greenbone-scanning/managed.json`: collection `2026-10-16T14:28:39.034610+00:00` (15:28 BST); authenticated managed report `35dc10c3-aac0-46fa-b6ce-7c1b31440d38`; Critical=0, High=0, Medium=0, Low=0 actionable; Log=828; `actionable_count=0`; `accepted_risk_count=30`. This is **historical saved evidence**, not a fresh result. Its 30 accepted findings comprise 14 ICMP timestamp replies (CVE-1999-0524), 15 TCP timestamp disclosures and one missing HttpOnly cookie for the BirdNET-Go listener on `docker-01` TCP/8080. Some accepted TCP timestamp observations may predate the Ansible hardening; re-scan before claiming removal.

The 16 October 06:50 scan reported successful evidence publication at 08:43 with 0 actionable / 30 accepted (772 informational), and a later 16 October 17:14 scan was launched without a completion record in the last 25 unit journal lines. A restart-associated scan at **18 October 16:17:47 BST** failed at **16:18:01 BST**, `ExecMainStatus=1`: `Could not connect to socket /run/gvmd/gvmd.sock. Error was [Errno 111] Connection refused`. The scheduled timer remained configured for 19 October 02:00 BST. Container startup/readiness immediately after boot is a **plausible hypothesis**, not confirmed root cause. No new scan should start until current `gvmd`/PostgreSQL state is checked; do not interpret a failed scan as clean.

**Next diagnostic IaC:** `IaC/ansible/playbooks/greenbone-stack-health-readonly.yml` checks Docker service, all Compose containers, `gvmd` socket presence and bounded `gvmd`/`pg-gvm` logs without restarting anything. Created alongside this handover update; syntax and live execution **not yet verified**.

**Recovery update — 18 October 2026:** User reports `Proxmox-2` has returned. This is **user-reported**, not verified live. First check PVE node status/quorum/QDevice and Greenbone TCP/22 through the Ansible connectivity playbook. If VM203 is accessible, run the separate read-only Greenbone evidence playbook. Do not start/restart a scan, guest or service just on the basis of this report.

**IaC diagnostic created:** `IaC/ansible/playbooks/greenbone-connectivity-readonly.yml` was initially committed at `1220e052`, then revised at `1ff5ed8d` (and probe-result display corrected at `4329652183`) to run read-only probes on `admin-01` and gather `pvecm status` and cluster resource views from surviving `PROXMOX` rather than SSHing into offline `Proxmox-2`. This connectivity diagnostic **passed Ansible syntax check and live execution** on 18 October 2026, with both PVE nodes/quorum and Greenbone TCP/22 healthy.



**Controller Git merge resolved — 18 October 2026:** `admin-01` successfully reconciled local-only `f752562f` (qBittorrent and Kodi DLNA firewall IaC) with GitHub `origin/main`. The user created protective branch `backup/media-before-sync-20261018`, retained remote `docs/architecture/MEDIA-01.md` when resolving the only merge conflict, and committed merge `9dbbacc9`. User-supplied terminal output confirmed `git push origin main` succeeded (`36f9fd20..9dbbacc9`), `python3 scripts/validate-estate.py` passed (20 active assets), `git diff --cached --check` had no warnings, and `ansible-playbook -i inventory/hosts.yml playbooks/greenbone-scan-evidence-readonly.yml --syntax-check` passed. **The actual Greenbone read-only inspection has NOT yet run.** The untracked Kodi-related paths `IaC/ansible/metadata.tvshows.themoviedb.org.python` and `IaC/ansible/tvshows` remain intentionally untouched. No change to host configuration was made during the merge.

**New completed scan emailed 19 October 2026 at 03:07 UTC (04:07 BST):** `Greenbone scan report - Homelab - Managed Infrastructure - Authenticated Daily`; report `6e75928d-f251-426f-809c-991ffcbf6603`; 0 Critical, 0 High, **2 actionable Medium**, 0 Low, 789 informational, 15 accepted. Medium (4.8) `media-01` `192.168.2.195:8081/tcp`: `Cleartext Transmission of Sensitive Information via HTTP`, OID `1.3.6.1.4.1.25623.1.0.108440`. Medium (5.0) `docker-01` `192.168.2.220:443/tcp`: `Missing 'Secure' Cookie Attribute (HTTP)`, OID `1.3.6.1.4.1.25623.1.0.902661`. Neither lists a CVE. The email records 14 accepted ICMP timestamp findings and one accepted missing HttpOnly cookie finding at `192.168.2.220:443` (15 accepted total). The earlier 16 October report listed 30 accepted (including 15 TCP timestamp findings), so the discrepancy must be reconciled rather than treated as confirmed remediation. CPU >90% warning on `greenbone-01` fired at 01:20 UTC and resolved at 02:55 UTC on 19 October; correlation with scan workload is plausible, not proven. **Only email completion has been validated**: new saved managed evidence `managed.json`, transfer to `monitor-01`, dashboard freshness and report consistency must still be checked. The staged `ExecStartPre` boot guard remains unvalidated and undeployed; the fact a scan succeeded does not prove reboot-time readiness is fixed. Do not mark Greenbone validation closed. Next investigate two Medium findings through non-invasive, Ansible-first service identification; prefer `media-01` HTTP 8081 and `docker-01` TLS cookie 443, then IaC remediation and another completed scan.

### Next action — offline-validate bounded systemd boot-readiness gate (Git only)

The **18 October production GMP preflight passed** using the deployed direct Unix-socket runner: `ok=10 changed=0 failed=0`, GMP exit code 0, `CHECK=PASS`, managed task lookup 0.1s and legacy temp credential file absent. The old scan unit still displayed `failed` from its premature boot-time invocation. No vulnerability scan was launched.

**New source-stage (NOT deployed):** The persistent systemd timer can invoke the scan service before Greenbone's GMP listener becomes ready after a reboot. Git-managed `homelab-greenbone-managed-scan.service.j2` now specifies an `ExecStartPre=` readiness helper before the existing full managed scan command. `homelab-greenbone-wait-ready.py.j2` exclusively executes the deployed `homelab-greenbone-scan managed --check` under the existing nonblocking flock. It retries every 15 seconds for up to **1800 seconds (30 minutes)** with 40-second bounds on each probe; requires the explicit `CHECK=PASS mode=managed` marker, never prints raw stdout/stderr or credentials, and fails closed if auth/task lookup never succeeds. Systemd `TimeoutStartSec` now includes readiness budget + scan budget + 900-second margin. The timer calendar and `Persistent=true` are unchanged. No network or Docker helper is invoked by the new gating code except GMP calls from the tested direct runner.

A **scoped deployment playbook**, `IaC/ansible/playbooks/greenbone-managed-boot-guard.yml`, installs only the readiness helper and managed scan systemd unit through `tasks/managed_scan_boot_guard.yml`. It checks no scan is active, compiles the helper, reloads systemd only on a changed unit, verifies the installed `ExecStartPre`, and **never** starts or enables/disables the service/timer, resets its failed state, or launches a vulnerability scan. Full-role deployment is intentionally avoided because its broader flow still operates legacy Docker Compose GMP configuration and timer enablement gates. The full role main.yml now also knows how to install the helper before the unit when a separately approved full deployment is needed.

Offline validator `scripts/validate-greenbone-boot-readiness.py` checks strict Jinja rendering and Python syntax, verifies unit template command/timeout, simulates a failed first check then success, and checks **fail-closed** behavior when a subprocess returns zero without `CHECK=PASS`. **All these files are committed but the validator, Ansible syntax check and live deployment have NOT been run on admin-01.** The old failed service state remains; a future successful scheduled run or explicit reset would clear it, but no reset was requested.

**Next commands on admin-01 (no deployment):**
```bash
cd ~/projects/homelab-platform
git status -sb
git pull --ff-only || exit 1
python3 scripts/validate-greenbone-boot-readiness.py
python3 scripts/validate-estate.py
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-managed-boot-guard.yml --syntax-check
```
Only after these pass should the scoped playbook be considered for a separately reviewed live application. **Do not run the playbook live or launch a fresh scan as part of the syntax/offline test.** After safe gate deployment, confirm unit/timer state and run a newly completed authenticated scan and evidence publication check before closing Greenbone remediation.

**Do not launch another scan yet.** Inspect/review the current `IaC/ansible/roles/greenbone_scanning/templates/homelab-greenbone-managed-scan.service.j2` and associated managed timer/role tasks, then stage a fail-safe readiness design. Preserve unrelated untracked Kodi/Mayday files.

**Do not** start an additional scan while one is running. The runner is `/usr/local/sbin/homelab-greenbone-scan` and the evidence path is `/var/lib/homelab-greenbone-scanning/managed.json`. The managed scan systemd service is `homelab-greenbone-managed-scan.service`; the timer is `homelab-greenbone-managed-scan.timer`. Source: `IaC/ansible/roles/greenbone_scanning/`.

After seeing the live result:
1. Verify freshness, report ID, mode and completed scan status (a recent JSON file alone does not prove target coverage).
2. Compare actionable and accepted-risk findings with the documented 14 October baseline, by host and NVT/OID as available.
3. Explicitly verify the Zabbix cleartext HTTP finding, Raspberry Pi speculative-execution findings, and TCP timestamp findings.
4. Resolve any remaining actionable items; formally reconcile intentional risks without treating them as fixed.
5. Verify that evidence transfer to `monitor-01` and the Grafana accepted-risk display match the authoritative report.
6. Update this file **and** `CURRENT-STATE.md` / backlog when the scan is genuinely reviewed and closure justified.

### Known locations

- Estate inventory: `IaC/inventory/estate.json`
- Ansible inventory: `IaC/ansible/inventory/hosts.yml`
- Greenbone playbooks: `IaC/ansible/playbooks/greenbone-scanning.yml`, `greenbone-scan-runner.yml`, `greenbone-authenticated-scan.yml`, **`greenbone-scan-evidence-readonly.yml`**, **`greenbone-connectivity-readonly.yml`**
- Greenbone implementation: `IaC/ansible/roles/greenbone_scanning/`
- Greenbone host: `greenbone-01` = `192.168.2.57`
- Evidence publisher destination: `monitor-01` via the managed reporting evidence pipeline; compare timestamp and report ID
- Current architecture: `docs/architecture/CURRENT-STATE.md`
- Remaining work: `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md`

## Programme context after the Greenbone gate

The core 15-host Ansible Linux baseline was patched on **16 October 2026**: **15 reachable, 0 pending package updates, 0 required reboots**. Core monitoring and security integration are operational; seven trusted HTTPS renewal paths were dry-run tested. The backlog estimated about **70–80%** practical overall completion, excluding optional/deferred capabilities.

Pending after vulnerability review (unless reprioritised):
1. Raspberry Pi overclocking **feasibility only**, read-only inventory/thermal/power checks before any proposed change.
2. Encode already-live Proxmox GDS `gather_data_sampling=force` in IaC.
3. Review the Certbot Cloudflare Python dependency compatibility warning.
4. Project 7: controlled estate-wide Docker image lifecycle review (BirdNET canary already complete).
5. Project 6: QEMU restore proof, application-consistent Nextcloud/PostgreSQL recovery, independent backup copy.
6. Project 8: deliberate legacy cleanup review. Optional password manager/web analytics and deferred Tunnel are not automatic tasks.

### Latest verified deployment — media-01 ICMP timestamp filter

**19 October 2026 deployment evidence supplied by user:** After pulling the staged pilot, the scoped `greenbone-icmp-timestamp-media01-cutover.yml` completed with **greenbone-01 `ok=8 changed=0 unreachable=0 failed=0`** and **media-01 `ok=18 changed=2 unreachable=0 failed=0`**. The final post-change scanner check explicitly reported:
- `MEDIA01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`
- `MEDIA01_ICMP_ECHO=PASS`
- `HTTPS_443=PASS; LAN_HTTP_8081=BLOCKED; LOOPBACK_HTTP_8081=AVAILABLE`
- `No Greenbone scan or accepted-risk changes.`

The earlier independent pre-pilot probe was `ICMP_TIMESTAMP_REQUESTS_SENT=3`, `ICMP_TIMESTAMP_REPLIES_MATCHED=3`, `REPLY_CONFIRMED`. Together with the post-change normal ping and no replies, this gives convincing independent operational evidence that **only the ICMPv4 type-13 timestamp request was suppressed** on media-01 by the installed nftables rule. The source default `media_firewall_icmp_timestamp_drop_enabled: true` remains authoritative. Rollback retained at `playbooks/greenbone-icmp-timestamp-media01-rollback.yml` (not used). User was not asked to reboot or edit the kernel. The reported live result is not equivalent to a new Greenbone vulnerability-scan report; **do not remove the existing accepted-risk entry yet**.

**Next:** Investigate firewall ownership and network constraints on each of the **other 13 reported ICMP hosts**, one host at a time or safe cohorts, before proposing any shared rule. In particular, treat Proxmox-2, Docker hosts and LXCs differently and preserve management and storage networking. The BirdNET-Go csrf HttpOnly exception still needs deployed-version/functional review. Then perform one completed authenticated managed Greenbone rescan after checking scan activity and GMP readiness, verify both prior Mediums, the ICMP finding count, report timestamp/ID and evidence publication, and reconcile accepted-risk allowlist based on fresh results.

### Previous plan — authorised media-01 ICMP timestamp firewall pilot

**19 October explicit revised user decision:** After checking `media-01`'s Pi 5 kernel 6.18.50 and finding `TIMESTAMP_SYSCTL=NOT_PRESENT`, user reversed their earlier no-firewall instruction and explicitly said **"lets add a firewall then"**. Use **the existing managed media-01 nftables firewall**; do not install another firewall, patch the kernel, reboot or disturb qBittorrent/Kodi/SMB/Proxmox NFS.

**Git-staged, NOT yet applied or validated on admin-01:** 
- `roles/media_firewall/defaults/main.yml` sets `media_firewall_icmp_timestamp_drop_enabled: true` and retains HTTPS/443 allowed, direct LAN/8081 denied.
- `roles/media_firewall/templates/nftables.conf.j2` conditionally adds **only** `icmp type timestamp-request drop comment "Block ICMPv4 timestamp requests"` *after invalid drop but before established/related and broad IPv4 ICMP accept*. Ordinary ping, IPv6 ICMP, loopback, SSH, SMB, HTTPS, Kodi SSDP/DLNA, Proxmox TCP2049 NFS and exporter access remain as before.
- `roles/media_firewall/tasks/main.yml` validates the new boolean and confirms the active nftables rule (the existing role already validates `nft -c -f` before reloading).
- `playbooks/greenbone-icmp-timestamp-media01-cutover.yml` has three explicitly scoped plays: scanner-side **pre-change** normal ping and timestamp-reply baseline; media-01 service and HTTPS+loopback+8081 safety gates then existing media_firewall role; scanner-side **post-change** normal ping and no matching timestamp replies. Verify all three plays run; **do not use `--limit media-01` alone**.
- `playbooks/greenbone-icmp-timestamp-media01-rollback.yml` explicitly sets `media_firewall_icmp_timestamp_drop_enabled: false`, retaining qBittorrent HTTPS-only policy and verifying services. **Rollback is manual**; the role does not silently revert in a failed post-probe. Do not use qBittorrent's HTTP rollback for this.
- `scripts/validate-media01-icmp-timestamp-firewall.py` validates both rendered rule modes/order, preserved services and playbook scope; `scripts/validate-qbittorrent-lan-firewall.py` and `scripts/validate-qbittorrent-http-cutover.py` updated with new required Jinja boolean. The existing packet self-test is unchanged.

**Next admin-01 commands (source-validation gates followed by explicitly approved scoped live cutover):**

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-media01-icmp-timestamp-firewall.py &&
python3 scripts/validate-icmp-timestamp-probe.py &&
python3 scripts/validate-qbittorrent-lan-firewall.py &&
python3 scripts/validate-qbittorrent-http-cutover.py &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-media01-cutover.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-media01-rollback.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-media01-cutover.yml \
  --limit 'media-01:greenbone-01' --forks 1
```

**Expected proof** after active nftables reload: preflight timestamp replies confirmed; postflight `MEDIA01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, `MEDIA01_ICMP_ECHO=PASS`, controller-trusted qBittorrent HTTPS/443 and loopback backend available, LAN HTTP/8081 blocked. Source validation and Ansible syntax check must pass first. Failure in either scanner postflight check means **don't claim remediation**; if networking disrupted run explicit scoped rollback:

```bash
cd ~/projects/homelab-platform/IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-media01-rollback.yml \
  --limit 'media-01:greenbone-01' --forks 1
```

**As of this handover update, only Git files changed. No live nftables, Greenbone task, risk allowlist, kernel, services or scans changed by the commit.** On success, user supplies Ansible output and Git docs are updated with live evidence; then refresh completed authenticated Greenbone scan and reconcile accepted-risk entries, not before.

### Kernel ICMP timestamp sysctl check complete — 19 October 2026

**User's new read-only Ansible output:** On media-01, `/proc/sys/net/ipv4/icmp_timestamp_ignore_all` does **not** exist: `TIMESTAMP_SYSCTL=NOT_PRESENT`. The command was read-only despite the Ansible ad-hoc `CHANGED` indicator. Host runs `6.18.50+rpt-rpi-2712`; existing `icmp_echo_ignore_all=0` and `icmp_echo_ignore_broadcasts=1` do not suppress the independently confirmed **unicast** timestamp replies (3 of 3). Linux's current kernel sysctl documentation does not include `icmp_timestamp_ignore_all`. The kernel's ICMP timestamp reply handler persists upstream. A 2024 proposal to introduce this exact sysctl did not establish a standard available control (see mailing-list review, including objection questioning the impact).

**Decision and operational boundary:** There is **no supported kernel sysctl exposed by this installed build** to stop only unicast ICMP timestamp replies. The historical 15-host TCP timestamp sysctl role does not apply. The user specifically declined firewall remediation. No kernel patch, package change, reboot, sysctl write, firewall change or acceptance policy modification was performed. The practical options are (a) continue the documented low-impact accepted risk on media-01; (b) reconsider narrow, Git-managed firewall mitigation **only after explicit renewed user approval**; or (c) explore a vendor/custom patched kernel, which introduces substantial maintenance/reboot risk and is not justified without evidence of material exposure. The pending fresh authenticated Greenbone scan for the two former actionable Mediums is separate.

### Live kernel evidence and upstream sysctl investigation — 19 October 2026

**Read-only Ansible output supplied by user:** `media-01` (Raspberry Pi 5, Debian 13) runs `6.18.50+rpt-rpi-2712`, package `1:6.18.50-1+rpt1`, ARM64; installed `linux-image-rpi-2712` metapackage and `linux-image-6.18.50+rpt-rpi-2712` both match that version. Earlier 6.18.34 and 6.18.39 image packages remain installed. Kernel built on 2026-09-11. `net.ipv4.icmp_echo_ignore_all=0`; `net.ipv4.icmp_echo_ignore_broadcasts=1`. That latter setting suppresses broadcast/multicast echo and timestamp requests, **not unicast type-13 requests**; independently verified 3/3 reply test remains valid. Ansible's ad-hoc shell output marked CHANGED by default, but the commands were strictly read-only (uname/cat/dpkg-query/sysctl queries); no kernel changed or rebooted.

**Research:** Linux kernel official sysctl documentation does not list a standard unicast ICMP timestamp disable switch; mainline `net/ipv4/icmp.c` contains `icmp_timestamp()` response handler. A May 2024 proposal `[PATCH net-next v2] icmp: Add icmp_timestamp_ignore_all to control ICMP_TIMESTAMP` would introduce `net.ipv4.icmp_timestamp_ignore_all`, but it encountered networking maintainer objections/questions and does not appear in current standard kernel sysctl documentation. Do not assume Raspberry Pi downstream includes it without checking `/proc/sys/net/ipv4/icmp_timestamp_ignore_all` **read-only**. A simple sysctl rate limit is not equivalent to suppressing replies; custom kernel rebuild/patch is more disruptive and not approved. User explicitly requested **no firewall modification**.

**Next one-time read-only Ansible command from admin-01:**

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible media-01 -i inventory/hosts.yml -b \
  -m ansible.builtin.shell \
  -a 'if test -r /proc/sys/net/ipv4/icmp_timestamp_ignore_all; then printf "TIMESTAMP_SYSCTL=AVAILABLE value="; cat /proc/sys/net/ipv4/icmp_timestamp_ignore_all; else echo "TIMESTAMP_SYSCTL=NOT_PRESENT"; fi'
```

If present, decide how to stage a deliberately scoped persistent sysctl in Ansible and validate on media-01 without reboot, then repeat the scanner-side ICMP test **only with user approval**. If absent, do not attempt to write an unknown sysctl or perform a kernel upgrade solely for a low-impact accepted finding; discuss risk/benefit of a custom kernel modification versus continued acceptance. Existing risk dispositions remain unchanged.

### Follow-up decision — investigate kernel options before final ICMP disposition

**19 October 2026:** User challenged the recommendation to retain the ICMP accepted risk without trying any kernel-level solution ("but we havent changed the kernel"). Acknowledge that the 3/3 positive ICMP timestamp network probe **only proved exposure**; no kernel/sysctl change was made or tested. Prior `net.ipv4.tcp_timestamps=0` hardening applies only to TCP. Linux upstream `net/ipv4/icmp.c` implements type-13 request/type-14 reply handling, and no supported dedicated sysctl to selectively disable unicast ICMP timestamp responses has been established. Kernel upgrade alone cannot be assumed to eliminate this handler. User still does **not** want a firewall change. **Before making the final accepted-risk decision**, identify live media-01 kernel version, installed image packages, and available vendor support via read-only Ansible, then assess whether any safe supported kernel-level control exists. Do not propose custom kernel rebuild, reboot, packet filtering, or risk-status changes without discussing their tradeoffs and obtaining approval. Previous note calling retention the final answer was premature.

### Latest verified result — media-01 ICMP timestamp replies reproducible

**19 October 2026 live Ansible evidence (user-provided output):** User pulled commit `5ab305da`, ran `scripts/validate-icmp-timestamp-probe.py` (RFC 792 packet/matching reply self-test PASS) and `scripts/validate-estate.py` (20 active, 0 planned, 5 retired-identity guards PASS), plus syntax check and scoped `greenbone-icmp-timestamp-media01-readonly.yml --limit greenbone-01`. Play recap `greenbone-01 ok=5 changed=0 unreachable=0 failed=0 skipped=0`. `ICMP_ECHO_BASELINE=PASS`; 3 ICMPv4 type-13 timestamp requests sent from greenbone-01 (192.168.2.57) to media-01 (192.168.2.195), **3 correctly matched ICMPv4 type-14 replies received**; `ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED` and `INTERPRETATION=TIMESTAMP_REPLY_CONFIRMED`. Confirms the prior Greenbone ICMP Timestamp Reply finding for media-01 is still genuinely reproducible; it has **not** been remediated. Neither firewalls, sysctls, services, the Greenbone task nor accepted-risk policy were modified. User explicitly rejected an ICMP firewall fix; keep media-01's low-impact disclosure **accepted** under the existing reviewed allowlist. **This is not a new completed Greenbone scan.**

**Next action:** No more firewall changes for ICMP. Decide whether to extend the read-only external probe to other 13 reported hosts (only if worthwhile) or turn to the separate BirdNET-Go `csrf`/HttpOnly exception and verify exact deployed application behaviour. A fresh completed authenticated managed Greenbone scan is still necessary for the two previously actionable Medium remediation claims and overall scan freshness; do not remove the accepted entries without new evidence and decision.

### Prior plan — media-01 ICMP timestamp external verification

**19 October live evidence already collected:** Read-only 14-host audit limited to media-01 completed `ok=2 changed=0 failed=0`, finding Debian 13, active nftables, a broad IPv4 ICMP accept and no timestamp-specific rules. The user rejected a firewall change, and **none was made**. Previous TCP timestamp sysctl hardening (16 October) addresses another protocol.

**New Git-only, not yet run on either host:** `IaC/ansible/playbooks/greenbone-icmp-timestamp-media01-readonly.yml` runs **only on greenbone-01 (192.168.2.57)** and probes only `media-01 (192.168.2.195)`. It asserts both inventory identities, runs the RFC 792 stdlib ICMP packet/reply matching self-test, attempts one ordinary IPv4 ping for context, then sends three ICMP type-13 timestamp requests and listens for matching type-14 replies (valid IPv4 source, ICMP checksum, identifier, sequence). Python source is `IaC/ansible/playbooks/files/icmp-timestamp-probe.py` and offline regression test is `scripts/validate-icmp-timestamp-probe.py`. Source file is passed via Ansible `command` with `python3 -c`, so it is not persistently installed on greenbone-01. This is a bounded active network diagnostic; it performs **no configuration change and does not run a Greenbone scan**. Only target, request/reply counts and result markers are printed (not timestamp payloads).

**Next from admin-01 (no `exit 1`, stop on first failure):**

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-icmp-timestamp-probe.py &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-media01-readonly.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-icmp-timestamp-media01-readonly.yml --limit greenbone-01
```

Interpret `ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED` as proof media-01 still answers timestamp requests. `NO_REPLY_OBSERVED` is **not proof of remediation**: check ping baseline, network/permission errors, packet loss, and preferably scanner evidence. No accepted-risk entries or firewall configuration should be altered without a new decision. After reporting the results, choose next read-only diagnosis or retain documented low-risk acceptance.

### Latest decision — no ICMP firewall changes

19 October 2026: User declined the proposed media-01 ICMP timestamp firewall pilot. No pilot was committed or deployed. Earlier read-only audit succeeded on media-01 (ok=2 changed=0 failed=0): active nftables, broad IPv4 ICMP allow, and no timestamp-specific rules. Previous TCP timestamp sysctl hardening does not cover ICMP timestamps. Linux kernel documentation provides no dedicated sysctl to disable unicast ICMP timestamp replies selectively. Preserve existing risk acceptances and working network configuration. Next review scanner evidence/read-only external ICMP behaviour rather than modifying nftables; do not propose an ICMP firewall change without renewed user approval.

### Next action — assess 15 accepted Greenbone findings before a new scan

**User reprioritised on 19 October:** The last completed scan's accepted findings were 14 ICMP Timestamp Reply Information Disclosure (NVT 1.3.6.1.4.1.25623.1.0.103190) and one BirdNET-Go non-HttpOnly csrf cookie (NVT 1.3.6.1.4.1.25623.1.0.105925). The larger Git risk allowlist also retains older TCP timestamp items, which are not part of those 15. No acceptances have been removed and no new scan started.

**Review:** ICMP timestamp-request type 13 can generally be selectively filtered via the existing controlled firewall without disabling ordinary ping/ICMPv6. Do not perform a blanket firewall rollout on Proxmox-2, Docker or LXC hosts: identify owner and preserve services. media-01 is a potential pilot because its Git-managed nftables policy currently broadly accepts IPv4 ICMP. The BirdNET csrf cookie intentionally omits HttpOnly in upstream, and is different from a session cookie; do not force HttpOnly until the running application's state-changing actions are verified. Details in docs/security/GREENBONE-ACCEPTED-RISKS-2026-10-19.md.

**Git-only preparation:** Created IaC/ansible/playbooks/greenbone-accepted-icmp-firewall-readonly.yml targeting exactly the 14 affected hosts to report operating system, firewall service indicators and counts of existing ICMP timestamp policy references. No rulesets/secrets printed and no service or firewall changes. This playbook has **not yet run on admin-01**.

**Next read-only commands:**

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-accepted-icmp-firewall-readonly.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-accepted-icmp-firewall-readonly.yml
```

Review results before building a targeted media-01 pilot with rollback, and do not change accepted-risk declarations until a fresh completed Greenbone scan proves each affected host's finding is absent. Earlier plans for Greenbone evidence and GMP preflight remain pending and are not superseded as a required safety gate before another scan.

### Earlier pending plan — Greenbone evidence and GMP preflight before rescan

**19 October final qBittorrent cutover executed and verified:** User's targeted `ansible-playbook -i inventory/hosts.yml playbooks/qbittorrent-https-cutover.yml --limit media-01` finished `ok=19 changed=2 unreachable=0 failed=0 skipped=0 rescued=0`, reporting:
- `QBITTORRENT_LAN_HTTPS=PASS HTTP_STATUS=200`
- `QBITTORRENT_DIRECT_LAN_HTTP_8081=BLOCKED`
- `QBITTORRENT_LOOPBACK_HTTP_8081=AVAILABLE`
- qBittorrent, Kodi, SMB and NFS were not restarted.

The active media nftables configuration was updated and verified. Existing Proxmox NFS/Kodi/SMB/SSH/monitoring allowances are protected by the tested media-firewall role. `roles/media_firewall/defaults/main.yml` now defaults to `media_firewall_qbittorrent_http_lan_enabled: false` and HTTPS true; explicit emergency rollback is `playbooks/qbittorrent-https-http-rollback.yml`, **not executed**. The user previously confirmed successful HTTPS WebUI login and password recovery. No new Greenbone scan or managed evidence publication has been observed since cutover.

**Next: check Greenbone's existing service state/evidence and GMP readiness safely before initiating any scan.** Both existing playbooks are read-only, do not restart Greenbone or start a scan, and are scoped to `greenbone-01`. Before running, pull the latest documentation and keep other work intact:

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
python3 scripts/validate-estate.py &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-scan-evidence-readonly.yml --limit greenbone-01 &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/greenbone-gmp-preflight.yml --limit greenbone-01
```

Read back task/service state, last evidence timestamp/report ID, whether any managed scan is currently active, and the GMP `CHECK=PASS` marker. Do **not** launch a new scan if one is active or GMP preflight fails. The Greenbone boot-readiness unit gate staged elsewhere in Git has not been deployed; do not assume systemd scans are guarded at reboot. Once safe read-only results are available, use a narrowly-scoped Git-managed trigger to initiate **one** authenticated managed scan without touching legacy Docker Compose/role-wide deployment. Validate the resulting report ID/completion time, absence of both former Mediums, preservation of 15 accepted-risk dispositions (or reconcile changes), and machine-readable `managed.json` publication. Only then review the accepted 14 ICMP timestamps and BirdNET CSRF `HttpOnly` exception for whether to continue acceptance or remediate. This is a follow-on from the original Greenbone remediation task, not confirmation that it is closed.

### Previous step — qBittorrent WebUI password recovery

**19 October live password diagnosis RESULT:** User executed `qbittorrent-webui-password-preflight.yml --limit media-01` successfully: `ok=6 changed=0 failed=0`. Non-secret output: `STORED_WEBUI_PASSWORD=no`, `CURRENT_SESSION_TEMP_PASSWORD_LOGGED=yes`, `QBITTORRENT_SERVICE=active`. The session's temporary admin password can be recovered from the current systemd invocation journal via an **ad-hoc read-only Ansible shell** (authorized by AGENTS.md for one-time read-only queries), displayed **only on the user's terminal**. Do not paste or share the temporary password, and do not commit it, record it in playbook output shared with ChatGPT, or restart qBittorrent. Use `admin` + temporary password at trusted LAN HTTPS, then immediately set a permanent strong password in Tools → Options → Web UI → Authentication. If login succeeds, verify functionality before separately closing direct LAN HTTP/8081. The existing Greenbone Medium remains open until final cutover and rescan.

**19 October user update:** HTTPS works in a real LAN browser at `https://qbittorrent.home.jrwroberts.co.uk`, but WebUI password needs reset or initial setup; authenticated browser login has not yet been confirmed. qBittorrent-nox version 5.1.0-2 was installed on media-01 on 17 October, running under service user `qbittorrent`, configuration `/var/lib/qbittorrent/.config/qBittorrent/qBittorrent.conf`. Its initial temporary password may already be present in the *current service invocation* journal; prefer recovering that without restarting active downloads.

**New read-only, Git-only preflight:** `IaC/ansible/playbooks/qbittorrent-webui-password-preflight.yml` reports whether a permanent `WebUI\\Password_PBKDF2` / `Password_ha1` entry exists and whether the **current invocation** journal includes a temporary WebUI password marker. It prints neither the temporary password nor hashes and does not restart, stop or change any service/credential/firewall. Not yet run/syntax-checked by user.

```bash
cd ~/projects/homelab-platform &&
git pull --ff-only &&
cd IaC/ansible &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/qbittorrent-webui-password-preflight.yml --syntax-check &&
ansible-playbook -i inventory/hosts.yml \
  playbooks/qbittorrent-webui-password-preflight.yml --limit media-01
```

If `STORED_WEBUI_PASSWORD=no` and `CURRENT_SESSION_TEMP_PASSWORD_LOGGED=yes`, user can retrieve the temporary password **locally** through read-only Ansible without copying it into ChatGPT or Git; log into HTTPS as `admin` then set a strong permanent password in WebUI settings (Tools > Options > Web UI > Authentication). If already logged in with valid credentials, change via settings directly. If password stored and unknown, stage a separate safe, scoped Git-managed reset, with controlled service restart, secret-safe backup and output; never edit live preferences while qBittorrent is running. **Do not remove LAN HTTP/8081 yet; recheck HTTPS authenticated login first.** After that, separately plan final firewall cutover and Greenbone rescan, followed by accepted findings.

### Previous step — verify qBittorrent HTTPS browser login before HTTP/8081 cutover

**LAN HTTPS firewall applied successfully 19 October 2026:** User ran `qbittorrent-https-lan-stage.yml --limit media-01` from admin-01 after pull. Play recap `media-01 ok=16 changed=2 unreachable=0 failed=0`. The managed nftables template changed and the `media_firewall : Reload nftables` handler ran; Nginx and qBittorrent were confirmed active; firewall/SSH/Kodi/SMB/NFS and Proxmox backup-client assertions passed. Controller-side tests both passed: `QBITTORRENT_LAN_HTTPS=PASS HTTP_STATUS=200` and `QBITTORRENT_LEGACY_HTTP=AVAILABLE HTTP_STATUS=200`. TLS is trusted from admin-01 and the existing HTTP fallback works. **No qBittorrent, Kodi, SMB or NFS restart was requested.**

**Do not close LAN HTTP 8081 yet.** An unauthenticated HTTPS HTTP 200 response does not establish successful login, session/cookie handling, or working WebUI controls. User's next action is to open `https://qbittorrent.home.jrwroberts.co.uk` in a real browser on the LAN; sign in and test WebUI function/download status. Confirm that the site shows a trusted certificate and remains usable after reload. If login fails, keep the existing 8081 rollback and investigate the reverse-proxy/header settings through read-only Ansible without weakening qBittorrent CSRF or host-header validation.

Once **explicit user confirmation of successful HTTPS browser login** arrives, stage and validate a separate Git-managed scoped media firewall cutover with `media_firewall_qbittorrent_http_lan_enabled: false`, preserving HTTPS/443 and all other service rules. The loopback Nginx→qBittorrent backend must stay reachable. Verify from admin-01 that HTTPS remains working and direct HTTP/8081 is blocked; keep rollback. Do not claim Greenbone remediation until a fresh completed authenticated scan shows both earlier Mediums cleared and machine-readable evidence/dashboard freshness is validated. Then evaluate the 14 accepted ICMP timestamp findings and the remaining BirdNET csrf HttpOnly classification. The separate Greenbone boot-readiness gate is still Git-only.

### Previous plan — trusted qBittorrent HTTPS staging; retain HTTP rollback

**19 October live evidence:** `birdnet-secure-cookie.yml` was executed on `docker-01`; Nginx syntax passed, both `csrf` cookie checks returned `SECURE_CSRF_COOKIE=PASS`, play recap `ok=7 changed=0 failed=0`, and the Nginx reload was skipped because desired config was already installed. BirdNET-Go did not restart. `qbittorrent-https-readiness-readonly.yml` on `media-01` returned `ok=3 changed=0 failed=0`, qBittorrent package `5.1.0-2`, qBittorrent active; Nginx/Certbot absent, no port 443 listener, no certificate, and both Pi-hole servers `192.168.2.50` and `.51` returned **no A record** for proposed `qbittorrent.home.jrwroberts.co.uk`.

**Git-staged qBittorrent HTTPS plan (not deployed):** `dns_resolver/defaults/main.yml` adds `qbittorrent.home.jrwroberts.co.uk` to the existing `media-01` local hosts entry (`192.168.2.195`) on both managed Pi-hole resolvers. Existing narrowly-scoped `dns-local-records.yml` deploys DNS only, not DNS package/service reinstall. New `qbittorrent_https` role installs Nginx with TLS termination for that name and preserves qBittorrent's backend `127.0.0.1:8081`. The proxy follows the qBittorrent project Nginx guide (`Host $proxy_host`, Forwarded-* headers), keeps CSRF/header protection, applies Secure to proxied session cookies, has no HTTP redirect/port 80 proxy listener, and checks the certificate and HTTPS endpoint. New `qbittorrent-https-stage.yml` first requires both resolvers to return the expected A record and confirms protected controller Cloudflare DNS-01 credentials and local HTTP backend. Then existing `homelab_certificate` role obtains a trusted DNS-01 Let's Encrypt certificate; the HTTPS role configures Nginx. This **does not change the LAN nftables 8081 firewall rule**, so the old WebUI remains reachable during initial rollout; port 443 is still default-denied by media-01 nftables until a **separately planned and verified final cutover**. No qBittorrent, Kodi, SMB or NFS restart is needed for the stage.

Offline validator `scripts/validate-qbittorrent-https.py` checks Jinja rendering, Nginx proxy/header policy, Git-managed DNS alias and non-cutover contracts. **Not yet run on admin-01; neither DNS nor HTTPS stage is deployed.**

**First run offline syntax/source tests only:**
```bash
cd ~/projects/homelab-platform
git status -sb
git pull --ff-only || exit 1
python3 scripts/validate-qbittorrent-https.py
python3 scripts/validate-estate.py
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/dns-local-records.yml --syntax-check
ansible-playbook -i inventory/hosts.yml playbooks/qbittorrent-https-stage.yml --syntax-check
```

If validation passes, separately deploy managed Pi-hole DNS records on **both** `dns-01,dns-02` first, then run the certificate/HTTPS staging playbook on `media-01`; inspect each result before the next phase. **Do not remove firewall access to port 8081 yet.** After validating HTTPS externally/browser login and preserving rollback, create a distinct firewall-only cutover replacing LAN `8081` with LAN `443` without altering Kodi/SMB/NFS paths; verify from the LAN before any repeat Greenbone scan. Then review the 14 accepted ICMP timestamp results and the BirdNET CSRF `HttpOnly` exception against live application behavior. Greenbone `ExecStartPre` boot guard and evidence-publication validation remain separate.

### Previous step — read-only diagnosis of two actionable Medium findings

The 19 October completed authenticated Greenbone email (report `6e75928d-f251-426f-809c-991ffcbf6603`) shows two actionable Medium findings: `media-01` `192.168.2.195:8081` HTTP cleartext sensitive information (qBittorrent Web UI, as identified by authoritative `docs/architecture/MEDIA-01.md` and `IaC/ansible/roles/qbittorrent`) and `docker-01` `192.168.2.220:443` missing Secure cookie flag (BirdNET-Go Nginx reverse proxy from `birdnet_go` role). The 15 remaining accepted entries are 14 ICMP timestamp replies and one missing HttpOnly cookie on `docker-01:443`; review them only after these two Medium findings are resolved.

**Git-only diagnostic, not run on admin-01:** `IaC/ansible/playbooks/greenbone-two-medium-readonly.yml` targets both specific hosts, collects qBittorrent listener, service/certificate and safe WebUI configuration keys, Nginx version/site cookie directives and live HTTPS cookie **names/flags only** for BirdNET-Go (no cookie values, HTTP body or credentials). No service/timer/scan change. Run source validation first, then execute:

```bash
cd ~/projects/homelab-platform
git pull --ff-only || exit 1
python3 scripts/validate-estate.py
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/greenbone-two-medium-readonly.yml --syntax-check && \
ansible-playbook -i inventory/hosts.yml playbooks/greenbone-two-medium-readonly.yml --limit media-01,docker-01
```

After this evidence, stage targeted, reversible IaC for an HTTPS qBittorrent Web UI and Nginx Secure cookie behavior. Do not yet close any finding, change a firewall rule, restart Kodi/BirdNET or mark accepted risks fixed. Preserve the separate staged Greenbone boot-readiness gate (`greenbone-managed-boot-guard.yml`), which is still not deployed or validated.

### Actionable Greenbone Med remediation — 19 October 2026

**Live read-only Ansible diagnostic completed** from `admin-01` against `media-01` and `docker-01`: `greenbone-two-medium-readonly.yml` syntax PASS, `media-01 ok=3 changed=0 failed=0`, `docker-01 ok=3 changed=0 failed=0`. On media-01, `qbittorrent-nox` owns `*:8081`, `qbittorrent.service=active`, `nginx=inactive`, no `/etc/letsencrypt/live` directory, and the single qBittorrent.conf contains `WebUI\\Port=8081`. On docker-01, `nginx.service=active`, version 1.26.3, syntax PASS, proxy is local BirdNET-Go `127.0.0.1:8080`. HTTPS `GET /` returned 302 and `GET /login` 200; both emitted exactly one `csrf` cookie with `Secure=False`, `HttpOnly=False`, `SameSite=True`. The two actionable Medium scanner findings are therefore concretely explained. The remaining accepted BirdNET missing HttpOnly should be reviewed only after checking whether JavaScript requires CSRF cookie access; do not indiscriminately set HttpOnly.

**IaC changes STAGED on GitHub, NOT deployed:** `birdnet_go/templates/nginx-birdnet.conf.j2` adds `proxy_cookie_flags csrf secure;` under the existing HTTPS location. New tightly scoped `birdnet_go/tasks/secure_cookie.yml` and `playbooks/birdnet-secure-cookie.yml` apply only that Nginx config, run `nginx -t`, reload Nginx only on change (do not restart BirdNET-Go), then verify `csrf; Secure` on both `/` and `/login`, outputting no cookie values. A separate **read-only** `playbooks/qbittorrent-https-readiness-readonly.yml` checks whether media-01 has a port 443 listener, existing Nginx/Certbot packages or qBittorrent HTTPS certificate, and whether both managed Pi-hole resolvers know the proposed `qbittorrent.home.jrwroberts.co.uk` name. This is preparation only; no new DNS alias/certificate was claimed or created. For qBittorrent, plan a trusted Certbot DNS-01 certificate, local Pi-hole record on BOTH resolvers, Nginx HTTPS proxy, then remove *external* plaintext WebUI access only **after** HTTPS/login verification; preserve downloads, Kodi, SMB/NFS and a rollback path. Prefer binding qBittorrent WebUI to loopback if supported and validated; do not change live listener prematurely.

**Next execution on admin-01:**
```bash
cd ~/projects/homelab-platform
git pull --ff-only || exit 1
python3 scripts/validate-estate.py
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/birdnet-secure-cookie.yml --syntax-check
ansible-playbook -i inventory/hosts.yml playbooks/qbittorrent-https-readiness-readonly.yml --syntax-check
# First check preflight; then apply only the BirdNET Nginx cookie change
ansible-playbook -i inventory/hosts.yml playbooks/birdnet-secure-cookie.yml --limit docker-01
ansible-playbook -i inventory/hosts.yml playbooks/qbittorrent-https-readiness-readonly.yml --limit media-01
```

Do not regard BirdNET Medium as remediated until Nginx reload/live cookie flag verification succeeds and a fresh scan confirms it. qBittorrent TLS and DNS remain OPEN. Keep the separate Greenbone boot-readiness guard Git-only and not deployed. After both Medium fixes and a fresh scan, review the 15 accepted items individually (14 ICMP timestamps, one BirdNET HttpOnly cookie), and reconcile the earlier missing TCP timestamp items.

**19 October 2026 offline test failure and correction (Git-only):** User pulled latest code then ran the chained qBittorrent LAN firewall checks; the offline validator stopped at Jinja2 rendering with `TemplateRuntimeError: No filter named 'bool' found`. This is a standalone Jinja2/Ansible filter mismatch in `scripts/validate-qbittorrent-lan-firewall.py`, not a problem in media-01 or nftables. The validator now registers a `bool` filter for its typed boolean fixtures (commit `06aa89b8`). The user's `&&` chain stopped before estate validation and Ansible syntax-check. **No firewall changes were made, no 443 allowance was deployed and 8081 remains open.** Next: pull and rerun all three checks; if they pass, review before separately applying the scoped LAN 443+8081 playbook. Do not use `|| exit 1` in an interactive SSH session.

## Latest session log

- **2026-10-19:** User confirmed HTTPS WebUI login/password resolved and explicitly approved closure of direct LAN 8081. Git-staged new HTTPS-only `media_firewall` default, scoped cutover and rollback playbooks, and two offline validators. **No cutover applied, source validation on admin-01 pending.** Next: run validators, estate and playbook syntax tests, then scoped cutover; verify controller HTTPS/local backend works and LAN 8081 blocks before a new Greenbone scan.

- **2026-10-19:** Password preflight succeeded on media-01: `ok=6 changed=0 failed=0`, permanent password absent, temporary password marker present in current systemd invocation. Recovery possible without service restart; user must see credential only locally, set a permanent WebUI password and confirm login before firewall cutover.


- **2026-10-19:** Browser HTTPS confirmed usable by user; administrator password not yet reset, authenticated login unconfirmed. Scoped Git-only read-only qBittorrent WebUI password preflight staged (current-session temporary log flag, password key presence; no secrets printed or service changes). Run syntax and playbook, then recover the temporary credential if available or plan reset if permanent password is unknown.

| Date | Change / observation | Evidence and validation | Next step |
| --- | --- | --- |
| 2026-10-19 | Five-LXC phase of seven-host mitigation staged in GitHub, not deployed. | Added allowlisted host-specific tag and backup helper (`icmp_timestamp_lxc.py`), serial fail-stop `greenbone-icmp-lxc5-cutover.yml`, exact-rule `greenbone-icmp-lxc5-rollback.yml`, and per-host isolated `scripts/validate-icmp-lxc5.py`. Includes mail-relay-01, dns-02, dns-01, zabbix-01, komodo-01; does not change Docker-owned ip/ip6 tables. Not yet syntax-checked or tested on admin-01; no live change. | Pull and run offline validator/Ansible syntax, resolve failures before deploying to LXC phase; admin-01 and Proxmox-2 require separate safer implementation and recovery gates. Keep risk acceptance records; 7/14 confirmed mitigated. |
| 2026-10-19 | Consolidated remaining-seven read-only preflight PASS across all 7 hosts. | Ansible play recap Proxmox-2, admin-01, dns-01, dns-02, komodo-01, mail-relay-01, zabbix-01 each `ok=10 changed=0 failed=0 skipped=1 unreachable=0`. Preflight includes native LXC firewall baseline checks and scanner-to-host ICMP timestamp probes. | Build reusable shared cutover for four matching native LXCs, staged with simulation and per-host rollback. Separate Docker/controller/Proxmox host-specific deployment and recovery. Operational count remains 7/14. |
| 2026-10-19 | Remaining seven firewall discovery classified and consolidated serial read-only preflight staged. | dns-01/dns-02/mail-relay-01/zabbix-01 same 60dac93f stock active nft LXC baseline as edge-01; komodo-01 native inet input empty and separate Docker-owned ip/ip6 tables; admin-01 no nft tables and nftables disabled; Proxmox-2 no nft tables in current snapshot but Proxmox firewall daemons enabled. New `greenbone-icmp-remaining7-preflight.yml` inventories seven, checks drift and independent scanner evidence, no mutation. Not yet run. | Pull and syntax-check preflight, then run read-only serial seven-host sweep. Build separate host-class cutovers and rollback with explicit admin/hypervisor gates. edge-01 verified idempotent; 7/14 operational mitigations. |
| 2026-10-19 | edge-01 repeat cutover proved idempotent, live firewall rule and on-disk persistence confirmed. | Ansible `ok=14 changed=0 failed=0`; `/etc/nftables.conf` line 8 has tagged type-13 DROP rule; nft live inet filter input handle 5 with `counter packets 9 bytes 360 drop`, nftables active, original 243-byte backup preserved. Greenbone-01 still observes no timestamp replies; SSH and echo PASS. | Proceed to remaining 7 hosts with separate ownership checks: mail-relay-01, dns-01/02, zabbix-01, then komodo-01, admin-01 and Proxmox-2. Reboot persistence and full authenticated Greenbone rescan remain due. |
| 2026-10-19 | edge-01 (192.168.2.56, CT103) ICMP timestamp mitigation operationally deployed and independent scanner probe PASS; seventh of 14 hosts. | Single-host Ansible edge cutover `ok=14 changed=2 failed=0`; after live nftables tagged type-13 drop plus persistent `/etc/nftables.conf` entry, greenbone-01 ordinary ping PASS, timestamp matches 0 and `NO_REPLY_OBSERVED`, SSH PASS. No nftables reload/reboot; backup and rollback playbook retained. | Repeat cutover for idempotency (`changed=0`), inspect rule/config/backup, defer reboot persistence proof until maintenance, rerun full authenticated Greenbone scan before formal closure. Remaining 7/14. |
| 2026-10-19 | edge-01 pilot source review strengthened before live deployment. | First controller offline validator, estate validation and both Ansible syntax checks PASS; untracked __pycache__ from initial py_compile validator (later replaced with in-memory compile). Git helper matching updated to recognise canonical nft display variants and reject ambiguous tagged rules; new mocked apply/reapply/rollback/drift test added but NOT yet executed on controller. | Pull Git changes and execute upgraded offline simulator and Ansible syntax; review failures before any edge-01 cutover. Operational mitigations remain 6/14. |
| 2026-10-19 | edge-01 native nftables cutover/rollback source and offline validator staged in Git only. | Following edge-01 rc=0 `nft -c` rule compatibility and 3/3 timestamp reply baseline, added single-host `greenbone-icmp-timestamp-edge01-cutover.yml`, dedicated exact-rule helper, `greenbone-icmp-timestamp-edge01-rollback.yml` and offline validator. No controller execution, live deployment or reboot proof yet; helper fails closed on unexpected INPUT state, writes exact persistent config insertion and applies one live tagged rule without reloading nftables. | Pull to admin-01 and run offline validator, YAML/Ansible syntax and source review. Do NOT run live cutover until validation and explicit review. Remediation remains 6/14. |
| 2026-10-19 | edge-01 native nftables boot/reload ownership verified read-only. | nftables enabled/active, `ExecStart/ExecReload=nft -f /etc/nftables.conf`, `ExecStop=nft flush ruleset`, `WantedBy=sysinit.target`, `Before=network-pre.target`; active inet filter input/forward/output accept with no rules. An existing `flush ruleset` in config means a separate live-only rule is lost on reload/restart unless reconciled. | Design Git-managed exact tagged rule with no full ruleset reload, scoped rollback, boot ordering, and explicit recovery plan for later nftables reload. No live change; 6/14 operational mitigations remain. |
| 2026-10-19 | edge-01 native nftables LXC baseline exposure independently reproduced, no changes. | From greenbone-01 to 192.168.2.56: echo PASS, 3 ICMP timestamp probes sent and 3 matching replies, `REPLY_CONFIRMED`; play recap `ok=4 changed=0 failed=0`. edge-01 LXC `/etc/nftables.conf` stock flush ruleset with empty inet filter INPUT/FORWARD/OUTPUT and nftables enabled; CAP_NET_ADMIN present. | Design and validate minimal exact-rule host INPUT nftables cutover with independent persistence and exact rollback; no nftables service reload, no blanket flush, verify from scanner and preserve Proxmox guest boundaries. Overall 6/14 remain operationally mitigated. |
| 2026-10-19 | greenbone-01 repeat cutover fully idempotent; three-VM ICMP remediation wave operationally verified. | User Ansible `greenbone-01 ok=31 changed=0 unreachable=0 failed=0 skipped=4`, exact rule present, Docker container identities and forwarding unchanged, ping PASS and 0 timestamp replies observed independently from monitor-01; post-change GMP authenticated preflight also PASS. Overall 6/14 hosts operationally mitigated. | Do not alter accepted risks until fresh authenticated scan. Review remaining eight host ownership starting with read-only LXC firewall analysis. Reboot persistence untested. |
| 2026-10-19 | greenbone-01 post-firewall GMP authenticated readiness verified. | Non-scanning GMP preflight `ok=10 changed=0 unreachable=0 failed=0`, managed task lookup completed in 0.1s with CHECK=PASS, scan service inactive and legacy temporary config absent. No vulnerability scan started. | Run greenbone-01 single-host cutover again for idempotency proof; hold operational count at 6/14 pending remaining hosts and future scanner/reboot confirmation. |
| 2026-10-19 | greenbone-01 ICMP timestamp mitigation deployed; third VM wave operationally complete, 6/14 mitigated. | User play recap `greenbone-01 ok=31 changed=3 unreachable=0 failed=0 skipped=4`; independent monitor-01 post-probe `VM_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, ping PASS, host INPUT-only, Docker container/forwarding checks passed, no application restarts. Authenticated GMP preflight had passed before change `ok=10 changed=0 failed=0`. | Re-run non-scanning GMP preflight after cutover, then idempotency test of greenbone-01. No reboot proof or completed authenticated scan; accepted risks unchanged. |
| 2026-10-19 | cloud-01 ICMP timestamp mitigation proven idempotent. | User-reported second single-host cutover `ok=31 changed=0 unreachable=0 failed=0 skipped=4`, output `VM_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, `VM_ICMP_ECHO=PASS`, `VM_FIREWALL_SCOPE=HOST_INPUT_ONLY`; previously checked Nextcloud `occ status` and HTTP 200 after change. Operationally 5/14 mitigated. | Read-only greenbone-01 firewall, scanner and Docker health baseline before considering final three-VM-wave change. Reboot proof and completed authenticated scan still pending. |
| 2026-10-19 | cloud-01 Nextcloud post-cutover application verification PASS. | Ansible `docker exec -u www-data cloud-01-app-1 php occ status` shows installed true, 34.0.3.2, maintenance false, needsDbUpgrade false; admin-01 HTTP `/status.php` returns 200, matching pre-cutover. ICMP mitigation remained 5/14 operational after prior successful scanner-side validation. | Pull handover update and run single-host cloud-01 VM cutover again to prove idempotency (`changed=0 failed=0`) before proceeding to greenbone-01. |
| 2026-10-19 | cloud-01 ICMP timestamp host INPUT mitigation deployed and independently checked; operational progress 5/14, pending application postcheck. | User-reported `cloud-01 ok=31 changed=3 unreachable=0 failed=0 skipped=4`; post-change Docker/FORWARD/INPUT policy invariant PASS, normal ping PASS, independent greenbone-01 timestamp probe `NO_REPLY_OBSERVED`, no restarts reported. Pre-change Nextcloud `occ status` installed 34.0.3.2, maintenance false, needsDbUpgrade false, HTTP `/status.php` 200; database/Redis healthy. | Repeat Nextcloud `occ status` and HTTP status post-change; verify idempotency before next VM. Reboot persistence and authenticated Greenbone rescan remain outstanding. |
| 2026-10-19 | sensor-01 VM ICMP rule repeat deployment proved fully idempotent. | Controller at fcde37c9: complete `greenbone-icmp-timestamp-vms-cutover.yml --limit sensor-01 --forks 1 --ask-become-pass` `ok=29 changed=0 unreachable=0 failed=0 skipped=6`; existing tagged INPUT rule detected, policy/FORWARD invariants, Suricata and Zeek states, SSH, independent ping and scanner timestamp suppression all passed. | Record 4/14 operationally mitigated; begin only read-only cloud-01 preflight. Reboot persistence and authenticated Greenbone scan remain pending. |
| 2026-10-19 | sensor-01 ICMP timestamp remediation independently verified: 4/14 operational. | Cutover `ok=23 changed=3 failed=1` after rule installation because packet counters altered chain declaration text. Exact tagged INPUT type-13 DROP verified, persistence enabled/active, Suricata/Zeek active; independent greenbone-01 scanner probe verified 0/3 matching replies and ping PASS, repeated three times (`ok=4 changed=0 failed=0`). | Pull revised chain-policy assertion, run validation and syntax, verify idempotency before next VM. Reboot persistence and fresh authenticated Greenbone scan pending. |
| 2026-10-19 | qBittorrent HTTPS-only LAN firewall cutover completed and verified live. | media-01 `ok=19 changed=2 failed=0`: HTTPS 443 HTTP 200; new LAN 8081 connections BLOCKED; Nginx loopback backend 8081 AVAILABLE. qBittorrent, Kodi, SMB and NFS not restarted. | Run read-only Greenbone evidence inspection and GMP preflight; only start a new managed scan after checking no scan is active, then verify both Medium findings and review accepted items. |
| 2026-10-19 | qBittorrent LAN TCP/443 firewall stage deployed successfully alongside HTTP/8081 fallback. | User Ansible: media-01 `ok=16 changed=2 failed=0`; nftables validated and reloaded; HTTPS from admin-01 HTTP 200; legacy HTTP 8081 from admin-01 HTTP 200; existing service/NFS rules validated. | Verify real browser HTTPS login and WebUI/download behavior before separate, reviewed 8081 firewall cutover. |
| 2026-10-19 | qBittorrent LAN 443/8081 firewall stage passed offline/controller validation; not yet applied. | User output: Jinja render, preservation of SSH/Kodi/SMB/NFS/monitoring, 8081 future-off option, estate validation (20 active), scoped Ansible syntax all PASS. The corrected standalone Jinja `bool` validator works. | Apply only `qbittorrent-https-lan-stage.yml --limit media-01`, verify HTTPS from controller plus 8081 fallback, then real browser login before 8081 cutover. |
| 2026-10-19 | qBittorrent trusted HTTPS confirmed deployed; a LAN-only HTTPS/443 firewall allowance with HTTP/8081 rollback is staged in Git, not deployed. | Ansible media-01: `ok=33 changed=9 failed=0`, HTTPS HTTP 200, Nginx syntax PASS, no Kodi/SMB/NFS/qBittorrent restart. New firewall code and offline validator not yet run on controller. | Pull and run firewall offline validator, estate and playbook syntax; separately deploy 443 alongside 8081 and verify HTTPS login from LAN. |
| 2026-10-19 | BirdNET Secure cookie verified live; qBittorrent HTTPS prerequisites missing; staged dual-resolver DNS alias, DNS-01 certificate/Nginx HTTPS proxy (Git only). | BirdNET `ok=7 changed=0 failed=0`; cookie Secure PASS on `/` and `/login`, no reload. qBittorrent readiness `ok=3 changed=0 failed=0`, no Nginx/Certbot/443/cert/DNS. New qBittorrent stage and offline validator **not yet run or deployed**. | Run offline/Jinja and Ansible syntax checks; then roll out DNS first, HTTPS second, preserve 8081 until verified cutover. |
| 2026-10-19 | Two Mediums traced to specific live services; BirdNET Secure cookie config staged, qBittorrent TLS preflight staged. | Read-only Ansible: media-01 8081 qBittorrent, no nginx/cert; docker-01 Nginx 1.26.3 csrf cookie Secure=False/HttpOnly=False; both hosts ok=3 changed=0 failed=0. Staged Git source only. | Syntax-check, deploy narrowly scoped BirdNET Nginx change and verify live flags; run qBittorrent HTTPS prerequisites check before certificate/DNS/IaC cutover. |
| 2026-10-19 | Identified `media-01:8081` as qBittorrent HTTP Web UI, and `docker-01:443` as BirdNET-Go Nginx; staged scoped read-only host checks. | Repository source: `docs/architecture/MEDIA-01.md`, qBittorrent and birdnet_go roles. New diagnostic playbook committed only; no Ansible live checks or remediation. | Pull/syntax/run `greenbone-two-medium-readonly.yml` on media-01 and docker-01, then plan reversible HTTPS and Secure cookie fixes. |
| 2026-10-19 | New authenticated Greenbone report email completed with two actionable Medium findings; evidence publication not independently verified. | Gmail report `6e75928d-f251-426f-809c-991ffcbf6603`, 03:07 UTC: Critical 0, High 0, Medium 2 (`media-01`:8081 HTTP cleartext; `docker-01`:443 cookie missing Secure), Low 0, Log 789, accepted 15. No CVEs reported. | Inspect services non-invasively via Ansible, reconcile accepted findings, validate newer `managed.json` transfer/freshness, remediate in IaC. Boot guard still Git-only. |
| 2026-10-18 | Staged fail-closed managed scan systemd boot-readiness gate in Git; offline and live validation pending. | Gate uses `ExecStartPre`, 30-minute cap/15-second retry/40-second per-probe bound with existing authenticated runner `--check`; dedicated scoped Ansible deploy path avoids timer changes. No service activation, reboot or scan. | Run offline validator, estate guard and Ansible syntax checks; deploy only after review and separately verify no scan triggered. |
| 2026-10-18 | Deployed production direct-socket GMP preflight passed in 0.1s, no scan. | User Ansible: syntax PASS, `ok=10 changed=0 failed=0`; `GMP check exit code: 0`, `CHECK=PASS`, legacy config absent True. Managed scan unit still `failed` from earlier run. | Review and stage scheduled scan boot-readiness gate before fresh scan and evidence verification. |
| 2026-10-18 | Direct-socket Greenbone production runner deployed through scoped Ansible, with live Python validation. | User: pulled `f621581d`, `greenbone-scan-runner.yml --limit greenbone-01` returned `ok=3 changed=1 failed=0 unreachable=0`; template installed and rendered Python compilation passed. No scan started. | Run the bounded non-scanning `greenbone-gmp-preflight.yml`; verify task lookup and legacy credential-file absence. |
| 2026-10-18 | Controller validated staged direct-socket Greenbone runner and preflight; deployment still pending. | On admin-01: Jinja render PASS, generated Python syntax PASS, mock GMP auth/task lookup PASS, estate PASS (20 active / 0 planned / 5 retired), Ansible syntax PASS for runner and preflight. No scans/host changes. | Deploy **only** `greenbone-scan-runner.yml --limit greenbone-01`; inspect result before non-scanning GMP preflight. |
| 2026-10-18 | Direct authenticated GMP task lookup PASSED using Unix socket; staged direct-socket replacement for automated runner (Git only). | Python syntax PASS; Ansible direct-auth diagnostic `ok=6 changed=0 failed=0`; auth 200, task 200, exactly one managed task. Runner/preflight changes **not yet deployed or syntax-tested on controller**. | Review staged diff/syntax; deploy only after approval. Then non-scanning preflight and startup-readiness work; no scan yet. |
| 2026-10-18 | Direct unauthenticated GMP XML query succeeded over Unix socket; staged short, credential-safe direct auth check without Docker Compose. | User Ansible returned `GMP_STATUS=200`, `GMP_VERSION=22.7` (rc=0). New direct-auth script/playbook are committed but not yet syntax/live checked. | Pull and run short non-scanning direct-auth GMP check; if PASS, consider reviewed runner direct-socket implementation. |
| 2026-10-18 | Direct host-side Unix socket connect on greenbone-01 succeeded using Ansible. | `GMP_SOCKET_CONNECT=PASS` rc=0; no service/config change, GMP XML not sent. | One short unauthenticated `<get_version/>` request over host socket, no Docker exec or scan. |
| 2026-10-18 | Revised passive GMP request-path playbook passed live. | User output: ok=9 changed=0 failed=0; gvmd socket present (Unix socket, mode 0666), correct volume, credentials absent, no recent helper, Docker journal helper activity at 17:17:41 BST. Listener connection not tested. | Run a single bounded read-only host Unix socket connection check via Ansible. |
| 2026-10-18 | Request-path Ansible diagnostic was interrupted while running Docker Compose exec in gvmd; replaced that task with host-volume socket inspection. | Syntax PASS; first run reached exec and Ctrl+C; second run incomplete. Revised playbook committed `8f4bb692` but not syntax/live validated. | Pull and run revised non-exec diagnostic; avoid GMP preflight and scans. |
| 2026-10-18 | Instrumented non-scanning GMP preflight still timed out at task lookup, but SIGTERM temporary-credential cleanup succeeded. Staged read-only request-path inspection. | User terminal: `GMP_CHECK_STAGE=querying_managed_task`, `rc=124` after 150s; signal 15; config absent True; `ok=9 changed=0 failed=1` (intended). New diagnostic untested. | Pull, syntax-check and run `greenbone-gmp-request-path-readonly.yml`; do not rerun GMP or scan until cause is clearer. |
| 2026-10-18 | Instrumented Greenbone scan runner deployed to `greenbone-01` via scoped Ansible; repeat confirmed idempotent. | Controller user output: first `greenbone-scan-runner.yml --limit greenbone-01` `ok=3 changed=1 failed=0`; `python3 -m py_compile` PASS; second `ok=3 changed=0 failed=0`. Both runner and GMP preflight syntax checks previously passed. **GMP preflight not yet rerun.** | Run `greenbone-gmp-preflight.yml --limit greenbone-01`, inspect non-secret stage markers and file cleanup; do not launch scan yet. |
| 2026-10-18 | Ran Greenbone historical GMP helper latency diagnostic and staged non-secret preflight instrumentation/cleanup safeguards in Git-managed IaC. | User evidence: `greenbone-gmp-latency-readonly.yml` syntax PASS, `ok=7 changed=0`; helper journal activity 16:45:46–47 BST; 5.6 GB RAM/61 GB disk available; orphan config absent. Cause still unknown. **New runner/preflight changes not deployed or validated on controller.** | Review Git diff, syntax-check runner/preflight, then deliberately deploy runner via Ansible and run guarded non-scanning GMP preflight. |
| 2026-10-18 | Successfully removed orphan temporary Greenbone GMP credentials through guarded Ansible. Added historical helper-latency read-only diagnostic. | User output: cleanup syntax PASS, `ok=12 changed=1 failed=0`; `REMOVED_ORPHANED_GMP_CONFIG`, file absent True; no service or scan change. New latency playbook **not yet tested**. | Pull, syntax-check and execute `greenbone-gmp-latency-readonly.yml`; examine event/journal evidence before any re-scan. |
| 2026-10-18 | Read-only Ansible confirmed orphan root-owned GMP credentials persisted after timeout, no lock owner/active helper, gvmd/pg-gvm healthy. Added fail-closed one-time orphan cleanup IaC. | `greenbone-gmp-timeout-readonly.yml` syntax PASS; live `ok=9 changed=0`; metadata root:0640, no processes/active helpers, old scan unit failure. New cleanup playbook **not yet executed**. | Run scoped Ansible cleanup with safety guards, then investigate GMP helper timeout without starting scans. |
| 2026-10-18 | Ansible authenticated GMP `managed --check` failed to verify readiness, timing out after 150s (`rc=124`, no output). Added strictly read-only timeout-residue diagnostic. | User-pasted `greenbone-gmp-preflight.yml` syntax check PASS and run `ok=6, changed=0`; debug states `GMP readiness: NOT VERIFIED`. Whether temp credentials/helper processes remain is unknown. New diagnostic **not yet syntax/live checked**. | Pull and execute `greenbone-gmp-timeout-readonly.yml` through Ansible; decide safe IaC fix after results, no scan yet. |
| 2026-10-18 | Greenbone stack health verified post-reboot; confirmed managed-scan/GMP startup race and completed VT rebuild. Added non-scanning GMP preflight IaC. | User Ansible output: Docker active, gvmd/pg-gvm healthy, socket present; scan failed 16:18:01 BST before gvmd ready 16:19:29; 190103 VTs rebuilt and feed sync complete around 16:37 BST. New preflight **untested**. | Syntax-check and run `greenbone-gmp-preflight.yml`; if authenticated lookup succeeds, design/apply reviewed startup guard and validate a fresh scan. |
| 2026-10-18 | Verified Proxmox-2/cluster recovery, obtained old Greenbone evidence and found new scan startup failure; added read-only Docker/gvmd diagnostic Ansible playbook. | User-pasted controller output: both PVE nodes online, quorum 3/3 with QDevice, Greenbone reachable; 16 Oct 14:28Z JSON report `35dc10c3` 0 actionable/30 accepted; 18 Oct 16:18 BST scan failed with gvmd socket connection refused. New diagnostic **not executed**. | Pull and syntax-check/run `greenbone-stack-health-readonly.yml`; investigate startup readiness before any repairs/re-scan. |
| 2026-10-18 | User reports `Proxmox-2` is back online after the outage. | **Reported by user only**; cluster quorum/VM203 and Greenbone SSH health not yet verified by Ansible; no scan evidence read. | Run existing Ansible connectivity diagnostics; if healthy, inspect Greenbone evidence read-only; reconcile findings. |
| 2026-10-18 | User reported `Proxmox-2` down after Greenbone read-only playbook failed to reach VM203 on TCP/22. Added/revised read-only Ansible connectivity/cluster diagnostic. | User-provided Ansible output: `greenbone-01` SSH timeout, `unreachable=1` (host assertion passed locally only); diagnostic IaC commits `1220e052`, `1ff5ed8d`, `4329652183`; **new diagnostic not yet executed**. | Verify surviving PVE quorum/node/guest state via the new Ansible playbook; defer Greenbone findings review until VM203 access returns. |
| 2026-10-18 | Confirmed clean controller merge/push and Ansible syntax test; updated handover after merge. | Merge `9dbbacc9` on `main` verified via GitHub; controller's user-pasted syntax check PASS, estate validation PASS; **Greenbone live evidence still pending**. | From `admin-01`, fast-forward local checkout and run `greenbone-scan-evidence-readonly.yml`; assess findings and update handover. |
| 2026-10-18 | Resolved `MEDIA-01.md` conflict retaining remote documentation, preserved local qBittorrent IaC and completed merge `9dbbacc9`; push succeeded. | Controller output: estate validation PASS (20 assets), no whitespace errors, Greenbone inspection playbook Ansible syntax PASS; no live scan inspection performed. | Pull latest handover fast-forward and run Ansible read-only Greenbone inspection. |
| 2026-10-18 | Controller history confirms exactly one local-only commit: `f752562f` (qBittorrent and Kodi DLNA firewall / `media-01`), with 7 remote-only commits at the time of the user's last fetch; the remote has since advanced. | User-supplied `git log` and `git diff --stat`; remote `788d8330` also changes `docs/architecture/MEDIA-01.md`, so conflict is possible; **full local patch not yet inspected**. | Preserve local commit with a backup branch, refresh origin, review/merge without dropping it, then run Ansible Greenbone evidence inspection. |
| 2026-10-18 | Local `admin-01` checkout reported divergent `main` and `origin/main`; fast-forward pull failed, so the new Greenbone playbook is not local. Untracked Kodi-related directories exist. | User-supplied controller output; **local-only commits and content not yet inspected; no Ansible run or live scan verified**. Preserve all local work, run read-only Git history/diff commands before choosing merge/rebase. | Inspect local commits and identify security/vulnerability progress; reconcile safely before attempting the Greenbone playbook. |
| 2026-10-18 | Confirmed Ansible-only host operations and Git-managed IaC for persistent changes; added reusable, read-only Greenbone Ansible inspection playbook. | `AGENTS.md` rule commit `98d2615269`; new `IaC/ansible/playbooks/greenbone-scan-evidence-readonly.yml` commit `4d688144a6`. **No live scanner or controller access; syntax check and playbook execution still required.** | On `admin-01`, sync the repo, syntax-check and run the playbook; return its results. |
| 2026-10-18 | Created cross-chat handover, then updated `AGENTS.md` to require handover updates for user/agent changes. | Handover commit `c0dbfedf0232`; AGENTS commit `cba755914606`. GitHub files read back successfully; **local `validate-estate.py` and GitHub Actions result not yet verified**, and **no live scanner access / new scan result verified**. | Obtain live managed scan status and evidence; reconcile findings. |
| 2026-10-17 | Latest existing repository work documented `media-01` service/UPnP port state. | Commits `788d8330d5` / `aecfd02d68`. | No change to Greenbone validation gate shown. |
| 2026-10-16 | TCP timestamp hardening and Suricata updater committed. | Commits `e27b864f4d` / `827e7c9e85`; repo changes inspected on 18 October. | Verify live rollout / scan findings as appropriate. |

## Session update checklist

For **every** change we make:
- [ ] Check current Git/repository state and read the authoritative inventory/docs first.
- [ ] Use Ansible for host-level inspection and deployment; encode any persistent host change in reviewed, Git-managed IaC before applying it.
- [ ] State exactly what changed (including path and commit/ref) and why.
- [ ] Record what was **tested live**, what was **tested syntactically**, and what is **not tested**.
- [ ] Update status and next actionable step here; update canonical docs/backlog if impacted.
- [ ] Validate with `python3 scripts/validate-estate.py` and applicable tests/workflows where execution is available.
- [ ] Commit/push changes and this handover together when possible; verify the new repository state.
