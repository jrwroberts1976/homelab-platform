# Router-01 download CAKE — Phase 2 staged candidate (31 October 2026)

## Scope and tested evidence

The temporary 43Mbit download CAKE on IFB `ifb-wan0` through `ppp0` ingress delivered ~41.6 Mbps and ~10ms download-loaded latency. The 10-minute timer successfully ran at 07:35:20 GMT, removing the IFB and ingress filter while preserving 13Mbit upload CAKE on `eth1`.

## Proposed managed components

- `router-qos-download-managed.sh`: candidate start/stop/check logic, with state under `/run/router-qos-download-managed`; marks its owned resources and checks PPP ifindex before teardown.
- `router-qos-download-managed.service`: one-shot service tied to PPPoE. Intentionally **no [Install] WantedBy** and not deployed or enabled in Phase 2. Service does not yet solve PPP interface recreation while the service remains active.
- Baseline upload CAKE, firewall, PPPoE, dnsmasq and Unbound are out of scope and must not be modified.

## Remaining blockers before deployment

1. Prove cleanup for partial start failures, especially when an error occurs after `clsact` but before filter creation; arrange service-level automatic cleanup.
2. Confirm ownership safety for filter identifiers, unexpected classifier output and replaced IFB devices; do not remove unrelated device state.
3. Add PPPoE reconnect hook/service lifecycle (Phase 3) and test disappearing `ppp0` plus new ifindex.
4. Add approval-gated activation, verification and rollback Ansible playbooks (Phase 4), test against dummy devices, and require an independent fallback route to the router before live changes.
5. Validate actual reboot recovery in a maintenance window. Do not enable or start this staged service until all tests and reviews pass.

## Operational rule

This phase only adds proposed files to GitHub. It must not change the router's live network. Trial evidence remains in `/var/lib/router-qos-download-trial`.
