<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 PPPoE TCP MSS persistence — 28 October 2026

**Status:** persistent MSS rules **confirmed present on Pi disk with valid nftables syntax**; temporary live workaround active. No reboot/reload has occurred in supplied evidence, so post-reboot persistence remains **unverified**. Original backup filename now verified; Ansible deployment recap not yet supplied. This document records user-supplied live evidence, not a comprehensive router migration sign-off.

## Observed problem and evidence

- The Raspberry Pi is serving LAN IPv4 gateway `192.168.3.1/24` on `eth0` and forwarding via PPPoE `ppp0`, whose observed MTU is **1492**.
- A Windows Wi-Fi client at `192.168.3.186` (gateway `192.168.3.1`) could ping BBC and reach Google HTTPS but initially timed out connecting to BBC HTTPS at `212.58.236.1` and `212.58.236.129`.
- On the Pi itself, BBC and Google HTTPS each returned 200. TCP capture confirmed LAN→PPP masquerade and returning SYN/ACK and TLS traffic, but showed incomplete receipt of some larger TCP segments. This is consistent with an MTU/PMTUD failure, but is not a controlled causal proof.
- Temporary `table ip pppoe_mss_test` forward priority `mangle` reduced IPv4 TCP SYN maximum segment size to **1452 bytes** for `eth0→ppp0` and `ppp0→eth0`. Last observed counters: **75** and **31** matching packets, respectively.
- With the temporary clamp active, both BBC destination IPs returned HTTP 200. Windows successfully fetched the complete BBC HTML body: **881.7 KiB** at **2.48 MiB/s**. Browser visual test was requested, not yet independently confirmed.
- The Pi's `nftables.service` is enabled. Startup loads `/etc/nftables.conf` with `nft -f`; stopping the service flushes the ruleset.
- User showed the actual startup configuration: `flush ruleset`, `table inet filter_router` (input and forward default DROP with LAN/PPP allowance) and `table ip nat_router` (source masquerade). It **does not** include any MSS clamping table.
- The temporary live table will disappear on service reload/reboot. The firewall draft on PR #207 has different table names (`router_filter`, `router_nat`) from the actual observed live state (`filter_router`, `nat_router`); do not copy/reload that draft.

## Proposed targeted Ansible change (NO live reload)

`IaC/ansible/playbooks/router-01-pppoe-mss-persist.yml` is intentionally limited to **on-disk persistence**:

1. Refuse to contact any host without `router_mss_persistence_approved=true` and exact `router-01 / 192.168.3.1` target.
2. Check onboard `eth0` MAC, LAN IPv4, `ppp0` MTU, active/enabled nftables, original live strict forwarding/NAT, and both already-tested temporary MSS rules.
3. Inspect `/etc/nftables.conf` and reject unexpected structure or an independently configured MSS table.
4. With Ansible `blockinfile`, back up the file and append a new `table ip router_pppoe_mss` at `priority mangle` with 1452-byte bidirectional MSS cap. Check the **whole candidate** with `nft -c -f` before atomic file replacement.
5. Recheck on-disk syntax and current temporary runtime table. **Never reload, restart, flush nftables, switch interfaces, or reboot.** Live network remains on the temporary table until separately authorised reboot.

Run from `admin-01` after fetching this feature branch and checking the actual new target is reachable from the controller:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/router-01-live-mss.yml playbooks/router-01-pppoe-mss-persist.yml --syntax-check

# Inspect only via check mode first; may need become password.
ansible-playbook -i inventory/router-01-live-mss.yml playbooks/router-01-pppoe-mss-persist.yml \
  --ask-become-pass --check --diff -e router_mss_persistence_approved=true

# ONLY following human review of diff and connectivity gates:
ansible-playbook -i inventory/router-01-live-mss.yml playbooks/router-01-pppoe-mss-persist.yml \
  --ask-become-pass --diff -e router_mss_persistence_approved=true
```

Do not run this against `docker-01` using stale `inventory/hosts.yml`. Do not infer that an older migration plan or draft PR describes live physical topology.

## Post-stage verification and maintenance gate

Before any reboot:

```bash
sudo nft -c -f /etc/nftables.conf
sudo grep -nE 'router_pppoe_mss|maxseg|ANSIBLE MANAGED' /etc/nftables.conf
sudo nft -a list table ip pppoe_mss_test
sudo systemctl is-enabled nftables
```

The persistent `router_pppoe_mss` table is **not expected in the live kernel** yet, because there is deliberately no reload. Schedule a separate guarded reboot with an offline recovery path and physical access. After reboot verify the persistent table, default-DROP WAN policy, NAT masquerade, PPPoE, DHCP/DNS, client BBC/Google HTTPS and a full-page download. Confirm that the temporary `pppoe_mss_test` table is gone.

## Rollback

- `blockinfile backup: true` creates a timestamped `/etc/nftables.conf.*` backup before changing the file. Capture the **exact** backup filename from the Ansible output.
- **Before reboot**, restore that known backup with a separately reviewed Ansible file-copy operation after `nft -c -f` validation; no live nft reload is required and the already-working temporary table stays active.
- If a future reboot causes loss of connectivity, a physical/console recovery path is required. Do not remotely run `systemctl restart nftables` or `nft flush ruleset` to troubleshoot; both can interrupt the whole household.
- Future router firewall IaC must incorporate this persistent MSS rule when consolidating/renaming the real live tables, or a later full ruleset replacement could erase it.

See router migration [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206) and unmerged [draft PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207).

## 28 Oct — On-disk verification after Ansible stage

User verified on Raspberry Pi:

```text
sudo nft -c -f /etc/nftables.conf    # exit 0, no output
27:# BEGIN ANSIBLE MANAGED: Router-01 PPPoE MSS
30:table ip router_pppoe_mss {
33: ... eth0 -> ppp0 ... set 1452
34: ... ppp0 -> eth0 ... set 1452
37:# END ANSIBLE MANAGED: Router-01 PPPoE MSS
sudo nft -a list table ip pppoe_mss_test  # present: counters 1581/306
sudo systemctl is-active nftables          # active
```

Therefore the **startup file now contains and validates** the persistent clamp, but no reload or reboot was carried out and the running kernel still uses `pppoe_mss_test`. No post-boot persistence claim is justified yet. The live Ansible deployment recap and backup filename have not been supplied; retrieve both before a separately approved, recoverable reboot.

At the next reboot, the startup file's `flush ruleset` will remove the temporary table and load `router_pppoe_mss`; verify exact tables and operational traffic as specified above. Do not restart or reload nftables as a substitute for controlled boot verification, and do not conflate host DHCP renumbering after the ASUS reset with the Pi's verified `192.168.3.1`.

## 28 October — Original-versus-persistent firewall diff verified

User ran `sudo diff -u '/etc/nftables.conf.2112.2026-10-28@13:09:59~' /etc/nftables.conf` on the live Pi. **The complete unified diff shows one appended block only** (11 lines, from original line 24 through appended lines 27–37), containing `table ip router_pppoe_mss` and the two bidirectional SYN MSS 1452 rules. No pre-existing `filter_router` or `nat_router` lines were modified or removed.

- Current file: `/etc/nftables.conf`, 1305 bytes; timestamp 28 October 2026 13:09.
- Original automatic Ansible backup: `/etc/nftables.conf.2112.2026-10-28@13:09:59~`, 765 bytes, original timestamp 27 October 2026 18:22.
- Disk `nft -c -f` validation already passed and temporary live MSS table remains active. The original deployment `PLAY RECAP` has not been provided.
- The disk configuration is **ready for controlled boot validation**, but no reboot is authorised or reported. Before planning the reboot, read-only check `is-enabled` and `is-active` for `nftables`, `router-pppoe`, `kea-dhcp4-server` and `unbound`, IPv4 forwarding and any outstanding router rollback timer. Have physical recovery available. Do not reload/restart nftables as a test.
