<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01: recover stable admin-01 DHCP address — 29 October 2026

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
