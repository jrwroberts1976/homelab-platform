# edge-01 native nftables ICMP timestamp pilot — 19 October 2026

**State: design gate only. No cutover or rollback playbooks approved or deployed.** Continue at 6/14 operational mitigations.

## Verified evidence

- edge-01 is Debian 13, unprivileged LXC CT103 on Proxmox-2, 192.168.2.56/24 on vmbr0; running.
- Guest has CAP_NET_ADMIN; native nftables service is enabled/active, with inet filter input/forward/output base chains all policy accept, no live rules.
- /etc/nftables.conf is a 243-byte stock config with `flush ruleset`; systemd nftables ExecStart and ExecReload run `nft -f /etc/nftables.conf`; ExecStop flushes ruleset.
- No detected UFW, firewalld or netfilter-persistent service, nft-related timer, unit override, or separate nftables.d configuration; no /etc/pve/firewall/103.fw guest file.
- From greenbone-01: ICMP echo passes, three timestamp requests yield three matching replies; Ansible baseline ok=4 changed=0 failed=0.
- `nft -c add rule inet filter input ip protocol icmp icmp type timestamp-request drop` returned rc=0 from edge-01; syntax only, no live modification.
- Existing media_firewall role manages a different full nftables ruleset on media-01 and must not be reused on edge-01.

## Required implementation constraints

1. Scope to edge-01 only for pilot; verify Ansible inventory address, LXC identity, expected nft family/table/chain and empty baseline INPUT and no unexpected changes. Stop on mismatch.
2. Preserve existing nftables rules, tables, chains and default policies. **Do not run `nft flush ruleset`, reload or restart `nftables.service` during cutover.**
3. A live-only added rule is NOT persistent: an nftables reload/restart wipes it. Prefer safely managing an exact dedicated commented type-13 rule within the existing INPUT block of the authoritative `/etc/nftables.conf`, with strict structural preconditions, atomic backup and `nft -c -f` validation before making any active change. Apply only the one rule to live INPUT; never load the whole config as part of the cutover.
4. On subsequent nftables restart/reload, the configuration must reproduce the rule. Do not assume a separate oneshot service alone guarantees re-application after reload.
5. Exact rollback must remove only the labelled pilot live rule by its current handle and reverse only the pilot's single config insertion. Fail closed if multiple matches, another rule changed, or the baseline no longer matches. Retain backup and explicit out-of-band recovery procedure.
6. Verify SSH/port 22, ordinary ICMP echo and scanner-side matching replies BEFORE; after cutover require ordinary echo still PASS and 0 matching replies from greenbone-01. Verify the unrelated nft chains and current policies remain unchanged. Re-run for idempotency (changed=0).
7. Test syntax, rendering, offline source invariants and rollback logic on admin-01 before any live deployment. Reboot persistence proof requires a separately approved maintenance event. Do not modify Proxmox-2 or the other LXC guests in this pilot.
8. Preserve the accepted-risk entry until a new completed authenticated Greenbone scan and evidence reconciliation, not merely a 3-packet probe.

## Next implementation action

Author narrowly scoped Git-managed Ansible cutover and rollback with a dedicated offline validator. Pull them to admin-01, run YAML/Ansible syntax + offline guard, and review outputs before explicitly authorising `--limit edge-01`. Do not deploy from this design document.
