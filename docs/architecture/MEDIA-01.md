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

Kodi also provides the host's built-in UPnP/DLNA capability. The following listeners were observed while the service was working on 17 October 2026:

```text
UDP/1900   SSDP discovery
TCP/1255   Kodi UPnP/DLNA service port (observed)
TCP/1879   Kodi UPnP/DLNA service port (observed)
```

The two TCP UPnP ports are recorded as observed runtime ports, not guaranteed permanent assignments. If Kodi is restarted and DLNA stops working, re-check Kodi's listeners before changing the firewall:

```bash
ss -lntup | grep -i kodi
```

Do not assume `1255` and `1879` will remain unchanged across every Kodi restart or upgrade.

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
| `192.168.2.0/24` | TCP/8081 | qBittorrent Web UI, HTTP rollback (still open) |
| `192.168.2.0/24` | UDP/1900 | Kodi SSDP/DLNA discovery |
| `192.168.2.0/24` | TCP/1255 | Kodi UPnP/DLNA service port observed 17 Oct 2026 |
| `192.168.2.0/24` | TCP/1879 | Kodi UPnP/DLNA service port observed 17 Oct 2026 |
| `192.168.2.70` | TCP/2049 | Proxmox NFS backup access |
| `192.168.2.71` | TCP/2049 | Proxmox NFS backup access |
| `192.168.2.52` | TCP/9100 | Prometheus node_exporter |

**19 October pending (Git-only) firewall stage:** The qBittorrent trusted HTTPS endpoint is working locally, but LAN/443 is not yet exposed. The intended first phase allows LAN/443 **and** retains LAN/8081 for rollback. After successful LAN browser login and session verification, a second, separately validated firewall-only change will disable LAN HTTP/8081. These are planned rules, not evidence of live firewall changes.

The firewall configuration is managed in:

```text
IaC/ansible/roles/media_firewall/
```

Do not add persistent firewall rules directly on the host; encode them in the Ansible role.

Because Kodi's observed UPnP TCP ports may change, validate Kodi listeners after a Kodi restart or upgrade. If the ports change, update the managed firewall deliberately rather than adding unmanaged host rules.

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

The following were confirmed after the qBittorrent installation and DLNA firewall remediation:

```text
Kodi:                 enabled / active
Kodi UPnP server:     enabled / active
Kodi SSDP:            UDP/1900
Kodi UPnP TCP:        1255 and 1879 observed
SMB:                  enabled / active
Kodi audio watchdog:  enabled / active
qBittorrent:          enabled / active
qBittorrent Web UI:   listening on TCP/8081
systemd failed units: 0
media firewall:       active, default-drop
DLNA client access:   working after UPnP TCP firewall allowance
```

**19 October 2026 pending change (Git only, not deployed):** The latest authenticated Greenbone scan flagged this Web UI's LAN HTTP listener as a Medium cleartext finding. A scoped qBittorrent HTTPS Nginx/Let's Encrypt DNS-01 implementation is staged in Git with internal name `qbittorrent.home.jrwroberts.co.uk`, and a corresponding managed Pi-hole alias is staged for both resolvers. As of the 19 October live check, media-01 had no Nginx/Certbot, trusted cert, or HTTPS listener; the Web UI still runs on `*:8081`. Managed Pi-hole DNS name has been deployed and verified on dns-01 and dns-02 (both return `192.168.2.195`), but trusted qBittorrent HTTPS now **has been deployed** and returned HTTP 200 (`media-01 ok=33 changed=9 failed=0`), but no firewall or HTTP cutover has occurred. Keep the legacy Web UI path available until HTTPS/login and rollback are tested, then change only the Web UI firewall rule.

The qBittorrent installation did not disrupt Kodi, SMB or the Kodi audio watchdog. Kodi DLNA connectivity was restored by allowing SSDP discovery and the two observed Kodi UPnP TCP service ports through the managed LAN firewall.
