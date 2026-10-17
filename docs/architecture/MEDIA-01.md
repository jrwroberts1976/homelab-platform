# media-01 Current Service State

**Status:** ACTIVE  
**Last validated:** 17 October 2026  
**Address:** `192.168.2.195`  
**Platform:** Raspberry Pi 5 / Debian  
**Configuration authority:** `IaC/ansible/`

This document records the current operational role and services on `media-01`. Where this document conflicts with validated live state, validated live state takes precedence.

## Current roles

`media-01` provides the following functions:

- Kodi media playback endpoint.
- Kodi built-in UPnP/DLNA media serving and discovery on the LAN.
- SMB media/file sharing on the LAN.
- Primary NFS backup target for the two Proxmox hypervisors.
- qBittorrent headless BitTorrent client with Web UI.
- Kodi audio watchdog timer.

## Network identity

```text
Hostname: media-01
IPv4:    192.168.2.195
LAN:     192.168.2.0/24
```

## Kodi

Kodi runs as a systemd-managed standalone process.

Validated live state on 17 October 2026:

```text
kodi.service: enabled
kodi.service: active
process: /usr/lib/aarch64-linux-gnu/kodi/kodi.bin --standalone
```

Kodi also provides the host's built-in UPnP/DLNA capability.

Validated UPnP/DLNA listeners on 17 October 2026:

- UDP/1900 — SSDP discovery
- TCP/1255 — Kodi UPnP service
- TCP/1879 — Kodi UPnP service

The managed nftables policy permits these ports from the LAN. TCP/1255 and TCP/1879 are observed runtime ports and may change after a Kodi restart or upgrade. If DLNA stops working after a restart, re-check them with `ss -lntup | grep -i kodi`.

## Kodi audio watchdog

The Kodi audio watchdog remains enabled and active:

```text
kodi-audio-watchdog.timer: enabled
kodi-audio-watchdog.timer: active
```

The watchdog exists to recover Kodi audio when the audio path becomes unhealthy without requiring manual intervention.

## SMB

Samba remains enabled and active and is bound to the media host's LAN address.

Validated listener:

```text
192.168.2.195:445/tcp
```

The managed firewall permits TCP port `445` from `192.168.2.0/24` only.

## Proxmox backup NFS

`media-01` is the primary Proxmox NFS backup target. NFS access is restricted by the managed firewall to the two Proxmox hosts only:

```text
PROXMOX    192.168.2.70 -> TCP/2049
Proxmox-2  192.168.2.71 -> TCP/2049
```

The firewall does not permit general LAN access to the NFS service.

## qBittorrent

qBittorrent was installed on 17 October 2026 using the Ansible `qbittorrent` role.

Service implementation:

```text
package:       qbittorrent-nox
service:       qbittorrent.service
service user:  qbittorrent
service group: qbittorrent
Web UI port:   8081/tcp
```

Validated live state:

```text
qbittorrent.service: enabled
qbittorrent.service: active
listener: *:8081
```

The qBittorrent Web UI is LAN-only through the managed nftables policy:

```text
http://192.168.2.195:8081/
```

Download directories are managed as:

```text
/srv/downloads/complete
/srv/downloads/incomplete
```

The initial qBittorrent Web UI administrator password is temporary until a permanent password is configured in qBittorrent. Credentials must not be stored in this repository.

## Firewall

`media-01` uses the Ansible-managed `media_firewall` role and nftables table `inet media_filter`. The input policy is default-deny.

Current explicitly authorised inbound services include:

| Source | Protocol/port | Purpose |
|---|---|---|
| `192.168.2.0/24` | TCP/22 | SSH administration |
| `192.168.2.0/24` | TCP/445 | SMB |
| `192.168.2.0/24` | TCP/8081 | qBittorrent Web UI |
| `192.168.2.0/24` | UDP/1900 | Kodi SSDP/DLNA discovery |
| `192.168.2.0/24` | TCP/1255 | Kodi UPnP service — observed runtime port |
| `192.168.2.0/24` | TCP/1879 | Kodi UPnP service — observed runtime port |
| `192.168.2.70` | TCP/2049 | Proxmox NFS backup access |
| `192.168.2.71` | TCP/2049 | Proxmox NFS backup access |
| `192.168.2.52` | TCP/9100 | Prometheus node_exporter |

The firewall configuration is managed in:

```text
IaC/ansible/roles/media_firewall/
```

Do not add persistent firewall rules directly on the host; encode them in the Ansible role.

## Ansible management

qBittorrent is managed by:

```text
IaC/ansible/roles/qbittorrent/
IaC/ansible/playbooks/qbittorrent.yml
```

The media host firewall is managed by:

```text
IaC/ansible/roles/media_firewall/
```

When only the media firewall needs reconciliation, use a firewall-only play rather than the complete media playbook if the unrelated SMB credential environment is not available.

The full media playbook requires the `MEDIA_SMB_PASSWORD` controller environment variable for the `media_smb` role.

## Validation snapshot — 17 October 2026

The following were confirmed after the qBittorrent installation:

```text
Kodi:                 enabled / active
SMB:                  enabled / active
Kodi audio watchdog:  enabled / active
qBittorrent:          enabled / active
qBittorrent Web UI:   listening on TCP/8081
systemd failed units: 0
media firewall:       active, default-drop
```

The qBittorrent installation did not disrupt Kodi, SMB or the Kodi audio watchdog.
