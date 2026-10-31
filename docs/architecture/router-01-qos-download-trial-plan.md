# Router download CAKE / IFB trial — 31 October 2026

## Verified baseline
- Router `router-01`; physical WAN `eth1` holds proven, persistent 13Mbit CAKE upload shaper (`ptm overhead 30`).
- Logical PPPoE `ppp0` MTU 1492, default IPv4 route. No `ppp0` ingress filter, no IFB devices, no physical `eth1` ingress filters.
- Modules `ifb`, `act_mirred`, `cls_matchall` are available. All essential services active. Read-only Ansible preflight passed (4 tasks, 0 changes).
- Prior download baseline ~47.37 Mbps with ~31.99ms download-loaded RTT. Initial IFB rate candidate 43Mbit; performance to be verified with fresh tests.

## Trial design (not yet activated)
- Prefer `ppp0` ingress (decapsulated IP) to avoid attempting IP-level classification on PPPoE Ethernet frames.
- IFB `ifb-wan0` created expressly for this trial; CAKE egress on IFB at 43Mbit, `besteffort flows`. The WAN ADSL/VDSL/PTM physical wire overhead may require adjustments to bandwidth and overhead after measurements; no assumption that `pppoe-ptm` is correct on decapsulated ppp0 ingress.
- Attach `clsact` ingress qdisc to `ppp0`; install `matchall` filter with `mirred egress redirect dev ifb-wan0`. Ensure IP/IPv6 and session packet behaviour are evaluated; attach only after rollback is armed.
- Time-limited systemd rollback should remove only trial-owned filter/qdisc and IFB, never modify WAN upload CAKE on `eth1`, PPP daemon, firewall or DNS.
- **Potential risk**: the `ppp0` interface can disappear and reappear on PPPoE reconnect; rollback and cleanup must tolerate that condition. Existing hooks not installed. Any trial may interrupt WAN traffic temporarily; spare router and local console should be available.
- Trial must fail closed on unexpected interfaces, active qdisc, existing filters or prior trial artifacts. Add Ansible unit verification, proper IFB teardown and rollback proof before deploying.
- After connection and speed tests: either allow rollback, or guarded acceptance; do not enable reboot persistence until separate recovery and reboot validation.
