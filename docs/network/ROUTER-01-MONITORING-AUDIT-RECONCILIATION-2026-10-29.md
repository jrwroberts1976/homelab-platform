<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 legacy monitoring PR #210 reconciliation — 29 October 2026

**Status: source-only read-only audit; NO live monitoring install, SSH/sshd change, package install, firewall change, exporter exposure or service restart.**

The original [draft PR #210](https://github.com/jrwroberts1976/homelab-platform/pull/210) mixed an older router toolset model (`192.168.3.1/24`), diagnostics package installation, local Node Exporter install, SSH metrics identity/provisioning, monitoring tunnels, many preflights and previously recovered `192.168.2.1` postcutover-baseline work. **The draft is not safe to merge wholesale.** Keep original branch as historical evidence; never run its `.3.1` inventories or service writers on the current Pi.

## Extracted safe step

`IaC/ansible/playbooks/router-01-monitoring-path-readonly.yml` is newly reconciled for **live** `router-01` at `192.168.2.1` via the already-merged isolated `inventory/router-01-postcutover-baseline.yml`. It refuses non-check mode, unknown controller or target, missing opt-in, wrong physical Pi `eth0` MAC or wrong `192.168.2.1/24` LAN identity. It reads only existing IPv4 routes, GETs Loki `http://192.168.2.52:3100/ready`, and makes bounded TCP connectivity checks to Zabbix `192.168.2.59:10051` from both `admin-01` and `router-01`. Failure to reach a monitoring destination is **reported**, not interpreted as permission to reconfigure routing, firewall, SSH or monitoring. It neither starts nor installs monitoring agents; it does not disclose credentials.

CI statically rejects mutating Ansible modules and old `.3.1` target references and checks syntax against current isolated inventory. CI is an offline safety check, **not** live network evidence.

When explicitly desired, read-only operator command from `admin-01` is:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/router-01-postcutover-baseline.yml \
  playbooks/router-01-monitoring-path-readonly.yml \
  --limit router-01 --check \
  -e router_monitoring_path_audit_approved=true
```

This is non-privileged; use the existing controller SSH identity. If Ansible needs interactive SSH authentication, supply that locally; do not paste secrets.

## Remaining #210 backlog — not merged or deployed

- The old `router-01-diagnostics-install.yml` APT writer uses hard-coded `192.168.3.1` and a NAT assertion mentioning `192.168.3.0/24`. A new exact `.2.1/.2.0/24` preflight and actual `apt-get -s` simulation are mandatory before considering a *separately approved* diagnostics install. No package installation is part of this merge.
- Old `router-01-node-exporter-local.yml` assumes `.3.1`. The 28 October live baseline already found Node Exporter **active on `127.0.0.1:9100`**, so do not rerun a Node Exporter installer without identifying actual runtime drift.
- `monitor-01` SSH metrics tunnel, agent keys, sudo/Match SSH rules, exporter port availability, and Zabbix/Alloy integration all need separate source and live review. Do **not** copy keys, activate SSH services or open firewall ports by merging this audit.
- Existing verified postcutover baseline source and audit were separately merged earlier; do not cherry-pick duplicate files from the old branch.
- In particular, the current active Bedroom ASUS DHCP reservation at `192.168.2.180` must be preserved; the obsolete `.181/.195` split DHCP exclusion is NOT a valid future migration plan. `media-01` `.195` uses DHCP, not static.

Current architecture source: `docs/architecture/CURRENT-STATE.md`. Track remaining monitoring/design tasks in issue #209; source PR #210 is retained as an accessible historical reference, not as an executable upgrade plan.
