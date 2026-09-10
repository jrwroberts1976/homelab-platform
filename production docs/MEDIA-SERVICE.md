# media-01 Production Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `media-01.jameshouse`  
**IPv4:** `192.168.2.195`  
**Platform:** physical Raspberry Pi 5, Debian 13, 512 GB-class NVMe
**Primary workload:** Kodi 21 media endpoint  
**Normal controller:** `admin-01.jameshouse` / `192.168.2.48`
**Status:** operational; extended Pi/NVMe monitoring and central logging remain follow-up work

## Service role

`media-01` is a dedicated Raspberry Pi 5 living-room/media endpoint built and maintained from Git-managed Ansible. It is not a Proxmox guest and is not a k3s node.

The operating-system service layer is reproducible. Media content under `/srv/media` is user data and is not recreated by the role.

## Managed services

### Kodi

Kodi runs as a dedicated systemd service:

- unit: `kodi.service`
- user: `james`
- launcher: `/usr/bin/kodi-standalone`
- LightDM disabled
- automatic restart after failure
- single `kodi.bin` process enforced across normal service restarts

Managed settings include playback cache tuning, Unknown Sources, loopback EventServer control, Open-Meteo weather, OpenSubtitles.com and autocompletion.

Credentials for third-party services are not stored in Git.

### Media storage and SMB

Media root:

```text
/srv/media
```

Managed directories:

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

Samba policy:

- authenticated access only;
- SMB signing required;
- guest access disabled;
- household-LAN writable share;
- credentials supplied outside Git;
- writes mapped consistently to the `james` account.

Kodi uses local filesystem paths rather than looping back through SMB.

### Time

`media-01` uses the homelab Chrony pair:

1. `192.168.2.70` — preferred `ntp-01`
2. `192.168.2.71` — secondary `ntp-02`

### Monitoring

Prometheus node exporter is expected on TCP/9100 and `monitor-01` (`192.168.2.52`) is the monitoring platform.

Additional useful coverage:

- Raspberry Pi temperature/throttling;
- NVMe SMART/health;
- Kodi service availability where actionable;
- Alloy/Loki log forwarding after the fresh central logging platform is deployed.

### Host firewall

The intended nftables policy is:

- default-deny inbound;
- SSH TCP/22 from the LAN;
- SMB TCP/445 from the LAN;
- node exporter TCP/9100 from `monitor-01` only;
- ICMP/ICMPv6 allowed;
- DHCP renewal from `192.168.2.1` allowed;
- loopback and established/related traffic allowed.

Do not mark firewall work complete unless the live rules and remote reachability tests prove the expected policy.

## IaC paths

```text
IaC/ansible/playbooks/media-01-preflight.yml
IaC/ansible/playbooks/media-01.yml
IaC/ansible/roles/chrony_client/
IaC/ansible/roles/media_endpoint/
IaC/ansible/roles/media_smb/
IaC/ansible/roles/node_exporter/
IaC/ansible/roles/media_firewall/
IaC/ansible/inventory/hosts.yml
```

## Controller deployment

Preferred controller:

```text
admin-01.jameshouse
192.168.2.48
```

Normal pattern:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook --syntax-check playbooks/media-01.yml
ansible-playbook playbooks/media-01.yml
```

If protected environment state is required, source it without printing its contents.

## Validation standard

A normal deployment is considered converged when a second run reports no unintended changes and zero failures.

Validate at least:

- exactly one Kodi process;
- managed Kodi settings persisted;
- Samba configuration valid;
- authenticated SMB access works;
- Chrony selects a homelab time source;
- node exporter is active/reachable according to policy;
- zero failed systemd units;
- firewall behaviour matches the documented allowlist.

## Recovery

Recovery order:

1. install/boot a supported Debian/Raspberry Pi OS base on the Pi 5;
2. restore SSH access from `admin-01`;
3. restore protected credential material outside Git;
4. run the authoritative Ansible playbook;
5. restore media content under `/srv/media` if required;
6. validate Kodi, SMB, Chrony, monitoring and firewall policy;
7. repeat the Ansible run and require no unintended drift.

The intended recovery identity is always `media-01`, not the historical `k3s-node-01` alias.

## Remaining follow-up

- confirm final firewall behaviour after any later network change;
- keep Prometheus target state aligned with the current inventory;
- add Pi temperature/throttling and NVMe health metrics;
- add Alloy/Loki logging when `CENTRAL-LOGGING-SERVICE.md` is implemented.
