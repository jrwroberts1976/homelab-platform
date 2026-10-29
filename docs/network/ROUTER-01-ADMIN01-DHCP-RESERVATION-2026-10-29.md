<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01: recover stable admin-01 DHCP address — 29 October 2026

## 29 October 2026 12:55 UTC — FINAL RECOVERY VERIFIED: 3/3 Proxmox votes, QDevice connected on both nodes

**Independently operator-verified after the admin-01 reboot:** Both `PROXMOX` and `Proxmox-2` reported via read-only `pvecm status` that cluster `jameshouse-pve` is **`Quorate: Yes`**, with **Expected votes: 3**, **Total votes: 3**, **Quorum: 2** and `Flags: Quorate Qdevice`. Membership identifies `PROXMOX 10.255.255.1` (1 vote, `A,V,NMW`), `Proxmox-2 10.255.255.2` (1 vote, `A,V,NMW`) and **`Qdevice` (1 vote)**. Read-only `corosync-qdevice-tool -s` on *both* nodes returned **`QNetd host: 192.168.2.48:5403`** and **`State: Connected`**, configuration version 3, model Net, Fifty-Fifty split algorithm. Thus the witness is actually contributing its vote, not just accepting TCP connections.

Host-side recovery independently verified immediately beforehand: Windows SSH to `james@192.168.2.48` succeeded; `admin-01 eth0 UP 192.168.2.48/24`; `sudo corosync-qnetd-tool -s` showed **Connected clients: 2** and **Connected clusters: 1**. Router-01's approved, independently verified Ansible `dnsmasq` reservation is `dhcp-host=b8:27:eb:e8:36:cd,192.168.2.48`, preserving the original ASUS `.180` entry and dynamic `.100-.199` range. The historical `.127` lease, disconnected client states, and 2/3 votes documented below are **incident history, not current operational status**.

**Operational status: admin-01 DHCP recovery and Proxmox witness restoration COMPLETE.** No Proxmox cluster configuration changes or additional network restarts required. Canonical Ansible inventory was already correct at `.48`; preserve it. Issue [#206](https://github.com/jrwroberts1976/homelab-platform/issues/206) records the full operator evidence; this does not imply unrelated router migration work is complete.


## Recovery interim evidence — .48 host and QNetd clients before final vote verification

**New live operator evidence supersedes the historical .127 / zero-client snapshots below.** From Windows 192.168.2.186, SSH to james@192.168.2.48 succeeded and identified host admin-01. After the reboot, a direct `ip -4 -br addr show eth0` reported **eth0 UP 192.168.2.48/24**. On admin-01, `sudo corosync-qnetd-tool -s` reported **Connected clients: 2** and **Connected clusters: 1**, QNetd listening at `*:5403` with TLS supported. The original management IP was recovered by restarting admin-01 after the independently verified router DHCP reservation for its MAC `b8:27:eb:e8:36:cd` at `.48` was installed.

**Final verification still outstanding:** independent post-recovery `pvecm status` and `corosync-qdevice-tool -s` on both Proxmox nodes before claiming the extra vote is counted. Two clients connected to the QNetd server do not independently prove both nodes count a QDevice vote. No Proxmox/Corosync config changes or additional firewall changes are required by this observed evidence. Ansible inventory already uses the intended `.48` address; keep it unchanged. Router dynamic pool `.100-.199` and existing ASUS `.180` reservation were independently verified intact. See [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206).


## Historical pre-recovery snapshot — Proxmox QDevice outage diagnosed

**Read-only definitive operator evidence** after physical router admin DHCP reservation installation and independent postflight PASS: on both Proxmox nodes, `corosync-qdevice-tool -s` reports **`QNetd host: 192.168.2.48:5403`**. `PROXMOX` shows `State: Connect failed`; `Proxmox-2` shows `State: Connecting`. The shared `/etc/pve/corosync.conf` has QDevice model `net`, algorithm `ffsplit`, `host: 192.168.2.48`, `tls: on`, `votes: 1`, config version `3`. Both Proxmox nodes' `corosync-qdevice.service` are running but show repeated connection timeouts, and `admin-01`'s `corosync-qnetd-tool -s` showed zero connected clients/clusters. The 2-node cluster `jameshouse-pve` is presently quorate with **2 votes out of 3 expected** (witness vote absent), so failure of either Proxmox host could cause quorum loss.

**Confirmed causal network mismatch:** `admin-01` is independently observed at DHCP **`192.168.2.127/24`**, so it does not currently own `.48` as QDevice clients require. Router `router-01` now has independently verified `dhcp-host=b8:27:eb:e8:36:cd,192.168.2.48` with dnsmasq active and syntax PASS; admin-01 has **not** renewed the old `.127` lease. This explains the failed connection to the configured endpoint; do not claim certificates/firewall or additional issues before re-checking after host reconnection.

**Next change not yet approved:** restore `admin-01` original IPv4 through a planned console-backed NetworkManager DHCP disconnect/reconnect of `netplan-eth0`; avoid running `nmcli connection down` over remote SSH. Preserve QDevice configuration on Proxmox and router DHCP configuration. Check the console and sudo access before interruption. Afterwards prove `admin-01 eth0 .48/24`, gateway/router reachability, Windows SSH `.48`, `corosync-qnetd-tool -s` restored client connections, both PVE `corosync-qdevice-tool -s` connected, and cluster quorum/witness vote. Only then update stale inventory/docs/DNS monitoring facts. This requires fresh explicit user approval, separately from prior router dnsmasq change. Tracked in [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206).


## Independently verified router-side postflight — PASS (29 October 2026)

Following the approved live Ansible writer PASS (router-01 ok=33 changed=8 unreachable=0 failed=0), the operator checked the actual physical router directly using **only read-only commands**. Evidence:
- `systemctl is-active dnsmasq` = **active**.
- Live `/etc/dnsmasq.d/router.conf`: line 5 `dhcp-range=192.168.2.100,192.168.2.199,255.255.255.0,24h`; line 9 existing `dhcp-host=24:4b:fe:5e:cc:c8,192.168.2.180`; lines 11–13 exactly one Ansible managed `admin-01` reservation with `dhcp-host=b8:27:eb:e8:36:cd,192.168.2.48`.
- `sudo dnsmasq --test` = **dnsmasq: syntax check OK**.
- Lease file still shows `b8:27:eb:e8:36:cd` at **`192.168.2.127`**, hostname `admin-01`, client ID `01:b8:27:eb:e8:36:cd`.
- `systemctl is-active unbound router-pppoe nftables` = **active** for each service.

**Interpretation:** The router configuration and essential services are now independently confirmed as intended. **No DHCP renewal or host-side address migration has occurred in the observed evidence**. The next independent stage is a controlled, separately authorised NetworkManager DHCP renewal on physical `admin-01`, with keyboard/monitor or other recovery access and a check on its Proxmox Corosync QNetd witness responsibilities. An SSH session may disconnect during the renewal. Do **not** restart/renew the admin interface from remote SSH alone, alter inventory/DNS prematurely, or assert `.48` is already live on admin-01. See router migration [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206).


## Current state: approved router-side deployment PASS; separate inspection pending

After live read-only preflight (ok=17 changed=0 failed=0), the user expressly approved the narrowly scoped router reservation writer plus dnsmasq restart and the residual .48 static-IP conflict risk. The operator ran the versioned Ansible writer from admin-01; its pasted tail shows candidate cleanup and final router-01 recap: **ok=33 changed=8 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0**. Eight changed tasks include temporary staging, backup and cleanup, not eight permanent changes. By playbook sequencing the deployment, dnsmasq activation and embedded assertions completed without Ansible failures. **An independent read-only inspection of the live router configuration is still outstanding.**

The target mapping is b8:27:eb:e8:36:cd -> 192.168.2.48, retaining the .180 ASUS reservation and DHCP pool 192.168.2.100-199. The last independently observed admin-01 IP remains **192.168.2.127**. The writer does not renew its DHCP lease, and no admin-01 cutover or firewall change has been authorised. Do not update inventory, DNS or claim admin SSH at .48 yet. The original source-only text below describes the earlier state, before approval and deployment. Issue #206 tracks this change.


**STATE: IaC STAGED ONLY; NO LIVE DHCP CHANGE OR RESTART.** Merge and offline syntax tests do not grant deployment permission.

## Operator evidence
- admin-01 physical Raspberry Pi 3 MAC b8:27:eb:e8:36:cd previously documented at 192.168.2.48. It became inaccessible at .48 despite the router .2.1, ASUS .2.2 and monitor .2.52 remaining accessible.
- Following a physical reboot, SSH is restored to admin-01 at 192.168.2.127. Host checks show NetworkManager with active netplan-eth0, ipv4.method auto, and a DHCP lease from server 192.168.2.1, 86400 seconds.
- router-01 dnsmasq was active, dynamic pool 192.168.2.100–199, with the existing separate reservation for MAC 24:4b:fe:5e:cc:c8 at 192.168.2.180.
- router-01 lease for admin-01 is b8:27:eb:e8:36:cd / 192.168.2.127; no admin reservation was found in the checked config.
- Follow-up router check found no lease for 192.168.2.48, no ping reply (3 requests), INCOMPLETE ARP/neighbor resolution, and dnsmasq --test passed.
- An offline static-IP device at .48 remains possible. No DHCP, Netplan, firewall or network modifications have been made in this investigation. Router metrics SSH key authorisation changed only router-metrics SSH files and is not established as the cause of the IP drift.

## Intended narrowly scoped change

Add exactly one dnsmasq host reservation: dhcp-host=b8:27:eb:e8:36:cd,192.168.2.48.
Retain dynamic pool 192.168.2.100–199 and the existing ASUS .180 reservation, with no lease file manipulation, network interface changes or PPPoE/firewall changes.

Files:
- IaC/ansible/playbooks/tasks/router-01-admin-dhcp-preflight.yml: exact identity and read-only DHCP state assertions, including the current admin lease on .127.
- IaC/ansible/playbooks/router-01-admin-dhcp-reservation-preflight-readonly.yml: safe to run now; no writes.
- IaC/ansible/playbooks/router-01-admin-dhcp-reservation.yml: **SOURCE ONLY, NOT APPROVED FOR LIVE RUN**. Default false gates on write, dnsmasq restart and separate .48 conflict acceptance. Offline candidate config syntax verification, protected backup, exact marked block, live syntax check, scoped dnsmasq restart and rollback attempt on error.
- IaC/ansible/playbooks/router-01-admin-dhcp-reservation-rollback.yml: defaults false; requires explicit rollback, restart and alternate admin access verification; preserves the other reservation.
- .github/workflows/validate-router-01-admin-dhcp-reservation.yml: CI safety and syntax validation.

## Safe read-only preflight command after PR merge

~~~bash
cd ~/projects/homelab-platform
git switch main && git pull --ff-only origin main
cd IaC/ansible
ansible-playbook -i inventory/router-01-postcutover-baseline.yml \
  playbooks/router-01-admin-dhcp-reservation-preflight-readonly.yml \
  --limit router-01 --ask-become-pass
~~~

**Do not run the writer yet.** For live approval later: independently confirm no host uses .48; obtain explicit authorization to modify router.conf and separately restart dnsmasq. Maintain physical admin console and access to router. Writer does not renew admin-01 lease. Confirm dnsmasq, .180 reservation and other DHCP clients first.

**Separate planned cutover:** only after router postflight, renew admin-01 DHCP under NetworkManager with physical console/alternate access, since remote SSH can disconnect. Independently verify .48 connectivity, SSH and gateway before changing canonical inventory, estate.json, DNS records or CURRENT-STATE.md; old .127 may not survive renewal.

**Rollback** requires fresh approval and alternate access, particularly if admin-01 is already at .48. Existing Bedroom reservation playbooks are not safe substitutes, because they assume an older DHCP configuration.

Evidence: [router migration issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206); monitoring issue #209 concerns a separate key change.
