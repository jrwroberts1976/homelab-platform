<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 PPPoE MSS — post-cutover verification

## Proven historical fix and current topology

On 28 October 2026, before the later DHCP/LAN migration, the Pi's PPPoE `ppp0` MTU was 1492; a temporary bidirectional TCP MSS clamp to **1452 bytes** restored previously failing BBC HTTPS requests from a Windows client. The operator then installed the persistent `table ip router_pppoe_mss` in `/etc/nftables.conf` via an approval-gated Ansible blockinfile and rebooted. Post-reboot observation showed both live MSS rules with **288 LAN-to-WAN / 22 WAN-to-LAN matches**, active `nftables`, PPPoE, dnsmasq and Unbound, default route `ppp0` and forwarding on. The pre-reboot original backup was `/etc/nftables.conf.2112.2026-10-28@13:09:59~`. The original deployment playbook recap and explicit absence of temporary `pppoe_mss_test` were not separately verified.

**Important subsequent change:** The user later migrated the *primary* Pi LAN address from `192.168.3.1` to **`192.168.2.1/24`** and dnsmasq DHCP range to `192.168.2.100–199`; ASUS ceased serving as the primary router. The user verified successful internet access after this migration, and the read-only post-cutover router baseline succeeded at 22:09:06 UTC. These facts **do not independently prove** that the old `192.168.3.0/24` firewall/NAT source range in draft PR #208 was reconciled on disk. Do not use the old `IaC/ansible/inventory/router-01-live-mss.yml` and old `router-01-pppoe-mss-persist.yml` on the new primary LAN without separate review.

## This main-compatible integration: read-only audit, not the old writer

The source-only scope of the safe integration is:
- `IaC/ansible/playbooks/router-01-mss-postcutover-readonly.yml` — **only** Ansible command, slurp, assert and debug tasks, no shell, files, systemd changes or nftables reload. Explicitly requires `admin-01`, `--check`, `router_mss_postcutover_audit_approved=true`, verified onboard MAC, `eth0 192.168.2.1/24`, `ppp0` default route with MTU 1492 and `net.ipv4.ip_forward=1`. Checks core services before and after.
- Reuses the **already merged** `IaC/ansible/inventory/router-01-postcutover-baseline.yml` from PR #211; this avoids the stale `.3.1` inventory.
- Reads live `filter_router`, `nat_router`, `router_pppoe_mss`, confirms default-drop policy, masquerading and two MSS 1452 rules. Reads existing on-disk `/etc/nftables.conf` and runs `nft -c -f` **without applying it**; verifies Ansible MSS block markers, table and rule count. Reports whether the old `pppoe_mss_test` table still exists, and separately reports presence of new `192.168.2.0/24` range in live and disk NAT (not assumed).
- A dedicated GitHub Action checks YAML task types and Ansible `--syntax-check`. This is source validation **not** a claim that the playbook has yet been executed on the Pi.

### Safe next operation from admin-01 after merge

```bash
cd ~/projects/homelab-platform
git switch main
git pull --ff-only origin main
cd IaC/ansible
ansible-playbook -i inventory/router-01-postcutover-baseline.yml \
  playbooks/router-01-mss-postcutover-readonly.yml --limit router-01 --syntax-check
ansible-playbook -i inventory/router-01-postcutover-baseline.yml \
  playbooks/router-01-mss-postcutover-readonly.yml --limit router-01 \
  --ask-become-pass --check -e router_mss_postcutover_audit_approved=true
```

Do not run a historical PR #208 writer playbook against the new gateway. No firewall edit, nftables restart, SSH reload or reboot is authorised by this audit. If the live table, persistent file or updated NAT range differs, **stop and inspect**, then design a separate guarded IaC reconciliation and rollback before changing any state.

## Remaining merge gate

Original **draft PR #208 stays open** because its persistence-writer guard and firewall/NAT assertions are still pinned to `192.168.3.1` / `192.168.3.0/24`; direct merge would misrepresent current deployed state. The standalone audit can be merged only after its own source/CI validation passes. Its later on-host results will determine whether the persistence writer can be reconciled and selectively merged safely.

See also `docs/network/ROUTER-01-BASELINE-2026-10-28.md`, issue #206 and issue #209.
