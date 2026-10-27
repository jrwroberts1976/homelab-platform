<!-- estate-authority: IaC/inventory/estate.json -->
# router-01 — in-place Docker retirement evidence and dependency gates

**27 October 2026. Evidence only / no changes deployed.** Tracks [issue #206](https://github.com/jrwroberts1976/homelab-platform/issues/206) and [draft PR #207](https://github.com/jrwroberts1976/homelab-platform/pull/207).

## SECOND live read-only audit — COMPLETE (27 October 2026)

User ran `router-01-inplace-dependencies-readonly.yml` on active `docker-01` using production inventory: **8 OK, 0 changed, 0 failed, 0 unreachable**. No packages removed; `apt-get` was simulated.

| Evidence | Verified result | Consequence |
|---|---|---|
| NetworkManager | `nmcli 1.52.1`; **eth0 connected** via `netplan-eth0`, UUID `75a1216a-9d1a-30cd-8aca-ace5526ec021` | Retain NetworkManager. No systemd-networkd migration |
| Active profile | autoconnect `yes`, `ipv4.method auto`, no static address/gateway in profile, `ipv4.never-default no` | Preserve DHCP/ASUS gateway at `192.168.2.220` until last-stage change |
| Docker apt simulation | `apt-get -s remove docker.io docker-compose containerd runc` returned **RC 0** and exactly 4 removals | In-place Debian OS package removal is feasible; **simulation is not real uninstall/rollback evidence** |
| Autoremove suggestions | `criu docker-buildx docker-cli libcompel1 libnet1 libprotobuf-c1 python3-protobuf python3-pycriu tini` | **DO NOT RUN APT AUTOREMOVE** as part of first retirement. Evaluate separately |
| Container monitoring | `homelab-trivy-docker.timer` enabled and scheduled; `alloy`, Alloy heartbeat/health timers, `zabbix-agent2` enabled | Retire Docker-specific scan and exporter safely; preserve Alloy/Zabbix and avoid false-green metrics |
| Legacy timestamp mitigation | `homelab-docker01-icmp-timestamp.service` enabled | Rework/rename firewall mitigation at a separate reviewed stage, do not blindly flush rules |
| Nginx | `nginx.service` active; TCP 80/443 listening; BirdNET proxy backend `127.0.0.1:8080` also listening | Audit Nginx site configuration before removing BirdNET; do not remove whole Nginx without checking other dependencies |
| Other services | `ssh.service`, local `127.0.0.1:12345`, TCP 10050, 9100, RPC 111, 5353 and other sockets | SSH and monitoring must remain reachable; identify unrecognised listeners before teardown |
| Live firewall | `iptables` filter **INPUT ACCEPT**, **FORWARD DROP**; Docker/DOCKER-USER/ISOLATION chains; nat DOCKER; `nft` tables `ip filter` and `ip nat` | Docker owns current bridge NAT/forwarding chains; **never flush whole nftables/iptables ruleset while containers remain** |

**Network management implications:** `netplan-eth0` strongly indicates Netplan generates/owns the persistent NetworkManager profile; confirm the actual `/etc/netplan/*.yaml` files and renderer using a **read-only, non-secret** inspection before authoring a new `eth0` configuration. Netplan settings are intended to persist and can regenerate NetworkManager profiles; changes to a generated profile may not survive reboot as expected. Refer to the [Debian Netplan documentation](https://wiki.debian.org/Netplan) and [NetworkManager checkpoint manual](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html). A checkpoint with a timeout is a useful *candidate* for an approved, console-supervised network change but **has not been tested here**. Keep the original `192.168.2.220` and ASUS route unchanged.

**Docker removal dependencies now confirmed:** BirdNET Compose at `/opt/birdnet-go/compose.yml`, Komodo Periphery Compose at `/etc/komodo/compose.yml`, Komodo volume containing agent keys, Trivy scheduled container scan, Alloy/Prometheus exporters, Zabbix, Nginx reverse proxy and the host ICMP timestamp mitigation. We need a source-controlled retirement plan for each before a single service is stopped. Docker `containerd` and `runc` are removable based on the simulated apt transaction, but keep `iptables` and `nftables` for router functions.

**Current status: evidence complete for phase-two audit; still NO LIVE CHANGE AUTHORIZED.**

## THIRD production read-only audit COMPLETE — Netplan, Nginx, Trivy, Komodo volume

User ran `router-01-retirement-config-readonly.yml --limit docker-01 --ask-become-pass` on **27 October 2026**, reporting **7 OK, 0 changed, 0 failed**. This was an observation only; no Docker or OS changes.

| Verified object | Observation | Next safe action |
|---|---|---|
| Persistent eth0 configuration | `/etc/netplan/90-NM-75a1216a-9d1a-30cd-8aca-ace5526ec021.yaml` declares `eth0`, `renderer: NetworkManager`, `dhcp4: true`, zero static addresses and routes | **Preserve file and NetworkManager** while `192.168.2.220` remains the SSH address; never install networkd config for eth0 |
| Other Netplan file | `90-NM-9ce9ccfd-823b-3512-8ce3-e18405b63bbf.yaml` exists but no eth0 stanza was reported | **Leave untouched**; ownership/purpose not determined |
| Nginx site | Exactly one reported enabled symlink: `/etc/nginx/sites-enabled/birdnet-go.conf`, marked BirdNET and upstream `127.0.0.1:8080` | After BirdNET retirement, safely disable **only** this symlink and validate/reload Nginx; preserve TLS cert/key and all other Nginx data |
| Docker Trivy textfile | `/var/lib/prometheus/node-exporter/homelab_container_estate.prom` **present** | At retirement, stop timer and any active scan, remove only this now-inapplicable textfile, preserve other node-exporter metrics |
| Komodo authentication volume | `komodo-periphery_komodo_periphery_keys` **present** | Preserve keys/volume; separately deregister/disable this server in Komodo Core before stopping Periphery |

The user has explicitly **approved BirdNET-Go and Komodo Periphery downtime**. That establishes service-outage intent only, not the other four prerequisites. Existing default-deny Ansible removal play is **NOT approved for execution yet**; Komodo Core resource/deployment link audit, metrics/dashboard lifecycle and backups/console validation remain unverified.

**Do not confuse service retirement with IP cutover.** The Pi must keep its existing Netplan-managed `eth0` connection and `192.168.2.220` SSH. Actual WAN handover and `192.168.3.1` are later operations. The legacy systemd-networkd rollback remains hard-disabled.

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
4. **The second audit confirmed eth0 is attached to NetworkManager's `netplan-eth0` DHCP profile**, but the persistence source under `/etc/netplan` still needs a read-only inspection. Do not treat the live NM profile as a replacement for Netplan's persistent configuration.
5. **Existing rollback script MUST NOT run on this host.** It expects `systemd-networkd` and `/etc/systemd/network/10-router-lan.network`, neither established. Redesign final `eth0` cutover around the observed NetworkManager profile, with a local rescue console. Upstream NetworkManager supports a `nmcli device checkpoint --timeout ...` transaction that can automatically restore a device if unconfirmed (reference: https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html). Test behaviour in isolation and on the installed version before trusting it.
6. **Avoid altering `eth0` while setting up the router**. Stage PPPoE profiles and disabled Kea/Unbound/firewall via IaC while old SSH remains available; final `.3.1` IP switch requires separate explicit handover.

## Previously completed second evidence collection

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

## Approved service outage and final read-only configuration check

**User approved taking BOTH BirdNET-Go and Komodo Periphery offline** when Docker retirement is performed; their historical BirdNET data need not be migrated. **This is not authorisation to begin an uncontrolled or incomplete decommission.** All production services remain running until verified Komodo deregistration, metrics/alerts retirement, backup/console proof and a controlled execution window. The Docker-retirement Ansible playbook's five preflight gates remain default false.

We identified that `container-vulnerability-docker-enable.yml` will currently enable the daily Trivy timer; `publish-estate-metrics.py` writes `/var/lib/prometheus/node-exporter/homelab_container_estate.prom`. A stopped scan timer alone will leave stale last-success metrics, so the retirement must also remove/retire the **Docker-specific textfile**, update central scan target dashboards/alerts and ensure playbook invocations cannot reinstall or re-enable the retired Docker workloads. Preserve other host node-exporter, Alloy, Zabbix and external container-scanning coverage. No fabricated "zero critical" scores.

Komodo Periphery is provisioned by `roles/komodo_periphery` and `IaC/komodo/resources/docker-01.toml`; verify `docker-01` is deregistered or explicitly disabled in running Komodo Core, and any auto-reconcile/stack deployment is disabled **before** Docker stops. Preserve the `komodo-periphery_komodo_periphery_keys` named volume; it contains authentication material.

**New safe preflight:** `IaC/ansible/playbooks/router-01-retirement-config-readonly.yml` inspects only non-secret Netplan `eth0` metadata, enabled Nginx config basenames with *boolean* BirdNET/backend markers, presence (not contents) of the old Trivy Prometheus textfile, and Komodo key volume existence. It does not show raw Netplan/Nginx config or credentials and makes no changes.

After checking that the new playbook passed CI, run from `admin-01` on the draft branch:

```bash
cd ~/projects/homelab-platform
git fetch origin
git switch feature/pi-router-iac-birdnet-poc-migration-20261027
git pull --ff-only origin feature/pi-router-iac-birdnet-poc-migration-20261027
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/router-01-retirement-config-readonly.yml \
  --limit docker-01 --ask-become-pass
```

**Read-only only**; do not run the disruptive `router-01-docker-retirement-approved.yml` yet. Keep SSH at `192.168.2.220` and ASUS gateway unchanged.

## Controlled Docker-retirement Ansible authored — DEFAULT DENY (not executed)

New source-only playbook: `IaC/ansible/playbooks/router-01-docker-retirement-approved.yml`. **This has NOT been run on `docker-01`** and WILL stop two production Docker workloads if activated. It is not safe simply because its syntax passes CI. No approval flags are set by default.

**Five approvals required on the Ansible controller before ANY SSH:**
1. `router_docker_retirement_approved=true`: the service interruption to BirdNET and Komodo is authorised.
2. `router_komodo_deregistration_verified=true`: the Komodo managed-host registration and automations/redeployment dependencies were deliberately retired or updated.
3. `router_trivy_monitoring_reconciled=true`: Trivy Docker scheduled scan, stale container metrics and central exporter/Grafana/Zabbix alerts have an approved, documented retired-state transition (never fabricate clean scan data).
4. `router_retirement_backup_verified=true`: host network config, Komodo onboarding key, needed Docker settings and off-Pi rescue/recovery are preserved as appropriate; BirdNET POC history is intentionally waived.
5. `router_retirement_console_ready=true`: an operator can restore the Pi through direct console if an unexpected outage occurs.

**On-host preflight before any service is stopped:** the active host is still Debian 13 `docker-01` at `192.168.2.220`, ASUS default route `.2.1`, active NetworkManager profile `netplan-eth0`; exactly two running containers named `birdnet-go` and `komodo-periphery-periphery-1`; the two expected Compose files exist; and a **fresh** apt simulation removes *exactly* four runtime packages.

**If fully approved at a later maintenance window**, the playbook would disable the Docker-specific Trivy timer, use Compose `down` on the exact BirdNET and Komodo YAML files without `--volumes`, stop/disable docker.socket/docker.service/containerd, and remove only `docker.io docker-compose containerd runc` with `purge: false`, `autoremove: false`. It then checks that `192.168.2.220`, the `netplan-eth0` profile, ASUS default route and core NetworkManager/SSH/Alloy/Zabbix/Nginx units remain active. No Docker data directories, named volumes or Komodo keys are deleted; no router software starts; no interface/IP, hostname, PPPoE, nftables, Nginx config or live inventory changes. BirdNET HTTPS would be unavailable after container shutdown until its old Nginx site is independently retired.

**Known follow-ups even after execution:** remove/replace the BirdNET-only Nginx site after verifying what serves 80/443, reconcile the old `homelab-docker01-icmp-timestamp` mitigation with new router firewall owner, update central monitoring/Komodo and canonical inventory ONLY after actual live verification, and separately approve `router-01` hostname change. The final LAN .3.1 cutover remains last and requires a tested NM-native rollback.

**WARNING:** Do NOT pass the five approval flags based solely on having read this plan. They are declarations that the prerequisite actions are already VERIFIED, not a way to skip work. No execution command is furnished until those prerequisites are complete.

## Future approved Docker retirement (NOT YET RUN)

- Reconcile Komodo agent registration/host dependencies; preserve or explicitly retire security scanning and monitoring with updated metrics inventory/alerts and verified no unexpected consumers.
- Back up relevant system/network config and any approved rollback data off the Pi; recordings/history are not required.
- Plan separately gated Ansible removal of the specific Compose projects, disable the old scan timer, stop Docker service/socket and containerd; only then use simulation-backed package removal. Do not delete named volume or config directories without explicit per-item approval.
- Verify no new Docker bridge/firewall conflict, SSH still works at `192.168.2.220`, default route remains ASUS, and OS NetworkManager still owns the LAN.
- Update monitored estate and canonical docs when the changes are actually done. Stage disabled PPPoE/Kea/Unbound/router firewall, and cut over `eth0` as **last** action with a tested local rollback transaction.

**All items under this section are PLANNING ONLY.**
