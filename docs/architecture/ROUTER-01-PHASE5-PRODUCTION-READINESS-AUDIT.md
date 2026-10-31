# Router-01 Phase 5 download QoS — production-readiness integration audit

Date: 2026-10-31  
Branch: `feature/router-download-qos-preflight-20261031`  
Scope: repository source inspection only; no system changes.

## Decision: NO-GO for production activation

The prototype has useful isolated tests and conservative refusal paths, but is not a single validated lifecycle for PPP up/down, install, recover and watchdog actions.

| Requirement | Evidence reviewed | Finding | Gate |
| --- | --- | --- | --- |
| Common exclusive ownership lock | `router-qos-download-durable-journal.py`, `router-qos-download-locked-kernel-audit.py`, `router-qos-download-ppp-event-replay.py`, `router-qos-download-isolated-executor.py` | Journal calls use flock; event planner is in-memory; test-only executor has no journal lock. No common real PPP handler/installer/watchdog lock demonstrated. | FAIL |
| Authentic recovery authorisation | `router-qos-download-durable-journal.py` | `finish(... externally_verified=True)` and `recover_clean(... externally_verified=True)` accept a caller assertion. Even correctly locked calls may clear pending intents without observing real kernel state. | FAIL |
| Fresh kernel observation and ownership | `router-qos-download-sensor-readonly-collector.py`, `router-qos-download-observation-adapter.py`, `router-qos-download-locked-kernel-audit.py` | Collector is restricted to disposable `sensor-01/qos-proof31`; missing namespace is INCONCLUSIVE. Its observations are not authoritative for production `router-01/ppp0`. The journal flock does not prevent uncoordinated external kernel/PPP changes. | FAIL |
| Evidence soundness | `router-qos-download-cleanup-evidence.py` | Absence checks depend on exact command return values and substring `does not exist`; namespace identity uses filesystem stat inode from a test owner file; no independent source session binding. Must validate kernel namespace identity, command outputs and errors against real environments and fail closed. | INCOMPLETE |
| Crash/restart reconciliation | `router-qos-download-durable-journal.py`, offline process tests | Durable pending intent and inter-process flock are tested. No demonstrated crash-safe service startup reconciliation, coordinated watchdog, or production rollback. | FAIL |
| Safe deployment/rollback | `router-01-qos-download-sensor-python-watchdog-proof.yml`, isolated executor | Playbook is intentionally retired and now read-only. Executor is explicitly test-only and isolated; no production rollout or rollback gate. | FAIL |

## Test evidence reported by operator

- Three multi-process journal tests passed.
- Nine durable journal tests passed.
- Seven cleanup-evidence tests passed.
- Three collector tests passed.
- Seven collector/evaluator adapter tests passed.
- Seven freshness audit tests passed.
- Seven locked-kernel audit tests passed.
- Read-only sensor audit showed host `sensor-01`, LAN `192.168.2.55/24`, default gateway `192.168.2.1`, no disposable namespace or owner path, and inactive test watchdog units.

These results validate individual offline conditions, **not production readiness**.

## Required next work, in order

1. **Eliminate caller-asserted completion:** design a capability restricted to a trusted verification path; no journal mutation based on a boolean. Preserve existing test-only API until a reviewed migration avoids silently changing semantics.
2. **Define one transaction boundary:** PPP event acceptance, durable pending write, watchdog arm, kernel operation, postcondition observation and commit must be coordinated. Specify ordering and rollback for failure after each stage.
3. **Establish authoritative ownership:** immutable session identifiers and actual PPP device identity; separate sandbox `qos-proof31` fixtures from production. Hold a stable lock across state + observation + authorised transition; address actors outside the lock.
4. **Crash/restart and watchdog design:** fail-closed boot recovery, orphaned qdisc/filter detection, no deletion of foreign resources, time-bounded rollback, and independently validated activation preflight.
5. **Evidence-first testing:** offline model/test matrix; namespace tests only after new approval and safe out-of-band access. No SIGKILL or production cutovers by default.

## Explicit prohibitions until gates pass

- Do not enable persistent 43 Mbps download CAKE on router-01.
- Do not change working 13 Mbps upload CAKE, PPPoE, nftables, DNS, or LAN.
- Do not run retired disruptive SIGKILL/watchdog proof.
- Do not turn a CLEAN fixture result into journal recovery authorisation.
- No blind Ansible deployment; update `gpt-handover.md` for each change.
