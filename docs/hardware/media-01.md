# media-01 Current-State Audit

**Original audit:** 6 September 2026
**Current-state refresh:** 10 September 2026
**Hostname:** `media-01`
**Address:** `192.168.2.195`
**Hardware:** Raspberry Pi 5 Model B Rev 1.0
**Current role:** dedicated Kodi/media endpoint
**Lifecycle:** operational

The earlier role-neutral audit is now superseded by an approved production role. `media-01` is a **physical Raspberry Pi 5**, not a Proxmox guest and not a k3s node.

## Identity

| Item | Current / audited state |
|---|---|
| Hardware | Raspberry Pi 5 Model B Rev 1.0 |
| OS | Debian GNU/Linux 13 (trixie) |
| Architecture | arm64 / aarch64 |
| CPU | ARM Cortex-A76, 4 cores |
| RAM | approximately 7.9 GiB |
| Address | `192.168.2.195/24` |
| Ethernet | 1 Gb/s |
| Normal controller | `admin-01` / `192.168.2.48` |

The historical `k3s-node-01.jameshouse` identity was stale. Current documentation and management must use `media-01`.

## Storage

### Boot/system device

- SanDisk USB 3.2 Gen1, approximately 28.7 GiB.
- Root filesystem approximately 28 GiB.
- SMART-style health could not be read through the USB bridge during the original audit; treat device health as unknown unless separately validated.

### NVMe

- WD PC SN740 512 GB class NVMe.
- Approximately 476.9 GiB usable device capacity.
- Original SMART audit: PASSED, 1% used, zero media/data-integrity errors, approximately 41 C.

The NVMe historically also contained backup-replica/old-k3s data. Historical data should be classified before any future storage repurpose, but it does not change the current media role.

## Production media role

`media-01` is retained as the dedicated Raspberry Pi 5 Kodi endpoint.

Current IaC/service intent includes:

- Kodi as the primary application;
- SMB media access;
- Chrony using the homelab time servers;
- node exporter / standard host monitoring;
- firewall configuration appropriate to the media endpoint;
- configuration through Ansible rather than preserving ad-hoc desktop state.

Relevant IaC:

```text
IaC/ansible/playbooks/media-01-preflight.yml
IaC/ansible/playbooks/media-01.yml
IaC/ansible/roles/media_endpoint/
IaC/ansible/roles/media_smb/
IaC/ansible/roles/media_firewall/
```

## Network and dependencies

```text
media-01          192.168.2.195
Gateway           192.168.2.1
DNS               192.168.2.51, 192.168.2.50
NTP preferred     192.168.2.70
NTP secondary     192.168.2.71
Admin controller  192.168.2.48 (admin-01)
```

`media-01` should not become a general-purpose Docker or k3s host merely because historical storage contains old k3s data.

## Monitoring

The expected baseline is host reachability and node metrics from `monitor-01`. Add media-specific alerts only when actionable; do not create noisy playback/content alerts by default.

## Recovery direction

A rebuild should be possible from:

1. clean supported Raspberry Pi OS/Debian base;
2. authoritative Ansible inventory/playbooks/roles;
3. media/share credentials supplied outside Git;
4. required local media configuration/data restored separately where it is not reproducible.

The Pi 5 hardware role is approved; a future rebuild should restore `media-01`, not recreate the stale `k3s-node-01` identity.

## Historical audit evidence

Original audit artifact:

```text
/var/tmp/media-01-audit-20260906T073637Z.txt
```

SHA256:

```text
a8e00978294a31b1aeb066a654f2880ae96234ecbfe0663eff7a6e8f311a82d8
```

Historical hardware audit: **COMPLETE**
Current production role: **OPERATIONAL**
