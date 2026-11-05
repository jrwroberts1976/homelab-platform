<!-- source-of-truth: docs/architecture/CURRENT-STATE.md -->
# Router-01 Zabbix Agent 2 (active-check only) rollout

## Status
**Agent installed LIVE on 4 November 2026; server-side Zabbix enrollment/item ingestion NOT YET VERIFIED.** Associated with #294. Preflight read-only operator evidence on 4 November 2026: router-01 at 192.168.2.1 is Debian 13 ARM64; no active Zabbix agent; outbound TCP to zabbix-01 192.168.2.59:10051 passes; router-pppoe, dnsmasq, unbound and nftables active; default route is ppp0. The generic zabbix_agents inventory does not include router-01, intentionally. Operator approved and ran scoped install with recap `ok=18 changed=8 failed=0 unreachable=0 skipped=2`; core router health and loopback-only passive listener postflight passed. The read-only Zabbix API previously returned 17 registered hosts without `router-01`, so recheck actual host registration and active-item freshness before declaring end-to-end monitoring.

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

## Approved installation (completed on 4 November 2026; reruns require separate review)
```sh
ansible-playbook -i inventory/hosts.yml playbooks/router-01-zabbix-agent-active.yml \
  --limit router-01 --ask-become-pass \
  -e router_zabbix_agent_install_approved=true \
  -e router_zabbix_agent_install_phrase=INSTALL_ROUTER01_ZABBIX_AGENT2
```
Recorded completed install recap above. Agent activity and core gateway checks passed; server-side active-check receipt remains unverified. A local no-change check-mode run is not an install proof.

## Emergency stop (separately authorised)
```sh
ansible-playbook -i inventory/hosts.yml playbooks/router-01-zabbix-agent-stop.yml \
  --limit router-01 --ask-become-pass \
  -e router_zabbix_agent_rollback_approved=true \
  -e router_zabbix_agent_rollback_phrase=STOP_ROUTER01_ZABBIX_AGENT2
```

## 4 November 2026 — host registration complete; telemetry not yet verified

Operator ran approved `router-01-zabbix-register.yml` successfully: `localhost ok=9 changed=1 failed=0 unreachable=0 skipped=0`. API postflight passed and verified one enabled `router-01` host, group `Homelab/Linux`, template `Homelab Linux OS Facts`, no passive interface. Zabbix host registration is complete. Fresh active-agent OS items and full CPU/memory/disk/uptime monitoring are **not yet verified**. Previous temporary expired-token failures were no-change fail-closed runs. No router networking changes.

## 5 November 2026 — core item idempotence validated

Operator reran approved `playbooks/router-01-zabbix-core-items.yml` after corrected postflight; **localhost ok=11 changed=0 failed=0 skipped=1**. Previous read-only API audit confirmed all six health metrics fresh. Two hourly OS Facts items and final PR #295 review remain to be checked before declaring the whole router Zabbix integration complete.

## 5 November 2026 — final OS Facts verification

Operator confirmed supported fresh active OS Facts items: system.sw.os.get (age 209 s) and system.sw.os[name] (age 208 s). Together with six core checks all 8 of 8 router monitoring items are live. Idempotent core-item rerun passed with changed=0. Router monitoring technically complete; PR review/merge pending. Wider issue #294 Grafana enrichment remains open.
