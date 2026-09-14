# media-01 Production Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `media-01`  
**IPv4:** `192.168.2.195`  
**Platform:** Raspberry Pi 5, Debian 13, 512 GB-class NVMe  
**Primary workload:** Kodi media endpoint and primary Proxmox guest-backup target  
**Status:** operational; nftables and extended Pi/NVMe monitoring remain follow-up gates  
**Last current-state review:** 14 September 2026

## Service role

`media-01` is a dedicated living-room/media endpoint managed through Git-backed Ansible. It also provides the current primary NFS target for Proxmox guest backups.

The operating-system/service layer is reproducible. Media content under `/srv/media` is user data and is not recreated by the role.

The former `k3s-node-01` identity is retired.

## Current live state

Validated 14 September 2026:

- Debian 13 / aarch64;
- Kodi 21.3 active/enabled;
- Samba active/enabled;
- Chrony active;
- Node Exporter 1.9.0 active;
- Alloy 1.19.2 active;
- NFS server active;
- NVMe SMART health PASS during backup-target validation;
- zero failed systemd units.

The intended nftables policy remains a separate follow-up and must not be described as active until deliberately deployed and remotely validated.

## Kodi

Kodi runs as a dedicated systemd service:

- unit: `kodi.service`;
- user: `james`;
- launcher: `/usr/bin/kodi-standalone`;
- service enabled and active;
- package version validated as `3:21.3+dfsg-1+rpt3`.

Managed Kodi configuration should remain in Ansible rather than being treated as authoritative GUI state.

## Media storage and SMB

Media root:

```text
/srv/media
```

Managed directories include:

```text
/srv/media/Movies
/srv/media/TV
/srv/media/Music
/srv/media/plugins
```

Authenticated SMB share:

```text
\\media-01\Media
```

Kodi uses local filesystem paths rather than looping back through SMB.

User media is persistent data and needs an intentional backup decision; IaC does not recreate it.

## Proxmox guest-backup target

`media-01` now provides separate NFS namespaces for the two standalone Proxmox nodes so duplicate VMIDs cannot collide in the backup repository:

```text
/srv/backup/pve-proxmox     -> PROXMOX .70 only
/srv/backup/pve-proxmox-2   -> Proxmox-2 .71 only
```

The original `/srv/backup/pve` export and `media-backup` PVE storage remain preserved temporarily as rollback evidence while the isolated-storage schedule cutover is completed and observed.

Validated backup-target state includes:

- NFS v4.2/TCP;
- exports restricted to the intended Proxmox client addresses;
- root-owned backup repositories;
- write/read/delete validation from both hypervisors;
- isolated per-node PVE storage registration;
- complete production guest backup sets on both isolated namespaces;
- approximately 414 GiB free after the first complete `.70` backup set.

The backup repository is on the same physical NVMe as the rest of `media-01`. It protects the Proxmox guests from hypervisor loss, but **does not protect `media-01` itself** from NVMe or host failure. User media under `/srv/media` still requires an independent failure-domain copy.

See:

```text
docs/architecture/BACKUP-STRATEGY.md
production docs/PROXMOX-BACKUP-RECOVERY.md
```

## Time

`media-01` uses Chrony as an NTP client with the two local Proxmox time sources as the intended upstreams:

```text
192.168.2.70
192.168.2.71
```

Chrony was active during the 14 September compact audit.

## Monitoring and logging

Current host observability includes:

- ICMP/availability coverage through the central monitoring design;
- Node Exporter on TCP/9100;
- Alloy 1.19.2 as part of the deployed central logging baseline;
- zero failed-unit validation.

The older statement that Alloy/Loki logging was future-only is superseded. Loki now exists centrally on `monitor-01`, and Alloy is active on `media-01`.

Still useful to add where actionable:

- Raspberry Pi temperature/throttling metrics;
- NVMe SMART/health metrics;
- Kodi service availability alerting;
- media/backup storage capacity and failure signals;
- backup freshness/status metrics for the isolated Proxmox namespaces.

## Host firewall

An nftables role/design exists but the live estate audit did not establish an active nftables policy on `media-01`.

The NFS backup-target deployment currently relies on the validated host/network controls encoded by the backup IaC and restricted exports. Any wider firewall rollout must be applied and remotely validated separately so SSH, SMB, monitoring, media and NFS backup functions are not accidentally cut off.

## IaC paths

Primary media deployment:

```text
IaC/ansible/playbooks/media-01.yml
```

Backup-target IaC includes:

```text
IaC/ansible/playbooks/media-backup-target.yml
IaC/ansible/playbooks/media-backup-split-prep.yml
IaC/ansible/roles/media_backup_target/
IaC/ansible/roles/media_backup_split_prep/
```

Supporting roles include:

```text
IaC/ansible/roles/chrony_client/
IaC/ansible/roles/media_endpoint/
IaC/ansible/roles/media_smb/
IaC/ansible/roles/node_exporter/
IaC/ansible/roles/alloy/
IaC/ansible/roles/media_firewall/
```

## Controller

Normal reconciliation is launched from:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired `TestServer` identity at `.220` must not be used as the controller. `.220` is `docker-01`.

## Validation standard

A stable Ansible reconciliation should normally produce a second run with no unintended changes and:

```text
failed=0
unreachable=0
```

Service validation should include:

- Kodi active;
- Samba healthy;
- expected media paths present;
- NFS backup exports and namespaces healthy;
- sufficient NVMe free space;
- Chrony healthy;
- Node Exporter healthy;
- Alloy healthy;
- zero unexpected failed units;
- firewall behaviour checked only after nftables is deliberately deployed.

## Recovery

The host is rebuilt from Git rather than restored as an opaque OS image.

Recovery order:

1. install supported Debian 13 on the Raspberry Pi 5;
2. restore approved SSH/controller access;
3. check out reviewed `homelab-platform` state;
4. restore protected SMB credential material;
5. run the media Ansible playbook and baseline observability roles;
6. restore/copy user media under `/srv/media` if required;
7. recreate the approved NFS backup namespaces through IaC;
8. restore backup archives from an independent copy if the NVMe itself was lost;
9. validate Kodi, SMB, NFS, Chrony, Node Exporter and Alloy;
10. apply/validate firewall only if that separate change has been approved;
11. run a second Ansible pass and require no unintended drift.

## Remaining completion gates

- apply and remotely validate the intended nftables policy if still required;
- add Pi temperature/throttling metrics;
- add NVMe SMART/health and backup-capacity metrics;
- establish an independent secondary copy for important Proxmox backups;
- decide/prove backup protection for user media;
- configure optional Kodi credentials/settings that are intentionally outside Git;
- continue central logging/dashboard work only where it adds operational value.
