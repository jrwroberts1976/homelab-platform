# GPT Handover — Homelab Platform

### 31 October 2026 — Phase 3 reconciliation planner tests passed

- User ran `router-01-qos-download-reconcile-planner-proof.yml`: **4 OK, 0 changed, 0 failed**; all 12 deterministic planner scenarios passed, including duplicate up, down, reconnect, missing PPP, foreign filters, partial failure and stale ownership.
- This confirms decision-making only; no live `tc` operations, hook installation, locks, or PPP manipulation.
- Next: implement and independently test serialized actuator, fail-safe rollback and event-driven service integration before any production deployment.


### 31 October 2026 — Phase 3 reconciliation decision planner staged

- Added pure Python `IaC/ansible/files/router-qos-download-reconcile-plan.py` and controller-only `playbooks/router-01-qos-download-reconcile-planner-proof.yml`, with 12 deterministic cases: first up, duplicate up, down, changed PPP ifindex, disappeared PPP, foreign filters, inconsistent state, partial activation, route not ready, missing interface, unrelated PPP and no state.
- **Not yet tested by user**. Planner returns decisions and planned steps only; it does **not** run tc/ip, acquire locks, install hooks, or change live network.
- Next: validate these tests, then implement side-effectful reconciler behind an isolated network-namespace/dummy test harness, strengthen ownership and abort/rollback, and add strict serialization. Remain GitHub-only; no production activation.


### 31 October 2026 — Phase 3 PPP event adapter isolated proof passed

- User ran `router-01-qos-download-ppp-hook-isolated-proof.yml` on controller: **9 OK, 3 changed, 0 failed**. Two simulated up events, one down event, and an unrelated PPP interface were handled as expected.
- This proves **event filtering/logging only**, not CAKE reconciliation, reconnect recovery or persistence. No router network changes.
- Next: build a separately testable serialized, ownership-aware reconciler and failure-injection tests. Stage code first; do not enable PPP event hooks or the managed service on the live router until approved deployment/rollback are verified.


### 31 October 2026 — Phase 3 PPP lifecycle discovery passed

- Read-only `router-01-qos-download-pppoe-hooks-discovery.yml` **4 OK, 0 changed, 0 failed**. pppd installed; `/etc/ppp/ip-up.d` and `ip-down.d` exist and contain `0000usepeerdns`. `router-pppoe.service` is Type=simple, Restart=always, ExecStart `/usr/sbin/pppd call homelab-wan nodetach`. PPP ifindex 5; upload CAKE remains 13Mbit, original ingress noqueue, trial rollback marker present.
- Staged candidate hook file `IaC/ansible/files/router-qos-download-ppp-hook.sh` only. It is **not installed**, and is only a non-mutating placeholder; PPP argument/event signalling, serialized reconciler, and fail-safe startup must be implemented and tested before any deployment.
- **No live router modifications in Phase 3 discovery.**


### 31 October 2026 — Phase 2 static validation passed; Phase 3 discovery staged

- User ran controller-only phase-2 validator: **4 OK, 0 changed, 0 failed**. Candidate is not installed or enabled.
- Added `docs/architecture/router-01-qos-download-pppoe-lifecycle-phase3.md` and read-only `IaC/ansible/playbooks/router-01-qos-download-pppoe-hooks-discovery.yml`.
- Phase 3 design requires real PPP event hook discovery, event-driven and serialized reconciliation, independent rollback, and isolated dummy interface testing. Existing phase-2 script is not production-ready; **do not deploy it yet**.


### 31 October 2026 — Phase 2 download QoS persistent candidate staged (no deployment)

- Created inactive candidate files `IaC/ansible/files/router-qos-download-managed.sh` and `router-qos-download-managed.service` plus `docs/architecture/router-01-qos-download-persistent-phase2.md`.
- Controller-only validator: `IaC/ansible/playbooks/router-01-qos-download-managed-phase2-validate.yml`. **Not yet run by user**.
- Candidate is **not production-ready**: reconnect orchestration, partial-start failure cleanup and safety tests remain. No `WantedBy`, no deployment playbook or activation. Router left in successful rollback state with upload CAKE at 13Mbit only.
- Trial results and 07:35:20 GMT successful automated rollback were previously recorded; retain all evidence.


### 31 October 2026 — Timed download QoS live-trial rollback verified

- Temporary 43Mbit download CAKE on `ifb-wan0` with `ppp0` ingress redirect (pref 49131) activated via approval-gated Ansible: **24 OK, 10 changed, 0 failed**. Existing `eth1` 13Mbit upload CAKE preserved.
- Client Ookla trial measurements: 41.57/12.07 Mbps, idle 10.12ms, download-loaded 10.10ms, upload-loaded 10.32ms; two later JSON runs 41.59/12.03 and 41.67/12.00 Mbps with download-loaded ~10ms. Both JSON exports were collected **after** shaping activation, not a pretrial baseline.
- Systemd timer triggered the rollback service at **2026-10-31 07:35:20 GMT**; user checked at 07:36:41 and confirmed `rolled-back` marker, no IFB, no `ppp0` clsact or ingress filter, original `ppp0` noqueue and unchanged 13Mbit upload CAKE. Journal: service started and deactivated successfully. **Production restored.**
- Next proposed work: review/design persistent download CAKE lifecycle, including PPPoE reconnect and reboot, safety gates, rollback and audits. Do not re-run trial or make live changes blindly. Retain /var/lib/router-qos-download-trial as evidence.


### 31 October 2026 — Download QoS replacement-interface proof passed

- User ran `router-01-qos-download-replacement-rollback-proof.yml`: **27 OK, 11 changed, 0 failed**. Disposable ingress device was deleted/recreated under the same name with a new ifindex; tested rollback preserved replacement `clsact`, removed trial IFB, recorded successful rollback, and verified live `ppp0` ingress and `eth1` 13Mbit upload CAKE untouched.
- Recent identity-aware repeat proofs also passed: normal **25 OK/13 changed/0 failed**, partial activation **21 OK/9 changed/0 failed**. All were disposable-interface tests; live 43Mbit download CAKE remains **not activated**.
- Remaining review: validate active-trial recovery on PPP replacement, re-check timer race/acceptance and connection recovery before approving live shaping. No automatic cutover authorised.


### 31 October 2026 — Partial download QoS rollback proof passed

- User executed `router-01-qos-download-partial-rollback-proof.yml`: **20 OK, 8 changed, 0 failed**. Test created disposable `clsact` without a matching ingress filter, used a namespaced copy of the recovery script, verified rollback marker and cleanup, and confirmed real `ppp0` ingress and `eth1` upload CAKE unchanged.
- Still pending: guard/review live trial acceptance, validate timing and rollback during active PPPoE, and measure download-loaded latency. No production download shaping applied.


### 31 October 2026 — Download QoS transient timer proof succeeded

- Re-run of `router-01-qos-download-timer-proof.yml`: **13 OK, 2 changed, 0 failed**. Bounded Ansible polling detected the systemd-run marker, the marker was removed, and the eth1 upload CAKE qdisc was verified unchanged. Previous fixed 16s wait was too short; journal had already demonstrated the timer executed after ~17s.
- IFB and mirred compatibility, isolated cleanup proof and marker-only timer test now passed independently. **No production ppp0 ingress filter or download CAKE has been activated.** Next: controlled combined trial with rollback armed before ingress redirection, explicit approval and live speed/latency tests.


### 31 October 2026 — Download QoS isolated rollback proof passed

- User ran `router-01-qos-download-rollback-proof.yml` on router-01: **24 tasks OK, 12 changed, zero failures**, testing a namespaced copy of the candidate rollback script against disposable dummy/IFB interfaces.
- Test teardown and assertions passed, including preservation of live `eth1` upload CAKE and absence of changes to real `ppp0` ingress. This **does not** prove rollback during a PPPoE disconnect or systemd timed rollback. No live download CAKE activation has occurred.
- Next safety gate: timed rollback service proof and final guarded pre-activation audit; do not apply the ingress filter until timer success and independent operational recovery are established.


### 31 October 2026 — Isolated download IFB compatibility test passed

- On branch `feature/router-download-qos-preflight-20261031` / PR #267, user ran `router-01-qos-download-ifb-compatibility.yml` on router-01: recap **19 OK, 9 changed, 0 failed, 0 unreachable**. This exercised disposable `qos-test0` and `qos-ifb0` links, CAKE at 43 Mbit and `matchall`/`mirred` syntax, including cleanup in the always block and guards checking production interfaces were unchanged.
- This is NOT evidence of live download traffic shaping. No production `ppp0` ingress QoS activated. Existing upload `eth1` CAKE 13 Mbit retained. Before a live trial, verify the ownership-safe rollback and timed systemd cleanup, specifically PPPoE reconnect and any non-owned ingress filters; require explicit approval.


### 31 October 2026 — CAKE explicit disable procedure staged (not executed)

- PR #266 adds `IaC/ansible/playbooks/router-01-qos-persistence-disable.yml`, which requires explicit approval, target identity, expected active 13Mbit CAKE, enabled/active service and preserved restore script. It stops/disables `router-qos-upload.service` **before** running the stored `fq_codel` restore script, verifies WAN route and inactive/disabled service, and attempts CAKE recovery in an Ansible rescue block if restoring fails.
- **Not yet syntax checked or run.** It must be reviewed and syntax validated before PR merge. Normal production state remains persistent CAKE at 13 Mbps; do not execute rollback merely to test it on the active household connection.


### 31 October 2026 — CAKE upload QoS survives controlled router reboot

- Router rebooted and reports `uptime -s` = `2026-10-31 06:12:01`. Initial Ansible SSH `Connection refused` was transient during reboot; interactive SSH to `192.168.2.1` subsequently succeeded.
- Post-boot read-only Ansible verification: `router-qos-upload.service` = `enabled` and `active`; `eth1` root qdisc = `cake ... bandwidth 13Mbit ... ptm overhead 30`; IPv4 default route `default dev ppp0 scope link`; `router-pppoe`, `nftables`, `dnsmasq`, `unbound`, and `ssh` all active. The router's LAN and WAN interfaces and PPPoE link were up.
- **Boot persistence confirmed** for 13 Mbps upload CAKE. USB NIC hot-reset and independent PPPoE reconnection resilience not yet tested. Continue to preserve recovery files and avoid unplanned link resets. Review/merge PR #266 and document separate disable/restore flow before considering upload QoS fully operationally closed.


### 31 October 2026 — Post-activation upload QoS verification

- Read-only audit: `router-qos-upload.service` reported `enabled` and `active`; `tc qdisc show dev eth1` showed `cake ... bandwidth 13Mbit ... ptm overhead 30`; default IPv4 route `default dev ppp0 scope link`; `router-pppoe`, `nftables`, `dnsmasq`, `unbound` and `ssh` all `active`.
- Upload shaping and startup enablement are confirmed; full reboot recovery has **not** been tested. Do not claim reboot-tested persistence yet. Preserve trial restore script. Finish guarded recovery checklist and boot test before final PR merge.


### 31 October 2026 — Router upload QoS persistence activated

- User ran `router-01-qos-persistence-activate.yml` from admin-01: 17 tasks OK, 2 changed, zero failures. The guarded activation playbook verifies live CAKE on `eth1` at 13Mbit with PTM overhead 30 and PPPoE default route, starts the pre-staged `router-qos-upload.service` without changing the existing qdisc, and enables it for future boots.
- Persistence is enabled, but not yet verified by a controlled reboot or WAN-interface recreation. Current router should remain online; next: read-only service/queue verification, prepare explicit disable/recovery and controlled reboot test, then review/merge PR #266. Preserve `/var/lib/router-qos-upload-trial` recovery evidence until reviewed.


### Router CAKE upload QoS trial and persistence staging — 30–31 October 2026

- On router-01 (Pi4 WAN physical `eth1`, PPPoE logical `ppp0`), measured pretrial 47.37 Mbps down / 14.52 Mbps up with upload-loaded latency 156.23 ms. Trial installed CAKE on `eth1` at `13mbit pppoe-ptm besteffort flows`, verified as `ptm overhead 30` without changing PPPoE or NAT. Trial 45.53 Mbps down / 11.97 Mbps up, upload-loaded latency 10.17 ms, download-loaded latency 31.43 ms. A single test showed major improvement; monitor after persistence.
- Ten-minute automatic rollback was armed before modification; trial acceptance playbook verified CAKE and network health, then explicitly disarmed timer. Recovery script and initial qdisc remain in `/var/lib/router-qos-upload-trial`. Current CAKE is LIVE BUT RUNTIME-ONLY; do not assume boot persistence.
- PR #266 branch `feature/router-qos-preflight-20261030`: trial/preflight/finalise playbooks validated; read-only persistence preflight passed (4 tasks, 0 changes). Persistence staging playbook installed script `/usr/local/sbin/router-qos-upload` and `/etc/systemd/system/router-qos-upload.service` with service disabled/inactive (13 tasks, 2 changed, 0 failed). Script syntax and service status audited; essential SSH, PPPoE, nftables, dnsmasq, Unbound healthy.
- New `router-01-qos-persistence-harden.yml` stages a USB-interface wait and retry-on-failure service behaviour, without enabling or starting it. Pending: syntax-check and run hardening playbook; independently inspect script and unit; guarded idempotent activation; verify runtime and service state; controlled boot/interface-reset evidence; design explicit disable/recovery; merge PR #266. Avoid restarting WAN or reboot before recovery plan. Download IFB shaping at 43 Mbps is a separate phase.


### Router SSH hardening finalised — 30 October 2026

- Draft PR #265 staged and validated router-01 SSH hardening through Ansible. Temporary-file systemd rollback proof succeeded after correcting execution on the `/run` noexec filesystem via `/bin/sh`; initial failure and stale unit were diagnosed and cleared.
- Temporary sshd candidate preflight passed 11 tasks with admin and router-metrics effective policy checks; production deployment passed 15 tasks, with a 10-minute rollback armed before changing SSH.
- Installed `/etc/ssh/sshd_config.d/00-router-hardening.conf`: `PermitRootLogin no`, `PasswordAuthentication no`, `PubkeyAuthentication yes`, `X11Forwarding no`. Existing router-metrics `Match User` policy retains `AllowTcpForwarding local` and `PermitOpen 127.0.0.1:9100`.
- Fresh public-key administrative SSH returned `ADMIN_SSH_OK`; Prometheus query `up{job="router-node-exporter"}=1` confirmed monitoring remained functional. Direct curl to host localhost:19101 was not a valid scrape test; tunnel target is inside the Prometheus environment. Finalization playbook passed 14 tasks with zero failures and stopped the rollback timer.
- Recovery transaction directory `/var/lib/router-ssh-hardening` intentionally remains for audit; review and remove separately rather than during deployment. The changes are live and verified; PR #265 pending repository merge and eventual branch cleanup.
- No PPPoE, DHCP, DNS, nftables, or other networking changes were made by SSH hardening.


### Router interface counter deltas — 30-second sample, 30 October 2026

- eth0 LAN: RX +20,208 packets, TX +44,570 packets; RX drops stayed 227, TX drops stayed 12; errors unchanged at 0. RX bytes +1,491,556 (~0.40 Mbps), TX bytes +64,416,157 (~17.18 Mbps).
- eth1 WAN USB: RX +44,571 packets, TX +20,146; RX drops stayed 1, TX drops stayed 0; errors unchanged at 0. RX bytes +64,173,097 (~17.11 Mbps), TX bytes +1,688,801 (~0.45 Mbps).
- ppp0 PPPoE: RX +44,566 packets, TX +20,144; drops and errors stayed 0. RX bytes +63,775,367 (~17.01 Mbps), TX bytes +1,084,405 (~0.29 Mbps).
- These rates reflect observed traffic over an approximately 30-second interval, not connection capacity. No new drop/error increments were observed; continued time-series monitoring is still needed.

### Router initial performance/security baseline — 30 October 2026, 10:15 GMT

- Read-only Ansible observation of router-01 (uptime 22h31m): load average 0.10/0.03/0.01; temperature 40.894°C; Raspberry Pi `vcgencmd get_throttled=0x0`; RAM 3.7 GiB total, 285 MiB used, 3.4 GiB available; swap 0 used; root filesystem 939 GB total, 4.6 GB used, 896 GB available.
- Network cumulative counters: eth0 LAN RX 19,687,357 packets / 226 drops / 0 errors; TX 41,682,942 packets / 12 drops / 0 errors. eth1 WAN adapter RX 41,629,006 packets / 1 drop / 0 errors; TX 19,297,860 packets / 0 drops / 0 errors. ppp0 RX 41,615,470 packets / 0 drops / 0 errors; TX 19,292,457 packets / 0 drops / 0 errors. These are *cumulative*, not drop-rate measurements.
- PPPoE `ppp0` configured with MTU 1492, current default route via ppp0. Public IP deliberately omitted from operational handover. nftables input and forward default drop, LAN->WAN forwarding and PPPoE NAT present; MSS clamp to 1452 has matched 69,073 outbound and 11,495 inbound TCP SYN packets.
- Initial observations show no evident thermal throttling or resource pressure. Outstanding: measure interface counter deltas over an interval, inspect router service/Alloy health and PPPoE stability, check IPv6 policy/external reachability and firewall rule persistence. No firewall, PPPoE or runtime router changes were made by this sampling.
- The legacy DHCP forwarder was stopped/disabled with the approved rollback playbook, preserving files; dnsmasq, nftables, Unbound and Alloy remained active. The direct Loki stream was proven earlier, and journal events from 09:43 appeared in Loki; a new event strictly *after* the forwarder stop is still needed to finish the post-cutover proof.

## 30 October 2026 — Direct DHCP observability deployed and verified

- Router `router-01` (192.168.2.1): Debian 13.7 ARM64, Alloy v1.21.3 installed and running/enabled via approval-gated Ansible role `router_dhcp_alloy` (PR #255; check-mode correction PR #256). dnsmasq remained active throughout.
- Alloy reads systemd journal entries matching `_SYSTEMD_UNIT=dnsmasq.service SYSLOG_IDENTIFIER=dnsmasq-dhcp`, sends to Loki on monitor-01 (192.168.2.52:3100) with `host=router-01`, `service=dnsmasq` and `source=journal` labels. Query `{host="router-01",service="dnsmasq"} |= "DHCP"` returned genuine DISCOVER, OFFER, REQUEST and ACK messages; recent Alloy journal showed no matching warnings/errors.
- Grafana dashboard `Homelab — Router DHCP Activity` (UID `homelab-router-dhcp`) added by PR #257, validated as JSON/Ansible, and deployed via the isolated `monitor-01-router-dhcp-dashboard.yml` playbook without restarting the monitoring stack. User confirmed dashboard is accessible and shows data at `https://grafana.home.jrwroberts.co.uk/d/homelab-router-dhcp`.
- Privacy: DHCP logs include local IP addresses, MAC addresses and device names; keep Grafana/Loki access restricted and review retention.
- **Legacy forwarder remains running pending controlled retirement.** Its existing gated rollback playbook `router-01-dhcp-log-forwarder-rollback.yml` can stop/disable the `homelab-router-dhcp-forwarder.service` with `router_dhcp_forwarder_rollback_approved=true`; leave `router_dhcp_forwarder_remove_files_approved=false` to retain files for reversibility. Confirm sustained direct ingestion and service state before retirement.
- Next: verify forwarder status, Alloy/Loki recent-ingestion health and baseline router resource/network/security counters; record readings, then authorise forwarder disable separately. No forwarder stop was performed in this documentation change.


## 30 October 2026 — Router inventory reconciliation (source-only proposal)

- GitHub branch consolidation completed: only main is retained as an active permanent remote branch; archived toolset, Pi migration and Grafana backup commits are preserved by matching archive tags. Multiple focused recovery PRs #243–#252 merged selected safe DNS, DHCP forwarder, monitoring and read-only diagnostic source into main. Historical Kea DHCP, obsolete 192.168.3.1 assumptions and SSH installation playbooks were intentionally not bulk-merged.
- Proposed canonical inventory change on review branch: define router-01 at 192.168.2.1 as a distinct router_hosts group; retire obsolete docker-01 memberships from birdnet_hosts, komodo_periphery_hosts, zabbix_agents, recovery_mirrors and generic alloy_hosts (through birdnet_hosts removal). Retain empty birdnet_hosts for legacy group compatibility. Do not automatically add the live gateway to generic package, monitoring or restart playbooks.
- No changes to live router/DHCP/DNS/firewall/PPPoE, monitoring services or SSH configuration are authorised by the inventory PR. Confirm consumers of the retired groups and run local inventory/syntax checks before merge; explicitly approve production monitoring enrolment separately.
- Verified router Node Exporter TCP listener is 127.0.0.1:9100; SSH bound to port 22 on IPv4 and IPv6; DNS on 127.0.0.1 and 192.168.2.1 port 53. Listener bindings alone do not prove firewall exposure.
- DHCPACK forwarding from router-01 to monitor-01:5514 was verified, but Loki/Grafana ingestion and device dashboards need end-to-end validation. Candidate monitoring work must preserve existing services and use staged IaC review and rollback.
- Next: validate canonical inventory target and stale references, then design a read-only metrics/log ingestion preflight and capture approved router performance/security baselines.


## 29 October 2026 — GitHub PR/branch reconciliation after admin-01 recovery

Final Proxmox vote verification has now been merged by PR #238: both PVE nodes `Quorate: Yes`, `Total votes: 3` of 3 expected, Qdevice vote 1, both QDevice clients `Connected` to admin-01 `.48`; no additional runtime changes. GitHub audit of `homelab-platform` found **zero open PRs** and **53 branch refs including main**. Of 52 other refs, 42 have merged PR history (mostly squash merged), 6 have only intentionally **closed unmerged** PRs (#196, #188, #207, #210, #208, #190), and 4 have no PR history. Three no-PR branches are ancestors of main (zero ahead), and `backup/router-device-grafana-wip-20261011` is a distinct old unreviewed WIP, not authorised for bulk merge.

**Do not merge old `.3.1` / Kea Pi cutover, broad router diagnostics, MSS writer, unsafe Docker retirement, or historical stale documentation wholesale.** Merged PRs #211, #212, #213, #215, #216, #217, #221, #222 and subsequent #233–#238 already provide reviewed current-state slices. Squash-merged branch refs may remain different from main; compare file contents, not only ahead/behind counts. No current safe open merge queue after #238. The [branch reconciliation runbook](docs/network/BRANCH-MERGE-RECONCILIATION-2026-10-29.md) records the full decisions. Future work should be reimplemented narrowly from latest main with offline CI and explicit runtime gates. This is source/documentation-only; no host changes or branch deletions.


## 29 October 2026 12:55 UTC — FINAL RECOVERY VERIFIED: 3/3 Proxmox votes, QDevice connected on both nodes

**Independently operator-verified after the admin-01 reboot:** Both `PROXMOX` and `Proxmox-2` reported via read-only `pvecm status` that cluster `jameshouse-pve` is **`Quorate: Yes`**, with **Expected votes: 3**, **Total votes: 3**, **Quorum: 2** and `Flags: Quorate Qdevice`. Membership identifies `PROXMOX 10.255.255.1` (1 vote, `A,V,NMW`), `Proxmox-2 10.255.255.2` (1 vote, `A,V,NMW`) and **`Qdevice` (1 vote)**. Read-only `corosync-qdevice-tool -s` on *both* nodes returned **`QNetd host: 192.168.2.48:5403`** and **`State: Connected`**, configuration version 3, model Net, Fifty-Fifty split algorithm. Thus the witness is actually contributing its vote, not just accepting TCP connections.

Host-side recovery independently verified immediately beforehand: Windows SSH to `james@192.168.2.48` succeeded; `admin-01 eth0 UP 192.168.2.48/24`; `sudo corosync-qnetd-tool -s` showed **Connected clients: 2** and **Connected clusters: 1**. Router-01's approved, independently verified Ansible `dnsmasq` reservation is `dhcp-host=b8:27:eb:e8:36:cd,192.168.2.48`, preserving the original ASUS `.180` entry and dynamic `.100-.199` range. The historical `.127` lease, disconnected client states, and 2/3 votes documented below are **incident history, not current operational status**.

**Operational status: admin-01 DHCP recovery and Proxmox witness restoration COMPLETE.** No Proxmox cluster configuration changes or additional network restarts required. Canonical Ansible inventory was already correct at `.48`; preserve it. Issue [#206](https://github.com/jrwroberts1976/homelab-platform/issues/206) records the full operator evidence; this does not imply unrelated router migration work is complete.


## Recovery interim evidence — admin-01 .48 and QNetd clients reconnected before vote verification

**Confirmed live after admin-01 reboot:** Windows SSH to `james@192.168.2.48` succeeded and identified `admin-01`. Direct `ip -4 -br addr show eth0` reported **`eth0 UP 192.168.2.48/24`**. Direct `sudo corosync-qnetd-tool -s` reported QNetd listening `*:5403`, TLS supported, **Connected clients: 2**, **Connected clusters: 1**. The original `.48` address is restored using router-01's already activated and independently verified fixed DHCP reservation for `b8:27:eb:e8:36:cd`. Earlier incident sections about the observed `.127` address and zero QNetd clients are historical and are superseded by this evidence.

**Still pending independent verification:** both Proxmox nodes' `pvecm status` and `corosync-qdevice-tool -s` for QDevice vote/quorum status. Two clients connected to QNetd is not proof of the final counted witness vote. No Proxmox/Corosync configuration edit or router firewall change observed. Canonical inventory has already retained `.48` correctly. Preserve the router DHCP pool `.100-.199` and existing ASUS reservation `.180`. Runbook: [admin DHCP recovery](../network/ROUTER-01-ADMIN01-DHCP-RESERVATION-2026-10-29.md); [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206).


## Historical pre-recovery snapshot — Proxmox QDevice outage diagnosed

**Read-only definitive operator evidence** after physical router admin DHCP reservation installation and independent postflight PASS: on both Proxmox nodes, `corosync-qdevice-tool -s` reports **`QNetd host: 192.168.2.48:5403`**. `PROXMOX` shows `State: Connect failed`; `Proxmox-2` shows `State: Connecting`. The shared `/etc/pve/corosync.conf` has QDevice model `net`, algorithm `ffsplit`, `host: 192.168.2.48`, `tls: on`, `votes: 1`, config version `3`. Both Proxmox nodes' `corosync-qdevice.service` are running but show repeated connection timeouts, and `admin-01`'s `corosync-qnetd-tool -s` showed zero connected clients/clusters. The 2-node cluster `jameshouse-pve` is presently quorate with **2 votes out of 3 expected** (witness vote absent), so failure of either Proxmox host could cause quorum loss.

**Confirmed causal network mismatch:** `admin-01` is independently observed at DHCP **`192.168.2.127/24`**, so it does not currently own `.48` as QDevice clients require. Router `router-01` now has independently verified `dhcp-host=b8:27:eb:e8:36:cd,192.168.2.48` with dnsmasq active and syntax PASS; admin-01 has **not** renewed the old `.127` lease. This explains the failed connection to the configured endpoint; do not claim certificates/firewall or additional issues before re-checking after host reconnection.

**Next change not yet approved:** restore `admin-01` original IPv4 through a planned console-backed NetworkManager DHCP disconnect/reconnect of `netplan-eth0`; avoid running `nmcli connection down` over remote SSH. Preserve QDevice configuration on Proxmox and router DHCP configuration. Check the console and sudo access before interruption. Afterwards prove `admin-01 eth0 .48/24`, gateway/router reachability, Windows SSH `.48`, `corosync-qnetd-tool -s` restored client connections, both PVE `corosync-qdevice-tool -s` connected, and cluster quorum/witness vote. Only then update stale inventory/docs/DNS monitoring facts. This requires fresh explicit user approval, separately from prior router dnsmasq change. Tracked in [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206).


## 29 October 2026 — independent live router DHCP postflight PASS; admin lease remains .127

After approved admin-01 DHCP reservation playbook completed with Ansible recap **router-01 ok=33 changed=8 failed=0**, the operator independently inspected router-01. Live dnsmasq was **active**; `/etc/dnsmasq.d/router.conf` retained dynamic pool `192.168.2.100-199`, original ASUS MAC `24:4b:fe:5e:cc:c8` reservation at `.180`, and exactly one new Ansible-managed reservation `b8:27:eb:e8:36:cd -> 192.168.2.48`. `dnsmasq --test` passed; `unbound`, `router-pppoe`, and `nftables` were active. The **live lease** still showed `admin-01` at **192.168.2.127**.

This independently confirms the router side only, **not** admin-01 DHCP renewal or ability to SSH at .48. Keep host at the observed .127 until separately approved, console-backed NetworkManager DHCP renewal. This host also provides a Proxmox Corosync QNetd witness, so check quorum connectivity/dependencies and allow for SSH disruption. Do not change canonical inventory, DNS or host records to claim .48 is already active. Next step is read-only pre-cutover health checks and explicit host-side renewal approval. See issue #206 and the dated admin DHCP runbook.


## 29 October 2026 — approved router admin-01 reservation writer LIVE PASS, host still observed .127

User approved source-staged fixed admin-01 DHCP reservation plus dnsmasq restart following successful read-only operator preflight: router-01 **ok=17 changed=0 failed=0**. Scope: mapping b8:27:eb:e8:36:cd -> 192.168.2.48 on router-01, preserving the existing .180 ASUS reservation and the .100-.199 dynamic pool; accepted the small residual possibility of an offline static-IP host at .48. Prior router read-only: no .48 lease, zero ping replies, neighbour INCOMPLETE, dnsmasq --test OK.

User's live Ansible writer output ends with temporary candidate cleanup and **router-01 ok=33 changed=8 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0**. As deployed playbook had offline syntax staging, protected backup, scoped marked configuration write, dnsmasq restart and built-in postflight, successful recap means those stages did not fail. Changes count includes temporary work, not eight permanent router changes. **An independent router postflight is pending**, and no user output yet confirms admin-01 DHCP renewal to .48.

**Current last verified admin-01 address is 192.168.2.127, NetworkManager DHCP.** No administrator interface cutover or network service restart was approved beyond router dnsmasq. Keep admin host at .127 pending independent live router checks and *new* approval for console-backed NetworkManager renewal and Windows SSH reconnection. Do not update inventory/DNS to assert .48 prematurely. See router issue #206 and dated runbook docs/network/ROUTER-01-ADMIN01-DHCP-RESERVATION-2026-10-29.md.


## 29 October 2026 — admin-01 DHCP address drift; safe reservation IaC STAGED ONLY

**Operational incident/recovery:** The admin-01 physical Raspberry Pi 3 (eth0 MAC `b8:27:eb:e8:36:cd`) stopped responding at its documented `192.168.2.48`; ASUS `.2.2`, router `.2.1` and monitor `.2.52` were reachable. After operator reboot, SSH to `admin-01` at **`192.168.2.127`** works. NetworkManager active with `netplan-eth0`, `ipv4.method=auto`, DHCP server identifier `192.168.2.1`, 24h lease; Netplan has two separate DHCP YAML files, only one observed active NM profile. Router's `dnsmasq` active, dynamic pool `.100-.199`, existing independent ASUS reservation `24:4b:fe:5e:cc:c8 -> .180`, but **no admin-01 reservation**; lease record explicitly gives admin MAC -> `.127`. Router direct read-only target `.48` check: no lease, 3 ping losses, `ip neigh INCOMPLETE`, `dnsmasq --test` PASS. This does not exclude an offline statically assigned .48; no causal evidence ties address drift to restricted router-metrics SSH key installation.

**Current change status: SOURCE ONLY / NO LIVE ROUTER DHCP CHANGE.** Created GitHub-controlled, staged `router-01-admin-dhcp-reservation` read-only shared preflight, separately approval-gated writer and scoped rollback, CI syntax/safety checks and [dated runbook](docs/network/ROUTER-01-ADMIN01-DHCP-RESERVATION-2026-10-29.md). Proposed only `dhcp-host=b8:27:eb:e8:36:cd,192.168.2.48` with protected backup, offline candidate config, preservation of `.180` and `.100-.199`, and explicit permission gates for dnsmasq restart, conflict-risk acceptance and rollback. **Do not run the writer or issue DHCP renewal without further explicit approval and physical/alternative admin access.** Run read-only preflight first. No changes made to admin-01 NetworkManager, actual DHCP leases, dnsmasq, router/firewall or current inventory. Canonical `admin-01` identity is physically same MAC but presently at `.127`; original `.48` remains desired, not an observed active address. See [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206).


## 29 October 2026 — restricted router-metrics monitoring public key LIVE deployed (operator PASS)

**New live state:** After PR #231 and independent operator local syntax checks, the user explicitly approved the existing restricted Pi authorisation Ansible writer only. Operator ran `router-01-metrics-authorized-key.yml` with both inventories, targeted `router-01`, approved `router_metrics_authorize_apply_approved=true`. All real Pi MAC/IP, `router-metrics` UID999 home/nologin, on-disk sshd restriction, monitor-01 original private/public ED25519 pair and exact client fingerprint `SHA256:JB8L+7kC5lArmXoRLWfZThwuGblCjzeEHqYxct2JpqY`, and independently pinned genuine Pi host fingerprint `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI` assertions **PASS**.

Exactly **two router changes**: created `/var/lib/router-metrics/.ssh` owner UID999 mode `0700`; created `/var/lib/router-metrics/.ssh/authorized_keys` owner UID999 mode `0600` with one matching monitored ED25519 public key and `from="192.168.2.52",restrict,port-forwarding,permitopen="127.0.0.1:9100"` restrictions. Exact postflight content, file security and `sshd -t` PASS. Final **`router-01 ok=43 changed=2 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0`**. No sshd reload, SSH tunnel, firewall/router networking, exporter binding, or Prometheus change. The earlier router `.ssh=MISSING` baseline elsewhere in this file is now **historical**, not current.

**Next independent gate:** read-only physical Pi verification of installed `authorized_keys` (one constrained key, correct fingerprint, no unexpected keys/symlinks, UID999 and directory permissions) without printing key bytes. **Do not yet claim SSH authentication, working tunnel or Prometheus router node-metrics ingestion**; those are separate proposed future stages. All further changes via GitHub Ansible/IaC, separately approved, with [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209) and [runbook](docs/network/ROUTER-01-RESTRICTED-MONITOR-KEY-AUTH-2026-10-29.md) updated.


## 29 October 2026 — restricted router-metrics public key authorisation STAGED in IaC only; no router change

Fresh independent read-only `monitor-01` source key audit **PASS**:
```text
MONITOR_IDENTITY=PASS
PUBLIC_KEY_METADATA=PASS
PRIVATE_KEY_METADATA=PASS
PRIVATE_PUBLIC_KEY_MATCH=PASS
PUBLIC_KEY_ALGORITHM=ssh-ed25519
PUBLIC_KEY_FINGERPRINT=SHA256:JB8L+7kC5lArmXoRLWfZThwuGblCjzeEHqYxct2JpqY
PUBLIC_KEY_PREFLIGHT=PASS
```
This is the exact existing dedicated monitoring **client** public key fingerprint, *not* router server's ED25519 **host** fingerprint `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI` (already independently pinned and checked by the monitor account).

Previous physical Pi read-only check **PASS**: `router-01` real eth0 MAC `d8:3a:dd:5a:51:44`, address `192.168.2.1/24`, `router-metrics` UID999 and nologin, home `/var/lib/router-metrics` mode0700; `.ssh`/`authorized_keys`/`authorized_keys2` all **MISSING**; `sshd -T -C` public-key-only, strictmodes, local-only TCP forwarding, only `127.0.0.1:9100` destination, maxsessions0. These checks are on-disk policy not proof sshd active process reloaded configuration. Pi Node Exporter still loopback `127.0.0.1:9100`; no tunnel or Pi exporter scrape.

**SOURCE-ONLY IaC** branch `feature/router-01-restricted-monitor-key-authorisation-20261029` includes `IaC/ansible/playbooks/router-01-metrics-authorized-key.yml` writer, separate `router-01-metrics-authorized-key-rollback.yml`, offline CI safety/syntax workflow and [runbook](docs/network/ROUTER-01-RESTRICTED-MONITOR-KEY-AUTH-2026-10-29.md). The default-disabled writer requires `router_metrics_authorize_apply_approved=true` under separate explicit operator consent, exact controller/Pi/monitor checks, protected existing source ED25519 public/private match and *exact source SHA256*, independently trusted Pi host-key SHA256, router `sshd` policy, absent/expected-only SSH files. It uses **delegated Ansible slurp directly from monitor** in-memory, no key bytes in GitHub, writes exactly one `from="192.168.2.52",restrict,port-forwarding,permitopen="127.0.0.1:9100"` line to dedicated UID999 `authorized_keys` mode0600 and `.ssh` mode0700, verifies byte-for-byte and uses scoped rescue. Rollback separately requires `router_metrics_authorize_rollback_approved=true`, a no-active-tunnel attestation and trust fingerprint match before removal; only empty directory cleaned up. No key rotation, router sshd reload, DHCP/DNS/network/firewall, Node Exporter listener, actual tunnel or Prometheus changes.

**IMPORTANT:** **No router-side authorisation has been deployed or approved**. Operator next syncs merged source and runs only `--syntax-check` using BOTH inventories: `-i inventory/router-01-postcutover-baseline.yml -i inventory/hosts.yml`; new explicit operator approval is required before any live key installation. The next live step may need monitor and Pi sudo escalation; do not bypass secure delegation with manual key transfer. All changes through Ansible/IaC; keep [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209) updated.


## 29 October 2026 — independent postflight confirms Pi SSH trust pin as monitoring service user

Following separately approved live host-key installation on `monitor-01`, the operator ran a **separate read-only validation** (Ansible ad-hoc shell `CHANGED` is reporting convention, no writes). `lstat` verified `/etc/homelab/router-metrics-ssh/known_hosts` is an expected root-owned, protected, regular file: **`TRUST_FILE_SECURITY=PASS`**. `runuser -u router-metrics-tunnel -- ssh-keygen -F 192.168.2.1 -f /etc/homelab/router-metrics-ssh/known_hosts` succeeded (`LOOKUP_EXIT_CODE=0`) and returned **exactly one** recognised entry (`HOST_KEY_RECORDS=1`). SHA256 of that stored ED25519 public key independently matched the genuine physical Pi: **`PINNED_FINGERPRINT=SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`**, `HOST_PIN_POSTFLIGHT=PASS`. No key content was printed.

**State:** Monitor-side private-key ACL access PASS; the dedicated private/public key pair matches PASS; Pi host-key trust installed LIVE and independently postflight-verified PASS. **Do not claim SSH authentication or a working tunnel yet.** Pi-side `router-metrics` `authorized_keys` and `authorized_keys2` were absent at last read-only audit, with no `AuthorizedKeysCommand`. Next independently verify Pi service-user directory, effective sshd restrictions and monitor public-key fingerprint, then design a **separately reviewed and approved** Pi authorized-key change through Ansible/IaC. Node Exporter remains on Pi `127.0.0.1:9100`; no Prometheus router node-metrics ingestion established. See [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209).


## 29 October 2026 — monitor-01 router-01 SSH ED25519 host-key pin LIVE deployed, PASS

**OPERATOR LIVE PROOF:** After PR #228 fixed initial two-line `ssh-keyscan` failure, operator synced `admin-01` main to `af175185`, confirmed writer and rollback Ansible syntax PASS, and provided **fresh explicit approval** for the host-key pin ONLY. The corrected `IaC/ansible/playbooks/monitor-01-router-ssh-host-pin.yml` then executed successfully on `monitor-01 192.168.2.52`:
- Router SSH scan classification, no duplicate/conflicting key, exact SHA256 comparison to **direct physical Pi** fingerprint `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI` all PASS.
- `TASK [Append only verified router key to existing dedicated trust file]`: **changed**.
- Dedicated `router-metrics-tunnel` SSH host-pin lookup matches the verified key **PASS**.
- Existing `root:root 0644` protected `/etc/homelab/router-metrics-ssh/known_hosts` ownership/mode and non-symlink status **PASS**.
- Exact Ansible recap: **`monitor-01 ok=27 changed=1 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`**. No rollback attempted. No router key authorisation, SSH authentication, sshd reload, tunnel, exporter/firewall or Prometheus change. The *earlier failed* attempt `ok=10 changed=0 failed=1` is resolved and superseded by this **verified successful live deployment**.

**CURRENT STATE:** local restricted private-key access and public/private pair PASS; **dedicated SSH host-key trust for `router-01 192.168.2.1` is now LIVE and verified by writer postflight**. Next independent read-only postflight may confirm exact record/fingerprint from `monitor-01` as the service identity without printing raw keys or opening SSH. **The Pi `router-metrics` authorised keys remain absent** from previous audit; do not start SSH tunnel or claim router node metrics ingestion. Next changes require separate, reviewed, opt-in Ansible/IaC authorisation of existing monitor public key, then a container-aware SSH tunnel design. Pi Node Exporter remains `127.0.0.1:9100` only. See [host pin runbook](docs/network/MONITOR-01-ROUTER-SSH-HOST-PIN-2026-10-29.md) and [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209).


## 29 October 2026 09:45 UTC — scheduled DHCP/router reconciliation checkpoint (GitHub read-only review)

This is a **repository-only review**, not a new Pi/ASUS probe or deployment. Current operator-verified truth, from main-branch runbooks and `docs/architecture/CURRENT-STATE.md`: physical Pi `router-01` serves `192.168.2.1/24`, PPPoE default via `ppp0`, dnsmasq DHCP single `192.168.2.100–199` 24h pool and router/DNS `.2.1`, Unbound and nftables active. ASUS Home `192.168.2.2` is static AP/AiMesh controller. ASUS Bedroom Ethernet-backed AiMesh at `192.168.2.180` has a **LIVE verified MAC-bound dnsmasq reservation**, deployed by approved Ansible PR #219 with operator recap `ok=28 changed=9 failed=0` and independent postflight PASS. Third ASUS unused; old `.181` is NOT a verified current node. `media-01` is **online and DHCP-managed** at `192.168.2.195`, `NetworkManager ipv4.method=auto` and default route from DHCP via `.2.1`; its *fixed reservation* is still pending independent MAC verification and separate approval. **DO NOT apply historical DHCP split-range exclusion for `.181/.195`**. Current `router-01-dhcp-exclusion-preflight-readonly.yml` incorrectly assumes zero `dhcp-host` rules; do not run until updated to accept the real Bedroom `.180` reservation.

The 28 Oct 22:09 UTC read-only Pi baseline was **actually run and passed** (`ok=15 changed=0`), with CPU 0.1%, 45.3°C, throttling 0x0, zero interface errors, 0% WAN packet loss/10.502ms mean, 18 DHCP lease rows. Safe baseline files/report selectively merged by PR #211. Later 29 Oct read-only Loki/Zabbix connectivity audit from Pi and admin-01 also passed (`ok=14 changed=0`); this does not imply monitoring agents/tunnel are activated. monitor-01 private-key directory traverse ACL was separately approved and deployed (`ok=24 changed=2`); Pi monitoring authorized_keys still absent. The genuine Pi ED25519 fingerprint `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI` was verified independently from Pi and monitor-01, but the initial host-pin writer **failed closed before writing trust** because `ssh-keyscan` returned 2 output lines with exactly 1 valid ED25519 record. A filtered-scan fix is merged in main at `af175185`, **not evidence the pin was installed**. Fresh explicit operator approval required before retrying host pin. No SSH reload, monitoring key authorisation, tunnel or firewall change is authorised.

**GitHub PR state checked 29 Oct 09:45 UTC:** PR #211 **merged**; legacy PRs #207, #208 and #210 are now **CLOSED UNMERGED** (some older issue #209 text still calls them draft/open; do not follow it). Issue #209 remains OPEN. Canonical `IaC/inventory/estate.json` is **still stale**: `asus-router` wrongly `.2.1` router/DHCP, legacy mesh `.181/.218`, missing Pi `router-01`. Reconcile with a new, separately reviewed, validator-tested IaC change using the verified `.2.1` Pi, `.2.2` ASUS AP, `.180` Bedroom and explicit uncertainty for other devices; do not invent or overwrite unknown asset identities. Keep the existing `router-01-postcutover-baseline.yml` as safe isolated target; **never run old `.3.1` SSH/migration writer playbooks**.

**NEXT READ-ONLY priorities:** (1) inspect current dnsmasq active scope, `dhcp-host` reservations and unexpired leases with MAC values handled privately, verify `media-01 .195` client MAC before proposing a reservation; (2) inspect DHCP option 3/6, DNS response, PPPoE route, LAN/firewall status and duplicate-IP risk; (3) verify ASUS Home `.2.2` static AP/AiMesh mode and Bedroom `.180` Ethernet backhaul without altering settings; (4) update obsolete DHCP preflight to permit the existing `.180` reservation, then run it in check mode after review; (5) stage canonical inventory + current-state + Ansible SSH target reconciliation as separate, reviewed source changes, with regression tests; (6) keep further SSH reload, key authorization/tunnel, DHCP/network changes and cutovers **ON HOLD**. Reference issue #209 (monitoring) and issue #206 (DHCP/router cutover), plus `docs/network/ROUTER-01-BEDROOM-ASUS-DHCP-RESERVATION-2026-10-29.md`. This handover entry is **documentation-only**; no live changes or tests were performed in this checkpoint.


## 29 October 2026 — monitor-01 SSH host-pin initial deployment stopped, filtered scan fix SOURCE ONLY

After the operator fast-forwarded local `admin-01` main to `57cfec26` and both host-pin/rollback syntax checks passed, the user explicitly approved the live host-pin action **only**. The `monitor-01-router-ssh-host-pin.yml` writer stopped at `host_pin_scan.stdout_lines | length == 1`: `monitor-01 ok=10 changed=0 unreachable=0 failed=1 skipped=0 rescued=0`. The `known_hosts` trust pin **WAS NOT INSTALLED**. This is a safe gate failure, not a router-key mismatch.

The operator's follow-up read-only diagnostic: `ssh-keyscan -T 5 -t ed25519 192.168.2.1` returned `rc=0`, `OUTPUT_LINES=2`, `VALID_ED25519_LINES=1`, `UNIQUE_FINGERPRINTS=1`, `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`, `EXPECTED_FINGERPRINT_PRESENT=True`. The second line's type/content was not displayed, so do not invent it. The initial one-total-line check (and `stdout_lines[0]` assumption) were overly restrictive. A **source-only** correction on branch `fix/monitor-01-host-pin-ssh-keyscan-record-filter-20261029` filters for exactly one valid current-Pi ED25519 record, fails on any other recognisable SSH host-key record, and cryptographically matches the independent physical-Pi SHA256 fingerprint **before** any trust write. Additional non-key stdout may be tolerated. CI adds synthetic cases for banner, no key, duplicate and unexpected key. No weaker SSH verification, no router/monitor runtime changes, no auto-accept and no replacement keys.

**Next**: CI check and source-only PR merge, `admin-01` sync/syntax check, then **fresh, explicit** approval before trying the corrected writer. The prior approval does not silently authorise another run. Pi `authorized_keys` and secure tunnel remain entirely separate, unapproved stages. See [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209) and [host pin runbook](docs/network/MONITOR-01-ROUTER-SSH-HOST-PIN-2026-10-29.md).


## 29 October 2026 — genuine Pi SSH host key verified from monitor-01; trust pin source STAGED, NOT EXECUTED

The operator read physical `router-01`'s actual `/etc/ssh/ssh_host_ed25519_key.pub` fingerprint directly after Pi MAC and live LAN `192.168.2.1/24` identity checks **PASS**: `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`. From `monitor-01` the operator then read the network-presented ED25519 key via **read-only** ssh-keyscan and compared the SHA256 fingerprint: **`ROUTER_HOST_KEY_MATCH=PASS`**. The existing dedicated host pin for `192.168.2.1` was **MISSING**. These facts independently establish genuine network host identity *for this observed key*, not existing SSH trust. No remote key acceptance, connection auth, pinned trust or tunnel has been executed.

The existing monitor-01 `router-metrics-tunnel` private/public key pair has also independently passed service-user parse and exact public/private match, following the approved live ACL repair (`ok=24 changed=2 failed=0`). The on-Pi `router-metrics` `authorized_keys` and `authorized_keys2` are still absent.

**New source-only, approval-gated IaC** on branch `feature/monitor-01-router-ed25519-host-pin-20261029`: `IaC/ansible/playbooks/monitor-01-router-ssh-host-pin.yml` (exact admin-01 to monitor-01 identity; verifies one ED25519 key's fingerprint against physical Pi; refuses mismatched existing pins; preserves root-owned `known_hosts` file and other entries; adds one audit-marked line only with explicit `router_host_pin_apply_approved=true`; checks dedicated service-user access; attempts to remove newly added line on failed postflight); `monitor-01-router-ssh-host-pin-rollback.yml` (separate approval, no-active-tunnel gate; removes only marker after exact fingerprint validation), CI workflow and [dated runbook](docs/network/MONITOR-01-ROUTER-SSH-HOST-PIN-2026-10-29.md). **Source is NOT live trust installation and is NOT operator approval to deploy.** No key bytes are committed to Git. No router SSH, Prometheus, Node Exporter, firewall or tunnel change is included.

**Next:** check CI and PR file scope, merge source, operator syntax-check from admin-01, request separate live host-trust approval. Only after successful live pinning, prepare Pi service authorised public key through new independently gated Ansible/IaC; tunnel and secure Docker-bridge integration require independent design and approvals. Track [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209).


## 29 October 2026 — LIVE monitor-01 traverse-only ACL repair deployed and verified (supersedes source-only preflight below)

**OPERATOR-VERIFIED LIVE SUCCESS.** After separate user approval of both installing Debian `acl` and applying a named-user traverse-only ACL on `/etc/homelab`, the operator ran the previously merged approval-gated `IaC/ansible/playbooks/monitor-01-router-metrics-acl-traverse.yml` on `monitor-01`. Pasted playbook tail confirmed `runuser` service-key readability **PASS**; non-login account private-key parsing **PASS**; root/group directory and private-key owner/mode assertions **PASS**; final debug: `Traverse-only named user ACL for router-metrics-tunnel: PASS`; private key `0600` and ownership unchanged; no Pi/sshd/SSH trust/tunnel/firewall/exporter/Prometheus edits. **Ansible recap: `monitor-01 ok=24 changed=2 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`.** The two changes are consistent with package install and named ACL application, but the pasted tail did not show individual package and ACL task output; preserve that evidence distinction.

**STATE:** This ACL repair is **LIVE**, not merely source-only. The linked source-only runbook and previous handover below describe its earlier preflight state and are superseded by the deployment postflight. Rollback playbook remains in repo for separately approved future use; it was **not** invoked. Do not recreate the SSH key or weaken `/etc/homelab` globally.

**NEXT GATES — still NOT implemented:** From monitor-01 independently verify private/public key match without printing contents; fetch Pi's genuine ED25519 public-host-key fingerprint locally on physical `router-01 192.168.2.1`, check it against a carefully verified pinned host-key entry (currently missing at last check). Pi `router-metrics` had neither `.ssh/authorized_keys` nor `.ssh/authorized_keys2` (and no AuthorizedKeysCommand), so a new public-key authorisation needs separate approved IaC; do not force SSH authentication, auto-accept host key, expose TCP/9100 or start tunnel yet. Prometheus Docker bridge is `monitoring_default` with gateway `172.18.0.1`; monitor host-loopback forwarding would not automatically be container reachable, needing a separately reviewed network path. Source [runbook](docs/network/MONITOR-01-ROUTER-METRICS-ACL-ACCESS-2026-10-29.md), [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209).


## 29 October 2026 — monitoring SSH key access blocker found on monitor-01; ACL FIX SOURCE ONLY, NOT RUN

After Prometheus transport/ICMP audit, independent on-host Pi and `monitor-01` investigation showed Node Exporter already serves `http://127.0.0.1:9100/metrics` (HTTP 200, 1547 `node_` lines), but `monitor-01` Prometheus has no confirmed Pi node-exporter scrape. The restricted `router-metrics` SSH policy on Pi is already configured (`permitopen 127.0.0.1:9100`, local forwarding only, noninteractive) but **both authorised-key files are absent**. Monitor-01 bridge `monitoring_default` is `172.18.0.0/16` with gateway `.0.1`; port 19100 unused, no matching tunnel unit; monitor-side `router-metrics-tunnel` UID 992 has a private key at `/etc/homelab/router-metrics-ssh/id_ed25519` (mode 0600, owner account). Host-key pin for the current Pi `192.168.2.1` **missing**. Nothing has authenticated or forwarded yet.

**ROOT CAUSE of current key parse/access failure:** operator read-only `namei -l` showed `/etc/homelab root:root 0750`, child `router-metrics-ssh root:root 0755`, private key `router-metrics-tunnel:router-metrics-tunnel 0600`. Root `ssh-keygen -y` parses the existing OpenSSH private key **PASS**, service identity cannot even read it (**FAIL**). **Do not regenerate key, change key mode, or make the root parent world traversable.** Subsequent audit confirmed `getfacl` and `setfacl` **both MISSING** on `monitor-01`; this establishes absent ACL utilities, not proof the filesystem lacks ACL support. `/etc/homelab` owner root:root, mode 750. Read-only commands report Ansible shell `CHANGED rc=0` by convention, without filesystem edits.

**Prepared new source-only IaC** under PR branch `feature/monitor-01-router-metrics-acl-traverse-20261029`: `IaC/ansible/playbooks/monitor-01-router-metrics-acl-traverse.yml` (two explicit false-by-default package/ACL approvals, exact `monitor-01` and `admin-01` guards, APT simulation rejecting unrelated removals/additions, root/UID/mode checks, install *only* Debian `acl` package, apply named-user **traverse-only** `u:router-metrics-tunnel:--x` on `/etc/homelab`, verify effective permissions and service-user private-key parser without output, rescue removes new rule on postflight failure); independently gated `monitor-01-router-metrics-acl-rollback.yml` removes only that named-user ACL, never deletes keys/uninstalls package; dedicated offline CI validation and dated [runbook](docs/network/MONITOR-01-ROUTER-METRICS-ACL-ACCESS-2026-10-29.md). **No host package, ACL, SSH, router, Docker or monitoring change has been run**; source must pass CI and be reviewed/merged before any separately approved live maintenance.

**Next gates:** review CI and exact files, operator syntax-check on `admin-01`, explicit live package+ACL approval, check service-user can parse key. After that, independently verify public/private key match, strictly pinned Pi host key (missing), Pi `authorized_keys` (missing), and container-safe SSH tunnel design, each with new review/approval. Keep `router-01` Node Exporter at loopback only, do not edit firewall or expose TCP/9100 on the Pi, and never reuse old `192.168.3.1` branch scripts. Findings and status in [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209).


## 29 October 2026 — LIVE router-01 monitoring path audit PASS (read-only)

After merge of [PR #221](https://github.com/jrwroberts1976/homelab-platform/pull/221), operator on `admin-01` fast-forwarded `main` to `06c00912`, then ran syntax-check **PASS** and `playbooks/router-01-monitoring-path-readonly.yml` using `inventory/router-01-postcutover-baseline.yml`, `--limit router-01 --check -e router_monitoring_path_audit_approved=true`. **Final recap `router-01 ok=14 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`.** Exact controller, physical Pi Ethernet MAC and `eth0 192.168.2.1/24` safeguards PASSED. Both `admin-01 192.168.2.48` and Pi `router-01 192.168.2.1` routed directly on `eth0` to Loki `192.168.2.52` and Zabbix `192.168.2.59`. Loki `http://192.168.2.52:3100/ready` gave **HTTP 200 from each host**. Zabbix TCP/10051 was **connected=true from both hosts**. Both paths healthy; no network/firewall change needed to establish these endpoints.

This was an actual operator-run read-only check, **not** just CI. No packages, services, SSH keys, exporter listeners, agent configuration, firewall or routes were modified. **Do not interpret HTTP readiness or TCP socket reachability as proof of Loki log ingestion, Zabbix item values, Prometheus scraping, Node Exporter tunnel, SSH credentials or dashboard data.** Next gate is read-only discovery of existing agents/listeners/configuration (prefer no credential disclosure) and query-side metric/log ingestion evidence before proposing separately approved additions. Track issue #209; dated [audit reconciliation](docs/network/ROUTER-01-MONITORING-AUDIT-RECONCILIATION-2026-10-29.md). The previous handover claim that no live monitoring probe had run is a **historical pre-audit statement**, superseded by this entry.



## 29 October 2026 — legacy router PR merge reconciliation (source-only)

After the separate successful live ASUS Bedroom DHCP reservation and independent Pi LAN/DNS/HTTPS postflight, the only old open GitHub drafts were **#207** (retired `192.168.3.1` Kea/PPPoE/Netplan/IP switch and `docker-01` BirdNET/Komodo retirement writer) and **#210** (older `.3.1` router diagnostics, SSH/monitoring tools). **Neither draft should be merged wholesale or run**: current physical `router-01` already works at `192.168.2.1` with `dnsmasq`, and `docker-01` remains an independent in-use BirdNET/Komodo host, not the new gateway. Source-only [PR #221](https://github.com/jrwroberts1976/homelab-platform/pull/221) recovered only a read-only Loki/Zabbix monitoring path diagnostic from #210, rebuilt for the current `.2.1` Pi and exact `admin-01`/MAC/`--check` guards; **both CI checks passed; it was merged**. No on-host monitoring probe run or agent/SSH/package activation is claimed. Remaining #210 packages, secure metrics/SSH writers and exporter/agent configuration remain unmerged and tracked under issue #209. Dated [PR #210 reconciliation](docs/network/ROUTER-01-MONITORING-AUDIT-RECONCILIATION-2026-10-29.md) documents what to review next.

The old #207's disruptive Docker retirement and `.3.1` change scripts are superseded, not authorised for any operational use. [PR #207 disposition](docs/network/ROUTER-01-PR207-MIGRATION-RETIREMENT-2026-10-29.md) records why this branch is historical and must not be used to remove live Docker/BirdNET/Komodo or replace the verified `.2.1` gateway. **Final PR housekeeping verified:** drafts [#207](https://github.com/jrwroberts1976/homelab-platform/pull/207) and [#210](https://github.com/jrwroberts1976/homelab-platform/pull/210) were both **CLOSED AS SUPERSEDED, NOT MERGED**, after scoped [PR #221](https://github.com/jrwroberts1976/homelab-platform/pull/221) and docs [PR #222](https://github.com/jrwroberts1976/homelab-platform/pull/222) merged with CI PASS. The original branches/history remain available; no old migration, Docker-retirement or router monitoring writers were cherry-picked or executed. **GitHub open PR count: zero at this review.** `media-01 .195` remains DHCP, with optional separate reservation pending MAC verification; broader DHCP issue #206 is not complete merely because Bedroom .180 is.


## LATEST VERIFIED — 29 October 2026: Bedroom ASUS DHCP reservation DEPLOYED; full LAN, DNS and HTTPS postflight PASS

**Live change complete** on the real Raspberry Pi `router-01` at `192.168.2.1`, via approved Git-managed Ansible `IaC/ansible/playbooks/router-01-bedroom-dhcp-reservation.yml` (source from merged PR #219, commit `7ff09647`). The operator fast-forwarded `main`, both deployment and rollback `ansible-playbook --syntax-check` passed, and the privately encrypted Ansible Vault file for the Bedroom client MAC returned `BEDROOM_MAC_VAULT=PASS` without disclosing its contents. **Deployment recap:** `router-01 ok=28 changed=9 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`. Ansible's guarded writer backs up `router.conf` privately outside dnsmasq's active include path and does a targeted dnsmasq restart; the operator supplied only the final task and recap, not the exact runtime backup filename. Automatic rescue was **not** invoked.

**Independent read-only postflight:** all four `systemctl is-active` statuses were `active`: `dnsmasq`, `unbound`, `router-pppoe`, `nftables`; `dnsmasq --test` returned `syntax check OK`. Assertions returned `DHCP_POOL=PASS`, `BEDROOM_RESERVATION=PASS`, `BEDROOM_LEASE=PASS`. This proves exactly one intact dynamic range `dhcp-range=192.168.2.100,192.168.2.199,255.255.255.0,24h` and exactly one active `dhcp-host` bound to `192.168.2.180`; the unexpired lease IP, name `RT-AC86U-CCC8` and private DHCP client MAC match the installed reservation. IPv4 default route still `default dev ppp0 scope link`. The check reported `router-01 | CHANGED | rc=0` because ad-hoc shell defaults to changed; the postflight script made **no writes**.

**Independent controller-side client/connectivity test on `admin-01`:** ICMP **PASS** for `192.168.2.1` Pi router, `192.168.2.2` ASUS Home static AP/AiMesh controller, `192.168.2.180` ASUS Bedroom DHCP fixed reservation, and `192.168.2.195` `media-01`. Direct DNS query `dig @192.168.2.1 example.com A` returned **NOERROR** with two A answers (`172.66.147.243` and `104.20.23.154` at test time); independent HTTPS request to `https://example.com` returned **HTTP 200**. Thus LAN host reachability, the Pi's DNS resolution and outbound client HTTPS passed after the restart. No proof of Bedroom **subsequent DHCP renewal** or future reboot persistence yet; configured reservation and a matching current, unexpired lease **were** observed.

**ASUS/media-01 inventory reality:** Home `.2` is manually static, Bedroom `.180` DHCP with now-live MAC-bound reservation, the third ASUS is unused and old `.181` not confirmed active. `media-01` came online and was independently observed on `eth0 192.168.2.195/24` with `NetworkManager` active, `nmcli ipv4.method=auto`, `default via 192.168.2.1 ... proto dhcp`. Thus `.195` is **DHCP, NOT static**; any fixed `.195` reservation is a **separate unimplemented** project requiring its own verified client MAC and source/approval. **Do NOT run the obsolete `.181/.195` split-pool proposal**; neither IP should be blindly excluded. The old `router-01-dhcp-exclusion-preflight-readonly.yml` assumes zero `dhcp-host` entries and is now **incompatible with the live desired state**; replace or update it before another audit, do not mistake its expected failure for DNS drift. Canonical `IaC/inventory/estate.json` still requires a separate controlled post-cutover reconciliation using verified active identities; past historical `asus-router` references to `.2.1` are obsolete.

**Status:** Bedroom .180 reservation **operationally completed and independently verified**; backups and rollback Ansible remain available. No further dnsmasq, WAN, firewall or ASUS edits are approved by this entry. Evidence: [Issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206) and [dated DHCP reservation runbook](docs/network/ROUTER-01-BEDROOM-ASUS-DHCP-RESERVATION-2026-10-29.md). Remaining follow-ups: media-01 fixed reservation if desired, obsolete read-only DHCP preflight update, and registry/current-state reconciliations. Avoid merging the unrelated legacy router migration/toolset PRs wholesale.


## HISTORICAL PREPARATION — 29 October 2026: Bedroom ASUS DHCP reservation source-only stage (superseded above)

**Verified real ASUS topology:** Pi `router-01 192.168.2.1` currently provides gateway/DNS/dnsmasq `192.168.2.100–199`; ASUS Home/AiMesh controller is **statically** `192.168.2.2` in AP mode; ASUS Bedroom RT-AC86U is **DHCP-managed** at `192.168.2.180`, Ethernet AiMesh. Local read-only Python comparison against dnsmasq leases gave `RESULT: MAC MATCHES ASUS GUI` for exact `.180` lease hostname `RT-AC86U-CCC8`. Bedroom MAC is NOT committed in plain text: must be passed via a protected private Ansible Vault vars file. Historical `RT-AC86U-5228`/`6238` leases at old `192.168.3.x` do not prove live device presence; user says third ASUS unused. Old `.181` failed ARP; do not exclude it blindly. `media-01 .195` remains offline/unverified for static-vs-DHCP. The previous 3-way exclusion design is **superseded as an implementation recommendation** and its historical plan is annotated, not erased.

**New Git-only branch `feature/router-01-bedroom-dhcp-reservation-20261029`:** includes separately approval-gated `IaC/ansible/playbooks/router-01-bedroom-dhcp-reservation.yml` and `router-01-bedroom-dhcp-reservation-rollback.yml`, private-MAC requirement, exact physical Pi/eth0/PPPoE/DHCP/lease guards, offline candidate full-config parse, off-path root-only backup, targeted single marked `dhcp-host` line in existing `router.conf`, dnsmasq restart **only after explicit, separately reviewed maintenance-window approvals**, failure recovery and independent rollback. A CI workflow performs Ansible syntax/safety checks and synthetic installed dnsmasq parser test. Documentation: `docs/network/ROUTER-01-BEDROOM-ASUS-DHCP-RESERVATION-2026-10-29.md`. **None of these playbooks has been run**, no DHCP restart, lease rewrite, LAN subnet change or ASUS config change. The current Pi's sole dynamic pool `.100-.199` remains untouched.

**Next gate:** review new PR file scope + CI, then have the operator explicitly approve a short dnsmasq maintenance window and supply the correct MAC in a private Ansible Vault file on `admin-01`; do not place it in a GitHub issue or shell history. Reverify current `.180` unexpired lease and router identity just before deploying. Postflight requires dnsmasq active, DNS/WAN connectivity, AiMesh Bedroom continues at .180 after lease renew. Previous read-only `router-01-dhcp-exclusion-preflight-readonly.yml` will reject `dhcp-host` after eventual activation; adapt it before future audits. Old router migration PR #207 and toolkit PR #210 remain separately gated, not safe to merge wholesale. Actual deployment must update this handover and issue #206 with operator-run evidence.


## NEWEST VERIFIED — 29 October 2026: Pi DHCP exclusion preflight 20/20 PASS, no router changes

Operator on `admin-01` updated `main` to `43c69dbf` and confirmed clean `## main...origin/main`. After syntax-check PASS, ran **merged** `IaC/ansible/playbooks/router-01-dhcp-exclusion-preflight-readonly.yml` via `inventory/router-01-postcutover-baseline.yml`, `--limit router-01 --ask-become-pass --check -e router_dhcp_exclusion_preflight_approved=true`. Final **`router-01 ok=20 changed=0 unreachable=0 failed=0 skipped=0`**. Exact trusted controller, physical Pi MAC, `eth0 192.168.2.1/24`, active dnsmasq, loaded `/etc/dnsmasq.d` exactly `README` and `router.conf`, unchanged single `192.168.2.100–199/24 24h` range, gateway/DNS `.2.1`, no unexpected DHCP directives, syntax test PASS and active service after: **all assertions PASS**. Lease-file IP rows **21** (18 in previous snapshot, identities of three additional rows unknown); no current lease entry at historically documented `192.168.2.181` (AiMesh) or `.195` (media-01, offline), and a `.198` record remains. **No DHCP change was deployed**, no dnsmasq reload/restart, no lease deletion. Reported split ranges `.100–.180`, `.182–.194`, `.196–.199` are **conditional candidate only**, not applied. Absence of a lease is not proof of a static assignment or offline client. Verify ASUS actual management address/static-vs-DHCP and media-01 intended addressing before deciding exclusion vs explicit reservations; a separate review, rollback and approval are mandatory for writer. Evidence in `docs/network/ROUTER-01-DHCP-EXCLUSION-PLAN-2026-10-28.md` and issue #206. Old router PRs #207/#208/#210 remain drafts, not safe for bulk merge. Canonical estate.json still needs post-cutover reconcile; no blind updates.


## 29 October 2026 — Grafana patch PR #204 docs-only reconciliation (NO RUNTIME UPDATE)

The current main repository already has the **approval-gated** `IaC/ansible/playbooks/grafana-security-patch-1324.yml`, validated source pin `monitoring_grafana_image: grafana/grafana:13.2.4`, corresponding secondary Komodo reference `compose.yml`, and `scripts/validate-grafana-security-patch-1324.py`. **This does not establish the live monitor-01 Grafana image has been upgraded.** Former open PR #204 is 92 commits behind main and has only its dated 27 October runbook plus an obsolete first-page handover prefix remaining in its current diff. Reconcile just the runbook with an explicit 29 Oct caveat: target playbook expects old live 13.2.1 and may fail closed if runtime has changed; no restart, Docker image pull or live patch is performed by docs merge. Before any deployment, read-only current runtime/Compose/SQLite verification, operator approval, risk review and backups/rollback are required. The original #204 is to be closed as superseded **only after** the replacement documentation PR is merged and confirmed; keep exact IaC as-is in main.


## 29 October 2026 — old security remediation PR #188 reconciled with current Pi topology (SOURCE ONLY)

The 20 October Greenbone Full LAN (7 Medium/25 Low) and Managed Infrastructure (0 actionable) email snapshots, plus five-host Trivy 191 Critical package-occurrence historical baseline, were preserved as **dated** evidence in `docs/security/SECURITY-REMEDIATION-PROGRAMME-2026-10-20.md`. The original PR #188 is approximately 400 commits behind current main and its stale 20 Oct device attribution must not be merged blindly. The reconciled plan explicitly marks the ASUS `192.168.2.1` scanner finding as a **historical target**, NOT a vulnerability observed on the now-active Pi `router-01 192.168.2.1`; ASUS AiMesh `.181` and offline media-01 `.195` have unverified current static/DHCP ownership. The Greenbone/Trivy metrics and 20 Oct scan counts are snapshots; current fresh scan and host/image identity checks are still necessary. A minimal planning link was added in `ACTIVE-INFRASTRUCTURE-BACKLOG.md`, without replacing more recent `CURRENT-STATE.md` or changing current operational priorities. **No scans, containers, routing, DHCP or service changes**. Original #188 may be closed as superseded only after the replacement PR passes CI and merges. Continue technical work in issue #187 with per-workload verified IaC changes/rollback after approval.


## 29 October 2026 — Nextcloud certificate renewal evidence recovery (docs-only)

The historical 26 October 2026 Nextcloud certificate renewal verification from old PR #190 was reconciled onto current `main` in a fresh **documentation-only** branch after GitHub rejected a direct merge as conflicting. The dated evidence added to `docs/security/NEXTCLOUD-HTTPS-HARDENING.md` records Certbot 4.0.0 with Cloudflare DNS validation, enabled renewal timer at test time, production certificate expiry 2027-01-19, staging `certbot renew --dry-run` PASS, successful isolated deploy-hook Nginx reload at 08:17:32 GMT, and HTTPS health PASS. **No real production certificate renewal was observed**, and Cloudflare Python library 2.20.x dependency deprecation review remains open. This Git-only integration runs no Ansible and changes no actual certificate or Nginx process; do not infer deployed state from a documentation merge. Original PR #190 needs to be closed as superseded only after the replacement PR passes CI and merges.


## LATEST — 28 October 2026: DHCP static-pool conflict audit complete; guarded source-only preflight STAGED

Live on physical Pi `router-01` at `192.168.2.1/24` with `dnsmasq` active: actual `/etc/dnsmasq.d/router.conf` contains `interface=eth0`, `bind-dynamic`, `dhcp-authoritative`, **one `dhcp-range=192.168.2.100,192.168.2.199,255.255.255.0,24h`**, DHCP router and DNS options both `192.168.2.1`. No DHCP host/reservation/exclusion entries surfaced in direct file grep. Debian vendor `dnsmasq.service` has no drop-ins; active systemd-helper launches dnsmasq with `-7 /etc/dnsmasq.d,.dpkg-dist,.dpkg-old,.dpkg-new`; directory contains `README` and `router.conf`. `dnsmasq --test` PASS. Output is **read-only** although ad-hoc Ansible shell reports `CHANGED` by default. On prior user lease inspection, 15 current pool addresses unexpired at observation, plus 3 legacy `192.168.3.x` records (until 29 October); **no lease** for `.181` or `.195`. Empty neighbour entries for those addresses prove neither ownership nor lack of conflict. Canonical `IaC/inventory/estate.json` validated 17 Sep still lists AiMesh node `.181` and `media-01 .195` inside dynamic scope. **media-01 offline**, AiMesh IP and both static/DHCP modes unverified. No confirmed duplicate address; potential future allocation collision exists.

**Source-only change in feature branch `feature/router-01-dhcp-exclusion-preflight-20261028`**: read-only Ansible `IaC/ansible/playbooks/router-01-dhcp-exclusion-preflight-readonly.yml`, separate GitHub workflow `.github/workflows/validate-router-01-dhcp-exclusion-preflight.yml`, detailed `docs/network/ROUTER-01-DHCP-EXCLUSION-PLAN-2026-10-28.md` and this handover. Conditional proposed three same-subnet DHCP ranges **`.100-.180`, `.182-.194`, `.196-.199`**, keeping 98 of the original 100 addresses, all 15 observed live-subnet lease IPs (including .198), original netmask and 24h lease duration. Excludes exactly `.181`, `.195` *only if independently confirmed to require static protection*. Debian trixie dnsmasq manpage permits multiple DHCP ranges in one subnet. Ansible preflight requires trusted controller admin-01, exact Pi MAC, current `.2.1` inventory, `--check` and explicit approval, checks config fragments and active scope; outputs preview; **NO writer/reload/lease edits**. Static source validation required in CI. Do not merge blind if CI fails.

**Next gates:** confirm ASUS AiMesh management and static-vs-DHCP status; verify media-01 intended static assignment when available (do not power it on just for this); run source review/CI then guarded read-only preflight from admin-01. Only then design a separate approved writer with full effective candidate syntax check, backups, rollback and low-risk activation; keep live dnsmasq untouched. The prior PPPoE MSS fix was independently verified and merged read-only (#211/#212/#213); old router PRs #207/#208/#210 remain draft. Existing local main tree was cleaned and synchronised by the operator earlier.


## LATEST — 28 October 2026: live Pi 192.168.2.1 MSS audit PASS after PR #212 merge

Operator on `admin-01` confirmed fast-forward of `main` to `6c573fee`, Ansible syntax PASS, then ran `router-01-mss-postcutover-readonly.yml` with isolated new Pi inventory, `--check`, become password and `-e router_mss_postcutover_audit_approved=true`. **PLAY RECAP router-01 ok=16 changed=0 unreachable=0 failed=0 skipped=0**. All exact controller/MAC/eth0 `192.168.2.1/24`/PPPoE default-route and MTU 1492/IPv4 forwarding checks passed. `nftables`, `router-pppoe`, `dnsmasq`, `unbound` active before and after. Live default-drop filter and NAT masquerade check PASS; **two bidirectional TCP MSS set 1452** rules in `table ip router_pppoe_mss` present. Persistent `/etc/nftables.conf` had one managed MSS block and syntax `nft -c -f` **PASS**; obsolete `pppoe_mss_test` table **absent**. Both `live_nat_mentions_new_lan_subnet` and `disk_nat_mentions_new_lan_subnet` **true** for `192.168.2.0/24`. This proves subnet text presence, not complete NAT predicate equivalence or traffic/capacity tests. **No live router modifications** by audit.

**Git integration decision:** Preserve verified results in a small documentation-only branch and merge after estate/docs CI. Existing PR #208 writer/inventory is **still pinned to historical .3.1/.3.0/24**, so avoid merging or rerunning it on current gateway; the persistent fix is already active and needs no blind restage. PR #207 contains historical Kea/firewall migration and remains held; PR #210 SSH activation remains held. DHCP .100–.199/static .195 collision possibility, estate.json drift, and ASUS management address still outstanding.

**Local worktree note:** user showed untracked `IaC/ansible/FETCH_HEAD`, `IaC/ansible/localhost]`, and `IaC/ansible/{` before switching feature branch to `main`. These are not evidence of network change. Do not auto-delete or `git clean -fd` them; inspect safely before cleanup.


## 28 October 2026 — MSS PR #208 split: safe post-cutover verification staged

The operator approved continuing GitHub merges after safe read-only baseline PR #211 was squash-merged (main `851a915f94f57e325faec7cc18b52cea3d7d5af8`). Audit of historical draft PR #208 confirms the original 28 Oct live reboot **did** load `table ip router_pppoe_mss` with bidirectional 1452-byte SYN clamp and matched packets; the *writer* playbook and isolated inventory still assert `eth0 192.168.3.1/24`, `192.168.3.0/24` NAT. Later verified DHCP/primary LAN cutover moved Pi to `192.168.2.1/24`; no postcutover live nftables NAT-file comparison was supplied. Do **not** merge PR #208 or blindly replace the firewall from draft #207.

A separate `merge/router-01-mss-postcutover-verification-20261028` branch stages only `IaC/ansible/playbooks/router-01-mss-postcutover-readonly.yml` using the already merged `.2.1` inventory, `docs/network/ROUTER-01-MSS-POSTCUTOVER-VERIFICATION-2026-10-28.md`, a targeted YAML/Ansible syntax CI workflow and this handover. The audit is gated to `admin-01`, exact Pi MAC/address, `--check`, explicit opt-in; reads live and disk nftables MSS, filter/NAT and reports actual `.2.0/24` NAT presence, with **zero intended host/network changes**. Source-only until CI passes and operator runs it; no claim of having already checked the new LAN NAT. Keep SSH monitoring/tunnel/PPPoE/DSL/ASUS changes held separately.

**Next:** review the isolated diff, CI PASS, merge only if clean, then on `admin-01` run read-only playbook on Pi and paste actual results to design the eventual guarded persistence-writer reconciliation. The original #208 stays DRAFT.


## LATEST — 28 October 2026 22:09 UTC router-01 post-cutover baseline VERIFIED; safe source isolated for main

On `admin-01`, operator confirmed `feature/router-01-toolset-audit-20261028` at `3e15857d`, Python AST PASS, Ansible conditional validator PASS and Ansible syntax check PASS, then ran strict `--check` isolated `router-01-postcutover-baseline-readonly.yml` against physical Raspberry Pi `192.168.2.1`. **Live PLAY RECAP router-01 ok=15 changed=0 unreachable=0 failed=0 skipped=0.** Exact Pi eth0 MAC, default PPPoE route and all four critical gateway services were validated. Snapshot `2026-10-28T22:09:06Z`: hostname still `raspberrypi`, 4-core CPU 0.1% (3 sec), load 0.09/0.04/0.01, temp 45.3°C, `throttled=0x0`, RAM 6.8% used (3538.2 MiB available), swap 0 MiB, disk 4.5% used (896.1 GiB available). eth0 and eth1 linked at 1 Gb/s, ppp0 up with IPv4 default route; 0 errors across interfaces, eth0 cumulative RX/TX drops 150/23 **unchanged** since 22:06:52 UTC; five `ppp0` WAN ICMP probes 0% loss / 10.502 ms average; 18 dnsmasq lease-file rows. All six sampled services active, Node Exporter listens on localhost `127.0.0.1:9100`; SSH listeners are wildcard and must remain protected by verified firewall controls. This was idle sampling, **not** a line-speed benchmark or reservation audit.

**Selective repository integration:** A standalone branch `merge/router-01-verified-readonly-baseline-20261028` carries only the exact three already-validated read-only collector source files, the new immutable report `docs/network/ROUTER-01-BASELINE-2026-10-28.md`, this handover entry and a dated current-state addendum. It does not import draft PR #210's unrelated SSH user/account/key changes or monitoring activations, PR #207's Kea/old LAN cutover, or PR #208's old-address MSS playbook. Original branch `feature/router-01-toolset-audit-20261028` stays open until reconciled. No host, router services, nftables, SSH, DHCP or WAN config changed through GitHub documentation work.

**Next gates:** reconcile `IaC/inventory/estate.json`, old `192.168.3.1` router Ansible guards, ASUS AP management, static DHCP reservations/exclusions including `media-01` at `.195` within scope `.100–.199`, then measure under representative client load. Keep draft PRs #207/#208/#210 held pending detailed integration and separate approvals. Every change via reviewed Git/IaC only.

## LATEST — 27 Oct 2026 security triage PR #205 MERGED; no live vulnerability remediation yet

User requested patching all outstanding problems. No bulk production upgrade has been run or authorised beyond specific staged planning. `security-container-triage-readonly.yml` is **MERGED** in PR #205 at commit `9463a84740ec75e1877b4dd2c3b728b3c069aab8` after two GitHub workflows PASS. It serially reads existing verified Trivy JSON for five exact Docker scanner hosts (identity/IPv4 checks, running image ID and report metadata, freshness, counts) and outputs per-image Critical/High count, fix-listed package rows, and at most 25 top advisory/package/version entries per host; no scans, host writes, image pulls or restarts. `scripts/validate-security-container-triage-readonly.py` and `docs/security/TRIVY-CRITICAL-HIGH-FIXABILITY-TRIAGE-2026-10-27.md` added. **User must run from admin-01** after main FF pull, source/Ansible checks and share bounded output to choose patch targets. Last central verification 26 Oct: five hosts **30/30** valid image references; image+severity+advisory counts 94 CRITICAL and 1,605 HIGH, NOT distinct CVEs or fixable vulnerabilities.

**Grafana first patch candidate:** Git main now has 13.2.4 pin and guarded `playbooks/grafana-security-patch-1324.yml`, but **no live deployment or checked controller validation confirmed**. Upstream release 13 Oct 2026 fixes multiple Grafana CVEs. `scripts/validate-grafana-security-patch-1324.py` for offline preflight; documentation PR #204 remains open and may need rebase/conflict resolution since main contains code. Do not merge blindly, and do not run disruptive Grafana recreation unless independently approved with preflight and verified pre-upgrade SQLite backup. The playbook touches Grafana only, no Prometheus/Loki/Alertmanager/Blackbox recreation. Database migration rollback is not automatic.

Other pending roots: Komodo core and Periphery 2.3.3 vs upstream 2.3.4 with root-store change (must verify TLS, Mongo rollback), Nextcloud 35.0.2 EXR mitigating policy only and residual libxml2/linux-libc-dev CRITICAL package findings, Greenbone scanner/feed coupled image versions and separate network/host risks (ICMP, RPC/cookies/TLS). No CVE may be marked Fixed until changed image runs healthy and fresh validated Trivy/Greenbone evidence confirms specific item resolved. Security issue #187 updated with phase status.

---

## 27 Oct 2026 — read-only five-host Trivy root-cause triage staged; NOT run on any host

User requested patching all outstanding security problems. Existing issue #187 explicitly disallows mass firmware/container upgrades without review; latest live verified Trivy as of 26 Oct: 30/30 valid current image refs, 94 Critical and 1,605 High image+severity+advisory records among 12,267 total, not independent fixes. Current Git pins: Grafana 13.2.1 (proposed 13.2.4 patch staged separately), Komodo 2.3.3 (official upstream 2.3.4 security-root-store update), Nextcloud 35.0.2 with residual libxml2, linux-libc-dev and OpenEXR package findings (EXR coder path mitigated only). Greenbone data feed images must be coordinated with late Trivy scan; no blind updates.

**New Git-only branch `security/vulnerability-root-cause-triage-20261027`:** `IaC/ansible/playbooks/security-container-triage-readonly.yml` targets exactly monitor-01/komodo-01/cloud-01/docker-01/greenbone-01, serial 1, asserting canonical hostname/IPv4/Debian13 and that currently running immutable image IDs match fresh (<=30h) complete saved Trivy summaries and report metadata. Prints bounded per-image Critical/High package counts and per-image count of fix-listed package rows, plus at most 25 CVE/package/installed/fixed examples per host. This is **read-only**, no scan, pull, restart, package upgrade, secrets or accepted-risk changes; guard script `scripts/validate-security-container-triage-readonly.py`, workflow `.github/workflows/validate-security-container-triage.yml`, runbook `docs/security/TRIVY-CRITICAL-HIGH-FIXABILITY-TRIAGE-2026-10-27.md`. Merge/CI and operator-run read-only Ansible remain pending; **do not invent per-image patchable totals or claim CVEs fixed without output**.

**Grafana 13.2.4 candidate** prepared in separate security branch/PR #204 with pinned IaC, explicit one-container `grafana-security-patch-1324.yml`, consistent protected SQLite/Compose backup and health checks, no live deployment. Official upstream v13.2.4 on 13 Oct includes four security fixes. Current main may independently already contain related patch files; reconcile Git state before merging and never duplicate/bypass review. The patch will cause brief Grafana UI downtime if operator separately approves deployment; automatic downgrade barred due to potential migrations.

**Next:** verify new PR CI, sync admin-01, inspect read-only output to assign image root-cause updates; stage and separately approve one-service Grafana patch as first canary only after matching runtime preflight. Then Komodo control plane/periphery, Nextcloud, Greenbone scanner and LAN/network vulnerabilities in order of exposure/compatibility. No live patch actions taken in this turn, and no scans/restarts initiated.

---

## NEWEST — 26 October 2026 vulnerability patch programme: PR #202 + #203 merged (NOT deployed)

**Operator goal** "patch all the problems now": DO NOT conflate the 12,267 current Trivy advisory series with 12,267 independent patches, nor Greenbone host/network results with container package CVEs. Latest live central Prometheus 30/30 validated Docker image references across 5 scanner hosts, 94 distinct-per-image/severity CRITICAL series and 1,605 HIGH series (not unique CVEs or verified exploits). Greenbone last weekly full-LAN baseline issue #187: 7 Medium (RPC, cookie, weak TLS certs, TLS renegotiation), 25 Low (ICMP/TCP timestamp), and separate accepted-risk register. Active production Nextcloud 35.0.2 still contains partially ImageMagick-mitigated EXR libraries plus libxml2 and linux-libc-dev Critical package findings; no confirmed supported Debian 13 patch for these at last assessment. Never silently alter risk or declare fixed without new scan.

**Already MERGED IN GIT, NOT LIVE**:
- **PR #202**, merge commit `a0f83aca45b69d80cc04fc94b21afe6229efc7fb`: active Grafana pin `grafana/grafana:13.2.1` -> `13.2.4` (official stable same-minor security release 13 Oct), auxiliary source pin synced. New limited scope approval-gated `IaC/ansible/playbooks/grafana-security-patch-1324.yml` requires exact running monitor-01 13.2.1/Compose, protected integrity-checked online SQLite backup, Compose backup, pulls exactly Grafana image, **recreates only Grafana** via docker compose --no-deps and verifies local /api/health 13.2.4 plus unchanged Prometheus/Loki/Alertmanager/Blackbox IDs. Offline validation `scripts/validate-grafana-security-patch-1324.py` & CI/Ansible syntax PASS. Operator must run after `git pull` and **explicit `-e grafana_security_patch_approved=true`** with maintenance/downtime awareness; do not run broad `monitoring.yml`. DO NOT claim security patches live until operator executes and verifies. Runbook `docs/security/GRAFANA-1324-SECURITY-PATCH-2026-10-26.md`. New Grafana image will temporarily invalidate that one Trivy report until separately approved new scan checks its immutable digest; never interpret stale findings as zero.
- **PR #203**, merge commit `9e6285788a62489ccb0d330475249a7573f35e74`: **read-only** 5-host serial Ansible `IaC/ansible/playbooks/trivy-fixability-readonly.yml` and `files/trivy-fixability-readonly.py`, CI and `scripts/validate-trivy-fixability-readonly.py` PASS. Exact active host identity, scanner 30h freshness, successful current immutable image ID, safe report paths incl symlink, report Metadata.ImageID and per-severity summary count matches; FAIL CLOSED if invalid. Prints top 24 Critical/High **scanner-listed fixed package versions** and top 12 Critical without listed fixes per host, plus by-image counts. No scans/changes/registry queries, `changed_when:false`. This identifies **actual remediation candidates** rather than guessing container versions. Operator run after sync: `ansible-playbook -i inventory/hosts.yml -b --ask-become-pass playbooks/trivy-fixability-readonly.yml`. Runbook `docs/security/TRIVY-FIXABILITY-AUDIT-2026-10-26.md`. Results still need upstream compatible image release and per-service rollback verification; Trivy `FixedVersion` is not a promised vendor image fix.

**Prioritised next actions:** (1) deploy Grafana v13.2.4 service-only, inspect backup/health, separately approve affected monitor-01 Trivy rescan after image change; (2) run read-only fixability inventory to rank actual remaining Critical/High by image/package/fix; (3) draft/deploy independent Komodo 2.3.4 CA-trust update only after validating Core Mongo backup and periphery compatibility, one node at a time; (4) investigate Nextcloud residual, Greenbone Mediums and Low firewall/firmware ownership, and current Debian apt upgrades with separate safe gates. Never mass-update all Docker containers, router, Proxmox hypervisors, DB engines or Greenbone feed images based on aggregate counts. **None of these host security updates have yet run live.** Security issue #187 tracks approvals/evidence; no background execution capability.

---

## NEWEST — read-only Trivy fixability inventory staged to rank actual container patches (26 Oct 2026)

**Patch remediation still constrained by running image identity and real fixed versions.** User requested to "patch all the problems now" after 5-host Trivy CVE dashboards. Immediate supported patch PR #202 was **MERGED to main** (commit `a0f83aca45b69d80cc04fc94b21afe6229efc7fb`, all 3 CI PASS) for Grafana 13.2.1 -> 13.2.4 pinned image and approval-gated one-service Ansible cutover `playbooks/grafana-security-patch-1324.yml`; **NOT LIVE**, creates protected SQLite backup, Compose backup and restarts Grafana only after explicit user maintenance approval. Source `docs/security/GRAFANA-1324-SECURITY-PATCH-2026-10-26.md`; official upstream release 13 Oct fixes additional CVEs. User must update admin-01 Git checkout, validate, then run with `-e grafana_security_patch_approved=true`; do not conflate merged Git with installed patch. `monitoring.yml` is unsafe for this narrow patch because it reconciles ALL containers.

**Next Git-only branch** `security/trivy-fixability-inventory-20261026` (PR/CI review pending): `IaC/ansible/playbooks/trivy-fixability-readonly.yml` serial five-host Ansible read-only query with exact IP/hostname/Debian 13 guards; `IaC/ansible/playbooks/files/trivy-fixability-readonly.py` reads ONLY existing fresh successful Trivy JSON and Docker ps/image inspect identities; fails closed on incomplete/stale/identity drift, malformed/escaping report paths or any per-severity count mismatch. Does not run a scanner, pull images or patch a host. Prints compact per-image CRITICAL/HIGH package-row counts, actual CVE identifiers, installed/fixed versions, first 24 fix hints and 12 no-fix Critical rows for follow-up. Validator `scripts/validate-trivy-fixability-readonly.py`, CI, runbook `docs/security/TRIVY-FIXABILITY-AUDIT-2026-10-26.md`. After Git merge, user can run `ansible-playbook -i inventory/hosts.yml -b --ask-become-pass playbooks/trivy-fixability-readonly.yml` from admin-01 and share bounded output. This ranks image-level supported upgrades and identifies where no patch exists. The 12,267 metric series (94 Critical, 1605 High) are NOT 12,267 patches. Nextcloud 35.0.2 has partial EXR mitigation but remaining libxml2 and linux-libc-dev findings. Komodo 2.3.4 released 22 October 2026 fixes compromised root trust but is NOT proof its old Perl/OpenSSH CVEs are fixed. Greenbone full-LAN 7 Medium and 25 Low need device-specific owner/configuration checks; never mass-update routers, hypervisors, LXC or Docker/Greenbone stack without supported rollback. None of these host updates were executed by ChatGPT.

---

## NEWEST — Security patching request, Grafana 13.2.4 FIRST gated patch in Git only (26 October 2026)

**Operator request:** "can we patch all the problems now" after verifying 5-host Trivy CVE data and successfully deploying Grafana vulnerability dashboard. Interpret as security remediation intent, **not safe blanket permission for simultaneous mass changes** to databases, router/Proxmox, security scanner and production Nextcloud. See existing issue #187 objective and `AGENTS.md`: one approved Git-managed Ansible change at a time with immutable image verification, backup, health and fresh post-update scans. Baseline: five running Docker hosts 30/30 validated image references, 12,267 image+severity+advisory records (94 Critical, 1,605 High) as of 26 Oct 16:30-16:50 GMT, **NOT 12,267 separate patches**. Latest Greenbone full-LAN report known in issue #187 had 7 Medium (RPC enumeration, session cookie, weak signature certs, TLS renegotiation) + 25 Low (ICMP/TCP timestamps); separate from Trivy. Documented Nextcloud 35.0.2 Critical status: 2 OpenEXR ImageMagick paths partially mitigated but Debian packages unpatched; libxml2 Trixie no official fixed version yet; linux-libc-dev package finding is not proof the host NFS server is running. NEVER reclassify those as fixed without fresh evidence.

**High-confidence immediately actionable vendor patch found:** Git-managed Grafana default and secondary Komodo monitoring Compose use `grafana/grafana:13.2.1`. Public Grafana official release API verifies same-minor **v13.2.4** released **13 Oct 2026**, with fixes for CVE-2026-15577, -33374, -93294, -95502 and intermediate patch fixes since 13.2.1. Government alert lists 13.2.1 affected. **New Git-only branch `security/grafana-1324-patch-20261026`**: update monitoring_stack/defaults/main.yml and legacy IaC/komodo/stacks/monitoring/compose.yml pin to `grafana/grafana:13.2.4`; add tightly scoped `IaC/ansible/playbooks/grafana-security-patch-1324.yml` which asserts exact monitor-01 identity, approvals, old live pin, valid Grafana 13.2.1 API, other monitoring container IDs, creates **consistent protected online SQLite backup**, pulls target image, backs up and replaces ONLY Grafana's image line in live managed Compose, `docker compose up -d --no-deps --no-build --force-recreate grafana` (Grafana only) and verifies Grafana 13.2.4 API and unchanged other container IDs. No full monitoring role, other-container restarts, secrets printing or automatic scan. Added offline validator, GitHub CI and `docs/security/GRAFANA-1324-SECURITY-PATCH-2026-10-26.md` for recovery/rollback. This is a *real container recreate/downtime* unlike previous JSON-only updates, and requires separate explicit operator approval after reviewed CI/merge and verified backup/recoverability.

**Other candidate:** Official moghtech/komodo v2.3.4 released **22 Oct 2026**, v2.3.3 currently pinned for Komodo Core + periphery. 2.3.4 drops compromised-root CA (webpki-roots 1.0.10), but there is NO proof it fixes many old Perl CVEs seen in running Periphery images. Stage separate patch after Grafana. The Trivy image reports and Greenbone issues must be triaged by actual package/installed/fixed version; do not guess from 12,267 Prometheus series. No live host operations were performed while preparing Git; operator must run from admin-01. After Grafana image update, its previous Trivy scan invalidates until new approved scan confirms identity and CVE disposition; don't claim Grafana or all security issues fixed on Git merge.

---

## 26 Oct 2026 18:16 GMT — PR #201 Grafana readability revision DEPLOYED on monitor-01

**Newer LIVE operator evidence; supersedes earlier PR #201 'not deployed' claims below.** From admin-01 the operator ran `git switch main; git pull --ff-only origin main`; it fast-forwarded local main `5b3fa247..753290aa`, changing **53 network/host Markdown files** in that pull (unrelated source changes; do not attribute those changes to the dashboard playbook). Both `python3 scripts/validate-trivy-cve-dashboard.py` and `python3 scripts/validate-unified-vulnerability-cves.py` **PASS**, as did `ansible-playbook ... playbooks/grafana-trivy-dashboard-update.yml --syntax-check`. The former printed `RUNNING_IMAGES=1 VALID_IMAGES=1`, then `1/0`, `1/0`: these are deliberate isolated offline fixture tests, NOT live estate status; previous Prometheus read-only check had 30/30 valid across five hosts.

User then executed scoped, explicitly approval-gated `ansible-playbook -i inventory/hosts.yml -b --ask-become-pass playbooks/grafana-trivy-dashboard-update.yml -e grafana_trivy_dashboard_update_approved=true` against **monitor-01**. **ok=9 changed=1 failed=0**. Existing dashboard identity preflight, Grafana localhost health both before and after, installed JSON syntax and guard for Greenbone host panels + **Trivy Target name | Severity | CVE | Details** all PASS. **File changed=True**, so this is a real provisioned JSON update; backup `/opt/monitoring/grafana/provisioning/dashboards/production/homelab-vulnerability-management.json.2178221.2026-10-26@18:16:14~`. No container/Grafana restart or new vulnerability scan.

**Now installed configuration:** same Grafana UID `homelab-vulnerability-management`, Critical-default severity filter with other/all severity choices, four Trivy CVE columns, link/wrap, no fixed Details width, pagination + per-column filter; Greenbone actionable/accepted/CVE tables omit scrape `target_name`; summed selected-host scan-complete/running/valid cards; oldest scan age as max; severity stat titles explicitly 'package findings', values without solid backgrounds; reduced accepted-risk panel height. **Still to verify after this specific deployment:** open Grafana dashboard and visually check that refreshed Details table fills width and expected card/Greenbone presentation, links work; passing Ansible health is NOT visual verification. Previously user supplied screenshot of prior revision showing four columns but cramped layout. Greenbone host CVE publisher already deployed at 16:51; new Trivy publishers all five hosts previously live and Prometheus verified 30/30. No further scans or exporter changes needed. Security issue #187 tracks this.

---

## NEWEST — PR #201 readability fix MERGED (not deployed), after user live Grafana screenshot 26 Oct 2026

**Verified UI before this PR:** User screenshot after independently approved ~16:51 GMT Greenbone host CVE exporter and Grafana dashboard Ansible showed live Trivy four-column **Target name | Severity | CVE | Details** table with actual CVE IDs, CRITICAL values, and source details. Greenbone host CVE/advisory rows also visible. However Details table only used a narrow part of the huge Grafana panel because of hard-coded 740px Details column width; Greenbone panels leaked `target_name`, summary cards repeated five noisy host chips and four saturated red package-findings counters, accepted-risk panel blank/No data. The screenshot alone does not prove clicking external CVE URLs works. Browser may be zoomed out; `Ctrl+0` can reset local zoom.

**New Git-only remedy now merged PR #201**, merge commit `9133f60a487ac633d40a20fa93ade921fbf5574e`, all four CI workflows PASS: removes fixed Details width and adds pagination/column filtering, keeps four visible fields + wrapped text + CVE URLs and Critical-default selector; excludes `target_name` in Greenbone tables 10/11/12; uses SUM counts for selected-host scan complete/running/valid summaries, MAX oldest scan age, more compact stat value coloring and titles naming **package findings** rather than unique CVEs, trims accepted-risk table height to reduce blank space (without removing its underlying findings), shifts later Trivy panels up six grid units. Guarded Grafana-only Ansible playbook verifier and Trivy/Greenbone tests extended. Source doc `docs/security/GRAFANA-VULNERABILITY-DASHBOARD-READABILITY-2026-10-26.md`. Does not change the source scanner data, CVE exporter, metrics, scan validity, risk status, Grafana UID or services. **No LIVE deployment of PR #201 confirmed.**

**Operator next action:** on admin-01 `git switch main && git pull --ff-only origin main` (stop if local changes), run both offline validators and `ansible-playbook -i inventory/hosts.yml playbooks/grafana-trivy-dashboard-update.yml --syntax-check`. Only **separately operator-approved** targeted Grafana JSON update on monitor-01: `ansible-playbook -i inventory/hosts.yml -b --ask-become-pass playbooks/grafana-trivy-dashboard-update.yml -e grafana_trivy_dashboard_update_approved=true`. Playbook backs up previous dashboard, asserts exact monitor-01 and Grafana health, does not restart Grafana/Docker or trigger a scan. Visually recheck at `https://grafana.home.jrwroberts.co.uk/d/homelab-vulnerability-management`, including CVE links. Previous Grafana JSON backup after 16:51 deployment remains `/opt/monitoring/grafana/provisioning/dashboards/production/homelab-vulnerability-management.json.2162805.2026-10-26@16:51:49~`; record new backup from next Ansible run. Existing five-host Trivy end-to-end verified 30/30 current images and 12,267 image+severity+CVE series as of 26 Oct, separate Greenbone host CVE publisher now LIVE, no scans required. Historical 'not deployed' notes below superseded.

---

## READ FIRST — screenshot review after live Grafana dashboard deployment, 26 Oct ~16:55 GMT

**New live visual evidence**: User sent a full Grafana screenshot of `homelab-vulnerability-management` after both independently approved monitor-01 publisher/dashboard deployments on 26 Oct at 16:51 GMT. Screenshot positively confirms the **Trivy CVE table displays only Target name, Severity, CVE, Details**, real rows with CRITICAL severity, blue clickable-looking advisory IDs, and machine names. Top Greenbone host CVE panel also has clickable-looking CVEs, and prior three Greenbone tables remain. This independently establishes Grafana provisioning refreshed and panel data rendered; **external advisory link destinations not actually clicked or tested**. Screenshot reveals UI readability issues: fixed-width Details column leaves much of wide panel blank; `target_name` extra Node Exporter scrape label appears at far right of two Greenbone host tables; repeated multi-host green status chips; saturated red lower-severity package-count stat backgrounds; accepted-risk panel says No data (not proof of zero risks). Browser zoom appears quite small; Ctrl+0 may help locally.

**New Git-only change**: branch `monitoring/vulnerability-dashboard-readability-20261026`, with scoped changes to Grafana provisioned dashboard JSON and offline validation/playbook assertions plus runbook `docs/security/GRAFANA-VULNERABILITY-DASHBOARD-READABILITY-2026-10-26.md`. Keep **exactly the four Trivy data columns** and severity selector default CRITICAL; remove fixed `Details` width to allow Grafana automatic responsive sizing and keep text wrap/links; add table pagination/column filters; hide `target_name` on Greenbone finding panels 10, 11, 12; aggregate 5-host Trivy scan-complete/running/valid cards into 5/30/30-style totals under selected filter, show oldest scan age as one value, reduce all-solid-red/green metric card backgrounds, explicitly title severity counts as **package findings** rather than unique CVEs. Reduce accepted-risk panel height (not its data) to reclaim space. Keep original evidence metrics, all 30/30 image validity, Greenbone risk dispositions, exact dashboard UID, existing CVE links and export controls. No scans, exporter edits or live changes made by PR. Grafana docs confirm automatic table widths and client-side pagination/filtering options.

**Next gates**: PR CI/review/merge; sync admin-01 main; offline Trivy + Greenbone dashboard validators + estate + Ansible dashboard playbook `--syntax-check`; then **separate operator approved** `playbooks/grafana-trivy-dashboard-update.yml -e grafana_trivy_dashboard_update_approved=true` on monitor-01 only, new rollback backup, Grafana local health and visual follow-up. Do not redeploy scanners or CVE publishers: they are LIVE and end-to-end central Prometheus data verified. Existing previously deployed dashboard backup `/opt/monitoring/grafana/provisioning/dashboards/production/homelab-vulnerability-management.json.2162805.2026-10-26@16:51:49~`. New display PR is not yet deployed.

---

## Step 161 — Greenbone HOST CVE publisher and four-column Grafana dashboard DEPLOYED on monitor-01 (26 October 2026 16:51 GMT)

**Newer LIVE operator evidence, superseding previous 'not deployed' references:** After fast-forwarding admin-01 main to `1ae36329`, offline `scripts/validate-trivy-cve-dashboard.py` and `scripts/validate-unified-vulnerability-cves.py` both PASSED; both targeted Ansible `--syntax-check` PASSED. User separately ran both explicit approval-gated Ansible playbooks on `monitor-01` with no failures:

1. `playbooks/grafana-greenbone-cve-metrics-update.yml -e greenbone_cve_publisher_update_approved=true`: **ok=10 changed=2 failed=0**. Existing Greenbone managed-scan evidence read, original counts preserved, new `homelab_greenbone_cve_finding_score` metric family validated, Node Exporter scrape healthy. Exporter updated=True. Rollback: `/usr/local/sbin/homelab-greenbone-metrics.2162392.2026-10-26@16:51:09~`. No Greenbone scan, service restart or image change. **Individual host CVE series in central Prometheus not yet independently queried**; presence of family is verified but nonempty series depend on evidence contents.
2. `playbooks/grafana-trivy-dashboard-update.yml -e grafana_trivy_dashboard_update_approved=true`: **ok=9 changed=1 failed=0**. File changed=True, provisioned JSON syntax and UID/table/Greenbone preservation assertions passed; Grafana localhost health before and after PASS. Backup: `/opt/monitoring/grafana/provisioning/dashboards/production/homelab-vulnerability-management.json.2162805.2026-10-26@16:51:49~`. Dashboard UID `homelab-vulnerability-management`, expected view: Trivy four columns **Target name | Severity | CVE | Details**, severity multi-select default CRITICAL and options HIGH/MEDIUM/LOW/UNKNOWN/All, hostname filter, clickable OSV advisory links. Provider polls every 30s; **Grafana API reload/visual verification has NOT yet been independently confirmed**, only file copy and health. No Grafana restart.

**Current pipeline:** Already verified before these two changes central Prometheus `PROMETHEUS_FIVE_HOST_COVERAGE=PASS` (all 5 Trivy Docker hosts, 30/30 fresh valid running image refs, 12,267 image/severity/advisory series including 94 CRITICAL and 1,605 HIGH, not distinct CVEs). New Trivy CVE exporters live all five. **Remaining validation only:** user opens `https://grafana.home.jrwroberts.co.uk/d/homelab-vulnerability-management`, confirms four clean Trivy data columns, severity filter, CVE links, Greenbone host CVE panels. If old pilot table remains, identify live dashboard UID rather than deleting unrelated panels. Optionally read-only Ansible query central Prometheus for `homelab_greenbone_cve_finding_score`, and on monitor-01 check dashboard UID via Grafana API if session/token allows. No further infra mutation should be performed unless UI verification reveals specific issue. Record screenshot/output in security issue #187.

---

## Step 160 completed — CVE severity-first presentation merged; host C V E + Grafana still not deployed (26 October 2026)

**Newer verified live evidence:** central Prometheus `PROMETHEUS_FIVE_HOST_COVERAGE=PASS`, 30/30 Trivy running image references validated on five hosts (monitor-01 6/6, komodo-01 2/2, cloud-01 4/4, docker-01 2/2, greenbone-01 16/16), scans fresh and complete. New per-image severity/advisory CVE records: cloud-01 Critical/High/Medium/Low/Unknown 9/230/822/606/105; docker-01 12/173/285/271/34; greenbone-01 64/992/5158/2245/398; komodo-01 5/66/151/125/7; monitor-01 4/144/195/151/15. Total **12,267 series** (not distinct CVEs), 94 Critical, 1,605 High. All five new all-severity publishers already LIVE; no need to redeploy those.

**User-facing four-column Trivy table, refined and MERGED as PR #200:** merge commit `60e4fcc0afedfe0b2b0cb39ca26a4819904445a4`; all four CI workflows PASS. New Grafana `trivy_severity` multi-select defaults to CRITICAL (94 current rows) and allows HIGH/MEDIUM/LOW/UNKNOWN or All without discarding Prometheus evidence. Keeps four columns **Target name | Severity | CVE | Details**, clickable CVEs, host selector, Greenbone existing findings, summary stats and provisioned UID. The 12,267 series would be an overly large initial table without this filter. Tests, runbook and CURRENT-STATE updated by PR. Merge is **GIT ONLY, NOT LIVE**.

**Immediate next approved Ansible stages on admin-01:** `git switch main && git pull --ff-only origin main`, validate offline + Ansible syntax, then use independently gated `playbooks/grafana-greenbone-cve-metrics-update.yml -e greenbone_cve_publisher_update_approved=true` to install **Greenbone host/network CVE** publisher on monitor-01 (distinct from Trivy Docker exporter) with rollback backup; verify original risk counts and new CVE metric. Then independently gated `playbooks/grafana-trivy-dashboard-update.yml -e grafana_trivy_dashboard_update_approved=true` on monitor-01, backing up old dashboard JSON, no Grafana restart. Read-only Grafana health/UID verification and **visual check** of four-column Trivy table, severity selector default CRITICAL and working CVE links are mandatory; the old Trivy pilot panel may live in a different UID. Don't claim live until operator reports output. Existing operator intent to deploy revised dashboard granted earlier, but playbook still asserts stage-specific approval flags and must be run explicitly. Security issue #187.

---

## LATEST — Step 160 Prometheus 30/30 PASS; Git-only severity-filtered four-column dashboard (26 October 2026)

**Verified LIVE read-only Prometheus via user-run Ansible on monitor-01:** All five Trivy publishers updated, all five current scan summaries valid and complete; monitor-01 RUNNING=6 VALID=6 COMPLETE=1 AGE=12.41h; komodo-01 2/2, age=11.49h; cloud-01 4/4 age=7.77h; docker-01 2/2 age=9.44h; greenbone-01 16/16 age=1.13h. All within 30-hour freshness limit, total **30/30**. New `homelab_container_estate_cve_detail_score` series centrally present on ALL five hosts. By severity from actual query: cloud-01 CRITICAL 9 HIGH 230 MEDIUM 822 LOW 606 UNKNOWN 105; docker-01 12/173/285/271/34; greenbone-01 64/992/5158/2245/398; komodo-01 5/66/151/125/7; monitor-01 4/144/195/151/15. Total **12,267 per-image/severity/advisory records**, including **94 Critical**, **1,605 High**; these are not estate-wide distinct CVEs or verified exploitability. Query ended `PROMETHEUS_FIVE_HOST_COVERAGE=PASS`.

**Next Git-only UI refinement:** with 12,267 rows across five hosts, do NOT render All severities at first load. Branch `monitoring/trivy-cve-severity-20261026` (review/CI/merge pending) adds *Severity* multi-select to existing UID `homelab-vulnerability-management`, default `CRITICAL` (only 94 live records observed), options HIGH/MEDIUM/LOW/UNKNOWN/All, while keeping only the four requested visible data columns `Target name | Severity | CVE | Details`; existing Host selector defaults All. Query adds `severity=~"${trivy_severity:regex}"`. Tests/playbook schema and runbook/current-state updated. This is only a display filter; it does not discard vulnerabilities from Prometheus or alter image evidence. **Neither the revised Grafana JSON nor the distinct Greenbone HOST-CVE metrics publisher is confirmed LIVE yet.** Next once CI passes: merge reviewed PR, sync admin-01; separately execute `grafana-greenbone-cve-metrics-update.yml -e greenbone_cve_publisher_update_approved=true` on monitor-01 using original managed-scan evidence and verify original Greenbone counts, new CVE family and Node Exporter, no Greenbone scan; then separately `grafana-trivy-dashboard-update.yml -e grafana_trivy_dashboard_update_approved=true`, verify provisioned dashboard UID and exact table/filter/clickable links, Grafana health. Both backup previous files. Do not delete unknown old "Trivy pilot" dashboard until verifying live UID. Security issue #187 tracks work. Earlier 9/16 Trivy status and older pre-deployment instructions are historical.

---

## Step 159 — all five all-severity Trivy CVE publishers LIVE with 30/30 local image coverage (26 Oct 2026)

**Latest operator evidence:** User completed the previously approved, serial four-host `IaC/ansible/playbooks/trivy-critical-cve-exporter.yml -e trivy_critical_cve_exporter_approved=true --limit 'monitor-01:komodo-01:docker-01:greenbone-01'`. Each host ended `ok=11 changed=2 failed=0`; exporter code updated True, existing validated Trivy reports re-published (NO new scan/containers/restarts), Python validation, textfile new `homelab_container_estate_cve_detail_score` + legacy family and Node Exporter checks PASS. Running/valid/complete: **monitor-01 6/6 TRUE**, **komodo-01 2/2 TRUE**, **docker-01 2/2 TRUE**, **greenbone-01 16/16 TRUE**. Together with Step 157 canary **cloud-01 4/4 TRUE**, all **30/30 image references validated locally** (not yet *centrally* re-verified on each of five hosts). Rollback publisher script backups: monitor-01 `/usr/local/sbin/homelab-container-estate-metrics.2157969.2026-10-26@16:29:56~`; komodo-01 `...3795740.2026-10-26@16:30:07~`; docker-01 `...262170.2026-10-26@16:30:21~`; greenbone-01 `...1187704.2026-10-26@16:30:34~`. Cloud-01 previous successful backup `...1792275.2026-10-26@16:16:43~`.

**Immediate next step:** User-run *read-only* Ansible against monitor-01 querying central Prometheus for each host: `homelab_container_estate_running_images`, `valid_images`, `scan_complete`, `last_scan_timestamp_seconds`, and `count by(target_name,severity)(homelab_container_estate_cve_detail_score)`. Ensure 30/30 totals and no errors; a host can legitimately have zero advisory rows if sources are empty while summary validated. Cloud-01's all-severity data already verified centrally (9 Critical, 230 High, 822 Medium, 606 Low, 105 Unknown = 1772 advisory series). Then separately approval-gated Ansible on monitor-01 for Greenbone **HOST** CVE publisher `playbooks/grafana-greenbone-cve-metrics-update.yml -e greenbone_cve_publisher_update_approved=true` (not Greenbone **Trivy image** exporter) followed by separately gated Grafana provisioned JSON `playbooks/grafana-trivy-dashboard-update.yml -e grafana_trivy_dashboard_update_approved=true`. Verify UID `homelab-vulnerability-management`, and four-column Trivy table **Target name | Severity | CVE | Details**, CVE links and actual Greenbone host findings. Live Greenbone-host CVE publisher and Grafana JSON deployment are **not yet confirmed**; do NOT claim dashboard fixed until verified. Old raw 'Trivy pilot' table may be on a different dashboard UID; don't delete it without identification.

---

## Step 158 — cloud-01 all-severity CVE details verified in central Prometheus (26 Oct 2026)

**NEWER LIVE evidence:** User ran read-only Ansible on monitor-01 querying local Prometheus `/api/v1/query`: for `target_name="cloud-01"`, `homelab_container_estate_running_images=4`, `valid_images=4`, `scan_complete=1`. Query of **`homelab_container_estate_cve_detail_score`** returned verified CVE/advisory series grouped by severity: **CRITICAL 9, HIGH 230, MEDIUM 822, LOW 606, UNKNOWN 105**, total **1,772 image+severity+advisory series**, NOT necessarily 1,772 unique CVEs, exploitable weaknesses, or remediation tasks. First example: LOW `CVE-2001-1534` under `nextcloud:35.0.2-apache` with real package names, Fix: Not listed and scanner Title. User's query concluded `PROMETHEUS_CVE_DETAILS=PASS`. This establishes cloud-01 **new all-severity publisher → Node Exporter → Prometheus** confirmed. It does NOT establish a deployed or visually verified four-column Grafana dashboard.

**NEXT APPROVAL-GATED DEPLOYMENT:** The user previously requested the revised Grafana workflow. Apply existing serial Ansible `IaC/ansible/playbooks/trivy-critical-cve-exporter.yml` on `monitor-01:komodo-01:docker-01:greenbone-01` with `-e trivy_critical_cve_exporter_approved=true`, after source checks. This republishes already validated Trivy JSON, no scans/restarts. Track individual backup paths, image coverage and scan-complete flags (greenbone-01 last local scan 15:29–15:31 GMT was 16/16). Then query central Prometheus for all five; empty CVE rows when scans invalid do NOT mean zero findings. After separate approval, deploy `grafana-greenbone-cve-metrics-update.yml` and finally `grafana-trivy-dashboard-update.yml` on monitor-01; inspect live UID `homelab-vulnerability-management`, and ensure **Target name | Severity | CVE | Details** only. Note high series cardinality (1,772 from cloud-01 alone); use proper severity filtering/pagination in Grafana if practical without hiding data. Security issue #187 comment 6421326895. No production changes performed in recording these results.

---

## Step 157 — NEW all-severity Trivy CVE exporter canary LIVE on cloud-01 (26 Oct 2026 ~16:16 GMT)

**Latest operator evidence supersedes Step 156's outdated-canary warning.** User reran the latest Git-managed `playbooks/trivy-critical-cve-exporter.yml` from admin-01 with `-e trivy_critical_cve_exporter_approved=true --limit cloud-01`. Play heading was **"Publish CVEs with severities and details from validated Trivy reports"**. Ansible **ok=11 changed=2 failed=0**, `Exporter updated=True`, `RUNNING_IMAGES=4 VALID_IMAGES=4 SCAN_COMPLETE=TRUE`; new `homelab_container_estate_cve_detail_score` metric family and old metrics passed file/Node Exporter verification. Rollback backup: `/usr/local/sbin/homelab-container-estate-metrics.1792275.2026-10-26@16:16:43~`. Re-published *existing Trivy reports* only; **no new scan, container update, restart or Grafana deployment**. This confirms the new publisher installed on cloud-01, but **central Prometheus read of new all-severity metric is NOT YET VERIFIED**. Immediate next action: read-only, controller-launched Ansible on monitor-01 querying local Prometheus for cloud-01 new series (`count by (severity) (homelab_container_estate_cve_detail_score{target_name="cloud-01"})`), and verify old 4/4 scan validity/age and a few actual CVE+details labels. Only if passed, separately approved guarded `trivy-critical-cve-exporter.yml --limit 'monitor-01:komodo-01:docker-01:greenbone-01'` to roll out other four; verify full central Prometheus coverage including greenbone-01 16/16. Then separately gated Greenbone HOST CVE exporter on monitor-01 and Grafana JSON deployment, with visual verification of exactly `Target name | Severity | CVE | Details`. Merged PR #199 has all four CI PASS; dashboard JSON is still **NOT confirmed deployed**. Earlier greenbone-01 manual 15:29–15:31 GMT Trivy scan is locally 16/16, independently of cloud-01. Preserve old metric and no-CVE report/count semantics.

---

## Step 156 — cloud-01 canary attempt used old local Trivy CVE exporter (26 Oct 2026)

User pasted an Ansible canary run targeting cloud-01 with explicit `trivy_critical_cve_exporter_approved=true`: all 11 tasks successful, `ok=11 changed=1 failed=0`, local metrics republished from existing reports, `RUNNING_IMAGES=4 VALID_IMAGES=4 SCAN_COMPLETE=TRUE`. **But this is NOT deployment of the new all-severity four-column CVE exporter:** the task still read `Publish critical CVE references from existing validated Trivy reports` / `Install critical CVE-aware exporter`, and Ansible reported **`Exporter updated=False`**. GitHub current main playbook now says `Publish CVEs with severities and details from validated Trivy reports` and checks `homelab_container_estate_cve_detail_score`; therefore admin-01 ran an older local checkout (or not yet synchronized playbook). **No evidence that the new metric was published.** NEXT: from admin-01, run `git status -sb; git switch main; git pull --ff-only origin main; git status -sb` (stop on local modifications/conflicts), validate `scripts/validate-trivy-cve-dashboard.py` and `scripts/validate-unified-vulnerability-cves.py`, and confirm new family appears in Git-controlled exporter/playbook. Then rerun *separately approved canary* on cloud-01 only; expect exporter updated=True, new metric family present in textfile/Node Exporter. Validate central Prometheus before rolling out the remaining four. The earlier operator-run greenbone-01 manual scan 15:29–15:31 GMT succeeded with 16/16 **locally**, distinct from this cloud canary. No host scanning, dashboard changes or fixes have been initiated by this note.

---

## LATEST — PR #199 merged: four-column Trivy CVE details (26 Oct 2026)

User requested the former cluttered Trivy severity/image raw Prometheus table show **only Target name, Severity, CVE and Details**. Implemented in **merged PR #199**, merge commit `2df2687d791ed97c5d1d4e84bcd0fdbd15e87c2f`, four GitHub CI workflows PASS. Shared Trivy publisher now provides `homelab_container_estate_cve_detail_score` across CRITICAL/HIGH/MEDIUM/LOW/UNKNOWN from validated original reports; gauge value is severity rank (not CVSS). Bounded Details contain running image, packages, fixes and source title; real advisory IDs clickable and deduplicated by image/severity. Strict count/freshness/immutable image checks preserve fail-closed behavior; old metric `homelab_container_estate_critical_cve` remains. Grafana UID `homelab-vulnerability-management` retains Greenbone panels and Trivy stats, replaces Trivy panel 39 with exactly four visible fields, removes duplicate 38 and 41, default host filter All. **NOT DEPLOYED LIVE** by PR merge. On `admin-01` pull current `main`, run `scripts/validate-trivy-cve-dashboard.py`, `scripts/validate-unified-vulnerability-cves.py`, estate check, Ansible syntax; operator must approve/run `playbooks/trivy-critical-cve-exporter.yml` on cloud-01 canary, verify Node Exporter and Prometheus new family, then remaining four hosts. Only after exporter verification, separately deploy Greenbone HOST CVE metrics publisher (if pending) and Grafana JSON from `playbooks/grafana-trivy-dashboard-update.yml`. **Do not say Grafana is fixed until visually inspected.** Existing unknown raw pilot panel may belong to another/live-old dashboard; verify UID instead of deleting. Manual greenbone-01 Trivy 26 Oct 15:29–15:31 GMT Result=success gave local **16/16 valid** and scan_complete=1; post-run central Prometheus not yet verified. Security issue #187 comment 6420873261; new runbook `docs/security/GRAFANA-TRIVY-FOUR-COLUMN-CVES-2026-10-26.md`. Any historic PR-pending or 9/16 statements below are superseded.

---


## READ FIRST — Trivy four-column CVE detail table, 26 October 2026 (newest Git proposal)

**User requested exactly four visible columns:** `Target name | Severity | CVE | Details` instead of the unreadable legacy `Trivy — findings by image / severity` raw Prometheus table (`Time`, `__name__`, `image`, `instance`, `job`, `severity`, `target_name`, `Value`). The old screenshot does NOT display a CVE; merely hiding columns would be misleading because the prior Trivy CVE exporter publishes CRITICAL IDs only. The user wants the vulnerability ID and practical explanation across severities. **Git-only work branch `monitoring/trivy-four-column-cves-20261026`** (not yet merged or deployed):
- Extend shared `IaC/ansible/roles/container_vulnerability_pilot/files/publish-estate-metrics.py` to parse only trusted, fresh, matching immutable-image Trivy JSON, check row counts for every severity against saved scanner summary, and expose `homelab_container_estate_cve_detail_score{image,severity,cve,details}`. Severity priority values 5/4/3/2/1 are NOT CVSS. Each real Trivy advisory ID deduplicated per image and severity, with bounded Details including image, scanner title/description, package list and available fixed versions. Missing IDs are never fabricated; valid-summary counts and legacy `homelab_container_estate_critical_cve` remain intact. Invalid or stale evidence remains fail-closed.
- Modify only the provisioned Grafana vulnerability management dashboard UID `homelab-vulnerability-management`: panel ID 39 is a full-width, four-column table with CVE advisory links, severity ordering, Details wrapping and Prometheus/extra image columns hidden; remove redundant Trivy image-summary table panels 38 and 41, retaining the summary STATs, the host selector (All default), Greenbone host CVEs, and other host finding views. Source `IaC/ansible/roles/monitoring_stack/files/grafana/dashboards/production/homelab-vulnerability-management.json`. The old raw pilot table title is absent from current Git-managed file, suggesting old live provisioned JSON or another Grafana dashboard; do not delete an unrelated dashboard without verifying its UID.
- Update approval-gated existing Trivy exporter rollout playbook `IaC/ansible/playbooks/trivy-critical-cve-exporter.yml` to assert new family and preserve the old one, and `IaC/ansible/playbooks/grafana-trivy-dashboard-update.yml` to assert exact four-column contract. Existing offline validators `scripts/validate-trivy-cve-dashboard.py` and `scripts/validate-unified-vulnerability-cves.py` adjusted, and GitHub CI checks apply; new operational runbook `docs/security/GRAFANA-TRIVY-FOUR-COLUMN-CVES-2026-10-26.md`. These are **source changes only** until tested, merged, pulled and separately approved on hosts.
- **Latest actual operational evidence (15:31 GMT 26 Oct):** User explicitly ran bounded manual Trivy scan on greenbone-01 from admin-01; all four monitored jobs inactive at preflight; service ran **15:29:14–15:31:51**, Result=success, local exporter **16/16 valid, scan_complete=1**. This SUPERSEDES earlier Greenbone 9/16 status; original image-ID mismatch is resolved locally by rescanning newly running feed images. Central Prometheus visibility after this run has not yet been confirmed. The Greenbone Trivy timer was previously changed to evening 19:00–19:30 UTC, next 19:05:39 GMT. **No new Trivy scan is required just to publish details:** the new exporter uses existing validated reports.
- **Rollout gates, no live changes automatically:** finish GitHub CI and review/merge new PR, sync admin-01, verify central Prometheus 16/16, separately approve a canary Trivy CVE-detail exporter update on cloud-01 before four-host roll-out, verify Node Exporter and central Prometheus all-severity series, separately approve Greenbone *HOST* CVE publisher on monitor-01 if not deployed, then separately approve one Grafana provisioned JSON update on monitor-01 and visually confirm four columns and CVE links. Neither the new exporter nor this Grafana table is known live. Security issue #187. The pre-existing separate documentation PR #196 remains open and may be incompatible with latest main; don't merge blindly.

---


## READ FIRST — 26 October Trivy/Greenbone scan ordering incident (latest verified status)

**LIVE evidence:** On greenbone-01, Trivy image scan SUCCESS 26 Oct **09:29:04–09:32:20 UTC**, then Greenbone feed refresh SUCCESS **10:00:04–10:20:57 UTC**. Greenbone managed scan completed **02:00:04–04:19:50 UTC**; weekly full-LAN completed 25 Oct **12:00:05–15:23:57 UTC**. Seven feed/data containers were recreated after their Trivy scan: cert-bund-data, data-objects, dfn-cert-data, notus-data, report-formats, scap-data, vulnerability-tests. Read-only Ansible verified **SCANNED IMAGE SHA != RUNNING SHA == CURRENT TAG SHA** for EACH. Trivy metric exporter on greenbone-01 correctly reported **9/16 VALID_IMAGES and SCAN_COMPLETE=FALSE**. The saved summary was complete but **no longer matches seven running immutable image IDs**; never treat these absent CVEs as no findings.

**Status of five-host Trivy CVE publisher:** cloud-01 4/4 valid, monitor-01 6/6, komodo-01 2/2, docker-01 2/2, greenbone-01 **9/16 invalid coverage** following feed image replacement. All five have the new script from merged PR #195. Operators have verified end-to-end central Prometheus critical-CVE series on cloud-01; no new scan has been requested or run by the diagnostic. Remaining four publishers installed successfully 26 Oct around 13:38 UTC (Ansible ok=11 changed=2 failed=0 per host), backups recorded in issue #187. The merged PR #197 adds Greenbone-host and Trivy-image CVE dashboard features in Git, but **new Greenbone host CVE metric publisher and provisioned Grafana dashboard JSON remain NOT DEPLOYED**.

**Cause and current Git-only proposal:** Trivy systemd timer is scheduled **09:00 UTC + up to 30m**, but Greenbone feed refresh occurs **10:00 local** and recreates seven data-image containers. A separate Git-only change branch security/greenbone-trivy-timer-order-20261026 moves the daily Trivy run to **19:00 UTC + up to 30m** after the feed updater's 3h limit and Sunday's full-LAN 6h15 limit. New bounded playbook: IaC/ansible/playbooks/trivy-greenbone-after-feed-timer.yml, with explicit greenbone_trivy_timer_change_approved=true, backup, exact host/previous-timer checks and **timer-unit-only restart**, not scan/Docker changes. Offline test: scripts/validate-greenbone-trivy-schedule.py; runbook: docs/security/GREENBONE-TRIVY-AFTER-FEED-SCHEDULING-2026-10-26.md. **NOT YET MERGED OR DEPLOYED.** Timer change requires explicit operator approval even after merge.

**Next gates:** review the timer PR/CI first; merge if approved, sync admin-01 and run offline/Ansible syntax; independently authorize live timer change on greenbone-01; allow next scheduled Trivy scan or separately authorize an on-demand scan; then verify 16/16 current immutable image IDs with read-only Ansible and central Prometheus. Only afterwards separately authorize Greenbone host CVE exporter and Grafana dashboard JSON updates. The feed refresh reported FEED_CONTAINERS_UPDATED_IMPORT_PENDING: **Greenbone asynchronous feed import completion is not independently verified** by its updater's service success. Proposed scheduling reduces the daily race but is not proof against manual/late image changes. Security issue #187 tracks evidence. Historical instructions below about PR #195 being unmerged, five-host rollout being pending or greenbone-01 being 16/16 current are **superseded**.

---


## Grafana Trivy critical CVE references — improved compact design pending PR review (26 Oct 2026)

**User feedback:** The Grafana `Trivy — findings by image / severity` and `Trivy — scan validity per image` tables were cluttered with raw Prometheus sample metadata and duplicated image rows. User explicitly wants **CVE references** and a simpler dashboard. Previous PR #194 was merged; *no new live deployment is confirmed*, and user pasted the original raw table after that merge. Keep Git merge and deployment as separate states.

**New proposed branch:** `monitoring/trivy-cve-focused-20261026`; not deployed, not merged until approved.
- Shared Trivy publisher `IaC/ansible/roles/container_vulnerability_pilot/files/publish-estate-metrics.py` updated to **also** publish `homelab_container_estate_critical_cve{image,cve,packages,fixed_versions}=1`, one row per distinct CRITICAL advisory per validated image, deduplicating multi-package repeats. Reads original local Trivy JSON, checks summary freshness, Docker image identity, path and report metadata + count agreement. Failed, absent, stale or mismatched evidence is **not reported as clean**. Existing counts remain untouched where verified.
- Dashboard `IaC/ansible/roles/monitoring_stack/files/grafana/dashboards/production/homelab-vulnerability-management.json` retains original UID, refresh and eight summary stat panels; adds a **Trivy host filter defaulting to cloud-01**, summary of only nonzero-CRITICAL images, compact per-image critical **CVE/advisory ID + packages + fixed version** table with clickable OSV links, plus host scan age. Removes redundant low-value Trivy tables. Readable fields remove `Time`, `__name__`, `instance`, `job`. CRITICAL image rows and CVEs are not confused with counts of package findings or mitigations.
- Existing targeted approval-gated `playbooks/grafana-trivy-dashboard-update.yml` validator adjusted for new compact table IDs, still copies only one JSON file to monitor-01 with rollback backup and no container restart.
- New `IaC/ansible/playbooks/trivy-critical-cve-exporter.yml`: explicit separate approval; exact identity checks on five known scanner hosts; `serial: 1`; copy metrics exporter with rollback backup; publish from existing scan JSON (no new Trivy scan), validate textfile and Node Exporter. Canary `--limit cloud-01` first, then remaining four.
- New offline regression test `scripts/validate-trivy-cve-dashboard.py`, CI workflow `.github/workflows/validate-trivy-cve-dashboard.yml`, runbook `docs/security/GRAFANA-TRIVY-CRITICAL-CVE-2026-10-26.md`. After PR merge, user should run validation, pilot exporter, check Prometheus data and coverage, roll out remaining four, then targeted Grafana playbook; Grafana production provider polls files every 30s. **No live host changes yet; do not state dashboard is fixed until deployed and visually verified.**
- Confirmed cloud-01 Periphery 2.3.3 old Perl packages unchanged. 13 CRITICAL **package rows** represent 4 distinct CVEs (3 Perl repeated across four packages, one openssh-client). Nextcloud 35 image last Trivy scan 4 CRITICAL/231 HIGH; EXR coder mitigation does not patch libraries. CVE row deduplication changes only presentation, never source vulnerability counts.
- Continue security issue #187 and eventual separate approved Komodo image upgrade.

---


## Grafana Trivy dashboard readability — proposed IaC change 26 October 2026 (NOT DEPLOYED)

**User report:** At 11:52:46 the Grafana *Trivy — findings by image / severity* panel showed Komodo Periphery 2.3.3 (cloud-01 CRITICAL 13/HIGH 152) plus PostgreSQL and Redis; *Trivy — scan validity per image* showed Nextcloud 35 present and valid. Prometheus table `Time` is scrape/sample time, **not actual Trivy scan completion**. The canonical existing findings query `homelab_container_estate_findings` had no Nextcloud filter; the pasted excerpt may be a partial table, so no exporter bug was established. Independent 26 Oct 08:53 UTC Trivy validated Nextcloud 35 with 4 CRITICAL/231 HIGH package rows; controls don't lower package counts.

**Komodo read-only verification:** On cloud-01 running `ghcr.io/moghtech/komodo-periphery:2.3.3`; Perl `libperl5.40`, `perl`, `perl-base`, `perl-modules-5.40` all `5.40.1-6`; `openssh-client 1:10.0p1-7+deb13u4`; `ssh` and `perl` binaries present. Image still has 13 CRITICAL package rows (12 Perl rows across 3 CVEs with Trixie fix `5.40.1-6+deb13u1`, 1 OpenSSH client CVE without fixed version listed). `apt-cache policy` in running image only knew old installed version—do NOT treat that as evidence no upstream fix exists. **No package or container change.**

**Proposed branch** `monitoring/trivy-dashboard-clarity-20261026`:
- Updates `IaC/ansible/roles/monitoring_stack/files/grafana/dashboards/production/homelab-vulnerability-management.json`: keeps dashboard UID, 30s refresh and all original panels, makes general findings table readable by host/image/severity, adds dedicated Nextcloud severity table, actual last completed scan age (hours) by host, scan-complete status by host, critical findings by host; explains freshness and missing-data semantics. Does **not change Prometheus metric values**.
- Adds `IaC/ansible/playbooks/grafana-trivy-dashboard-update.yml`, an **explicit approval-gated, monitor-01-only** dashboard-file copy with JSON validation and backup, before/after Grafana health verification; avoids `monitoring.yml`, container reconciliation or Grafana restarts. Grafana provisioning file polling configured at 30s.
- Adds `docs/security/GRAFANA-TRIVY-DASHBOARD-2026-10-26.md` with PromQL diagnostics, runbook, verification and rollback.
- **Do not claim dashboard live until PR merged and the user executes approved Ansible playbook on admin-01, then verifies Grafana.** No live Grafana or Prometheus changes made in this conversation.
- Still need eventual controlled Komodo Periphery image upgrade and Trivy rescan through IaC, separate from dashboard work.

---


## Nextcloud remaining CRITICAL CVEs — read-only exposure triage completed 26 October 2026

**Current documented status:** No live host/container modifications during this triage. On `cloud-01`, Nextcloud `35.0.2.2` remained installed/healthy with maintenance false and needsDbUpgrade false. Earlier EXR IaC mitigation is live and merged; `CVE-2026-42216` and `CVE-2026-42217` are **mitigated for the ImageMagick EXR coder path only** (OpenEXR Debian libraries remain unpatched).

**`CVE-2026-6653` libxml2:** Debian image package `2.12.7+dfsg+really2.9.14-2.1+deb13u3`; PHP compiled and loaded libxml2 2.9.14, with DOM, SimpleXML, XMLReader, XMLWriter enabled. XML handling entry points found in bundled Sabre XML, phpseclib key parsers, Symfony DOM crawler and translation, Masterminds HTML5. Greps in apps/core/lib/3rdparty/custom_apps for explicit risky XML entity/DTD flags returned no matches; **this is not proof of safety**. Sabre `Service.php` defaults `$options=0` but callers can change it; `Reader.php` only invokes `libxml_disable_entity_loader` if `LIBXML_VERSION < 20900` (not true on 2.9.14). Symfony `addXmlContent` defaults to `LIBXML_NONET`, caller option overrides possible. No confirmed externally exploitable path for the CVE. Debian tracker lists Trixie vulnerable, `no-dsa` minor issue; no Trixie fixed package listed. **Keep open, no XML disablement/untrusted package mixing.**

**`CVE-2026-93221` kernel NFS server:** Trivy records `linux-libc-dev 6.12.113-1` inside Nextcloud image; these are **headers, not a running container kernel**. Host kernel is `6.12.111+deb13-cloud-amd64`. On cloud-01, `nfs-server.service` inactive / unit not found, `nfsd` absent from `/proc/modules`, no readable NFS-server thread status or TCP 2049 listener. Thus **no active NFS-server exposure observed** for the NFSv4 grace/recovery race at inspection. Do not equate with fixed Debian 13 host kernel; Debian tracker still lists 6.12 security branch vulnerable. Retain kernel patch monitoring, and reassess if NFS server enabled. **No Nextcloud container remediation required solely for dev headers.**

Trivy scan 26 Oct 08:53:20 UTC predates EXR mitigation and remains the last verified counts: Nextcloud image 4 CRITICAL/231 HIGH package finding rows; cloud-01 total 18 CRITICAL/427 HIGH. Do NOT decrement the scan findings based on mitigation/exposure review. New runbook `docs/security/NEXTCLOUD-REMAINING-CRITICAL-CVES-2026-10-26.md` holds evidence/decisions; `docs/security/CONTAINER-VULNERABILITY-STATUS.md` updated on proposed docs branch `security/nextcloud-critical-triage-20261026`. Track issue #187. Continue monitoring vendor security fixes for supported Debian 13 images and approved host kernel; avoid deploying or restarting services merely to clear scanner counters.

---


## Latest verified security outcome — Nextcloud EXR policy LIVE and accepted (2026-10-26)

**SUCCESS — operator-approved Ansible hardening completed on `cloud-01`: `ok=18 changed=1 unreachable=0 failed=0 skipped=1 rescued=0 ignored=0`.** Corrected IaC branch `security/nextcloud-exr-policy-20261026`, operator-local commit `768963d0` at execution. Managed ImageMagick `/etc/ImageMagick-7/policy.xml` retains eleven original active restrictions and ends with `<policy domain="coder" rights="none" pattern="EXR"/>`. Both Nextcloud app and cron containers have its read-only mount. App mount was already present and app recreation deliberately skipped; **only cron recreated**, with `--no-deps`. The playbook verified PNG/JPEG image encoding, **explicit EXR read and write policy denials in app**, matching policy in cron, HTTPS status, Nextcloud 35.0.2.2 health and `127.0.0.1:8080` loopback-only HTTP. PostgreSQL 18.6 and Redis 8.2.9 remained up and healthy, not recreated; Nginx unchanged.

**Security classification:** `CVE-2026-42216` and `CVE-2026-42217` are **mitigated for the ImageMagick EXR coder path only**, not package-fixed. OpenEXR 3.1.13-2 remains installed, scanner package findings may persist; no comprehensive proof that all OpenEXR library entry points are unreachable. Remaining `CVE-2026-6653` (libxml2) and `CVE-2026-93221` (linux-libc-dev) are open for separate investigation. The 26 Oct 08:53 UTC Trivy baseline (4 CRITICAL / 231 HIGH for the Nextcloud image) predates the policy rollout and must **not** be retrospectively reduced. Rollback remains via approved `IaC/ansible/playbooks/nextcloud-exr-rollback.yml`, not required by current evidence.

**Repository tracking:** GitHub PR **#192** holds IaC templates, Compose policy mounts, safe resumable hardening/rollback playbooks, validator and post-deployment documentation. This PR is separate from the live execution; do not presume it is merged. Security programme issue **#187** is to be updated with confirmed mitigation status, while remaining open for package-level fixes and other CVEs. Latest operational runbook: `docs/security/NEXTCLOUD-EXR-MITIGATION-2026-10-26.md`. Continue work on PR review/merge by explicit user approval, then libxml2 and linux-libc-dev triage.

---


## Active security change — Nextcloud OpenEXR decoder policy (26 October 2026)

**Historical pre-deployment state (superseded by the verified live outcome above).** Branch `security/nextcloud-exr-policy-20261026` prepares an ImageMagick EXR deny to mitigate access to the vulnerable OpenEXR decoder in `nextcloud:35.0.2-apache`. The user-provided 26 Oct Trivy report detected 4 CRITICAL rows: `CVE-2026-42216`, `CVE-2026-42217` in `libopenexr-3-1-30 3.1.13-2`; `CVE-2026-6653` in `libxml2`; `CVE-2026-93221` in `linux-libc-dev`. No fix versions listed in the local report. PHP Imagick 3.8.1/ImageMagick 7.1.1-43 advertises EXR; `coders/exr.so` was independently shown linked to libOpenEXR and libOpenEXRCore. Existing `/etc/ImageMagick-7/policy.xml` contains resource, HTTP/HTTPS/URL and @* read restrictions, but no EXR rule. Nextcloud 35.0.2.2 still healthy, maintenance false.

**Proposed IaC:** `IaC/ansible/roles/cloud_stack/templates/imagemagick-policy.xml.j2` retains all 11 active baseline rules then adds a last-matching EXR coder deny; the role manages a policy under `/opt/cloud-01/imagemagick/policy.xml` after its approval gate. Compose mounts policy read-only into **app and cron**, conditionally via `cloud_nextcloud_exr_policy_enabled`. New separate guarded Ansible cutover and rollback playbooks: `nextcloud-exr-hardening.yml`, `nextcloud-exr-rollback.yml` (both require explicit `-e ..._approved=true`, only `app` and `cron` recreated with `--no-deps`). Static validator `scripts/validate-nextcloud-exr-policy.py`; runbook `docs/security/NEXTCLOUD-EXR-MITIGATION-2026-10-26.md`.

**PARTIAL LIVE CUTOVER 2026-10-26 ~10:17 local:** User approved `nextcloud-exr-hardening.yml`. Ansible `ok=10 changed=4 failed=1` installed managed EXR-deny policy, updated Compose and recreated `app`, but stopped on an **ambiguous EXR write test**. The original `getImageBlob()` reported `Failed to get the image contents (empty or invalid image?)`; it did not prove writing allowed. Subsequent read-only probe confirmed `readImage("EXR:/dev/null")` explicitly failed with ImageMagick `not allowed by the security policy 'EXR'`; thus **app EXR reads are demonstrably denied**. Docker Compose ps confirmed app recreated, cron still ~2 hours old and not yet mounted, PostgreSQL/Redis still healthy (Up 10 days). HTTPS Nextcloud 35.0.2.2 remains healthy; HTTP still bound only to 127.0.0.1:8080. Do NOT call whole service fully mitigated, do not merge as verified.

**Resumption fix on PR #192:** playbook permits either original 11 active rules or approved 12-rule policy, checks existing app read-only bind mount and skips app recreation if already present. Corrected EXR write test uses actual `writeImage("EXR:/dev/null")` with explicit policy-denial assertion; read test follows the previously proved exception. Update local branch, run static/estate/syntax checks, perform a safe standalone write probe first, then seek explicit approval before continuing. If unexpected writing exception, investigate rather than bypass; cron deployment is still pending. Runbook has the exact partial-deployment timeline.

**Historical checklist before the successful cutover (already completed).** First validate branch diff, `python3 scripts/validate-nextcloud-exr-policy.py`, estate validator, and Ansible syntax for both playbooks. Only then seek approval for live cutover. After cutover, PHP Imagick must throw actual policy denial on EXR read/write, PNG/JPEG smoke tests pass, Nextcloud HTTPS 35.0.2 and loopback-only backend healthy, PostgreSQL/Redis unchanged. A policy does not remove vulnerable OpenEXR packages; Trivy counts may stay 4 CRITICAL pending vendor fixes. If failures, run the dedicated rollback playbook with explicit approval and do not invoke full cloud-stack role blindly. Track against issue #187. `CVE-2026-6653` and `CVE-2026-93221` need separate investigations.

---

## Latest completed change — Nextcloud 35 upgrade and security verification (26 October 2026)

**Current deployed state (verified by user-run Ansible and Docker commands):** `cloud-01` (192.168.2.53), Nextcloud **35.0.2.2**, image `nextcloud:35.0.2-apache` for `cloud-01-app-1` and `cloud-01-cron-1`. PostgreSQL `18.6-alpine` and Redis `8.2.9-alpine` remained running/healthy and were not recreated. Nginx HTTPS endpoint `https://nextcloud.home.jrwroberts.co.uk/status.php` passed version and health assertions; Docker backend remains **127.0.0.1:8080 only**. `php occ status`: installed true, maintenance false, needsDbUpgrade false. No data requiring production preservation, per user; directly upgraded from 34.0.3.2 to 35.0.2.2 without first deploying 34.0.5. **Do not blindly downgrade after DB schema migration** or rerun a one-time source-version-gated upgrade playbook.

**Change control:** Branch `security/nextcloud-34-to-35` was created and pushed on 26 Oct. Original upgrade IaC commit **`519cbc31`** updated `IaC/ansible/roles/cloud_stack/defaults/main.yml` and created `IaC/ansible/playbooks/nextcloud-upgrade-35.yml`. The playbook checks target identity and explicit `nextcloud_upgrade_approved=true`, deploys validated Compose, pulls only app/cron, stops cron, recreates app with `--no-deps`, waits for Nextcloud health and schema readiness, recreates cron with `--no-deps`, checks loopback binding, and verifies HTTPS server version and maintenance/upgrade states. Syntax check passed; the live upgrade recap was **ok=12, changed=5, unreachable=0, failed=0**, and post-upgrade Docker/OCC checks succeeded.

**Fresh Trivy evidence at 2026-10-26 08:53:20 UTC:** `homelab-trivy-cloud.service` result success / exit 0; scanner identified Nextcloud 35 immutable local image ID `sha256:1d5a25fae9df8df7ba9b49dbd75628c5e08e9a2fc463c02596641ee950935937`. Complete coverage, `RUNNING_IMAGES=4 VALID_IMAGES=4 SCAN_COMPLETE=TRUE`. Nextcloud image package-finding rows fell from **33 CRITICAL / 502 HIGH** (historical 34) to **4 CRITICAL / 231 HIGH** (35). Other cloud images: Komodo Periphery 13 CRITICAL / 152 HIGH; PostgreSQL 1 / 36; Redis 0 / 8. Current cloud-01 totals **18 CRITICAL / 427 HIGH**. These are package findings, not distinct CVEs, fixed-specific CVEs or confirmed exploitability; retain historical baseline separately. The remaining four Nextcloud critical rows need CVE/package/fixed-version triage from JSON reports.

**Official release notes:** [Nextcloud 35.0.2](https://github.com/nextcloud-releases/server/releases/tag/v35.0.2) (15 October 2026); selected upstream fixes cover sharing permissions, remember-me cookies, encryption metadata, filenames, search/rename and performance. These are *upstream release notes*, not proof every functionality was tested locally.

**Proxy/certificate status:** Nginx logs record real client `192.168.2.48`; Apache logs Docker peer `172.18.0.1`; Nextcloud's `getRemoteAddress()` logic uses `HTTP_X_FORWARDED_FOR` from a trusted proxy by default. Both `172.18.0.1` and `192.168.2.53` are trusted; actual live application-resolved IP still unobserved. Certbot DNS-01 renewal **dry-run** and explicitly executed deploy hook successfully reloaded Nginx on 26 Oct; real production renewal not yet observed. Renewal evidence is in separate PR #190 (do not presume merged).

**Documents updated on this same upgrade branch:** `docs/security/NEXTCLOUD-HTTPS-HARDENING.md`, `docs/security/CONTAINER-VULNERABILITY-STATUS.md`, `docs/network/hosts/cloud-01.md`, and this handover. Continue tracking GitHub security programme issue #187. Maintain canonical architecture and older dated Greenbone/Trivy records without retroactively overwriting their historical findings.

**Next safe actions:** review the branch diff and CI, create/review PR to main; run a read-only JSON triage of four remaining Nextcloud CRITICAL CVEs and refresh Prometheus/Grafana after the new scan; record individual CVE dispositions. Keep Ansible/IaC ownership, don't trigger the full `cloud-stack.yml` deploy or recreate PostgreSQL/Redis. Local `admin-01` branch will need `git pull --ff-only` to acquire these GitHub-side documentation commits.

---

**Last updated:** 26 October 2026

**Session focus:** Nextcloud 35.0.2 upgrade; post-upgrade Trivy image findings; ongoing Greenbone security programme

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
| 2026-10-19 | Daily Greenbone community-feed refresh timer enabled after safe active-scan preflight. | `greenbone-feed-refresh-timer.yml -e greenbone_feed_enable_timer=true`: ok=10 changed=0 failed=0. `systemctl list-timers` confirms `homelab-greenbone-feed-refresh.timer` next Tue 2026-10-20 10:00 BST; authenticated scan daily 02:00 and full-LAN weekly Sun 12:00 remain active. Prior dry-run returned `FEED_REFRESH=SKIPPED_ACTIVE_SCAN` with one authenticated task Running. | Verify first non-skipped feed pull/reconcile and actual Greenbone feed import; add feed freshness/failed-update monitoring. Do not interpret timer enabled as proof of updated CVE data. |
| 2026-10-19 | Weekly full-LAN Greenbone systemd timer enabled using original Ansible greenbone_scanning role; existing daily authenticated timer preserved. | `greenbone-full-lan-weekly.yml -e greenbone_scanning_full_lan_enable=true` recap greenbone-01 ok=14 changed=3 failed=0; both existing `managed --check` and `full-lan --check` passed. systemctl list-timers: daily authenticated next 2026-10-20 02:00 BST, full LAN weekly next Sun 2026-10-25 12:00 GMT. No scans started by timer deployment. | Verify automated CVE/VT feed refresh freshness/ownership and avoid image/container updates while active authenticated scan. Review authenticated post-remediation report when complete; reboot persistence of ICMP mitigations not yet proven. |
| 2026-10-19 | Missing full-LAN weekly Greenbone task created using existing host-side GMP runner, authenticated lookup PASS. | Ansible script created `Homelab - Full LAN - Weekly` task UUID `294085f9-541f-4f88-923f-d765b30822d8` (Greenbone target 192.168.2.0/24); subsequent `/usr/local/sbin/homelab-greenbone-scan full-lan --check` rc=0, PASS, task lookup 0.2s. Existing authenticated daily scan untouched. | Stage/enable existing-role weekly systemd timer only, verify next trigger and confirm authenticated daily timer unchanged. Feed refresh automation remains to assess; authenticated post-ICMP scan still running/pending results. |
| 2026-10-19 | Weekly Greenbone reconciliation DRY_RUN via Ansible PASS; not applied. | `greenbone-weekly-reconcile.yml` recap greenbone-01 ok=3 changed=0 failed=0; existing authenticated managed-infrastructure task `02b610fc-647a-4fb8-98c3-7763e0425c34` is Running; target has SSH credential, weekly full LAN task does not exist. Proposed (not active) full LAN Sunday 03:00 Europe/London and reuse authenticated task Wednesday 03:00. | Do not run apply while authenticated scan Running. Recheck task state and then authorise schedule setup, verifying resulting GMP tasks/schedules. 14/14 operational ICMP mitigations; authenticated scan report still pending. |
| 2026-10-19 | Proxmox-2 second ICMP cutover PASS, idempotent; 14/14 operational mitigations scanner-probe verified. | Live `homelab-icmp-proxmox2.service` enabled and active; dedicated inet table contains only tagged type-13 DROP, counter 3 packets/120 bytes. `pve-firewall status` unchanged `disabled/running`; pvecm quorate 3 votes with QDevice. Second `greenbone-icmp-proxmox2-cutover.yml` run ok=17 changed=0 unreachable=0 failed=0, scanner timestamp replies suppressed, normal ping/SSH and corosync/quorum remain healthy. | Run fresh full authenticated Greenbone scan and review findings before risk acceptance reconciliation; reboot persistence test outstanding. |
| 2026-10-19 | Proxmox-2 dedicated ICMP type-13 mitigation live cutover PASS; 14/14 operational mitigations applied. | `greenbone-icmp-proxmox2-cutover.yml --ask-become-pass` recap Proxmox-2 ok=17 changed=3 unreachable=0 failed=0. Dedicated helper and systemd unit deployed/enabled/started; independent Greenbone timestamp probe asserted zero matching replies; scanner ping and SSH before/after PASS; corosync active and pvecm cluster quorate before/after. Offline mocked apply/idempotency/rollback/drift guards and playbook syntax checks passed before cutover. | Inspect live dedicated nft table and service, ensure Proxmox firewall unchanged, run second idempotent cutover. Then perform full authenticated Greenbone rescan and review risk acceptances; reboot persistence still unverified. |
| 2026-10-19 | Proxmox-2 dedicated table nft ruleset syntax validated with `nft -c -f -` (Ansible rc=0), no live changes. | Controller reported nftables v1.1.3; staged Proxmox-2-only helper, dedicated boot unit, cutover and rollback playbooks, and mocked apply/rollback test in GitHub. Neither Proxmox firewall service or corosync is restarted in playbooks. | Pull and run offline mocked test, `python3 -m py_compile` and both Ansible syntax checks. Review source and table ownership before any cutover. Current 13/14 operational mitigations. |
| 2026-10-19 | Proxmox-2 final-host read-only cluster/firewall preflight PASS; no mitigation deployed. | Proxmox VE 9.2.21 kernel 7.0.14-24-pve, pve-firewall status disabled/running, pve-firewall and proxmox-firewall enabled, nftables v1.1.3, empty native nft tables and iptables INPUT ACCEPT in earlier read-only preflight. Cluster jameshouse-pve quorate (3 expected/3 total votes, QDevice present), corosync active, vmbr0 192.168.2.71/24, enx00249b7b346d 10.255.255.2/30. | Validate syntax only for separate host-owned inet table; stage audited persistence, exact rollback and scanner/SSH/quorum checks; never restart Proxmox firewall or corosync. Overall 13/14 operational mitigations. |
| 2026-10-19 | admin-01 controller ICMP mitigation second cutover run PASS, idempotent. | `greenbone-icmp-admin01-cutover.yml --ask-become-pass` second run recap ok=15 changed=0 unreachable=0 failed=0; Greenbone scanner no matching type-14 responses, ordinary ping and SSH available, QNetd active. Dedicated systemd unit enabled/active, nft counter 3 packets/120 bytes; stock nftables.service inactive. | Final host Proxmox-2: inspect firewall ownership and persistence read-only prior to any change. Reboot persistence and full authenticated Greenbone scan pending; preserve accepted-risk evidence. Overall 13/14 operationally mitigated. |
| 2026-10-19 | admin-01 controller-only ICMP timestamp mitigation live cutover PASS; 13/14 operational. | `greenbone-icmp-admin01-cutover.yml --ask-become-pass` recap admin-01 ok=15 changed=3 unreachable=0 failed=0. Dedicated helper and systemd unit installed, service started/enabled; independent Greenbone type-13 0-reply assertion, ordinary ping, SSH, and QNetd active all passed. | Confirm rule/unit state and second idempotent run; remaining Proxmox-2 only. Reboot persistence and full authenticated Greenbone scan still pending; retain risk acceptance until confirmed. |
| 2026-10-19 | admin-01 controller-only ICMP mitigation package staged in GitHub, NOT deployed. | Dedicated nft helper, systemd boot unit, cutover, rollback and static offline validator committed. Existing controller syntax checks for nft ruleset rc=0; nftables disabled, QNetd active. Live nft JSON output/rollback not simulated or validated yet. | Pull and run static validator and Ansible syntax; inspect helper's exact JSON matching and idempotent preflight before live change. Do not run cutover until dynamic test/rollback checks pass. Operational count 12/14. |
| 2026-10-19 | admin-01 nftables dedicated-table syntax compatibility confirmed read-only. | On admin-01, `sudo nft -c add table inet homelab_icmp_timestamp` returned TABLE_CHECK=0; nftables v1.1.3. No live tables/rules added. nftables.service remains disabled/inactive; QNetd active. | Stage dedicated controller-only boot-persistent type-13 rule with strict empty-table precondition, independent scanner verification and exact rollback; do not enable stock nftables.service or modify Proxmox cluster services. 12/14 operationally mitigated. |
| 2026-10-19 | admin-01 firewall ownership preflight PASS, no changes. | eth0 192.168.2.48/24, nft list tables empty, nftables.service disabled/inactive; stock unit ExecStart loads `/etc/nftables.conf` and ExecStop flushes whole ruleset. corosync-qnetd active. | Design separate, minimal nftables table INPUT type-13 drop with ACCEPT base policy, dedicated persistence and exact rollback; never enable/reload stock nftables service. Then Proxmox-2 gated host-specific review. Remediation remains 12/14. |
| 2026-10-19 | Komodo Docker post-firewall read-only health verification PASS. | `docker.service` active, `komodo-core-1` up, `komodo-mongo-1` healthy; iptables FORWARD DROP with DOCKER-USER/DOCKER-FORWARD jump chains intact; native inet filter input tagged `homelab-icmp-komodo-01` type-13 DROP counter 6 packets/240 bytes. Shell ad-hoc `CHANGED` reflects reporting only. | Develop separate controller and Proxmox mitigations; avoid stock nftables service reload/flush. Full authenticated Greenbone rescan and reboot persistence proof still pending. 12/14 operational mitigations. |
| 2026-10-19 | Five-LXC ICMP timestamp cutover idempotency verified across mail-relay-01, dns-02, dns-01, zabbix-01, komodo-01. | Repeat `greenbone-icmp-lxc5-cutover.yml`: all five hosts `ok=12 changed=0 failed=0 unreachable=0`; per-host Greenbone delegated ping and timestamp suppression assertions and SSH connectivity all PASS. Reboot persistence not yet tested; Komodo Docker application health still needs independent check. | Validate Komodo Docker service/networking, create separate host-specific safe controller (`admin-01`) and Proxmox-2 rollout, then full authenticated scan and risk-acceptance reconciliation. Overall 12/14 operationally mitigated. |
| 2026-10-19 | Four-host five-LXC continuation successful: dns-01, dns-02, zabbix-01, komodo-01; 12/14 operationally mitigated. | `greenbone-icmp-lxc5-cutover.yml --limit dns-02,dns-01,zabbix-01,komodo-01`: each `ok=12 changed=2 failed=0 unreachable=0`; per-host scanner ICMP suppression assertion, ping and SSH tasks completed successfully. Komodo post-cutover Docker application reachability not separately confirmed. | Independently verify Docker/Komodo service health, repeat batch idempotency, then develop guarded management-host and hypervisor mitigations. Retain risk acceptance pending full completed authenticated Greenbone scan and reboot persistence evidence. |
| 2026-10-19 | mail-relay-01 ICMP timestamp drop operational cutover successful (8/14). | Serial five-LXC playbook limited to mail-relay-01: `ok=12 changed=2 failed=0 unreachable=0`; helper and rule/config applied, Greenbone-independent post-probe `REPLIES_MATCHED=0` assertion passed, ordinary ping and SSH PASS. | Proceed to dns-02, dns-01, zabbix-01, komodo-01 serially with stop on failure; verify idempotency and persistence separately, retain risk acceptance until full Greenbone rescan. |
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

## 2026-10-29 — router-01 metrics tunnel staged (Git-only)

- Branch: feature/router-01-prometheus-metrics-tunnel-20261029.
- Estate validation PASS: 20 active, 0 planned, 5 retired guarded.
- Restricted SSH authentication from monitor-01 to router-01 previously verified PASS.
- OpenSSH 10.0p2 on monitor-01.
- Effective SSH configuration confirms localforward [127.0.0.1]:19100 [127.0.0.1]:9100.
- Existing tunnel service: inactive / not-found.
- Local TCP/19100 listener: absent.
- Stage installer and staged-unit rollback pass Ansible syntax checks.
- systemd unit template passes local systemd-analyze verify.
- Installer fingerprint and idempotency logic staged but not runtime-tested.
- No tunnel, firewall changes, Docker changes, Prometheus reload or router changes deployed.
- Next: add exact failure-safe installation handling, offline tests and independent staging verification before authorising installation.

### 29 October 2026 — installation approval gate verified

- Ran router-metrics-tunnel-stage.yml without approval.
- Expected failure at first task: Require explicit installation approval.
- Ansible recap: ok=0 changed=0 unreachable=0 failed=1.
- Default-deny gate PASS.
- No installation, systemd reload or service activation.
- Installation remains pending independent preflight and failure-path tests.

### 2026-10-29 — router metrics tunnel safety validation

- Router SSH host-key tests PASS:
  - Genuine pinned key accepted.
  - Incorrect address rejected.
  - Incorrect fingerprint rejected.
  - Duplicate router host records rejected.
- Corrected Ansible file lookups to use rstrip=False.
- Verified template SHA256:
  78280ee4f0910b49b7e72a9da8c4aa8a38cf0b536d74d7b076c116165915816d.
- Existing-unit state checks tightened.
- Added post-installation SHA256 verification.
- Six local unit-guard model tests PASS.
- Installer and rollback default-deny tests PASS in check mode.
- Both approval tests reported changed=0.
- Ansible syntax checks and estate validation PASS.
- No production services changed.
- Remaining: isolated actual-playbook failure-path tests,
  partial-installation recovery verification, and CI review.

### 2026-10-29 — isolated Ansible safety tests

- Added reusable isolated tests under tests/router-metrics-tunnel/.
- Real Ansible copy/slurp/SHA256 validation PASS.
- Modified unit caused expected assertion failure; rescued=1, failed=0.
- Temporary test directory cleaned up.
- State-guard test suite PASS with changed=0, failed=0.
- Unsafe active, enabled, failed, activating and inconsistent states rejected.
- Tests do not execute the production installer or systemd activation.
- Remaining: production-playbook failure-path verification,
  systemd sandbox review and CI checks.
- Deployment remains blocked.

### 2026-10-29 — static systemd unit rendering correction

- Found that Jinja2's default rendering strips the trailing newline.
- Verified the mismatch using standalone Jinja2 rendering.
- Tested actual Ansible rendering with newline preservation.
- Selected ansible.builtin.copy for the static systemd unit.
- Removed the temporary Jinja2 directive.
- Verified source SHA256:
  78280ee4f0910b49b7e72a9da8c4aa8a38cf0b536d74d7b076c116165915816d.
- Isolated Ansible content and state-guard regression tests PASS.
- Installer and rollback syntax checks PASS.
- Estate validation PASS: 20 active assets.
- No production changes.
- Outstanding: systemd sandbox access, partial-installation
  recovery, production installer/rollback execution tests and CI.

### 2026-10-29 — router metrics rollback recovery review

- Added checks for loaded systemd unit identity and state.
- Verified exact FragmentPath before allowing unit removal.
- Added post-reload and final pre-removal state checks.
- Added final unit SHA256, ownership and permission checks.
- Isolated rollback-resolution test PASS: failed=0, changed=0.
- Test covers missing, disabled, active, enabled and unexpected-path states.
- This is a model test, not execution of the production rollback.
- Real systemd reload/recovery and sandbox behaviour remain untested.
- Production staging and activation remain blocked.

### 2026-10-29 — router metrics tunnel runtime activated

- Guarded unit installation completed successfully on monitor-01.
- Actual staged-unit rollback completed successfully.
- Unit reinstalled and activation tested.
- Initial activation exposed an Ansible handling issue:
  systemctl is-enabled returns rc=1 for disabled units.
- Corrected activation playbook and repeated successfully.
- Runtime verification PASS:
  service active, disabled at boot, listener 127.0.0.1:19100,
  Node Exporter metrics accessible through restricted SSH.
- Router Node Exporter remains loopback-only.
- Prometheus and Docker networking not yet modified.
- Remaining: secured Prometheus connectivity, monitoring verification,
  persistent tunnel activation decision, CI and PR review.

### 2026-10-29 — router metrics private Unix relay

- Staged router-metrics-relay.service on monitor-01 using Ansible.
- Dedicated non-root service account: router-metrics-relay.
- Private socket: /run/router-metrics-relay/metrics.sock.
- Socket permissions: 0660; runtime directory: 0750.
- Initial test identified systemd shutdown exit-status handling.
- Added SuccessExitStatus=143 to the systemd unit.
- Corrected cleanup handling and repeated activation test.
- Final test: 12 successful tasks, 2 changes, 0 failures.
- Non-root process successfully retrieved Node Exporter metrics
  through Unix socket and restricted SSH tunnel.
- Relay remains disabled at boot and is stopped after testing.
- Existing Prometheus and Docker configuration unchanged.
- Remaining: container-side relay, Prometheus scrape job,
  end-to-end verification and boot persistence.

### 2026-10-29 — router metrics Prometheus integration

- Router Node Exporter scraped through restricted SSH forwarding.
- monitor-01 tunnel: 127.0.0.1:19100.
- Private Unix relay: /run/router-metrics-relay/metrics.sock.
- Docker sidecar shares Prometheus network namespace.
- Prometheus job router-node-exporter verified UP.
- 34 other targets UP during independent verification.
- Existing 192.168.2.220:9100 target DOWN; likely stale
  docker-01 identity, requiring separate inventory reconciliation.
- SSH tunnel and host Unix relay enabled at boot.
- Docker relay recovery timer enabled and active.
- Recovery tested by stopping only the relay container.
- Reconciler confirmed healthy-container idempotence.
- Prometheus container not restarted or recreated.
- Original configuration backup retained at
  /opt/homelab-router-metrics-relay/prometheus.yml.pre-router.
- Guarded rollback playbook created; not executed.
- Prometheus-container recreation recovery not independently
  tested; do not claim that scenario verified.

### 2026-10-29 — PR #240 post-deployment review

- Runtime confirmed: router-node-exporter UP; 34 other targets UP; SSH tunnel and Unix relay active/enabled, Docker relay running; recovery timer enabled/active.
- Removed obsolete docker-01 (192.168.2.220:9100) from monitoring_node_exporter_targets in Git. This is a template/defaults correction only; the live Prometheus config has NOT yet been re-rendered/reloaded to apply this removal.
- Draft PR previously described Git-only staging and was stale; PR metadata updated to reflect deployed services and remaining validation.
- Remaining checks before merge: validate the updated target list, scoped live config update/reload with rollback, review CI checks, and verify recovery after Prometheus container recreation (not yet tested).

### 2026-10-29 — live stale Docker exporter target cleanup

- Approval-gated `router-metrics-stale-target-cleanup.yml` completed on monitor-01: ok=11, changed=2, failed=0, rescued=0.
- Scoped Prometheus template was validated with promtool beforehand. The cleanup playbook asserted removal of only retired docker-01 (`192.168.2.220:9100`) and required router-node-exporter target health UP.
- Previous live Prometheus configuration backed up at `/opt/homelab-router-metrics-relay/prometheus.yml.pre-stale-cleanup`; original pre-router backup remains separate.
- Note: the new cleanup playbook is currently local/uncommitted on admin-01; add it to the PR via Git before merge.
- Prometheus-container recreation recovery remains untested; do not recreate production Prometheus merely to test it.

### 2026-10-29 — historical documentation branch reconciliation

- Archived 21 unmerged documentation branches under
  docs/archive/branch-evidence-2026-10-29/.
- Original patch content, branch heads, base commits and
  commit summaries preserved in the archive manifest.
- Historical records have not been applied to live IaC.
- Do not delete source branches until the reconciliation
  PR is merged and archived content is verified.
- Router configuration and security feature branches retained.

### 2026-10-29 — router toolset reconciliation

- Recovered the monitor-01 Loki readiness and router metrics
  SSH key access read-only diagnostic playbooks.
- Excluded obsolete router-side diagnostics targeting the
  former 192.168.3.1 staging network.
- No Ansible playbooks executed against live systems.
- Original router toolset branch retained pending separate
  reconciliation of its remaining installation and rollback work.

### Pi-hole DHCP DNS cutover — 2026-10-29

Branch: feature/router-01-pihole-dhcp-dns-20261029

LIVE CUTOVER SUCCESSFUL:
- router-01 DHCP now advertises 192.168.2.51 and 192.168.2.50.
- Default gateway remains 192.168.2.1.
- DHCP pool remains 192.168.2.100-199, 24h.
- Bedroom ASUS reservation .180 preserved.
- admin-01 reservation .48 preserved.
- dnsmasq --test passed.
- dnsmasq, Unbound, nftables and router-pppoe active.
- Both Pi-hole servers successfully resolved bbc.co.uk
  when queried directly from router-01.
- Cutover Ansible recap: failed=0, rescued=0.
- Original DHCP configuration backed up on router-01.

OUTSTANDING:
- Verify DHCP option 6 on a renewed client.
- Correct older reservation-sensitive DHCP preflight assertions.
- Retain rollback backup until client verification succeeds.

### Router DNS/DHCP final verification — 2026-10-29

- Windows client James-LT confirmed DHCP from 192.168.2.1.
- Client received DNS servers 192.168.2.51 and 192.168.2.50.
- Original DNS recovery backup retained under /var/backups/.
- Redundant Ansible backup removed from /etc/dnsmasq.d/ via
  validated cleanup playbook; no service restart required.
- DHCP exclusion preflight now recognises existing reservations.
- DHCP exclusion deployment remains blocked by a lease on .195.
- media-01 (2c:cf:67:30:be:1f) successfully rebooted and renewed
  its DHCP lease at 23:18:32, retaining 192.168.2.195.
- Reserve .195 through Ansible before future pool changes.
- No DHCP pool exclusions have been deployed.

### Historical monitoring recovery — 2026-10-29

- Recovered three Grafana router-device dashboards.
- Recovered LAN presence, router device events and Nmap worker
  Ansible roles, source code, tests and playbooks.
- Original recovery validation: 172 offline unit tests passed.
- Three recovered Ansible playbooks passed syntax checks.
- No recovered device-scanning roles or timers were deployed.
- At recovery time, DHCP forwarding was not yet configured.
  It was subsequently deployed and verified on router-01.
- Further Grafana integration and monitoring validation remain pending.

### Router DHCP forwarder implementation — 2026-10-29

Original implementation: c5a00284
Process cleanup hardening: 7355e494

Purpose:
- Forward filtered dnsmasq DHCPACK events from router-01
  to monitor-01 at 192.168.2.52:5514.

IaC:
- Role: IaC/ansible/roles/router_dhcp_log_forwarder
- Deploy: router-01-dhcp-log-forwarder.yml
- Rollback: router-01-dhcp-log-forwarder-rollback.yml

Validation:
- Deployment and rollback syntax checks passed.
- Non-root journal access verified.
- systemd unit validation passed.
- Tests cover filtering, transport, journal exit and cleanup.
- Forwarder subsequently deployed and enabled on router-01.
- Genuine DHCPACK delivery to monitor-01 verified.

Outstanding:
- Grafana and log pipeline integration.
- Durable journal replay/cursor support.
- Continued monitoring of forwarding reliability.

### Live DHCP forwarding verified — 2026-10-29

- Forwarder deployed through approved Ansible playbooks on router-01.
- Installation-only repeat: changed=0, failed=0.
- Dedicated non-root service account confirmed.
- systemd IP restrictions tested: monitor-01 allowed;
  an alternative destination was blocked (EPERM).
- Forwarder enabled at boot and running successfully.
- dnsmasq, nftables and Unbound remained active.
- Genuine DHCPACK received by monitor-01 at 21:17:17:
  192.168.2.198, MAC 16:c1:05:ad:4b:8a, james-s-A13.
- Receiver writes to the legacy rt-ac86u.log.
- Loki/Grafana integration remains unverified.
- Journal replay and forwarding metrics remain outstanding.

### Monitoring integration validation — 2026-10-29

- Recovered monitoring code consolidated into an integration branch.
- Offline unit tests: 186/186 passed.
- Five Ansible playbook syntax checks passed.
- Inventory review identified that inventory/hosts.yml does not
  currently define router-01.
- Legacy docker-01 entries remain in BirdNET, Komodo and monitoring groups.
- Router inventory reconciliation is required before any deployment.
- No monitoring roles, scans or services deployed by this integration.
