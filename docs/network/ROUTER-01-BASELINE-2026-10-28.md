<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 post-cutover verified baseline — 28 October 2026

## Purpose, authority and safety

This is **observed live evidence**, not a proposed target configuration. Source is an operator-run, approval-gated Ansible **read-only** playbook on `admin-01` against physical Raspberry Pi 4 `router-01` at `192.168.2.1`. The exact source files were selectively ported from draft PR #210, without incorporating its incomplete monitoring/SSH stages or the historical migration PR #207.

**UTC timestamp:** `2026-10-28T22:09:06+00:00`. Controller source revision: `3e15857d` (`feature/router-01-toolset-audit-20261028`). Python AST validation: PASS; Ansible conditional validator: PASS; Ansible syntax check: PASS. Actual playbook recap: **router-01 ok=15 changed=0 unreachable=0 failed=0 skipped=0**. Preflight verified exact onboard MAC `d8:3a:dd:5a:51:44`, `eth0=192.168.2.1/24`, IPv4 default route via `ppp0`, and core services before and after the snapshot. No intentional configuration writes, service restarts, nftables changes, DHCP changes or SSH reloads. Ansible may use ephemeral execution files as normal. The collector emits diagnostic output only; it does not install itself or persist measurements on the router.

## Hardware and utilisation

| Metric | Verified observation |
| --- | --- |
| Hostname | `raspberrypi` (not yet renamed) |
| Kernel | `6.18.50+rpt-rpi-v8` |
| Uptime | 8.84 h |
| CPU cores | 4 |
| Three-second CPU busy | 0.1% |
| Load averages 1/5/15 min | 0.09 / 0.04 / 0.01 |
| CPU frequency / governor | 1800 MHz / `ondemand` |
| Board temperature | 45.3°C |
| Pi throttling bits | `throttled=0x0` |
| Memory | 3,795.7 MiB total; 3,538.2 MiB available; 6.8% estimated used |
| Swap | 0 MiB used |
| Root disk | 938.2 GiB size; 896.1 GiB available; 4.5% used |

## Interfaces and routing

| Interface | Carrier / state | Link speed | 3-sec RX / TX | Cumulative RX / TX errors | Cumulative RX / TX drops |
| --- | --- | --- | --- | --- | --- |
| `eth0` (LAN) | 1 / up | 1,000 Mb/s | 127.4 / 124.3 kbps | 0 / 0 | 150 / 23 |
| `eth1` (USB WAN) | 1 / up | 1,000 Mb/s | 123.0 / 126.9 kbps | 0 / 0 | 0 / 0 |
| `ppp0` (PPPoE) | 1 / unknown | n/a | 121.2 / 120.8 kbps | 0 / 0 | 0 / 0 |

`ppp0` has an IPv4 address and is the default route. The `unknown` interface state is not by itself evidence of failure. Counter totals are cumulative since interface reset, not three-second errors. The earlier independently recorded snapshot at `22:06:52 UTC` had exactly the same LAN drop totals (150 RX, 23 TX), supporting **no increase across these two samples**. Continuous error/drop monitoring under representative load is still pending.

A five-probe `ping -I ppp0 1.1.1.1` returned **0% loss**, minimum **10.339 ms**, mean **10.502 ms**, maximum **10.826 ms**, exit code 0. Earlier operator sample at `22:06:52 UTC` also showed 0% loss and mean 10.283 ms. This is a short WAN reachability check, not continuous SLA evidence or a WAN throughput benchmark.

## Services and sockets

`nftables`, `router-pppoe`, `dnsmasq`, `unbound`, `ssh` and `prometheus-node-exporter` were all **active**. DHCP lease file existed and contained **18 rows**; this is a row count, not proof of uniqueness or exclusion safety. The established DHCP scope from separate operator evidence is `192.168.2.100–199`; the baseline collector does **not** read the live dnsmasq range or reservations.

Listening sockets: DNS TCP/UDP `192.168.2.1:53` plus `127.0.0.1:53`; DHCP UDP `0.0.0.0:67`; SSH TCP `0.0.0.0:22` and `[::]:22`; Node Exporter TCP **`127.0.0.1:9100`**. Binding SSH to wildcard addresses is not proof the firewall allows unsolicited WAN SSH; independently inspect nftables before making claims about exposure.

## Interpretation and integration boundaries

**Healthy idle reference:** in these short snapshots there is no observed CPU, temperature, memory, disk, PPPoE or interface error issue, and no growth in LAN drop counters. These readings do not prove maximum PPPoE throughput, sustained stability, DNS correctness on all clients, DHCP reservation safety, firewall access policy or monitoring tunnel readiness.

**Unresolved and not included in this merge:**
- Canonical `IaC/inventory/estate.json` and legacy `hosts.yml` are not reconciled to the newly verified `192.168.2.1` Pi gateway and retired old router assumptions.
- Existing `router-01-toolset-audit.yml` and related C2 SSH playbooks on draft PR #210 still pin the **old primary** `192.168.3.1` address and are not suitable for blanket execution after the cutover.
- DHCP pool `192.168.2.100–199` overlaps at least the historically static `media-01` address `192.168.2.195`. Audit actual leases, exclusions and reservations before changing DHCP.
- ASUS remains an AP/AiMesh component based on separate user-reported cutover evidence. Its new management IP/backhaul details require revalidation.
- Do not auto-activate the old Kea migration configuration (PR #207), merge the historical MSS persistence playbook (PR #208) without adapting its address gates, restart nftables, or reload SSH/authorise the monitoring tunnel.
- Continue measurements under a controlled, representative client load in a separate approved step.

## Repeating the safe check

From the `admin-01` IaC repository after fetching the updated `main`:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/router-01-postcutover-baseline.yml playbooks/router-01-postcutover-baseline-readonly.yml --limit router-01 --syntax-check
ansible-playbook -i inventory/router-01-postcutover-baseline.yml playbooks/router-01-postcutover-baseline-readonly.yml --limit router-01 --ask-become-pass --check -e router_postcutover_baseline_approved=true
```

**Note:** The separate `validate-ansible-assert-conditions.py` helper used in the original successful operator run remains on draft PR #210. It is not part of this minimal merge. Ansible `--syntax-check` and exact reviewed read-only playbook remain required. This document records the previous real success and does not claim any later run.
