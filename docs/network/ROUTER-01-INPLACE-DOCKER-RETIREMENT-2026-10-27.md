<!-- estate-authority: IaC/inventory/estate.json -->
# router-01 — in-place Docker retirement evidence and dependency gates

**27 October 2026. Evidence only / no changes deployed.** Tracks [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206) and [draft PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207).

## Latest binding decisions

- **Keep existing Debian 13 OS and SSH**, no reimage. Preserve Pi4 `eth0 = 192.168.2.220/24` and ASUS `192.168.2.1` gateway until last approved network cutover. Pi4 USB `eth1` is future raw untagged PPPoE WAN.
- **Do not stop BirdNET/Komodo, remove Docker, replace the network manager or write firewall rules until an explicit impact review and approved transition.** User waives preserving BirdNET POC history. Fresh BirdNET on Pi5 `media-01` is a different later project; don't test microphone/audio during router project.
- The final identity `router-01`, conversion marker, canonical inventory and `CURRENT-STATE.md` changes must reflect VERIFIED LIVE state, not design.

## READ-ONLY live findings supplied by user (27 October 2026)

Command: `router-01-docker-retirement-readonly.yml --limit docker-01 --ask-become-pass`, **12 OK / 0 changed / 0 failed**.

| Inventory item | Current verified finding |
|---|---|
| Host / LAN | `docker-01`, Pi4, Debian13; `eth0 192.168.2.220/24`, default gateway ASUS `192.168.2.1`, DHCP |
| Future WAN adapter | `eth1` exists with **no carrier**, no IP |
| Running containers | `birdnet-go` image `ghcr.io/tphakala/birdnet-go:20260823` (healthy), `komodo-periphery-periphery-1` image `ghcr.io/moghtech/komodo-periphery:2.3.3` |
| Compose projects | `birdnet-go` at `/opt/birdnet-go/compose.yml`; `komodo-periphery` at `/etc/komodo/compose.yml` |
| Docker volume | `komodo-periphery_komodo_periphery_keys` |
| Docker networks | `bridge`, `host`, `none`, `birdnet-go_default`, `komodo-periphery_default` |
| Docker packages | `docker.io 26.1.5+dfsg1-9+deb13u1`, `docker-compose 2.26.1-4`, `containerd 1.7.24~ds1-6+deb13u1`, `runc 1.1.15+ds1-2+b4` |
| Other firewall packages | `iptables 1.8.11-2`, `nftables 1.1.3-1`; **do not purge merely because Docker is retired** |
| Running daemons | `docker.service`, `docker.socket`, `containerd.service`, `NetworkManager.service`, `ssh.service` |
| Inactive daemons | `systemd-networkd.service`, `networking.service`, `dhcpcd.service`; `birdnet-go.service` / `komodo-periphery.service` are inactive (actual containers are managed by Compose) |
| Scheduled scan | `homelab-trivy-docker.timer` currently active; must retire/replace monitoring gracefully |
| Docker bridges | `172.17.0.1/16` docker0; `172.18.0.1/16`, `172.19.0.1/16` named bridge networks |

### Consequences

1. **Docker removal takes down two actual services**, not just BirdNET. Plan Komodo host deregistration / control-plane inventory adjustment and ensure old jobs do not re-create Periphery.
2. **Container security monitoring becomes invalid if left enabled.** Stop/disable old `homelab-trivy-docker.timer` and dependent exporter/scrape entries under IaC during approved retirement. Alert thresholds and dashboards should show deliberately retired/not-applicable, never a fabricated zero findings or silent `scan_complete=1`.
3. Review BirdNET HTTPS reverse-proxy dependencies, host Alloy/Zabbix/Trivy service setup and the existing Docker-01 ICMP timestamp mitigation. Retain SSH and required firewall rules; do not blindly flush iptables/nftables.
4. **NetworkManager is active but current eth0 connection ownership/profile is not yet proven** by this audit; `networkctl` returned no active networkd information. Obtain the active NM profile and harmless IP properties before authoring live cutover automation.
5. **Existing rollback script MUST NOT run on this host.** It expects `systemd-networkd` and `/etc/systemd/network/10-router-lan.network`, neither established. Redesign final `eth0` cutover around the observed NetworkManager profile, with a local rescue console. Upstream NetworkManager supports a `nmcli device checkpoint --timeout ...` transaction that can automatically restore a device if unconfirmed (reference: https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html). Test behaviour in isolation and on the installed version before trusting it.
6. **Avoid altering `eth0` while setting up the router**. Stage PPPoE profiles and disabled Kea/Unbound/firewall via IaC while old SSH remains available; final `.3.1` IP switch requires separate explicit handover.

## NEXT safe evidence collection

Use `IaC/ansible/playbooks/router-01-inplace-dependencies-readonly.yml` via the PRODUCTION inventory on current `docker-01`. It collects:
- `NetworkManager` version and **only** eth0 active profile ID, UUID and safe IPv4 properties (never `--show-secrets`);
- `apt-get -s remove docker.io docker-compose containerd runc` **simulation only** (check exactly what would be removed);
- related systemd unit/timer names, listener port numbers, basic firewall table/chain metadata.

```bash
cd ~/projects/homelab-platform
git fetch origin
git switch feature/pi-router-iac-birdnet-poc-migration-20261027
git pull --ff-only origin feature/pi-router-iac-birdnet-poc-migration-20261027
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-inplace-dependencies-readonly.yml \
  --limit docker-01 --ask-become-pass
```

**No actual Docker removal commands are approved in this document.**

## Future approved Docker retirement (NOT YET RUN)

- Reconcile Komodo agent registration/host dependencies; preserve or explicitly retire security scanning and monitoring with updated metrics inventory/alerts and verified no unexpected consumers.
- Back up relevant system/network config and any approved rollback data off the Pi; recordings/history are not required.
- Plan separately gated Ansible removal of the specific Compose projects, disable the old scan timer, stop Docker service/socket and containerd; only then use simulation-backed package removal. Do not delete named volume or config directories without explicit per-item approval.
- Verify no new Docker bridge/firewall conflict, SSH still works at `192.168.2.220`, default route remains ASUS, and OS NetworkManager still owns the LAN.
- Update monitored estate and canonical docs when the changes are actually done. Stage disabled PPPoE/Kea/Unbound/router firewall, and cut over `eth0` as **last** action with a tested local rollback transaction.

**All items under this section are PLANNING ONLY.**
