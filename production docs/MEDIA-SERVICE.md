# media-01 Production Service

**Authority:** `jrwroberts1976/homelab-platform`  
**Host:** `media-01.jameshouse`  
**IPv4:** `192.168.2.195`  
**Platform:** Raspberry Pi 5, Debian 13, 512 GB-class NVMe  
**Primary workload:** Kodi 21 media endpoint  
**Status:** operational; final nftables deployment and extended Pi/NVMe monitoring remain follow-up gates

## Service role

`media-01` is a dedicated living-room/media endpoint built and maintained from Git-managed Ansible.

The operating-system service layer is reproducible. Media content under `/srv/media` is user data and is not recreated by the role.

## Managed services

### Kodi

Kodi runs as a dedicated systemd service:

- unit: `kodi.service`
- user: `james`
- launcher: `/usr/bin/kodi-standalone`
- LightDM is disabled
- service restarts automatically after failure
- service start/stop enforces a single `kodi.bin` instance
- boot target remains `graphical.target`

Managed Kodi settings include:

- playback cache mode: all network filesystems
- playback cache size: 768 MiB
- read factor: 4x
- Unknown Sources: enabled
- local EventServer control: enabled on loopback only
- weather service: Open-Meteo
- movie/TV subtitle service: OpenSubtitles.com

Managed official Kodi add-ons:

- `weather.openmeteo`
- `service.subtitles.opensubtitles-com`
- `plugin.program.autocompletion`

OpenSubtitles.com requires a user account to download subtitles. Credentials are not stored in Git.

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

- user authentication required
- user: `james`
- SMB signing required
- guest access disabled
- share writable on the household LAN
- Samba credentials are supplied from protected controller environment state, not Git
- writes are forced to the `james` account so Kodi and SMB see consistent ownership

Kodi uses local filesystem paths rather than looping back through SMB.

### Time

`media-01` uses Chrony as an NTP client.

Preferred homelab sources:

1. `192.168.2.70` — primary/preferred
2. `192.168.2.71` — secondary

The Ansible role refuses to complete unless a homelab source is selected and Chrony reports a normal leap state.

### Monitoring

Prometheus node_exporter is installed and enabled on TCP/9100.

Target monitoring host:

```text
monitor-01.jameshouse
192.168.2.52
```

Still to add:

- Raspberry Pi temperature/throttling metrics
- NVMe SMART/health metrics
- Kodi service availability alerting
- Kodi log forwarding through Alloy to Loki once Loki is deployed

### Host firewall

An nftables role is defined in the media branch and is the intended host policy.

Target inbound policy:

- default deny
- SSH 22/tcp from `192.168.2.0/24`
- SMB 445/tcp from `192.168.2.0/24`
- node_exporter 9100/tcp from `192.168.2.52` only
- ICMP/ICMPv6 allowed
- DHCP renewal allowed from `192.168.2.1`
- loopback and established/related traffic allowed

The live host audit before this role was applied showed no UFW, firewalld, nftables or iptables firewall. Do not mark the firewall production gate complete until a live apply and remote port test prove the nftables policy.

## IaC paths

Primary deployment:

```text
IaC/ansible/playbooks/media-01.yml
```

Roles:

```text
IaC/ansible/roles/chrony_client/
IaC/ansible/roles/media_endpoint/
IaC/ansible/roles/media_smb/
IaC/ansible/roles/node_exporter/
IaC/ansible/roles/media_firewall/
```

Inventory:

```text
IaC/ansible/inventory/hosts.yml
```

## Controller deployment

Preferred controller:

```text
TestServer
192.168.2.220
```

Normal apply:

```bash
cd /var/tmp/media-01
git fetch origin --prune
git checkout --detach origin/feature/media-01

source "$HOME/.config/homelab-iac/media-01.env"

cd IaC/ansible
ansible-playbook playbooks/media-01.yml
```

Do not print the contents of `media-01.env`.

## Validation standard

A normal deployment is considered converged when a second run reports:

```text
changed=0
failed=0
```

Validated service gates include:

- exactly one Kodi process
- Kodi managed settings persisted
- approved official add-ons installed
- Samba configuration valid
- authenticated SMB access works
- Kodi media sources point to local media directories
- Chrony selects a homelab time source
- node_exporter is active
- zero failed systemd units

Two consecutive idempotent Ansible runs were proven before the final add-on/firewall additions. Re-run the idempotence gate after the final firewall deployment.

## Recovery

The service is intentionally rebuilt from Git rather than restored as an opaque OS image.

Recovery order:

1. install/boot supported Debian 13 on the Raspberry Pi 5;
2. restore SSH/controller access;
3. check out the reviewed media branch;
4. restore protected SMB credential environment state;
5. run `playbooks/media-01.yml`;
6. restore/copy media content into `/srv/media` if required;
7. validate Kodi, SMB, Chrony, monitoring and firewall policy;
8. run a second Ansible pass and require zero drift.

Kodi configuration that is explicitly managed by the role is reproducible. User media files are not.

## Remaining completion gates

- apply and remotely validate nftables
- verify node_exporter 9100 is reachable from `monitor-01` and blocked from ordinary LAN clients
- deploy the `media-01` target change to the live Prometheus configuration
- add Pi temperature/throttling and NVMe health metrics
- set the final Open-Meteo location in Kodi
- configure the user's OpenSubtitles.com account
- add Alloy/Loki logging when the central Loki service exists
