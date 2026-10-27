# Router-01 reboot migration — deployment gates (27 October 2026)

Status: DESIGN AND PREFLIGHT ONLY. No reboot migration staged, armed or deployed.

## Verified live baseline
- admin-01 Ansible router-01-reboot-migration-preflight-readonly.yml: ok=13, changed=0, failed=0.
- docker-01 eth0 192.168.2.220/24 on old ASUS LAN, eth1 carrier=0, no ppp0.
- PPPoE systemd unit active but not connected; Kea/Unbound masked.
- Old cutover and rollback timers inactive, no cutover markers.
- Docker stopped and disabled; residual Docker iptables-nft rules remain in kernel.
- No independent console; physical restoration of cabling is needed after rollback.

## Blockers to permanent reboot activation
1. Create separate Ansible stage and activate playbooks; previous 120-second timer cutover must not be reused.
2. Back up original Netplan and firewall and retain boot-persistent rollback state.
3. Replace old eth0 DHCP profile cleanly at cutover (do not use overlapping active Netplan definitions).
4. Keep eth1 unmanaged by NetworkManager and ensure pppd can bring it up.
5. Configure Kea/Unbound to start at boot only after eth0 isolated from ASUS LAN.
6. Audit and retire old Docker iptables-nft FORWARD DROP without deleting unrelated ICMP timestamp protection.
7. Test router nftables NAT and forwarding boot ordering without global flush surprises.
8. Make rollback service independent of SSH, reboot-safe and tested before deployment; validate return path and warn that cable reversal is required.
9. Validate ASUS WAN Automatic IP, with ONT -> Pi eth1, Pi eth0 -> ASUS WAN, ASUS LAN -> HP switch.
10. After boot require ppp0 IPv4/default route, Kea lease for ASUS WAN, DNS and public reachability before disarming rollback.

Do not run router-01-lan-arm-inplace.yml or router-01-dhcp-trial-arm.yml as a permanent boot migration.
Do not reboot, unmask Kea on old LAN, or move cables while deployment is not staged.

Source configuration remains under IaC/ansible; update gpt-handover.md and CURRENT-STATE.md only with verified state.