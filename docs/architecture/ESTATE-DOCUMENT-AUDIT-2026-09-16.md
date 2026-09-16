<!-- estate-authority: IaC/inventory/estate.json -->
# Estate and Documentation Audit — 16 September 2026

## Purpose

This audit reconciles the operational documentation after the 16 September commissioning work for Komodo, Zabbix, Zabbix Agent 2 and the associated Proxmox backup-schedule changes.

The goal is to prevent an earlier point-in-time document from being mistaken for current deployment truth.

## Authority used

The audit used the repository authority order defined in `DOCUMENT-AUTHORITY.md`:

1. validated live evidence from the completed commissioning/verification runs;
2. `IaC/inventory/estate.json` for asset identity, addressing and lifecycle state;
3. `docs/architecture/CURRENT-STATE.md` for the human-readable production view;
4. `IaC/` for desired configuration;
5. current operational/recovery documents;
6. dated historical records as evidence only.

The machine inventory remained authoritative and did not require an identity/address change during this audit.

## Canonical estate result

The active estate contains 15 Ansible-managed Linux systems:

```text
admin-01       192.168.2.48
dns-02         192.168.2.50
dns-01         192.168.2.51
monitor-01     192.168.2.52
cloud-01       192.168.2.53
mail-relay-01  192.168.2.54
sensor-01      192.168.2.55
edge-01        192.168.2.56
greenbone-01   192.168.2.57
komodo-01      192.168.2.58
zabbix-01      192.168.2.59
PROXMOX        192.168.2.70
Proxmox-2      192.168.2.71
media-01       192.168.2.195
docker-01      192.168.2.220
```

Network appliances remain separate non-Ansible-managed assets in `estate.json`.

No new Home Assistant hostname, IP address or VMID is allocated by this audit.

## Confirmed live platform state

### Proxmox

The production platform is the two-node `jameshouse-pve` cluster.

Current guest placement is:

```text
PROXMOX
  CT100 dns-02
  CT102 mail-relay-01
  CT104 komodo-01
  CT105 zabbix-01
  VM200 cloud-01
  VM201 sensor-01

Proxmox-2
  CT101 dns-01
  CT103 edge-01
  VM202 monitor-01
  VM203 greenbone-01
```

### Backup schedule

IaC defines the current nightly guest selections as:

```text
PROXMOX / 02:15 / media-backup-proxmox
  100,102,104,105,200,201

Proxmox-2 / 03:15 / media-backup-proxmox-2
  101,103,202,203
```

CT104, CT105 and VM203 have manual snapshot/integrity evidence and are included in their scheduled jobs. The documents deliberately do **not** claim unattended proof for those newly added guests until the relevant overnight cycles have actually been observed.

### Komodo

`komodo-01` is commissioned, not planned work. Docker, MongoDB and Komodo Core are operational. Application backup and isolated database-restore proof exist, as does a successful manual Proxmox snapshot backup/integrity check.

Remaining Komodo work is operational hardening/onboarding: first unattended Proxmox backup observation, protection decision, HTTPS hardening and deliberate Periphery/managed-host onboarding.

### Zabbix

`zabbix-01` is commissioned, not planned work. Zabbix Server, PostgreSQL/TimescaleDB, Agent 2 and Nginx are operational.

The `zabbix_agents` inventory group contains all 15 managed Linux systems. Matching Zabbix host objects were created in `Homelab/Linux`, linked to `Linux by Zabbix agent active`, and all 15 were observed reporting on 16 September 2026.

The first all-host Agent2 Ansible run exposed an `admin-01` become-password issue. That is retained as Ansible housekeeping; it is not represented as a Zabbix reporting failure because `admin-01` subsequently reported successfully.

## Documentation drift found

The audit found the following current-document drift:

| Area | Drift | Correction |
|---|---|---|
| Root README | omitted CT104/CT105 and still presented Komodo as future work | refreshed active estate, guest placement, backup schedule, Komodo and Zabbix state |
| `CURRENT-STATE.md` | Zabbix Agent2 rollout still marked pending; CT104 backup inclusion marked pending; CT105 schedule wording overclaimed proof | recorded 15/15 reporting; recorded CT104/CT105 manual evidence and schedule inclusion; separated scheduled configuration from unattended proof |
| `TARGET-STATE.md` | omitted CT104/CT105 from implemented placement and treated Komodo as future platform | moved Komodo/Zabbix into implemented baseline and made Home Assistant the remaining major infrastructure workstream |
| `BACKUP-STRATEGY.md` | primary job still showed `100,102,200,201` | reconciled to `100,102,104,105,200,201` and recorded evidence boundaries |
| Proxmox backup runbook | manual command/current scope omitted CT104/CT105 | reconciled operational commands and current scheduled scope |
| `IaC/README.md` | reflected an older estate snapshot and called the Ansible inventory the identity authority | restored `estate.json` authority and refreshed Terraform/current-estate description |
| Ansible README | called Proxmox nodes standalone, described sensor capture as pending, omitted Greenbone/Komodo/Zabbix groups | refreshed inventory/service state and documented the `admin-01` become caveat |
| Ansible inventory comments | stale descriptive metadata for cluster/edge/Komodo state | corrected metadata only; host addresses/groups were already correct |

## Historical documents

Dated migration, audit and superseded-layout records were not rewritten merely because current state moved on. Their point-in-time content remains useful evidence when they are clearly marked historical/superseded.

Current operational readers should use `estate.json`, `CURRENT-STATE.md`, current IaC and current runbooks before relying on older evidence.

## Home automation position

Home automation is the remaining major infrastructure platform identified by the owner.

This audit intentionally leaves `planned_assets` empty because a live/canonical preflight has not yet allocated a Home Assistant hostname, address, VMID or Proxmox node placement.

The next Home Assistant stage is therefore:

1. live collision/capacity preflight;
2. reviewed deployment design;
3. canonical planned-asset reservation only after that preflight;
4. Terraform/IaC build;
5. backup/restore proof;
6. health monitoring;
7. promotion to active estate only after commissioning evidence.

The design direction in `TARGET-STATE.md` prefers a supported dedicated Home Assistant deployment on Proxmox, with Home Assistant OS VM preferred unless integration requirements justify another supported model.

## Audit conclusion

After the reconciliation in this branch:

- canonical asset identity/addressing remains internally consistent;
- current Ansible inventory targets the canonical managed estate;
- cluster guest placement documentation includes CT104 and CT105;
- backup documentation matches the IaC job selections;
- Komodo and Zabbix are represented as commissioned platforms rather than future work;
- the 15-host Zabbix Agent2 estate is represented as reporting;
- Home Assistant remains planned but deliberately unallocated pending preflight;
- historical documents remain historical rather than being silently rewritten as current truth.

Future deployment/document changes should continue to pass `scripts/validate-estate.py` and the `Estate and documentation guard` workflow before merge.
