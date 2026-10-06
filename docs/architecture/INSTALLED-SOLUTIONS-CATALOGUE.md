<!-- estate-authority: IaC/inventory/estate.json -->
# Installed Solutions Catalogue

**Purpose:** Human-readable catalogue of the major solutions currently used by the homelab, what they do, why they are present, where they run and which ports matter operationally.  
**Current-state authority:** `IaC/inventory/estate.json` and `docs/architecture/CURRENT-STATE.md`  
**Reviewed:** 6 October 2026

This page lists **currently installed/operational** solutions. Planned, deferred or retired products are called out separately and must not be inferred as deployed.

For terminology such as STUN, NAT, CVE, QoD, SPAN and quorum, see `docs/network/TERMS-AND-REFERENCE.md`.

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
| Proxmox VE | VM/LXC virtualisation and cluster management | `PROXMOX .70`, `Proxmox-2 .71` | 8006/TCP LAN/VPN; 22/TCP SSH |
| Corosync / Kronosnet | Cluster membership/messaging | both PVE nodes | dedicated cluster links |
| QDevice / QNetd | Third quorum vote | `admin-01 .48` | 5403/TCP |
| Chrony | LAN NTP service | `.70`, `.71` | 123/UDP |
| Pi-hole | DNS filtering/local DNS | `dns-01 .51`, `dns-02 .50` | 53/TCP+UDP |
| Unbound | Recursive DNS behind Pi-hole | both DNS LXCs | 127.0.0.1:5335 |
| ASUS RT-AC86U | Router/DHCP/AiMesh/OpenVPN | `.1` | LAN admin; OpenVPN UDP transport |
| HP ProCurve 2510G-24 | Core switch / SPAN | `.16` | legacy LAN management; mirror ports 1–23 -> 24 |
| OpenVPN | Remote administration | ASUS router | router-controlled UDP listener |
| Prometheus | Metrics | `monitor-01 .52` | 9090/TCP |
| Grafana | Dashboards | `monitor-01 .52` | 3000/TCP |
| Alertmanager | Alert routing | `monitor-01 .52` | 9093/TCP |
| Blackbox Exporter | Reachability/service probes | `monitor-01 .52` | 9115/TCP |
| Loki | Central log store | `monitor-01 .52` | 3100/TCP |
| Grafana Alloy | Log/telemetry forwarding | managed estate | 12345/TCP local/API where enabled |
| Node Exporter | Linux host metrics | 15 managed Linux hosts | 9100/TCP |
| Zabbix | Agent-oriented monitoring | `zabbix-01 .59` | 8080/TCP web; 10051/TCP server |
| Zabbix Agent 2 | Host telemetry | 15 managed Linux hosts | 10050/TCP passive where used; active to `.59:10051` |
| Network Host discovery | LAN inventory/enrichment/OS evidence/first-seen | **`monitor-01 .52`** | no user-facing listener |
| Suricata | IDS/signature detection | `sensor-01 .55` | passive capture |
| Zeek | Network metadata/behaviour analysis | `sensor-01 .55` | passive capture |
| Greenbone Community | Vulnerability scanning | `greenbone-01 .57` | 443/TCP LAN/VPN |
| Komodo Core | Container-management control plane | `komodo-01 .58` | 9120/TCP LAN/VPN |
| Komodo Periphery | Managed Docker-host agent | explicitly commissioned Docker hosts | outbound management path; no general public listener |
| Docker | Application container runtime | selected application hosts | daemon not LAN-published |
| MongoDB | Komodo database | internal `komodo-01` stack | 27017/TCP internal |
| Nextcloud | Private cloud application | `cloud-01 .53` | 8080/TCP |
| PostgreSQL | Application database | `cloud-01`, `zabbix-01` | 5432/TCP internal/local |
| Redis | Nextcloud cache/locking | `cloud-01` | 6379/TCP internal |
| Home Assistant OS/Core | Home automation | `home-01 .60` | 80/TCP LAN/VPN |
| BirdNET-Go | Bird-call identification | `docker-01 .220` | 8080/TCP |
| Postfix | Internal SMTP relay | `mail-relay-01 .54` | 25/TCP LAN; outbound 587/TCP TLS |
| NFS | Proxmox guest-backup storage | `media-01 .195` | 2049/TCP |
| Samba / SMB | Media sharing | `media-01 .195` | 445/TCP |
| Kodi | Local media endpoint | `media-01 .195` | local application |
| Ansible | Configuration management | run from `admin-01 .48` | SSH to targets |
| Terraform/OpenTofu source | Infrastructure provisioning | run from `admin-01 .48` | provider/API access |
| Git / GitHub | Desired-state/change authority | external repository service | HTTPS/SSH outbound |
| GitHub Actions | CI validation | GitHub-hosted | external HTTPS |
| Cloudflare Pages | Public portfolio hosting | external | HTTPS/443 |

## Virtualisation and cluster

The two physical nodes form `jameshouse-pve`. Corosync uses a preferred direct `10.255.255.0/30` link and management-LAN fallback. `admin-01` supplies QNetd/QDevice.

Current guest disks remain node-local. Cluster membership and quorum therefore do **not** mean automatic guest-data HA.

Current production guest placement:

```text
PROXMOX
  CT100 dns-02
  CT102 mail-relay-01
  CT104 komodo-01
  CT105 zabbix-01
  VM200 cloud-01
  VM201 sensor-01
  VM204 home-01

Proxmox-2
  CT101 dns-01
  CT103 edge-01
  VM202 monitor-01
  VM203 greenbone-01
```

## DNS

Pi-hole provides filtering/local DNS while Unbound performs recursive resolution on localhost port 5335.

Approved resolver pair:

```text
192.168.2.51  dns-01
192.168.2.50  dns-02
```

`admin-01 .48` is not a resolver. The earlier resolver cross-record parity issue is fixed in current IaC.

## Monitoring, logging and dashboards

`monitor-01` provides Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki. Alloy forwards logs/telemetry from managed systems according to inventory/role scope.

The production Grafana estate foundation includes:

- Home/operations overview;
- Hosts overview;
- Patch & Reboot Status;
- Node Detail navigation;
- Network Hosts overview and per-device pages.

The 15 managed Linux systems are also covered by Zabbix Agent 2 with the dedicated server on `zabbix-01`.

## Network Host discovery

The active Network Host discovery platform is on **`monitor-01`**, following the verified single-owner cutover on 27 September 2026.

It includes collector/enrichment, OS-evidence publication, trusted Proxmox guest identity refresh, targeted Nmap profiling, first-seen notification, persistent host-page generation, Grafana publication, DNS evidence correlation and bounded host assessment.

`Proxmox-2` is the former source; its source timers are disabled/inactive and retained state is rollback/history evidence.

## Security platforms

### Suricata / Zeek

`sensor-01` consumes the dedicated SPAN capture path. Suricata provides signature/detection logic; Zeek provides protocol/connection metadata and behavioural context.

### Greenbone

`greenbone-01` performs active vulnerability scanning. The managed-infrastructure scan/evidence path is operational and feeds the management-report evidence store on `monitor-01`.

Greenbone and `sensor-01` are complementary; there is no requirement for a direct sensor-to-Greenbone feed.

### CrowdSec

**Not deployed.** CrowdSec is not a current production signal source. Evaluate it only if a future ingress/public-exposure design creates a justified need.

## Container management

`komodo-01` runs Komodo Core and MongoDB. Periphery is commissioned on explicitly managed Docker hosts and existing application stacks were adopted without recreation during commissioning.

Container application/version updates belong to the approved Komodo/container workflow, not the OS patch process.

## Automated patching

Managed Linux hosts publish `homelab_patch_*` telemetry. Security-only unattended upgrades are enabled; automatic reboot is disabled.

The controlled 5 October 2026 maintenance cycle ended at:

```text
15 reporting
0 pending updates
0 security updates
0 reboot required
15 unattended-upgrades installed
0 automatic reboot
```

## Backup platform

`media-01` provides node-scoped NFS backup namespaces.

```text
PROXMOX   -> media-backup-proxmox   -> guests 100,102,104,105,200,201,204
Proxmox-2 -> media-backup-proxmox-2 -> guests 101,103,202,203
```

Mode is snapshot, compression zstd, retention keep-last=3. CT103 has an isolated LXC restore proof; unattended CT105 and VM203 evidence is observed. Recovery-depth and second-copy work remain separate backlog items.

## Remote access

The ASUS router's OpenVPN server is the accepted production remote-administration path. External Windows-laptop access with split tunnelling was accepted on 18 September 2026.

No dedicated VPN VM is deployed.

## Application platforms

### Nextcloud

`cloud-01` hosts Nextcloud, PostgreSQL, Redis and cron. It uses a dedicated 200 GiB data disk mounted at `/srv/cloud-01-data`. VM-level backup is proven; application-consistent restore remains open.

### Home Assistant

`home-01` runs HAOS VM204. Native backup and manual Proxmox backup/integrity evidence exist and VM204 is included in the nightly backup schedule.

### BirdNET-Go

`docker-01` is deliberately a single-purpose BirdNET-Go Docker host. Do not rebuild the retired TestServer container estate on it.

### Media

`media-01` runs Kodi/Samba and provides the Proxmox NFS backup target. User media requires independent protection because writing another copy to the same NVMe does not create a separate failure domain.

## Tooling / desired-state authority

`admin-01` is the normal Git/Ansible/Terraform control point. Secrets, Terraform state and recovery identities remain outside Git.

Stable Ansible reconciliation should normally produce a second real run with `changed=0`, `failed=0` and `unreachable=0`.

## Planned / deferred / absent — not installed

The following must not be presented as deployed merely because designs or backlog items exist:

- Cloudflare Tunnel / `cloudflared` on `edge-01` — deferred until a real service requirement exists;
- Authelia — not deployed; Cloudflare is the intended MFA boundary for future public exposure unless explicitly changed;
- CrowdSec — not deployed;
- Nginx Proxy Manager — not deployed;
- password-manager/Vaultwarden candidate — product/design not yet authoritative;
- automatic guest HA/shared storage — not part of current design.

## Documentation rule

For exact current host identity/addressing use `IaC/inventory/estate.json`. For current architecture use `CURRENT-STATE.md`. Treat older audits and snapshots as dated evidence, not current deployment authority.
