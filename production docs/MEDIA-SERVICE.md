# media-01 Production Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `media-01`  
**IPv4:** `192.168.2.195`  
**Platform:** Raspberry Pi 5, Debian 13, 512 GB-class NVMe  
**Primary workload:** Kodi media endpoint  
**Status:** operational; nftables and extended Pi/NVMe monitoring remain follow-up gates  
**Last current-state review:** 14 September 2026

## Service role

`media-01` is a dedicated living-room/media endpoint managed through Git-backed Ansible.

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
- media storage capacity and failure signals.

## Host firewall

An nftables role/design exists but the live estate audit did not establish an active nftables policy on `media-01`.

Do not confuse a defined Ansible role with deployed firewall state. Apply and remotely validate any firewall change separately so SSH, SMB, monitoring and media functions are not accidentally cut off.

## IaC paths

Primary deployment:

```text
IaC/ansible/playbooks/media-01.yml
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
7. validate Kodi, SMB, Chrony, Node Exporter and Alloy;
8. apply/validate firewall only if that separate change has been approved;
9. run a second Ansible pass and require no unintended drift.

## Remaining completion gates

- apply and remotely validate the intended nftables policy if still required;
- add Pi temperature/throttling metrics;
- add NVMe SMART/health metrics;
- decide/prove backup protection for user media;
- configure optional Kodi credentials/settings that are intentionally outside Git;
- continue central logging/dashboard work only where it adds operational value.
