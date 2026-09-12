# media-01 Production Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `media-01`  
**IPv4:** `192.168.2.195`  
**Platform:** Raspberry Pi 5, Debian 13, 512 GB-class NVMe  
**Primary workload:** Kodi media endpoint  
**Status:** operational; nftables and extended Pi/NVMe monitoring remain follow-up gates  
**Last current-state review:** 12 September 2026

## Service role

`media-01` is a dedicated living-room/media endpoint managed through Git-backed Ansible.

The operating-system/service layer is reproducible. Media content under `/srv/media` is user data and is not recreated by the role.

The former `k3s-node-01` identity is retired.

## Current live state

Validated 12 September 2026:

- Debian 13;
- Kodi active/enabled;
- LightDM inactive/disabled;
- Samba active/enabled;
- SMB listening on TCP/445;
- media directories under `/srv/media` present;
- Chrony active and using the local Proxmox time service;
- Node Exporter active on TCP/9100;
- Prometheus ICMP and Node Exporter targets healthy;
- nftables inactive/disabled;
- zero failed systemd units.

`hostname -f` returned the short hostname `media-01` during the audit. Local DNS naming remains `media-01.jameshouse`, but the host itself should not be documented as having a proven FQDN configuration until that is deliberately checked/reconciled.

## Kodi

Kodi runs as a dedicated systemd service:

- unit: `kodi.service`;
- user: `james`;
- launcher: `/usr/bin/kodi-standalone`;
- LightDM disabled;
- service configured to restart after failure;
- boot target remains suitable for the local media/HDMI role.

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

`media-01` uses Chrony as an NTP client.

Preferred homelab sources:

```text
192.168.2.70
192.168.2.71
```

The 12 September audit confirmed Chrony was active and the host was using the local time service.

## Monitoring

Node Exporter is already live and scraped by Prometheus.

Current monitoring:

- ICMP probe: healthy;
- Node Exporter TCP/9100: healthy.

Still useful to add:

- Raspberry Pi temperature/throttling metrics;
- NVMe SMART/health metrics;
- Kodi service availability alerting if actionable;
- Alloy/Loki logging only after the central logging platform actually exists.

## Host firewall

An nftables role/design exists but the live 12 September audit confirmed nftables is **not deployed**.

Intended policy remains a follow-up change and must not be marked complete until a live apply and remote validation prove it.

Do not confuse a defined Ansible role with an active firewall.

## IaC paths

Primary deployment:

```text
IaC/ansible/playbooks/media-01.yml
```

Supporting roles:

```text
IaC/ansible/roles/chrony_client/
IaC/ansible/roles/media_endpoint/
IaC/ansible/roles/media_smb/
IaC/ansible/roles/node_exporter/
IaC/ansible/roles/media_firewall/
```

## Controller

Normal reconciliation is launched from:

```text
admin-01
192.168.2.48
~/projects/homelab-platform
```

The retired `TestServer` identity at `.220` must not be used as the controller. `.220` is now `docker-01`.

## Validation standard

A stable Ansible reconciliation should normally produce a second run with:

```text
changed=0
failed=0
unreachable=0
```

Service validation should include:

- Kodi active and only the intended runtime present;
- Samba configuration/service healthy;
- expected media paths present;
- Chrony healthy;
- Node Exporter healthy;
- zero unexpected failed units;
- firewall behaviour checked only after nftables is actually deployed.

## Recovery

The host is rebuilt from Git rather than restored as an opaque OS image.

Recovery order:

1. install supported Debian 13 on the Raspberry Pi 5;
2. restore approved SSH/controller access;
3. check out reviewed `homelab-platform` state;
4. restore protected SMB credential material;
5. run the media Ansible playbook;
6. restore/copy user media under `/srv/media` if required;
7. validate Kodi, SMB, Chrony and monitoring;
8. apply/validate firewall only if that separate change has been approved;
9. run a second Ansible pass and require zero unintended drift.

## Remaining completion gates

- apply and remotely validate the intended nftables policy;
- add Pi temperature/throttling metrics;
- add NVMe SMART/health metrics;
- decide/prove backup protection for user media;
- configure optional Kodi user-service credentials/settings that are intentionally outside Git;
- add central logging only when Loki/Alloy exists.
