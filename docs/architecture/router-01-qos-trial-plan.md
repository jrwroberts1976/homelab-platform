# router-01 CAKE/SQM — staged trial plan (30 October 2026)

Status: **DESIGN ONLY — no QoS modifications authorised or deployed**.

## Access technology confirmed by owner
- Vodafone **SoGEA VDSL2 through a separate modem**, with router-managed PPPoE. CAKE trial overhead candidate: `pppoe-ptm` (30-byte overhead plus PTM framing). Check for modem/ISP VLAN tag(s) before applying; additional tag overhead may be required. This is not FTTP/ONT.


## Baseline evidence
- Vodafone Ookla tests from wired admin-01: 47.42 / 14.75 Mbps and 47.37 / 14.52 Mbps download/upload.
- Idle RTT 9.43–9.66 ms; loaded download RTT ~31.5–32 ms; loaded upload RTT ~156–157 ms.
- router-01: Debian 13 Raspberry Pi 4, PPPoE ppp0 MTU1492, default route ppp0; eth1 AX88179 USB Ethernet.
- ppp0 has noqueue, eth1 fq_codel, eth0 mq with fq_codel child queues. Interface counters advance normally; no ingress tc filters / IFB configured.
- sch_cake and ifb modules available, not yet active. PPPoE managed by router-pppoe.service with Restart=always; no custom PPP lifecycle hooks installed.
- Baseline router temperature ~41.8C and PPPoE, dnsmasq, unbound, nftables all active.

## Ethernet capture evidence (30 October 2026)
- A 15-frame header-only tcpdump on eth1 showed PPPoE session frames in both directions, with no visible 802.1Q tags on the router-to-modem Ethernet segment. This does not exclude VLAN encapsulation applied inside the modem.
- Kernel capture reported zero dropped frames. Captured `tcp 1452` lengths represent TCP payload lengths, **not** direct MSS negotiation evidence; existing MSS clamp should be validated independently if needed.
- Owner confirms SoGEA via standalone VDSL modem. Use `pppoe-ptm` as the initial CAKE overhead candidate, then test latency/throughput.

## Deployment prerequisites and safety gates
1. SoGEA VDSL2 with separate modem is confirmed. Verify presence of VLAN tagging; use the `pppoe-ptm` overhead profile as the initial candidate and tune after measurement.
2. Determine correct egress location by inspecting ppp0 and eth1 packet paths. Prefer applying CAKE where it can see the desired flow classification and shaping; physical eth1 is PPPoE-encapsulated and may not permit desired host isolation.
3. Choose a controlled, reversible **temporary** trial, not persistence in the first step. Provisional targets: 13 Mbit/s upload, 43 Mbit/s download. Re-test and tune.
4. Verify before mutating: named router identity, working key-based admin SSH, WAN route, DNS, PPPoE service, existing tc filters/qdiscs, no prior trial transaction, and a functioning rollback timer.
5. Capture detailed baseline qdisc and filter state and prepare a narrowly scoped, tested restore procedure. Avoid blind `tc qdisc del` on an interface whose queue has changed unexpectedly.
6. Arm an automatic recovery timer **before any traffic-control modification**. A recovery script on /run must be invoked through /bin/sh because /run is noexec. Ensure transient systemd unit names are not already loaded.
7. Initially trial upload shaping alone if downstream path / IFB construction remains uncertain. For download, IFB may redirect PPP ingress; prefer staging and testing this separately.
8. Run objective after-tests from wired admin-01: new-connection admin SSH, DNS lookup, WAN reachability, Prometheus router metrics, repeat Ookla loaded latency and throughput; inspect `tc -s qdisc` drop and overlimit counters and host CPU/temperature.
9. Explicitly stop rollback timer only after all checks pass and the trial is accepted. Retain recovery evidence for review.
10. After validated trial, implement persistent idempotent Ansible IaC and PPPoE reconnect lifecycle handling, along with controlled disable/rollback.
11. Preserve Avahi for local media discovery; do not modify PPPoE, MSS clamp, DNS, DHCP, nftables or SSH policies in QoS work.

## Known limitation
WAN `eth1` egress contains PPPoE frames and its qdisc byte accounting differs from ppp0. Interface byte counters alone cannot demonstrate suitability for CAKE host isolation; a staged trial and comparison is required.
