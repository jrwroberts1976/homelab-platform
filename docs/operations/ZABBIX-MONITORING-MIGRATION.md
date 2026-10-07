# Zabbix monitoring migration — homelab-platform

**Status:** IN PROGRESS — playbooks added, not yet deployed
**Scope:** Migrate homelab health checks to Zabbix as the primary data source

## Purpose

Migrate homelab health checks to use Zabbix as the primary data source, replacing the parallel Prometheus/node_exporter/Blackbox stack for host telemetry, reachability, and service probes.

Grafana stays as the dashboard frontend. Loki stays for log aggregation. Prometheus stays for custom network-host-discovery metrics that Zabbix can't model.

## What these playbooks do

| Playbook | Scope | Run on |
|---|---|---|
| `zabbix-homelab-linux-host-template.yml` | Creates the "Homelab Linux Host" template (CPU, memory, disk, network, triggers) and links it to all managed hosts | `localhost` (hits Zabbix API) |
| `zabbix-homelab-userparams.yml` | Deploys homelab-specific UserParameters to every managed host: patch state, DNS health, Proxmox cluster, Corosync, QDevice, sensor capture, backup freshness, service health | `zabbix_agents` hosts |
| `zabbix-nonagent-monitoring.yml` | Registers non-agent hosts (router, switch, AiMesh, Home Assistant, media-01, docker-01) with ICMP checks; creates HTTP/TCP/DNS service checks on a synthetic "homelab-services" host | `localhost` (hits Zabbix API) |

## Prerequisites

1. Zabbix 7.0 platform healthy on `zabbix-01` (validated 2026-10-07)
2. Zabbix Agent 2 installed on all 15 managed hosts
3. `HOMELAB_ZABBIX_API_TOKEN` in the environment. Note: the token used by `zabbix-network-inventory-exporter.yml` is read-only and is **not** sufficient for template/host creation — this migration needs a Super Admin API token.
4. The `zabbix_agents` inventory group contains the 15 managed Linux hosts

## Run order

```bash
# 1. Deploy the template (idempotent)
HOMELAB_ZABBIX_API_TOKEN=<admin-token> \
ansible-playbook -i IaC/ansible/inventory/hosts.yml \
  IaC/ansible/playbooks/zabbix-homelab-linux-host-template.yml \
  -e zabbix_linux_host_template_allow_deploy=true

# 2. Deploy UserParameters to every managed agent
HOMELAB_ZABBIX_API_TOKEN=<admin-token> \
ansible-playbook -i IaC/ansible/inventory/hosts.yml \
  IaC/ansible/playbooks/zabbix-homelab-userparams.yml

# 3. Register non-agent hosts and service checks
HOMELAB_ZABBIX_API_TOKEN=<admin-token> \
ansible-playbook -i IaC/ansible/inventory/hosts.yml \
  IaC/ansible/playbooks/zabbix-nonagent-monitoring.yml \
  -e zabbix_nonagent_allow_deploy=true
```

All playbooks are idempotent — they skip items/triggers/hosts that already exist.

## What gets created

### Template: "Homelab Linux Host"

**Items:**
- CPU: `system.cpu.util`, loads (1/5/15 min)
- Memory: total, available, pused; swap total, pfree
- System: uptime, boot time, kernel info, process counts
- Agent health: agent.ping, agent.version

**Discovery rules:**
- Filesystems (`vfs.fs.discovery`) → total/used/free/pused item prototypes
- Network interfaces (`net.if.discovery`) → inbound/outbound bps prototypes (with ×8 multiplication for bits)

**Triggers:**
- CPU >90% for 5 min (warning)
- Load avg15 >5 for 15 min (warning)
- Memory >90% for 5 min (warning)
- Swap <20% free (information)
- Host restarted (uptime <600s) (warning)
- Agent unreachable for 3 min (high)
- Filesystem <10% free / <5% free (prototype triggers)

### UserParameters: "homelab.*" keys

Deployed to every managed host. Per-host relevance is noted below.

| Key | Returns | Where |
|---|---|---|
| `homelab.patch.pending` | Count of pending apt upgrades | all agents |
| `homelab.patch.security` | Count of pending security upgrades | all agents |
| `homelab.patch.reboot_required` | 1/0 | all agents |
| `homelab.patch.unattended_status` | "active" or "inactive" | all agents |
| `homelab.patch.last_run` | Epoch of last unattended-upgrades run | all agents |
| `homelab.service.active[<name>]` | systemctl is-active result | all agents |
| `homelab.pve.quorate` | 1/0 | PROXMOX, Proxmox-2 |
| `homelab.pve.node_count` | Cluster member count | PROXMOX, Proxmox-2 |
| `homelab.pve.member_info[<name>]` | Address and state stanza | PROXMOX, Proxmox-2 |
| `homelab.pve.vm_count` | Running VMs | PROXMOX, Proxmox-2 |
| `homelab.pve.ct_count` | Running CTs | PROXMOX, Proxmox-2 |
| `homelab.corosync.link0` | 1/0 | PROXMOX, Proxmox-2 |
| `homelab.corosync.link1` | 1/0 | PROXMOX, Proxmox-2 |
| `homelab.qdevice.service` | "active"/"inactive" | admin-01 |
| `homelab.qdevice.port` | 1/0 (port 5403 listening) | admin-01 |
| `homelab.backup.newest_proxmox` | Epoch of newest backup | media-01 |
| `homelab.backup.newest_proxmox2` | Epoch of newest backup | media-01 |
| `homelab.backup.count_proxmox` | Backups in last 3 days | media-01 |
| `homelab.backup.count_proxmox2` | Backups in last 3 days | media-01 |
| `homelab.dns.pihole_status` | 1/0 | dns-01, dns-02 |
| `homelab.dns.unbound_status` | "active"/"inactive" | dns-01, dns-02 |
| `homelab.dns.queries_today` | DNS query count | dns-01, dns-02 |
| `homelab.dns.blocked_today` | Blocked query count | dns-01, dns-02 |
| `homelab.dns.blocked_pct` | Blocked percentage | dns-01, dns-02 |
| `homelab.sensor.suricata_drops` | Kernel drop % | sensor-01 |
| `homelab.sensor.zeek_gaps` | Capture gap count | sensor-01 |
| `homelab.sensor.suricata_service` | "active"/"inactive" | sensor-01 |
| `homelab.sensor.zeek_service` | "active"/"inactive" | sensor-01 |
| `homelab.zabbix.queue` | "ok"/"error" | zabbix-01 |
| `homelab.zabbix.db_size` | Database size string | zabbix-01 |
| `homelab.media.kodi_service` | "active"/"inactive" | media-01 |
| `homelab.media.smb_check` | SMB share count | media-01 |
| `homelab.media.nfs_rpcs` | NFS export count | media-01 |
| `homelab.birdnet.service` | "active"/"inactive" | docker-01 |
| `homelab.birdnet.http` | HTTP status code | docker-01 |
| `homelab.komodo.http` | HTTP status code | komodo-01 |
| `homelab.komodo.mongo` | "active"/"inactive" | komodo-01 |
| `homelab.cloud.http` | HTTP status code | cloud-01 |
| `homelab.cloud.postgres` | "active"/"inactive" | cloud-01 |
| `homelab.mail.queue_size` | Postfix queue size | mail-relay-01 |
| `homelab.mail.postfix_service` | "active"/"inactive" | mail-relay-01 |
| `homelab.greenbone.http` | HTTP status code | greenbone-01 |
| `homelab.cert.expiry[<host>,<port>]` | Certificate expiry epoch | any HTTPS host |

### Non-agent host registration

7 hosts registered with ICMP ping/packet loss/response time items and unreachable triggers:
- ASUS router, HP switch, 2× AiMesh nodes, Home Assistant, media-01, docker-01

### Service checks (on "homelab-services" synthetic host)

- 11 HTTP checks with triggers
- 7 TCP port checks with triggers
- 4 DNS resolution checks with triggers

## Open items

1. **Zabbix-side items for the `homelab.*` keys are not yet created.** The UserParameters are deployed to the hosts, but Zabbix needs matching items and triggers referencing each key before it collects and alerts on them. A follow-up playbook is required.
2. **Backup freshness paths are placeholders.** `zabbix-homelab-userparams.yml` looks in `/srv/backup/proxmox` and `/srv/backup/proxmox-2`, which are inferred, not confirmed. Reconcile against the real `media-01` NFS export layout.
3. **Pi-hole UserParameters assume the web API is reachable at `http://127.0.0.1/admin/api.php`** on `dns-01` / `dns-02`. Verify.
4. **Do not retire Prometheus/Blackbox targets until Zabbix demonstrates equivalent coverage.** Running both permanently is not the goal.

## What stays outside Zabbix

| Component | Reason |
|---|---|
| Loki / Alloy log pipeline | Zabbix is not a log aggregator |
| Network host discovery / Nmap | Custom Python pipeline too complex for Zabbix items |
| Management report generator | Already pulls from Zabbix API; keep the custom pipeline |
| Grafana (frontend) | Keep it; add Zabbix as a data source |

## Documentation follow-up

`docs/architecture/CURRENT-STATE.md`, `docs/architecture/INSTALLED-SOLUTIONS-CATALOGUE.md` and `docs/architecture/ACTIVE-INFRASTRUCTURE-BACKLOG.md` should be updated once this migration reaches production, following the closure-record convention used for the security/monitoring integration project.
