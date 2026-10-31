# Router-01 download QoS — Phase 5 production readiness review

Status: DESIGN REVIEW ONLY. No router-01 changes approved or made.

## Verified baseline
- Existing upload CAKE: 13 Mbit on physical WAN eth1; must remain unchanged.
- Temporary 43 Mbit download trial previously measured approximately 10 ms loaded latency and was rolled back.
- Independent watchdog rollback of real IFB/CAKE on an isolated sensor-01 namespace passed (17 OK, 6 changed, 0 failed).
- Production download persistence is OFF.

## Reviewed source
`IaC/ansible/files/router-qos-download-managed.sh` (Phase 2 candidate, NOT approved for live deployment).

## Blocking gaps
1. **Reconnection ownership and lifecycle**: `start` refuses any managed state or existing IFB; `stop` guards current PPP ifindex but leaves recovery/state handling dependent on orderly invocation. Design a deterministic reconcile routine for PPP disappearance/recreation, stale IFB, and concurrent reconnect events, with strict refusal to remove foreign resources.
2. **Reboot persistence**: `/run/router-qos-download-managed` is volatile. Never assume it preserves ownership through boot. Design boot-safe discovery/adoption versus teardown based on verified interface identity and owned filter handles. Avoid deleting unmatched resources.
3. **Partial-install recovery**: Ownership markers are created after network modifications; a crash in between leaves unmarked objects. Use pre-declared intent, atomic state updates, verified fingerprints/handles and independent rollback, with idempotent recovery at every failure boundary.
4. **Production watchdog and ordering**: Isolated sensor proof is not a router PPP lifecycle proof. Ensure rollback independent of installer, lock coordination, bounded timeout, script retention until callbacks finish, and `systemd`/PPPoE event ordering.
5. **Observability, rollback and safety**: Preserve router SSH, PPPoE, dnsmasq, Unbound, nftables and upload CAKE. Snapshot `tc -s`, routes, PPP ifindex, latency, and service state before/after. Approval gate, timed rollback and explicit verification required for any live trial.

## Proposed controlled sequence
1. Capture router-01 baseline **read only** using existing Ansible inventory.
2. Implement offline namespace fixtures for PPP up/down/new-ifindex, partial failures, racing events, stale IFB and timer rollback.
3. Review and syntax/check-mode validate new Ansible/IaC changes without deployment.
4. Perform separately approved timed router trial with automatic revert and connectivity checks.
5. Only after repeated PASS: propose persistent service/event hooks with explicit approval and a documented rollback.

Never cut over or modify production router automatically from this review.
