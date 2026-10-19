<!-- estate-authority: IaC/inventory/estate.json -->

# Greenbone accepted-risk assessment — 19 October 2026

**Status:** Review only. No accepted-risk policy or live firewall changes, and no new Greenbone scan completed by this review.

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
