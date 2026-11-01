# Router-01 download QoS: legacy IFB cutover gate (2026-11-01)

Status: **NOT APPROVED FOR EXECUTION**. Draft PR #271 has been staged and
hash-verified only. This document describes the next engineering gate; it is
not an instruction to manually run tc/ip commands on the live router.

## Verified production baseline
- LAN eth0: 192.168.2.1/24, WAN ppp0 online.
- Upload root CAKE on eth1: 13Mbit, PTM overhead 30, reboot-tested.
- Download root CAKE on ifbqosdl0: 43Mbit. Legacy IFB ifindex 24,
  without kernel ownership alias or ownership record.
- ppp0 ingress has pref 49132 mirred redirect to ifbqosdl0.
- Active controller SHA256:
  16f7db14bf5962360e7c684e374c7d676240f78ea1351effc66472031f0486a7.
- Active PPP hook SHA256:
  25b96d3504f226a789cc959772a995e51e2867ecc797c3e218c3b6d89b75df8b.
- All six candidate files staged and SHA256-matched in
  /usr/local/libexec/router-qos-download-candidate/.
- Read-only audit: 8 tasks OK, 0 changes, 0 failures.

## Must fix before any live replacement
1. Preserve the existing live controller and PPP hook in a root-only,
   checked rollback location. Do not replace live entrypoints until the
   rollback path is verified from an independent SSH session.
2. The new controller currently requires newly-created IFB stamping and
   must refuse to adopt ifbqosdl0 based only on name/rate. Legacy cutover
   needs a dedicated approval-gated transaction with an automatic rollback
   watchdog, not a direct run of the existing activation playbook.
3. Protect against PPP reconnection and installer races. Verify exclusive
   lock ownership, no unexpected IFB users, and all ingress filters/handles
   before and after each mutation. No blind IFB deletion.
4. Fix the production controller's explicit remove path: it currently
   identifies a 'complete live fingerprint' without validating the recorded
   kernel ownership token. Disable this operation for unmarked live IFBs.
5. Add real-kernel integration tests for stamp CLI and record-release path,
   not only mocked shell tests. Exercise failures after the record write,
   after clsact installation, and interrupted reconnection.
6. Ensure staged candidate helper imports and Ansible executable paths
   agree; preserve owner records across retries, and validate restoration.
7. Define watchdog behaviour: when verification fails, restore the prior
   controller and hook, undo only this transaction's changes, and verify
   LAN/PPPoE/DNS connectivity. Avoid relying on SSH alone for recovery.

## Approved cutover acceptance criteria (future)
- Explicit operator approval and maintenance window.
- Proven emergency access to router-01 and timed rollback.
- One managed IFB with verified kernel token and private owner record.
- Upload CAKE unchanged (13Mbit with PTM overhead 30).
- Download CAKE 43Mbit, only expected ingress redirect, no foreign filters.
- PPPoE reconnection verified live, then separately reboot persistence tested.
- Normal routing, DNS, firewall, DHCP, monitoring and SSH all healthy.
- Update gpt-handover.md and CURRENT-STATE.md on verified success.
- Review/merge PR #271 and clean up only branches proven merged or
  safely superseded; never bulk-merge experimental PR #267.

Until these gates pass, keep the live legacy QoS setup unchanged.
