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

## LAN access (Ansible-managed, operator execution pending)

The existing `media_firewall` role now allows TCP/8080 from `192.168.2.0/24` only, guarded by `media_firewall_birdnet_lan_enabled: true`. Other rules (SSH, HTTPS qBittorrent, SMB, restricted NFS, monitoring, and existing Kodi discovery) are retained. Use **only** the scoped `media-01-birdnet-lan.yml` playbook, not `media-01.yml` (which also runs a Kodi endpoint role). The scoped playbook verifies BirdNET locally before changing firewall, checks full active nftables policy afterward, checks LAN HTTP from the controller, and checks service/NFS listener.

```bash
cd ~/projects/homelab-birdnet && git pull --ff-only
cd IaC/ansible
ansible-playbook --syntax-check playbooks/media-01-birdnet-lan.yml
ansible-playbook playbooks/media-01-birdnet-lan.yml
```

Dashboard address after successful LAN check: http://192.168.2.195:8080/. Roll back just this allow rule with `ansible-playbook playbooks/media-01-birdnet-lan.yml -e media_firewall_birdnet_lan_enabled=false`; the scoped playbook skips the positive LAN HTTP test for this rollback setting. For permanent rollback, also revert the enabled default in Git and re-apply through Ansible.

**New host direction (operator decision):** media-01 is to be a media-serving/Docker host instead of a Kodi playback endpoint; do not change or remove existing Kodi until the new media server and client workflows are chosen and validated. Existing Docker installation and forwarding functionality are NOT verified. Current nftables rules contain a `flush ruleset` and a forward-chain drop policy; Docker's bridge/NAT rules need dedicated review before any Docker workload cutover, not an ad hoc change in this BirdNET firewall PR. Preserve Proxmox NFS storage.

## Internal DNS alias and trusted HTTPS (planned; operator must deploy)

Desired browser URL: `https://birds.home.jrwroberts.co.uk/`. The existing managed local A record for `media-01` at `192.168.2.195` is extended with `birds.home.jrwroberts.co.uk` on **both** Pi-hole resolvers (`dns-01` and `dns-02`), preserving the existing qBittorrent record. Cloudflare DNS-01 is used only to issue/renew the Let's Encrypt certificate using the pre-existing protected controller credentials; the DNS alias itself is local, not an externally exposed A record.

Use a separate scoped DNS apply **first**:

```bash
cd ~/projects/homelab-birdnet && git pull --ff-only
cd IaC/ansible
ansible-playbook --syntax-check playbooks/dns-local-records.yml
ansible-playbook playbooks/dns-local-records.yml
for dns in 192.168.2.50 192.168.2.51; do dig @"$dns" birds.home.jrwroberts.co.uk A +short; done
```

Both DNS answers must be `192.168.2.195`. Only then apply scoped certificate/proxy configuration:

```bash
ansible-playbook --syntax-check playbooks/media-01-birds-https.yml
ansible-playbook playbooks/media-01-birds-https.yml
```

The HTTPS playbook reuses the `homelab_certificate` Certbot/Cloudflare role, creates a **separate** `birds.conf` Nginx virtual host on TCP 443, and proxies requests/websockets to native BirdNET-Go on localhost:8080. It does not alter the working qBittorrent Nginx virtual host or open a new firewall port; TCP/443 is already permitted from the LAN. No Kodi, NFS, Docker, BirdNET systemd or media firewall role executes. This does not itself restrict the existing direct `http://192.168.2.195:8080/` LAN connection, which can be retired through a separate reviewed firewall change after HTTPS is confirmed from a browser. Do not call DNS/certificate/HTTPS live until both Ansible runs have succeeded.

## HTTPS-only LAN cutover — staged, not yet applied

After the operator confirmed `https://birds.home.jrwroberts.co.uk/` works in their browser, the `media_firewall_birdnet_lan_enabled` default was changed to `false` in Git. The existing scoped `playbooks/media-01-birdnet-lan.yml` now checks trusted HTTPS from the controller **before and after** applying the firewall and checks that TCP/8080 is unreachable from the controller afterward. Loopback TCP/8080 remains available to Nginx; TCP/443 remains LAN-accessible and Proxmox NFS is preserved. This removes only the temporary direct LAN HTTP rule, without restarting BirdNET-Go, Kodi, qBittorrent or Docker.

```bash
cd ~/projects/homelab-birdnet && git pull --ff-only
cd IaC/ansible
ansible-playbook --syntax-check playbooks/media-01-birdnet-lan.yml
ansible-playbook playbooks/media-01-birdnet-lan.yml
```

Rollback for direct HTTP access, if required and approved: `ansible-playbook playbooks/media-01-birdnet-lan.yml -e media_firewall_birdnet_lan_enabled=true`, then return to Git to reconcile the variable with intended policy. Do not use the broad `media-01.yml` playbook.
