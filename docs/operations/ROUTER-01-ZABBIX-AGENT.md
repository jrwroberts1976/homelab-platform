<!-- source-of-truth: docs/architecture/CURRENT-STATE.md -->
# Router-01 Zabbix Agent 2 (active-check only) rollout

## Status
**Staged in GitHub, NOT YET DEPLOYED.** Associated with #294. Preflight read-only operator evidence on 4 November 2026: router-01 at 192.168.2.1 is Debian 13 ARM64; no active Zabbix agent; outbound TCP to zabbix-01 192.168.2.59:10051 passes; router-pppoe, dnsmasq, unbound and nftables active; default route is ppp0. The generic zabbix_agents inventory does not include router-01, intentionally.

## Safety boundaries
- Use only `playbooks/router-01-zabbix-agent-active.yml`, never broad `zabbix-agent.yml` and never edit the gateway firewall to expose 10050.
- Zabbix Agent 2 connects to 192.168.2.59:10051 with active checks. Passive listener and permitted passive source are loopback-only 127.0.0.1; check service and socket after rollout.
- The scoped playbook checks router services, default route and server reachability before and after. Packages/agent config may change; no PPPoE, DHCP, DNS, firewall, NAT or QoS tasks are permitted.
- The separately approval-gated `playbooks/router-01-zabbix-agent-stop.yml` stops and disables only zabbix-agent2; it deliberately preserves package/config for diagnosis. It is a service-stop rollback, not a package purge.
- Installing the agent **does not register router-01 in Zabbix**. Register or audit host/template assignments separately, with least-privileged credentials and explicit approval; the existing read-only management-report token cannot create hosts.
- No host/IP-only identity inference: any future DHCP dashboard Zabbix enrichment must match canonical host identity, current MAC/IP and telemetry freshness.

## Controller validation (read-only)
```sh
cd ~/projects/homelab-router-zabbix/IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/router-01-zabbix-agent-active.yml --syntax-check
ansible-playbook -i inventory/hosts.yml playbooks/router-01-zabbix-agent-stop.yml --syntax-check
```

## Approved installation (not automatic)
```sh
ansible-playbook -i inventory/hosts.yml playbooks/router-01-zabbix-agent-active.yml \
  --limit router-01 --ask-become-pass \
  -e router_zabbix_agent_install_approved=true \
  -e router_zabbix_agent_install_phrase=INSTALL_ROUTER01_ZABBIX_AGENT2
```
Record exact recap, agent socket binding, service status, router core health and eventual active-check receipt before marking complete. A local no-change check-mode run is not an install proof.

## Emergency stop (separately authorised)
```sh
ansible-playbook -i inventory/hosts.yml playbooks/router-01-zabbix-agent-stop.yml \
  --limit router-01 --ask-become-pass \
  -e router_zabbix_agent_rollback_approved=true \
  -e router_zabbix_agent_rollback_phrase=STOP_ROUTER01_ZABBIX_AGENT2
```
