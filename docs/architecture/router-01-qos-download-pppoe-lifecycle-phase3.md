# Router-01 download QoS — Phase 3 PPPoE lifecycle design

Status: **design only — not deployed, enabled or approved for production**.

## Verified state

- 43Mbit IFB CAKE temporarily achieved about 41.6 Mbps downstream and ~10ms download-loaded latency.
- Temporary systemd rollback fired on schedule, restoring the original `ppp0` ingress and preserving 13Mbit `eth1` upload shaping.
- Phase 2 controller validation passed: 4 OK, 0 changed. It checks syntax and a deliberately disabled candidate service, **not reconnect behaviour**.

## Proposed lifecycle

A PPP-layer **ip-up.d / ip-down.d** hook (or equivalent event-driven mechanism that is verified on the actual router PPP installation) must signal an independent, serialized systemd reconciliation unit. Do not assume `After=router-pppoe.service` means `ppp0` exists or that `RemainAfterExit=yes` will reapply QoS after a reconnect.

1. **On PPP up:** receive and verify the current `ppp0` identity; reconcile owned IFB/ingress state under a single lock. Verify the default route, upload CAKE, and absence of foreign ingress filters before attachment. Never modify `eth1` upload CAKE, PPP daemon, firewall, DHCP or DNS.
2. **On PPP down:** identify the original interface via recorded interface identity and detach only owned redirect/clsact; if the interface has already disappeared, clean up only the owned IFB and stale owned state. Never remove filters from a replacement interface.
3. **On repeated up:** no duplicate filters or IFB creation. On a new PPP ifindex, remove obsolete trial-owned resources and apply exactly once to the replacement, with ownership verification.
4. **On partial start failure:** preserve an independent, timed rollback that can run even if the reconciliation unit fails or the control connection drops. The current phase-2 script does **not** provide sufficient automatic startup rollback.
5. **On reboot:** wait for real PPP-up event instead of sleeping a fixed duration; test separately in a planned maintenance window. Ensure service is opt-in and off by default until all safeguards pass.
6. **On operator rollback:** disable hook/reconciliation services first; remove only owned ingress and IFB resources; verify WAN route and essential services remain available.

## Risks to resolve before implementation

- The current phase-2 `start` writes ownership markers *after* creating devices or qdiscs, leaving narrow interruption windows.
- The current script's `stop` must be tested with foreign filters, partially created resources, missing `ppp0`, and replaced interfaces before it can be used on live traffic.
- `tc` classifier ownership should match more than filter priority; a foreign rule could use the same priority. Enforce exact action/target identity and avoid adopting stale state.
- Interface index can be recycled over time. Use an event-specific PPP session identifier or stronger lifecycle tracking where available, not interface index alone.
- An isolated network namespace/dummy-interface proof of repeated up/down, failed start and rollback is required before any WAN reconnect test.
- The systemd configuration has no installation target deliberately. **Do not enable or deploy the Phase 2 service yet**.

## Next evidence

Read-only inventory of PPP daemon hook directories and router service unit definition; use the result to choose the actual event source. Build mockable reconciliation and isolated tests in GitHub. Only after these pass, add a separate approval-gated deployment and rollback playbook.

## IaC gate

The persistent system must be controlled via Ansible, documented in `gpt-handover.md`, and reviewed through PR #267. No automatic cutovers.
