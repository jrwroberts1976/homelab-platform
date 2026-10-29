<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 DHCP static-address protection: draft only — 28 October 2026

## Live preflight VERIFIED — 29 October 2026 (no changes)

After merged [PR #214](https://github.com/jrwroberts1976/homelab-platform/pull/214), the operator on `admin-01` fast-forwarded clean `main` to `43c69dbf` and ran syntax-check **PASS** followed by the approval-gated, **read-only** `router-01-dhcp-exclusion-preflight-readonly.yml` against the isolated `192.168.2.1` inventory with `--check -e router_dhcp_exclusion_preflight_approved=true`. Actual final Ansible recap: **`router-01 ok=20 changed=0 unreachable=0 failed=0 skipped=0`**.

All assertions passed: exact controller and Pi MAC, live `eth0 192.168.2.1/24`, active dnsmasq before/after, expected running configuration directory and only `README` plus `router.conf` in `/etc/dnsmasq.d`, exact single dynamic `.100–.199` range, gateway and DNS `.2.1`, no unreviewed per-host/other DHCP allocation directives, and `dnsmasq --test` syntax OK. **The currently configured DHCP pool was NOT changed.**

The lease file held **21 records** at this observation, versus **18** at the preceding observation; the three additional IPs and their expiry/status were **not output**. The proposed protected addresses `192.168.2.181` and `192.168.2.195` had no lease-file rows at the time, and `192.168.2.198` remained listed. The candidate three ranges, retaining 98 IPs total, were printed only as a proposal. Absence of a lease row does not prove the address unused or establish static addressing. **ASUS AiMesh actual address and static-vs-DHCP setting remain unverified, and `media-01` is offline; no deployment is approved.**

**Next decision gate:** reconcile the 21 lease IP records without MAC/hostname disclosure; independently confirm `.181` and `.195` ownership and whether they use manual IPs or DHCP. Use split-pool exclusions only for genuine static assignments; otherwise plan verified MAC-based reservations. Any implementation requires an independent reviewed IaC change, targeted candidate-config syntax check, backups, safe activation and rollback. Do not restart dnsmasq from this documentation update.


## Observed live facts

This is the **observed** Raspberry Pi 4 at `192.168.2.1/24` on `eth0`, physically pinned by onboard MAC `d8:3a:dd:5a:51:44`, currently serving internet through PPPoE. The earlier read-only gateway baseline and MSS audit both passed without changing the router (merged PRs #211, #212 and #213).

Operator-executed Ansible ad-hoc inspection (Ansible `CHANGED` here is a reporting default for shell, not a host modification) found:

- `dnsmasq.service` active, Debian vendor unit `/usr/lib/systemd/system/dnsmasq.service`; no systemd drop-ins; `/usr/share/dnsmasq/systemd-helper exec` as startup helper.
- Live daemon arguments include `-7 /etc/dnsmasq.d,.dpkg-dist,.dpkg-old,.dpkg-new`. Directory contains `router.conf` and `README`.
- DHCP configuration directives verified directly in `/etc/dnsmasq.d/router.conf`:
  ```ini
  interface=eth0
  bind-dynamic
  dhcp-authoritative
  dhcp-range=192.168.2.100,192.168.2.199,255.255.255.0,24h
  dhcp-option=option:router,192.168.2.1
  dhcp-option=option:dns-server,192.168.2.1
  ```
- No DHCP allocations, reservations or DHCP include directives were visible in the grep output for `/etc/dnsmasq.conf`; full file and ancillary sources have not yet been reproduced line-for-line in the conversation. `dnsmasq --test` returned **syntax check OK**.
- `/var/lib/misc/dnsmasq.leases` had 18 records, **15 in the live `.2.100-.2.199` range**: `.100, .109, .112, .125, .153, .164, .168, .171, .174, .179, .180, .186, .189, .190, .198`. All 15 were unexpired at the point of inspection. Three additional historical records `192.168.3.113`, `.142`, `.187` were still unexpired at the time, each due to expire on 29 October 2026, but this does NOT prove those clients remain on the old LAN.
- There was **no lease row** for `192.168.2.181` or `192.168.2.195`, and `ip neigh` returned no entries for either. Neither absence establishes that an address is free or excluded.
- Canonical `IaC/inventory/estate.json` last validated 17 September, before the cutover, historically lists `asus-aimesh-181` at `192.168.2.181` and `media-01` at `192.168.2.195`. `media-01` is **currently powered off** according to operator; ASUS AiMesh node's current management address and actual static/DHCP mode remain unverified.

### Risk statement

The Pi's active DHCP allocator is configured with one broad dynamic scope of `192.168.2.100–199`, which includes two *historically documented* host addresses. This creates a **possible future allocation collision**, not evidence of a duplicate address right now. A DHCP lease record or an empty neighbour cache cannot prove that host addressing is static. No DHCP exclusion has yet been applied.

## Proposed *conditional* IaC split (not deployed)

If the operator verifies both addresses are still intended as statically configured infrastructure, the following three same-subnet dynamic ranges would exclude precisely the two candidate addresses while preserving the other 98 available IPs:

```ini
dhcp-range=192.168.2.100,192.168.2.180,255.255.255.0,24h
dhcp-range=192.168.2.182,192.168.2.194,255.255.255.0,24h
dhcp-range=192.168.2.196,192.168.2.199,255.255.255.0,24h
```

All 15 recorded current-subnet lease IPs remain inside a proposed range, including `.198`. DNS, gateway and lease duration would remain unchanged. The candidate retains 81 + 13 + 4 = **98** addresses and excludes exactly `.181` and `.195`. Debian's current dnsmasq manpage explicitly permits multiple `dhcp-range` directives in one subnet: https://manpages.debian.org/trixie/dnsmasq-base/dnsmasq.8.en.html

**Do not deploy merely because the address ranges have valid syntax.** If the AiMesh node actually uses `.181` via DHCP rather than statically (or has renumbered), removal from the pool could break its next renewal. If media-01 is configured via DHCP rather than statically, removing `.195` may have similar effects after power-on. Keep it offline until its configuration and the correct exclusion policy are verified. Explicit MAC-based reservations could be preferable if both clients are DHCP-managed; do not fabricate MACs. A separate static-IP allocation segment for the estate may be appropriate in a broader network reconciliation, but must be designed against existing leases and rollback.

## Source-only preflight, current branch

`IaC/ansible/playbooks/router-01-dhcp-exclusion-preflight-readonly.yml` **only reads**: exact Pi identity, current LAN IP, dnsmasq systemd status and process arguments, directory file set, current main and router config, current lease *IP addresses*, and current `dnsmasq --test` status. It refuses unexpected DHCP/reservation directives, changed input range, extra fragments and any lease at the two proposed exclusions. It shows candidate ranges for human review. Requires `admin-01`, isolated `router-01-postcutover-baseline.yml`, Ansible `--check` and explicit `-e router_dhcp_exclusion_preflight_approved=true`. Its check-mode commands are explicitly non-mutating and mark `changed_when: false`. No file writes, DHCP reload/restart, lease deletion, IP reassignment or DNS change is included.

An offline GitHub workflow verifies the playbook task allowlist and syntax, exactly two excluded IPs, same netmask and 24h lease time, no overlap/missing addresses, and retention of all 15 previously recorded lease addresses. CI does **not** prove live device ownership or actual DHCP behaviour.

### Proposed safe operator command, only after the PR has been reviewed and fetched

```bash
cd ~/projects/homelab-platform
git switch main
git pull --ff-only origin main
cd IaC/ansible
ansible-playbook -i inventory/router-01-postcutover-baseline.yml \
  playbooks/router-01-dhcp-exclusion-preflight-readonly.yml \
  --limit router-01 --syntax-check
ansible-playbook -i inventory/router-01-postcutover-baseline.yml \
  playbooks/router-01-dhcp-exclusion-preflight-readonly.yml \
  --limit router-01 --ask-become-pass --check \
  -e router_dhcp_exclusion_preflight_approved=true
```

If the PR has **not** been merged, do not run those commands on `main`; use a specifically reviewed checkout with the same isolated inventory. **This source-only stage is not a request to run or deploy yet.**

## Deployment and rollback gates — future separate PR

1. Verify the ASUS AiMesh node's current management IP, physical identity and static-versus-DHCP setting. Verify media-01's **stored** static/DHCP configuration when independently available without unnecessarily powering it up. Determine whether exclusions or explicit DHCP reservations are appropriate.
2. Recheck lease-file state immediately before any change; fail closed if `.181` or `.195` is now leased, if the dynamic scope changed, or if the full effective dnsmasq configuration contains unreviewed overrides. Preserve a bounded backup of the exact original `router.conf` and non-secret verification artifacts.
3. Prepare an Ansible writer which *only* replaces the one original `dhcp-range` directive, preserves all other contents, independently checks the **entire effective candidate config** with the **installed** dnsmasq version, and refuses unsanctioned execution. Provide a reviewed rollback that restores only that known original file and validates it. Never `git clean` or overwrite unrelated files.
4. Set an explicit maintenance/rollback window and decide on the minimal DNS/DHCP activation mechanism **after separately testing its behaviour**. Do not restart dnsmasq as part of a source merge or preflight. Validate healthy DNS/DHCP service, existing client internet reachability and lease renewals; prepare emergency access if Pi routing changes unexpectedly.
5. Update authoritative `IaC/inventory/estate.json`, `CURRENT-STATE.md` and `gpt-handover.md` to match verified live roles and final deployed settings, explicitly documenting any historical ASUS IP entries superseded by the cutover.

## Decision

**Source-only stage. No live change approved or performed.** The operator will review the safety-gated preflight and verify host address ownership before any guarded writer/deployment is considered. Historical PRs #207, #208 and #210 remain separate and should not be used as a source for replacing current dnsmasq or nftables live configurations.
