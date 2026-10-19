<!-- estate-authority: IaC/inventory/estate.json -->

# Finish the remaining 11 ICMP timestamp findings — 19 October 2026

**User decision:** Proceed with remediation across the rest of the affected estate. This authorises planning and carefully scoped changes, **not** a single unverified firewall replacement across mission-critical hosts.

## Verified starting point

The latest completed authenticated Greenbone report recorded 14 ICMP Timestamp Reply findings (NVT `1.3.6.1.4.1.25623.1.0.103190`). Independent before/after scanner-side network probes have already validated IPv4 type-13 request suppression while ordinary ping works on **media-01, docker-01, monitor-01**. The existing accepted-risk register remains unchanged, and no new completed Greenbone report has formally closed these findings.

Remaining 11 (from the active estate and Ansible inventories):

| Class | Target host (IPv4) | Service/criticality | Design constraint |
| --- | --- | --- | --- |
| Physical controller | admin-01 (192.168.2.48) | Ansible, SSH, Corosync QNetd | Do not interrupt operator access or quorum |
| LXC | dns-02 (192.168.2.50) | Pi-hole, Unbound, CT100 on PROXMOX | Preserve DNS; guest netfilter capability may be absent |
| LXC | dns-01 (192.168.2.51) | Pi-hole, Unbound, CT101 on Proxmox-2 | Preserve DNS and both Pi-hole resolvers |
| VM | cloud-01 (192.168.2.53) | Production Nextcloud, PostgreSQL and Redis | Preserve HTTPS, database and backup operations |
| LXC | mail-relay-01 (192.168.2.54) | Postfix internal SMTP, CT102 on PROXMOX | Preserve email delivery and alerting |
| VM | sensor-01 (192.168.2.55) | Suricata and Zeek passive sensor | Preserve monitored/captured network traffic |
| LXC | edge-01 (192.168.2.56) | Reserved edge CT103 on Proxmox-2 | Confirm effective packet-filter owner |
| VM | greenbone-01 (192.168.2.57) | Greenbone Community scanner | Probe from monitor-01, **not from itself** |
| LXC | komodo-01 (192.168.2.58) | Docker/Komodo control plane CT104 on PROXMOX | Preserve Komodo and Docker forwarding |
| LXC | zabbix-01 (192.168.2.59) | Zabbix, PostgreSQL, nginx CT105 on PROXMOX | Preserve critical monitoring |
| Proxmox hypervisor | Proxmox-2 (192.168.2.71) | Cluster node, storage, guests and NTP | Assess Proxmox-native firewall and cluster network first |

**Do not modify PROXMOX (192.168.2.70)** based on this 11-host ICMP list. It is a supporting hypervisor for some LXC guests, not a reported ICMP timestamp target in the last completed 14-item report.

## Stage 1 — capture compatibility and remaining exposures

The committed `IaC/ansible/playbooks/greenbone-icmp-timestamp-remaining11-readonly.yml` is **read-only** and serialises checks. It captures bounded, non-secret service/firewall indicators: active nftables/UFW/firewalld/Proxmox firewall services, container marker, effective `CAP_NET_ADMIN`, iptables backend and INPUT/FORWARD policy, existing INPUT timestamp references, Docker chain count and nft input/forward hooks. It then sends 3 ICMP timestamp requests per target from greenbone-01, **except greenbone-01 itself, which is probed externally from monitor-01**. Ordinary ping provides context; no reply alone does not establish a fix.

Required offline source check: `python3 scripts/validate-icmp-timestamp-remaining11-audit.py`; existing estate validator `scripts/validate-estate.py`; Ansible syntax check. **Audit has been staged in Git but not yet executed on any of these 11 hosts.**

## Stage 2 — grouped, individually validated remediation

Build narrow target-specific Ansible cutovers only when the relevant Stage 1 findings support a safe mechanism:

1. **VMs** (cloud-01, sensor-01, greenbone-01): where confirmed authoritative, apply a single exact-destination IPv4 type-13 DROP in host INPUT using the installed packet-filter backend. Pre/post check current services, access, and external scanner response. Never flush a ruleset.
2. **admin-01:** handle independently because it is the Ansible controller, SSH jump and QNetd arbitrator. Validate management/cluster connectivity and recovery access; do not change broader firewall policy.
3. **Six LXC guests:** if no `CAP_NET_ADMIN` or the effective guest firewall is Proxmox-managed, do **not** try to enable nftables/iptables inside containers. Implement through the correct cluster/guest policy after identifying Proxmox owner and rules. Protect both DNS resolvers and Proxmox networking.
4. **Proxmox-2 hypervisor:** separate change plan based on the active Proxmox-native firewall mode and existing node/cluster policy. Preserve cluster, heartbeat, storage, migration and guest traffic. No blanket iptables restore, global rule flush or cluster-wide policy change.

Before each cutover, verify scanner-side baseline replies, normal ping, critical services, and SSH/recovery route. Change one host at a time with a persisted IaC rule and exact rollback. Post-change test ping, absence of timestamp replies and unaffected critical paths. Never restart critical Docker/application services just to install the single rule. Stop and investigate on unexpected failure.

## Stage 3 — scanner proof and accepted-risk reconciliation

After controlled mitigations, verify no managed scan is already active, check Greenbone GMP readiness, and start **one** fresh completed authenticated managed scan. Reconcile real scan report timestamps/ID with the accepted-risk register, including the two previously actionable Mediums and the separate BirdNET-Go CSRF cookie HttpOnly exception. Do not remove risk acceptance records solely because a three-packet probe saw no reply.

**Current state:** Stage 1 code committed only; **3 of 14** ICMP hosts were already independently mitigated; **11 remain**. No changes to the other hosts, kernel, Proxmox policy, scan scheduler or accepted-risk register have been made by preparing this plan.
