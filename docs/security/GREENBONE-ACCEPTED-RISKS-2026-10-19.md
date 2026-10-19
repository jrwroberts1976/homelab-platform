<!-- estate-authority: IaC/inventory/estate.json -->

# Greenbone accepted-risk assessment — 19 October 2026

**Status:** Two hosts, media-01 and docker-01, have now been independently verified with ICMP timestamp replies suppressed while normal ping still works. The remaining 12 ICMP findings and the BirdNET csrf HttpOnly exception are not remediated. The accepted-risk register is unchanged; a new authenticated Greenbone vulnerability scan has not yet been completed.

## Confirmed live docker-01 ICMP timestamp filter — 19 October 2026

**Deployment complete:** User ran the scoped, Git-managed `greenbone-icmp-timestamp-docker01-cutover.yml`. `docker-01 ok=22 changed=3 unreachable=0 failed=0`; independent `greenbone-01 ok=8 changed=0 unreachable=0 failed=0`. Before remediation, 3/3 timestamp requests yielded replies. After the host INPUT-only iptables-nft type-13 drop was installed, the scanner-side assertion verified zero matching replies and `DOCKER01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, while `DOCKER01_ICMP_ECHO=PASS`. Docker service stayed running, container identities remained unchanged, DOCKER and FORWARD chain invariants passed, and trusted BirdNET HTTPS continued responding without Docker restart. The dedicated systemd persistence unit was installed but **has not been reboot-tested**. Explicit rollback `greenbone-icmp-timestamp-docker01-rollback.yml` remains available and unused. This is **operational mitigation 2/14**, not new Greenbone scan clearance; all risk acceptance entries remain in place until later scanner verification. Twelve more ICMP hosts and the BirdNET csrf HttpOnly exception remain outstanding.

## docker-01 audit and verification gate — 19 October 2026
## docker-01 timestamp responses confirmed — 19 October 2026

Read-only Ansible completed on `docker-01` (`ok=3 changed=0 failed=0`) and `greenbone-01` (`ok=5 changed=0 failed=0`). Normal ping to `192.168.2.220` passed; three type-13 requests produced **three matching type-14 replies** (`ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED`). Thus the accepted ICMP timestamp disclosure remains reproducible on docker-01. No host changes were made. The submitted excerpt does **not contain the `Report non-secret Docker firewall indicators` output** from the first play; so iptables backend, INPUT policy, Docker chain counts and ownership remain unknown. Re-run the existing read-only diagnostic with `--limit docker-01 --forks 1` to collect that specific result before developing any Docker-safe mitigation. Do not install media-01's nftables ruleset on docker-01.



The user ran the existing one-host read-only firewall audit on docker-01 (Raspberry Pi 4, Debian 13): `ok=2 changed=0 failed=0`. No active nftables, UFW, firewalld or Proxmox firewall service; nftables rules readable, **zero input hooks**, no timestamp-specific rules; iptables-save readable, no timestamp references. These are **not** proof that iptables owns host INPUT filtering or that the old ICMP finding is still reproducible. The existing Docker networking must be preserved.

New Git-staged, **not run**, `IaC/ansible/playbooks/greenbone-icmp-timestamp-docker01-readonly.yml` reports non-secret filter policy and backend indicators on docker-01 and performs bounded scanner-side ICMP timestamp probing from greenbone-01. It changes no firewall, service, sysctl, kernel, scan or risk acceptance. Only after this evidence should a Docker-safe, narrowly scoped mitigation and rollback be designed; do not copy the media-01 nftables ruleset.

## docker-01: host INPUT evidence and staged targeted mitigation

**19 October latest read-only audit:** `docker-01 ok=3 changed=0 failed=0`: Docker active with two containers; `iptables v1.8.11 (nf_tables)`; filter INPUT ACCEPT with zero INPUT rules; FORWARD DROP, four DOCKER filter chains; nftables INPUT hooks 0, FORWARD hooks 1; no timestamp rule. Scanner-side probe `greenbone-01` previously confirmed 3 of 3 matching timestamp replies and ordinary ping PASS.

**Git-only, not deployed or independently rechecked yet:** New Ansible role `IaC/ansible/roles/docker_icmp_timestamp` uses a single idempotent `iptables -w -I INPUT 1 -d 192.168.2.220/32 -p icmp --icmp-type 13 -m comment --comment homelab-docker01-icmp-timestamp -j DROP`, guarded by `iptables -C` and backend detection. A dedicated oneshot unit persists the rule over reboot without enabling global nftables or restarting Docker. A scoped manual rollback stops and disables only that service, removing just the exact tagged host INPUT rule; it does not alter DOCKER chains, FORWARD, or NAT. `greenbone-icmp-timestamp-docker01-cutover.yml` includes scanner pre/post tests and Docker/BirdNET invariants. `scripts/validate-docker01-icmp-timestamp-firewall.py` is the offline preflight. No live change, risk reclassification or full Greenbone rescan is claimed yet; source validation, syntax checks and scoped deployment are still required.

## monitor-01 preliminary read-only evidence — 19 October 2026

`monitor-01` (192.168.2.52) read-only audit succeeded (`ok=2 changed=0 failed=0`): Debian 13, nftables/UFW/firewalld/Proxmox services not active/unknown, `NFT_RULESET=not-readable`, `IPTABLES_RULESET=readable`, no existing iptables timestamp references. This does **not** prove what INPUT rules or backend are in effect. Existing monitoring workloads should be preserved. A scoped, Git-only `greenbone-icmp-timestamp-monitor01-readonly.yml` checks iptables policy/backend, constrained monitoring service health indicators and independently probes three ICMP type-13 requests from greenbone-01 with an ordinary ping comparison. It has not run yet. No other host configuration or risk acceptance changes have occurred.

## Last report's 15 accepted findings

| Finding | NVT OID | Count | Disposition |
| --- | --- | ---: | --- |
| ICMP Timestamp Reply Information Disclosure | 1.3.6.1.4.1.25623.1.0.103190 | 14 | Candidate for narrow IPv4 ICMP timestamp-request (type 13) filtering, once firewall owner is identified |
| BirdNET-Go csrf cookie missing HttpOnly | 1.3.6.1.4.1.25623.1.0.105925 | 1 | Keep accepted pending deployed-version CSRF compatibility verification |

The accepted-risk **allowlist** also contains 15 older TCP timestamp NVT 1.3.6.1.4.1.25623.1.0.80091 entries; these are not among the 15 findings in the last report. Do not indiscriminately turn off TCP timestamps.

## Host scope for ICMP timestamp review

| Host | IPv4 | Special considerations |
| --- | --- | --- |
| media-01 | 192.168.2.195 | First pilot candidate: Git-managed nftables input currently broadly accepts ICMP; protect Kodi, SMB, NFS, HTTPS |
| docker-01 | 192.168.2.220 | Docker/BirdNET networking |
| admin-01 | 192.168.2.48 | SSH, Ansible controller, QNetd |
| dns-02 | 192.168.2.50 | Pi-hole/Unbound LXC |
| dns-01 | 192.168.2.51 | Pi-hole/Unbound LXC |
| monitor-01 | 192.168.2.52 | Grafana/monitoring |
| cloud-01 | 192.168.2.53 | Nextcloud |
| mail-relay-01 | 192.168.2.54 | SMTP relay |
| sensor-01 | 192.168.2.55 | Network sensor |
| edge-01 | 192.168.2.56 | LXC policy |
| greenbone-01 | 192.168.2.57 | Scanning and Docker |
| komodo-01 | 192.168.2.58 | Container control plane |
| zabbix-01 | 192.168.2.59 | Monitoring |
| Proxmox-2 | 192.168.2.71 | Hypervisor: Proxmox-native firewall/cluster safety |

PROXMOX at 192.168.2.70 is NOT in the last report's 14 ICMP findings. Its older TCP timestamp acceptance is a separate category.

## Confirmed live evidence — media-01 responds to ICMP timestamps

**19 October 2026:** User ran the scoped read-only Ansible probe from greenbone-01 to media-01 after successful offline probe self-test, estate validation and playbook syntax check. Greenbone probe execution ended `ok=5 changed=0 unreachable=0 failed=0`. Normal IPv4 ping passed. **3 of 3 ICMPv4 timestamp requests received matching ICMPv4 timestamp replies**: `ICMP_TIMESTAMP_RESULT=REPLY_CONFIRMED`. This independently confirms the ICMP timestamp disclosure remains present on media-01, not that it has been eliminated. No new Greenbone scan was run. Per user's explicit no-firewall direction, **retain this risk acceptance**; neither nftables, sysctl nor risk disposition changed. No equivalent observation has yet been collected for the other 13 hosts.

## Historical staging note — scanner-perspective probe (now executed)

A scoped Ansible diagnostic `IaC/ansible/playbooks/greenbone-icmp-timestamp-media01-readonly.yml` plus Python packet probe `IaC/ansible/playbooks/files/icmp-timestamp-probe.py` has been committed. It uses root raw IPv4 ICMP on **greenbone-01** to transmit **three ICMP timestamp requests (type 13)** to **media-01**; it counts only matching, checksum-valid **timestamp replies (type 14)** and runs an ordinary ping as a reachability baseline. `scripts/validate-icmp-timestamp-probe.py` checks the offline logic. It does not change firewalls, sysctl, Greenbone scans, service state or risk acceptance. The diagnostic is **Git-staged, not yet syntax-checked or executed by the user**. Positive replies confirm exposure; absence of replies does not by itself clear the accepted finding. This approach honours the user's decision against firewall changes.

## Current user decision: no firewall modification
## Follow-up kernel investigation — read-only evidence, 19 October 2026
## Live pilot outcome — media-01 timestamp requests blocked

**19 October 2026, user-provided Ansible evidence:** The approved `greenbone-icmp-timestamp-media01-cutover.yml` completed successfully on **media-01 (`ok=18 changed=2 failed=0`)** and independent verifier **greenbone-01 (`ok=8 changed=0 failed=0`)**, with neither unreachable. Before mitigation, the scoped scanner-side test recorded **3 matching replies from 3 unicast ICMP timestamp requests**. After activating the narrow, Git-managed `icmp type timestamp-request drop` rule, the verifier returned `MEDIA01_ICMP_TIMESTAMP=NO_REPLY_OBSERVED`, `MEDIA01_ICMP_ECHO=PASS`, and `HTTPS_443=PASS; LAN_HTTP_8081=BLOCKED; LOOPBACK_HTTP_8081=AVAILABLE`. This is strong independent evidence of successful operational mitigation **on media-01 only**, not confirmation from a completed new Greenbone vulnerability report. No application, kernel or sysctl change was required. Scoped manual rollback remains Git-managed but unused. **Existing risk acceptances have not been removed or reclassified.** 13 other reported ICMP hosts and the one BirdNET csrf HttpOnly finding remain for separate decisions.

## Historical pilot plan — approved and now deployed

After the no-sysctl kernel investigation, user explicitly approved **adding a firewall mitigation** for media-01. Do **not install a second firewall**: `media_firewall` already manages `/etc/nftables.conf`. A single conditional IPv4 timestamp-request (type 13) drop is Git-staged before broad ICMP allow, with a separate opt-out rollback playbook and pre/post independent scanner probes. **The user has not yet deployed it; the previously reproduced 3/3 replies remain the last live evidence.** Leave all 15 accepted-risk allowlist entries unchanged until a fresh completed Greenbone scan confirms findings are eliminated; the BirdNET HttpOnly acceptance remains separate. No kernel modifications or reboots.

## Verified downstream kernel sysctl absence — 19 October 2026

User ran the read-only Ansible check on media-01: `TIMESTAMP_SYSCTL=NOT_PRESENT` for `/proc/sys/net/ipv4/icmp_timestamp_ignore_all`, on active Raspberry Pi kernel `6.18.50+rpt-rpi-2712`. Together with the independent 3/3 positive timestamp-response probe, this confirms the issue remains present and that **this build does not provide the proposed selective unicast ICMP timestamp sysctl**. Current Linux kernel sysctl documentation does not list it; the corresponding 2024 patch proposal encountered upstream review objections. TCP timestamp hardening is unrelated. No firewall/sysctl/package/kernel/service/risk disposition changes were made. The user declined a firewall change. A custom kernel modification would require a separate formal risk/maintenance review and reboot and is not being staged. Keep current low-impact risk acceptance while the user determines priorities.



The user confirms they have **not changed the kernel**. media-01 is running Raspberry Pi ARM64 Debian 13 kernel 6.18.50+rpt-rpi-2712 (package 1:6.18.50-1+rpt1, built 2026-09-11). The installed rpi-2712 kernel package matches the running version; older 6.18.34 and 6.18.39 packages remain installed. Current settings: net.ipv4.icmp_echo_ignore_all=0, net.ipv4.icmp_echo_ignore_broadcasts=1. The latter suppresses broadcast/multicast timestamp requests but not the unicast timestamp requests that returned 3/3 from greenbone-01. No kernel, sysctl or firewall changes were made. A proposed upstream May 2024 patch added icmp_timestamp_ignore_all, but this does not appear in standard kernel sysctl docs and drew maintainer objections. Next check for its availability in the running Raspberry Pi downstream /proc/sys tree **read-only**, without assuming it exists. Do not disable ping or set an unknown sysctl; do not rebuild kernel without an explicit risk review and approval. Keep the existing low-risk acceptance in force for now.



The read-only media-01 audit passed (ok=2 changed=0 failed=0) and identified active nftables with broad IPv4 ICMP acceptance and no timestamp-specific rule. The user does not want a firewall change for these accepted ICMP findings. The previously described nftables pilot is **not authorised** and remains only a historical technical option. The existing TCP timestamp sysctl role does not affect ICMP replies; documented kernel sysctls do not selectively disable unicast ICMP timestamp responses. Do not alter the 15 accepted-risk findings based on this review. Investigate from an independent scanner perspective, read-only, before revisiting the risk disposition.

## Previously considered mitigation strategy (not approved)

For a confirmed nftables-managed input chain, an IPv4 ICMP type 13 request drop before a broad IPv4 ICMP allow is promising. Do not drop all ICMP: preserve echo/ping, path MTU and IPv6 network/neighbor discovery. Some hosts may use Proxmox-native filtering, UFW or Docker-managed rules; these must be diagnosed separately. Never introduce an unmanaged temporary host firewall rule as the persistent fix.

The BirdNET-Go csrf cookie is intentionally not HttpOnly in upstream middleware, and is different from a login-session cookie. The frontend in newer source also retrieves its token from /api/v2/app/config, which does NOT prove that every deployed code path tolerates an HttpOnly override. The Nginx Secure flag has already been corrected. Do not set HttpOnly without testing the exact installed version and state-changing WebUI actions.

## Execution plan

1. Run the new read-only Ansible playbook IaC/ansible/playbooks/greenbone-accepted-icmp-firewall-readonly.yml on the 14 affected hosts after syntax checking. Only non-secret firewall indicators and rule-reference counts are printed.
2. Use results to choose a single pilot, likely media-01; stage a Git-managed narrow ICMP filter with rollback and non-disruptive validation.
3. Expand only with mechanism-specific code where each host's firewall owner is known; treat the hypervisor and containers with particular care.
4. Obtain a fresh completed authenticated Greenbone report. Only remove corresponding accepted-risk entries after scanner evidence confirms they no longer occur.
5. Leave the BirdNET HttpOnly exception accepted unless compatible CSRF behaviour is demonstrated on the running version.

**No mitigation has been deployed and no risk status has been changed by this review.**
