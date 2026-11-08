# BirdNET-Go on media-01 — native IaC deployment

Status: STAGING ONLY; no native installation has been performed.

Target: Debian 13 ARM64 Raspberry Pi 5 `media-01`; Kodi remains in service and the host is a Proxmox NFS backup target.

Use `feature/media01-birdnet-native-20261108` in a dedicated worktree on `admin-01`. Do not run the legacy `birdnet-01.yml` playbook (Docker-centric and configured for retired `docker-01`). Do not run `media-01.yml` for this change because it can reconcile/restart Kodi.

## Completed operator checks

- ALSA USB PnP audio device `plughw:CARD=Device,DEV=0` recorded 5 seconds of 48 kHz mono audio.
- Port 8080 free, Kodi active, Debian 13 ARM64, 158 GB free.
- `media-01-birdnet-preflight.yml`: syntax passed; recap `ok=10 changed=0 failed=0 unreachable=0`.

## Release staging

```bash
cd ~/projects/homelab-birdnet/IaC/ansible
ansible-playbook --syntax-check playbooks/media-01-birdnet-stage.yml
ansible-playbook playbooks/media-01-birdnet-stage.yml
```

This scoped playbook fetches the 20261031 release archive and checksums from upstream, requires a single valid SHA256 entry, validates the archive checksum, lists entries and checks that Kodi remains active. It does **not** extract, install, enable a service, open a firewall port or touch existing BirdNET detection history.

## Remaining acceptance gates

- Review actual archive file layout, including whether packaged audio/model libraries require additional runtime dependencies.
- Design native user, state directories, systemd unit and port binding for LAN-only operation. Require native microphone source identity verification.
- Confirm previous BirdNET-Go history and configuration migration policy.
- Implement Ansible-managed native installation and rollback, with check-mode/syntax checks and no Kodi or NFS ownership changes.
- Validate app health, live audio processing and playback coexistence with Kodi before considering migration complete.

## Native installation (ready for operator execution; unverified live)

The scoped `playbooks/media-01-birdnet-install.yml` uses `media_birdnet_native`, not the old Docker role. It unpacks the already SHA256-verified 20261031 native archive into `/opt/birdnet-go/releases/20261031`, uses `LD_LIBRARY_PATH` for its two bundled libraries, and creates a dedicated `birdnet` system account in the `audio` group. Persistent configuration and history are under `/var/lib/birdnet-go`. The installed systemd unit starts `birdnet-go serve --config /var/lib/birdnet-go/config.yaml` and retains the existing 0c76:161e USB source identifier as a *candidate*; verify actual live audio enumeration rather than assuming it is correct for native runtime.

```bash
cd ~/projects/homelab-birdnet && git pull --ff-only
cd IaC/ansible
ansible-playbook --syntax-check playbooks/media-01-birdnet-install.yml
ansible-playbook playbooks/media-01-birdnet-install.yml
```

No Kodi, NFS or nftables role is invoked. The media firewall is default-drop and this change does **not** open TCP/8080, so web UI may only work on media-01 itself until a separate scoped firewall change. To inspect a failed startup read-only: `ssh media-01 'sudo systemctl status birdnet-go --no-pager; sudo journalctl -u birdnet-go -n 60 --no-pager'`. Preserve output for diagnosis. Stop only BirdNET with `sudo systemctl stop birdnet-go` as immediate isolation if Kodi playback degrades; reconcile any service state change back into the IaC decision. No old BirdNET data has been migrated; old host recovery remains a distinct check.

Before closing: verify service HTTP, BirdNET audio levels and detections, available model assets, Kodi video/audio playback, storage and host temperature. Do not advertise a LAN URL until firewall access is intentionally updated and validated.
