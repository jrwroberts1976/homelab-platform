<!-- estate-authority: IaC/inventory/estate.json -->
# media-01 Production Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `media-01`  
**IPv4:** `192.168.2.195`  
**Platform:** Raspberry Pi 5 / Debian 13 / 512 GB-class NVMe  
**Primary workload:** Kodi media endpoint + primary Proxmox guest-backup target  
**Status:** OPERATIONAL  
**Last current-state review:** 6 October 2026

## Service role

`media-01` is a dedicated media endpoint and infrastructure backup target managed through Git-backed Ansible.

Primary responsibilities:

- Kodi local media playback;
- authenticated SMB sharing for `/srv/media`;
- NFS v4.2 backup target for both members of `jameshouse-pve`;
- host monitoring/logging agents.

Earlier host identities for this hardware are historical only. <!-- historical -->

## Current live state

Current operational baseline includes:

- Debian 13 / aarch64;
- Kodi active/enabled;
- Samba active/enabled;
- NFS server active;
- Chrony active;
- Node Exporter active;
- Grafana Alloy active;
- Zabbix Agent 2 active;
- Kodi audio watchdog service/timer enabled;
- zero failed systemd units after the 5 October maintenance cycle;
- pending updates 0;
- reboot required no.

The intended nftables policy remains a separate reviewed change unless current live validation establishes otherwise.

## Kodi and media storage

Kodi runs as a systemd-managed workload using local paths under:

```text
/srv/media
```

Key persistent directories include Movies, TV, Music and plugins content. User media is persistent data and is not recreated by IaC.

Authenticated SMB share:

```text
\\media-01\Media
```

Kodi uses local filesystem paths rather than looping back through SMB.

## Proxmox backup target

`media-01` provides node-scoped NFS namespaces for the two **cluster members**:

```text
/srv/backup/pve-proxmox   -> PROXMOX 192.168.2.70
/srv/backup/pve-proxmox-2 -> Proxmox-2 192.168.2.71
```

Current scheduled jobs:

```text
PROXMOX
  02:15
  storage: media-backup-proxmox
  guests: 100,102,104,105,200,201,204

Proxmox-2
  03:15
  storage: media-backup-proxmox-2
  guests: 101,103,202,203

mode: snapshot
compression: zstd
retention: keep-last=3
```

Unattended evidence has been observed for CT105 and VM203 as well as the established Proxmox-2 guest set. CT104 and VM204 remain the explicit first-unattended evidence gaps in the current record.

The backup repository shares this host/NVMe failure domain, so it is **not** the independent second copy still required by the wider DR plan.

## Time

Chrony uses the two PVE cluster nodes as local NTP sources:

```text
192.168.2.70
192.168.2.71
```

## Monitoring and logging

Current observability includes:

- central availability checks;
- Node Exporter;
- Grafana Alloy to Loki;
- Zabbix Agent 2;
- patch telemetry;
- backup/service checks where implemented.

Alloy is production state, not future work. The exact Alloy version is dated runtime evidence; package maintenance on 5 October left the host healthy with no pending OS updates.

Useful future signals include:

- Raspberry Pi temperature/throttling;
- NVMe SMART/health;
- Kodi availability where actionable;
- storage capacity and NFS backup freshness.

## IaC ownership

Primary paths include:

```text
IaC/ansible/playbooks/media-01.yml
IaC/ansible/playbooks/media-backup-target.yml
IaC/ansible/roles/media_endpoint/
IaC/ansible/roles/media_smb/
IaC/ansible/roles/media_backup_target/
IaC/ansible/roles/node_exporter/
IaC/ansible/roles/alloy/
```

Normal reconciliation runs from `admin-01`.

## Operational safety

- do not reboot `media-01` casually during active Proxmox backup windows;
- preserve SMB/NFS access when changing firewall/network configuration;
- do not treat the primary NFS copy as an independent second failure domain;
- preserve user media separately from rebuildable OS/application state.

## Recovery

1. install supported Debian 13;
2. restore approved SSH/controller access;
3. reconcile Git-managed media/monitoring roles;
4. restore protected SMB credentials;
5. restore/copy user media as required;
6. recreate NFS backup namespaces through IaC;
7. restore backup archives from an independent copy if the NVMe itself was lost;
8. validate Kodi, SMB, NFS, Chrony, Node Exporter, Alloy and Zabbix;
9. run a second Ansible pass and require no unintended drift.

## Remaining gates

- independent second copy for important backup archives/data;
- explicit protection strategy for user media;
- additional Pi/NVMe/storage telemetry where useful;
- nftables only through a separately reviewed, remotely validated change.
