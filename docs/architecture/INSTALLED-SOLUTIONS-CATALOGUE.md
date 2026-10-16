<!-- estate-authority: IaC/inventory/estate.json -->
# Installed Solutions Catalogue

**Purpose:** Human-readable catalogue of the major solutions currently used by the homelab, what they do, where they run and which ports matter operationally.  
**Current-state authority:** `IaC/inventory/estate.json` and `docs/architecture/CURRENT-STATE.md`  
**Reviewed:** 16 October 2026

This page lists **currently installed/operational** solutions. Planned, deferred or retired products are called out separately and must not be inferred as deployed.

## Port-scope rule

Port information below is descriptive, not a firewall allow-list.

- **LAN/VPN** — intended for trusted administration/service clients.
- **internal** — service-to-service only; not intentionally LAN-published.
- **loopback** — localhost only.
- **passive** — observes mirrored traffic rather than exposing a normal application listener.
- **external** — hosted outside the homelab.

## Estate overview

| Solution | Purpose | Runs on / address | Main port(s) / scope |
|---|---|---|---|
| Proxmox VE | VM/LXC virtualisation and cluster management | `PROXMOX .70`, `Proxmox-2 .71` | 8006/TCP trusted HTTPS LAN/VPN; 22/TCP SSH |
| Corosync / Kronosnet | Cluster membership/messaging | both PVE nodes | dedicated cluster links |
| QDevice / QNetd | Third quorum vote | `admin-01 .48` | 5403/TCP |
| Chrony | LAN NTP service | `.70`, `.71` | 123/UDP |
| Pi-hole | DNS filtering/local DNS + trusted web UI | `dns-01 .51`, `dns-02 .50` | 53/TCP+UDP; 443/TCP LAN/VPN |
| Unbound | Recursive DNS behind Pi-hole | both DNS LXCs | 127.0.0.1:5335 |
| ASUS RT-AC86U | Router/DHCP/AiMesh/OpenVPN | `.1` | LAN admin; OpenVPN UDP transport |
| HP ProCurve 2510G-24 | Core switch / SPAN | `.16` | legacy LAN management; mirror ports 1–23 -> 24 |
| OpenVPN | Remote administration | ASUS router | router-controlled UDP listener |
| Prometheus | Metrics | `monitor-01 .52` | 9090/TCP LAN/VPN |
| Grafana | Dashboards | `monitor-01 .52` | 443/TCP trusted HTTPS; 3000/TCP loopback only |
| Alertmanager | Alert routing | `monitor-01 .52` | 9093/TCP LAN/VPN |
| Blackbox Exporter | Reachability/service probes | `monitor-01 .52` | 9115/TCP |
| Loki | Central log store | `monitor-01 .52` | 3100/TCP |
| Grafana Alloy | Log/telemetry forwarding | managed estate | 12345/TCP local/API where enabled |
| Node Exporter | Linux host metrics | 15 managed Linux hosts | 9100/TCP |
| Zabbix | Agent-oriented monitoring | `zabbix-01 .59` | 443/TCP trusted HTTPS; 10051/TCP server |
| Zabbix Agent 2 | Host telemetry | 15 managed Linux hosts | 10050/TCP passive where used; active to `.59:10051` |
| Network Host discovery | LAN inventory/enrichment/OS evidence/first-seen | **`monitor-01 .52`** | no user-facing listener |
| Suricata | IDS/signature detection | `sensor-01 .55` | passive capture |
| Zeek | Network metadata/behaviour analysis | `sensor-01 .55` | passive capture |
| Greenbone Community | Vulnerability scanning | `greenbone-01 .57` | 443/TCP trusted HTTPS LAN/VPN |
| Komodo Core | Container-management control plane | `komodo-01 .58` | 9120/TCP trusted HTTPS LAN/VPN |
| Komodo Periphery | Managed Docker-host agent | explicitly commissioned Docker hosts | outbound certificate-validated WSS |
| Docker | Application container runtime | selected application hosts | daemon not LAN-published |
| MongoDB | Komodo database | internal `komodo-01` stack | 27017/TCP internal |
| Nextcloud | Private cloud application | `cloud-01 .53` | 8080/TCP LAN/VPN |
| PostgreSQL | Application database | `cloud-01`, `zabbix-01` | 5432/TCP internal/local |
| Redis | Nextcloud cache/locking | `cloud-01` | 6379/TCP internal |
| Home Assistant OS/Core | Home automation | `home-01 .60` | 80/TCP LAN/VPN |
| BirdNET-Go | Bird-call identification | `docker-01 .220` | 8080/TCP LAN/VPN |
| Postfix | Internal SMTP relay | `mail-relay-01 .54` | 25/TCP LAN; outbound 587/TCP TLS |
| NFS | Proxmox guest-backup storage | `media-01 .195` | 2049/TCP |
| Samba / SMB | Media sharing | `media-01 .195` | 445/TCP |
| Kodi | Local media endpoint | `media-01 .195` | local application |
| Certbot + Let's Encrypt | Trusted certificate issuance/renewal using Cloudflare DNS validation | dns-01, dns-02, greenbone-01, monitor-01, zabbix-01, both PVE nodes | automated renewal; service-specific deploy hooks |
| Ansible + Git | Reviewed, repeatable configuration and infrastructure change from `admin-01` | controller + GitHub | SSH/HTTPS as required |
| GitHub Actions | CI validation | GitHub-hosted | external HTTPS |
| Cloudflare Pages | Public portfolio hosting | external | HTTPS/443 |

## Virtualisation and cluster

The two physical nodes form `jameshouse-pve`. Corosync uses the preferred direct `10.255.255.0/30` link and management-LAN fallback. `admin-01` supplies QNetd/QDevice. Guest disks remain node-local; the cluster does not provide automatic guest-data HA.

Both nodes completed the 16 October patch session at pve-manager 9.2.21 with running kernel `7.0.14-24-pve`, no pending packages, no reboot requirement and healthy quorum. The unused Ceph enterprise repository is disabled through IaC.

A GDS kernel mitigation is active but its GRUB/kernel-parameter configuration still needs to be encoded in IaC.

## DNS

Pi-hole provides filtering/local DNS while Unbound performs recursive resolution on localhost port 5335. The approved resolver pair is `dns-01 .51` and `dns-02 .50`; `admin-01 .48` is not a resolver.

Both Pi-hole web interfaces use trusted Let's Encrypt HTTPS and renewal hooks rebuild the Pi-hole combined PEM before restarting FTL.

## Monitoring, logging and dashboards

`monitor-01` provides Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki. Alloy forwards logs/telemetry according to inventory/role scope. The production Grafana foundation includes operations, host, patch/reboot, network-host and accepted-risk detail views.

Grafana is exposed through nginx at `https://grafana.home.jrwroberts.co.uk/`; the Docker port is bound only to `127.0.0.1:3000`.

Zabbix administration uses `https://zabbix.home.jrwroberts.co.uk/`. The final post-remediation Greenbone scan is pending to confirm the prior cleartext-management finding has disappeared from scanner evidence.

## Network Host discovery

The active Network Host discovery platform is on `monitor-01`, following the verified single-owner cutover on 27 September 2026. `Proxmox-2` is the former source; its source timers remain disabled/inactive.

## Security platforms

### Suricata / Zeek

`sensor-01` consumes the dedicated SPAN capture path. Suricata provides signature/detection logic; Zeek provides protocol/connection metadata and behavioural context.

### Greenbone

`greenbone-01` performs active vulnerability scanning. Managed scan evidence feeds the management-report path on `monitor-01`; accepted risks are separated from actionable findings and accepted-risk details are exported to Grafana.

The final 16 October post-hardening scan is currently running/pending completion.

### Raspberry Pi TF-A hardening

`docker-01` uses a validated Trusted Firmware-A v2.15.0 release artifact for Cortex-A72 speculative-execution mitigation. The artifact, SHA-256, licence, provenance and boot configuration are managed by `raspberry_pi_tfa_hardening`; repeat reconciliation is idempotent.

### CrowdSec

**Not deployed.** CrowdSec is not a current production signal source.

## Trusted HTTPS / certificate lifecycle

Trusted Let's Encrypt certificate renewal has been dry-run validated end-to-end for:

- `dns-01.home.jrwroberts.co.uk`;
- `dns-02.home.jrwroberts.co.uk`;
- `greenbone.home.jrwroberts.co.uk`;
- `grafana.home.jrwroberts.co.uk`;
- `zabbix.home.jrwroberts.co.uk`;
- `proxmox.home.jrwroberts.co.uk`;
- `proxmox-2.home.jrwroberts.co.uk`.

Each endpoint has a service-specific deploy hook. The Cloudflare Python 2.20.x warning seen during Certbot testing is non-fatal but should be addressed through deliberate dependency version management before a future incompatible major release.

## Container management

`komodo-01` runs Komodo Core and MongoDB. Periphery is commissioned on explicitly managed Docker hosts. The BirdNET-Go controlled update/rollback canary is complete; the remaining estate-wide Docker image lifecycle audit/update work remains open.

## Automated patching

Managed Linux hosts publish `homelab_patch_*` telemetry. Security-only unattended upgrades are enabled; automatic reboot is disabled.

The controlled **16 October 2026** maintenance cycle ended with all 15 Ansible-managed hosts reachable, `0` pending updates and `0` reboot requirements. Docker application/version updates remain owned by the Komodo/container workflow rather than OS patching.

## Backup platform

`media-01` provides node-scoped NFS backup namespaces. An isolated LXC restore proof exists for CT103. Representative QEMU restore, application-consistent Nextcloud/PostgreSQL recovery and an independent second copy remain backlog items.

## Remote access

The ASUS router's OpenVPN server is the accepted production remote-administration path. No dedicated VPN VM is deployed.

## Application platforms

### Nextcloud

`cloud-01` hosts Nextcloud, PostgreSQL, Redis and cron. VM-level backup is proven; application-consistent restore remains open.

### Home Assistant

`home-01` runs HAOS VM204. Native backup and Proxmox backup/protection are established; deeper recovery validation remains open.

### BirdNET-Go

`docker-01` is the dedicated BirdNET-Go Docker host. Do not rebuild the retired TestServer container estate on it. <!-- historical -->

### Media

`media-01` runs Kodi/Samba and provides the Proxmox NFS backup target.

## Tooling / desired-state authority

`admin-01` is the normal Git/Ansible control point. Secrets, Terraform state and recovery identities remain outside Git. Stable Ansible reconciliation should normally produce a second real run with `changed=0`, `failed=0` and `unreachable=0`.

## Planned / deferred / absent — not installed

The following must not be presented as deployed merely because designs or backlog items exist:

- Cloudflare Tunnel / `cloudflared` on `edge-01` — deferred until a real service requirement exists;
- Authelia — not deployed;
- CrowdSec — not deployed;
- Nginx Proxy Manager — not deployed;
- password-manager candidate — product/design not yet authoritative;
- automatic guest HA/shared storage — not part of current design.

## Documentation rule

For exact current host identity/addressing use `IaC/inventory/estate.json`. For current architecture use `CURRENT-STATE.md`. Treat older audits and snapshots as dated evidence, not current deployment authority.
