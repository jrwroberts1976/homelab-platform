# Parallel IFB cutover — design gate (not executable)

Status: DESIGN ONLY. No production activation approved.

## Reason for changing approach

The current production IFB `ifbqosdl0` is unmarked and working with
43Mbit CAKE; the ppp0 ingress matchall pref 49132 points to it. The current
recovery actor can only create an IFB when **none** exists and ingress is
clean. That does not protect a destructive cutover. Never treat the
unmarked legacy IFB as owned.

Prefer a **parallel candidate IFB**, keeping the original kernel IFB alive
throughout activation and rollback. A separate name (proposed
`ifbqosdl1`) is required; controller and ownership helper code currently
hardcode `ifbqosdl0` and **must be changed and regression-tested**.

## Mandatory transaction model

1. Read the complete tc topology and live ifindex/alias/boot ID. Refuse any
   foreign filter or unrecognised IFB consumer. Hold the shared QoS flock.
2. Install a *newly created* candidate IFB with independently recorded
   kernel alias token and 43Mbit CAKE. Do not change the live ppp0 redirect.
   Verify the candidate does not capture traffic before switching.
3. Prepare a durable transaction record and independent rollback supervisor.
   Record the exact legacy redirect and IFB identity. Its cancellation
   mechanism must be explicit, atomic and tested.
4. Modify only the expected ppp0 ingress filter in one guarded transaction,
   redirecting to the candidate. Keep the legacy IFB intact.
5. Verify counters, routing, DNS, upload CAKE, download CAKE and connectivity
   during the rollback window. On expiry or failure, restore the exact
   original redirect to still-existing legacy `ifbqosdl0`, leaving any
   ambiguous candidate IFB alone for separate inspection.
6. Only confirm after reconnect and reboot persistence tests (these may
   require a distinct follow-up phase if the fallback cannot span reboot).
   Retirement of legacy IFB must be a *separate* operator-approved step,
   never an implicit part of the cutover.

## Explicit limitations and current blockers

- The existing timer restores controller and hook *files only*. It cannot
  switch a kernel redirect back. It is **not** sufficient for step 3.
- This document does not authorise deleting/replacing ppp0 clsact, an IFB,
  or the current pref 49132 filter. Exact kernel ownership and filter
  identity remain prerequisites.
- A PPP reconnect may recreate ppp0 and lose ingress state. The rollback
  supervisor must account for that, not just assume a stable interface.
- Existing controller `owned()` and stamp/observer modules assume
  `ifbqosdl0`, so no current candidate script can be used for parallel
  mode without code changes.
- The current create-only recovery actor can leave a partial IFB and
  progress journal after interruption. It is not a rollback supervisor.
- Production remains on legacy IFB until a fully tested transaction is
  implemented; no blind cutover, no forced reboot.

## Acceptance evidence required

- Isolated network-namespace integration tests for both original and
  candidate IFBs, success and partial failures.
- Rollback supervisor independently verified against process interruption
  and timeout. Refuses any unexpected filter/handle changes.
- Locked cutover, token-bound candidate identity, recorded legacy baseline,
  restored redirect and connectivity verified on failure.
- Reconnect and reboot persistence proven live under scheduled supervision.
- Updates to CURRENT-STATE.md and gpt-handover.md; then merge reviewed PR.
