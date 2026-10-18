<!-- estate-authority: IaC/inventory/estate.json -->
# Current-State Architecture

**Status:** CURRENT OPERATIONAL TRUTH  
**Current-state review:** 16 October 2026  
**Identity/address authority:** `IaC/inventory/estate.json`  
**Configuration authority:** `IaC/`

This document records what is live now. Dated audits, migration notes and commissioning records remain evidence, but they do not override validated live state or the canonical estate inventory.

## Authority model

Use this precedence when documents disagree:

1. validated live state;
2. `IaC/inventory/estate.json` for identity, address and lifecycle state;
3. this `CURRENT-STATE.md` for human-readable architecture;
4. Git-managed IaC for intended/deployed configuration;
5. production service/runbook documents;
6. dated audits and historical migration evidence.

## Active estate

| Asset | Address | Current role | State |
|---|---:|---|---|
| `admin-01` | `192.168.2.48` | Raspberry Pi 3 administration / SSH jump / IaC controller / Corosync QNetd | ACTIVE |
| `dns-02` | `192.168.2.50` | Pi-hole + Unbound, CT100 on `PROXMOX` | ACTIVE |
| `dns-01` | `192.168.2.51` | Pi-hole + Unbound, CT101 on `Proxmox-2` | ACTIVE |
| `monitor-01` | `192.168.2.52` | Prometheus/Grafana/Alertmanager/Blackbox/Loki + active network discovery, VM202 on `Proxmox-2` | ACTIVE |
| `cloud-01` | `192.168.2.53` | Nextcloud/PostgreSQL/Redis, VM200 on `PROXMOX` | ACTIVE |
| `mail-relay-01` | `192.168.2.54` | Internal Postfix relay, CT102 on `PROXMOX` | ACTIVE |
| `sensor-01` | `192.168.2.55` | Suricata/Zeek passive sensor, VM201 on `PROXMOX` | ACTIVE |
| `edge-01` | `192.168.2.56` | Reserved edge LXC, CT103 on `Proxmox-2`; `cloudflared` absent | ACTIVE HOST |
| `greenbone-01` | `192.168.2.57` | Greenbone vulnerability scanner, VM203 on `Proxmox-2` | ACTIVE |
| `komodo-01` | `192.168.2.58` | Komodo Core control plane, CT104 on `PROXMOX` | ACTIVE |
| `zabbix-01` | `192.168.2.59` | Zabbix platform, CT105 on `PROXMOX` | ACTIVE |
| `home-01` | `192.168.2.60` | Home Assistant OS, VM204 on `PROXMOX` | ACTIVE |
| `PROXMOX` | `192.168.2.70` | `jameshouse-pve` node 1 / NTP | ACTIVE |
| `Proxmox-2` | `192.168.2.71` | `jameshouse-pve` node 2 / NTP; former discovery source retained for rollback evidence | ACTIVE |
| `media-01` | `192.168.2.195` | Raspberry Pi 5 Kodi endpoint / primary Proxmox NFS backup target | ACTIVE |
| `docker-01` | `192.168.2.220` | Raspberry Pi 4 BirdNET-Go Docker host | ACTIVE |
| ASUS RT-AC86U | `192.168.2.1` | Router / DHCP / AiMesh controller / OpenVPN endpoint | ACTIVE |
| ASUS AiMesh node | `192.168.2.181` | Wireless mesh node | ACTIVE |
| ASUS AiMesh node | `192.168.2.218` | Wireless mesh node | ACTIVE |
| HP ProCurve 2510G-24 | `192.168.2.16` | Core switch / active SPAN source | ACTIVE |

The normal Ansible-managed Linux baseline is **15 hosts**. `home-01` is active but HAOS and intentionally outside that 15-host Linux/Ansible baseline.

## Retired identities

These names are historical only and must not be used as active deployment, monitoring or recovery targets:

- `TestServer` -> hardware now `docker-01`; <!-- historical -->
- `DietPi` -> hardware now `admin-01`; <!-- historical -->
- `ids-01` -> decommissioned; <!-- historical -->
- former `k3s-node-01` identity -> hardware now `media-01`; <!-- historical -->
- former `dns-02` address `192.168.2.242` -> retired. <!-- historical -->

## Proxmox platform

The live virtualization platform is the two-node `jameshouse-pve` cluster:

```text
PROXMOX    192.168.2.70
Proxmox-2  192.168.2.71
```

Corosync uses the preferred direct `10.255.255.0/30` interconnect with management-LAN fallback. `admin-01` runs QNetd and supplies the external third vote. Current quorum is healthy with QDevice present.

Latest controlled maintenance evidence from 16 October 2026:

```text
pve-manager: 9.2.21
running kernel: 7.0.14-24-pve
quorum: healthy / QDevice present
pending packages: 0
reboot required: no
```

Production guest disks remain node-local. Cluster membership and quorum do not provide automatic guest-data HA after loss of the node that owns a guest disk.

A GDS kernel mitigation is active on the PVE hosts through `gather_data_sampling=force`. The live mitigation is proven, but the GRUB/kernel-parameter change still needs to be encoded in IaC before that item is considered fully reproducible.

## DNS

Approved resolver pair:

```text
dns-01  192.168.2.51
dns-02  192.168.2.50
```

Both run Pi-hole + Unbound and forward Pi-hole to local Unbound at `127.0.0.1#5335`. `admin-01` is not a DNS resolver.

## Monitoring, logging and dashboards

`monitor-01` hosts Prometheus, Grafana, Alertmanager, Blackbox Exporter and Loki. The 15 managed Linux systems report through the host-monitoring baseline and Zabbix Agent 2; Zabbix Server runs on `zabbix-01`.

Production Grafana includes the operations overview, host dashboards, patch/reboot status, network-host views and accepted-risk detail reporting. Factual network inventory remains owned by `monitor-01`.

The Network Host discovery single-owner cutover remains `monitor-01`; former source timers on `Proxmox-2` remain disabled/inactive.

## Automated patching

The managed Linux estate uses security-only unattended upgrades with **automatic reboot disabled**. A full controlled patch session completed on **16 October 2026**.

Final validated estate state:

```text
Ansible-managed hosts:      15
reachable:                  15
pending updates:            0
reboots required:           0
```

Patch telemetry was refreshed across all 15 hosts. No patch-induced service regression was found. Known pre-existing failed one-shot/helper units remain separate operational debt and are not patch failures.

The Proxmox Ceph enterprise repository was found enabled although Ceph is not in use. It is now explicitly disabled through the `proxmox_repositories` Ansible role (`9dc60394` after rebase), allowing normal package maintenance without an enterprise Ceph subscription.

## Trusted HTTPS and certificate management

Trusted browser-facing HTTPS is now deployed and renewal-tested for the managed administration endpoints below. Certificates use Let's Encrypt with Cloudflare DNS validation and service-specific deploy hooks.

| Service | Trusted URL | Renewal/deploy behaviour |
|---|---|---|
| Pi-hole dns-01 | `https://dns-01.home.jrwroberts.co.uk/` | rebuild combined Pi-hole PEM; restart FTL |
| Pi-hole dns-02 | `https://dns-02.home.jrwroberts.co.uk/` | rebuild combined Pi-hole PEM; restart FTL |
| Greenbone | `https://greenbone.home.jrwroberts.co.uk/` | deploy cert/key into Greenbone TLS path; restart nginx container |
| Grafana | `https://grafana.home.jrwroberts.co.uk/` | nginx reverse proxy; reload nginx |
| Zabbix | `https://zabbix.home.jrwroberts.co.uk/` | nginx reverse proxy; reload nginx |
| PROXMOX | `https://proxmox.home.jrwroberts.co.uk:8006/` | install custom `pveproxy` certificate; restart pveproxy |
| Proxmox-2 | `https://proxmox-2.home.jrwroberts.co.uk:8006/` | install custom `pveproxy` certificate; restart pveproxy |

All seven certificate renewal paths were exercised with Certbot dry-runs on 16 October 2026 and the corresponding service remained healthy afterwards.

Grafana's Docker listener is hardened to `127.0.0.1:3000`; direct LAN access to `192.168.2.52:3000` is no longer available. Grafana is configured with its canonical HTTPS domain/root URL and secure cookies. Implementation is committed on `main` as `bb5aecd9`.

The Cloudflare Python 2.20.x compatibility warning observed during Certbot dry-runs is non-fatal today, but dependency version control should be reviewed before an incompatible Cloudflare Python 3.x transition.

## Vulnerability management

`greenbone-01` is the active LAN-only Greenbone scanner. The operating model includes managed scans, machine-readable evidence, restricted evidence transfer to `monitor-01`, schema/freshness validation, accepted-risk separation and management-report integration.

The 14 October managed validation had 0 Critical, 0 High, 1 actionable Medium (Zabbix cleartext management HTTP), 0 Low and 30 accepted risks. Trusted Zabbix HTTPS/reverse-proxy remediation was implemented subsequently.

The latest **available saved managed evidence**, inspected through Ansible on **18 October 2026**, was collected **16 October 2026 at 14:28 UTC** (report `35dc10c3-aac0-46fa-b6ce-7c1b31440d38`):

```text
Critical / High / Medium / Low actionable: 0
Log / informational:                    828
Accepted risks:                          30
```

The `Proxmox-2` outage temporarily made VM203 unreachable; the 18 October 16:29 BST cluster inspection showed both nodes online, quorum healthy with QDevice and VM203 running. **The 18 October 16:18 BST scheduled/restart-associated scan failed**, because GMP could not connect to `/run/gvmd/gvmd.sock` (`Connection refused`). The 16 October evidence is historical and stale as of the 18 October review; a fresh successful scan is still required before vulnerability-remediation closure. Ansible health checks after recovery show `gvmd` and `pg-gvm` both healthy and the management socket present. The restart-associated scan launched at **16:17:47 BST** before `gvmd` became GMP-ready at **16:19:29 BST**, establishing a startup timing defect. The 190,103-VT rebuild and feed synchronisation subsequently finished around **16:37 BST**; the PostgreSQL logs also warned of frequent checkpoints during this heavy import. A subsequent non-scanning Ansible GMP preflight on 18 October **timed out after 150 seconds (exit 124)** with no output; authentication and managed task lookup remain unverified even though the containers were healthy. Its external timeout may have left a protected temporary GMP credentials file or a helper container. Inspect only metadata and process/container state through the read-only `greenbone-gmp-timeout-readonly.yml` playbook; do not print credentials or launch another scan yet. Codify safe cleanup/readiness handling in reviewed IaC after diagnosis, then validate a newly completed authenticated report.

The accepted-risk dashboard/export path now exposes the accepted-risk details rather than only a count.

Missing, invalid or stale Greenbone evidence must never be represented as zero vulnerabilities.

## Raspberry Pi speculative-execution hardening

`docker-01` is Raspberry Pi 4 Model B Rev 1.5 (`c03115`), Debian 13/aarch64. Trusted Firmware-A v2.15.0 is active for Cortex-A72 speculative-execution mitigations.

Validated live state:

```text
TF-A artifact SHA-256:
b1d31e5094c692b41ee9418a20216176bd1c2764f27e18a5fdc4d6187a307405

Spectre v2: Mitigation: Branch predictor hardening, BHB
Speculative Store Bypass: Not affected
```

The mitigation is now fully managed through `roles/raspberry_pi_tfa_hardening`, including the validated firmware artifact, checksum, licence/provenance, guarded Pi model/revision/architecture checks, FAT-safe boot-config backup and managed `config.txt` block. Repeat reconciliation completed with `changed=0`, `failed=0`. Implementation is committed as `b3047742`.

## Network sensor and switch SPAN

`sensor-01` is the active passive sensor. Suricata and Zeek consume the dedicated capture interface.

```text
HP ProCurve 2510G-24
mirror destination: port 24
mirror sources:     ports 1-23
```

The older switch-port map that shows port 24 as a router uplink is historical pre-repatch evidence only.

## Container management

`komodo-01` runs Komodo Core and MongoDB. Komodo Core uses strict HTTPS and managed Periphery hosts connect over certificate-validated WSS. The BirdNET-Go controlled image/update/rollback canary is proven; the remaining estate-wide image lifecycle review is still open.

Komodo adoption must not silently recreate existing production Compose workloads.

## Backup platform

Primary Proxmox guest backups use NFS on `media-01` with node-scoped backup namespaces and `keep-last=3` retention.

An isolated LXC restore proof exists for CT103. A representative QEMU restore, application-consistent `cloud-01`/PostgreSQL recovery and an independent second backup copy remain open.

## Remote access

The production remote-access path is the native OpenVPN server on the ASUS RT-AC86U. External split-tunnel acceptance was completed from a Windows laptop on 18 September 2026.

## Cloud / Nextcloud

`cloud-01` hosts Nextcloud, PostgreSQL, Redis and cron on VM200 with a dedicated application-data disk. VM-level backup is proven; application-consistent recovery remains outstanding.

## Home Assistant

`home-01` is active as VM204 on `PROXMOX` using Home Assistant OS. Native backup, Proxmox protection and scheduled backup inclusion are established. Deeper recovery proof and external availability monitoring remain future work.

## Administration and recovery control plane

`admin-01` is the normal Git/Ansible controller and QNetd host. It should remain lightweight and should not become a general application server, DNS resolver, monitoring server or backup target. Protected recovery state and secret material remain outside Git.

## Public / edge services

`edge-01` exists as CT103 but `cloudflared` is not deployed. Authelia and CrowdSec are not deployed. Do not describe any of them as active services until explicitly implemented and validated.

## Important service endpoints

| Service | Current administration/service URL |
|---|---|
| Grafana | `https://grafana.home.jrwroberts.co.uk/` |
| Prometheus | `http://192.168.2.52:9090/` |
| Alertmanager | `http://192.168.2.52:9093/` |
| Loki | `http://192.168.2.52:3100/` |
| Nextcloud | `http://192.168.2.53:8080/` |
| Greenbone | `https://greenbone.home.jrwroberts.co.uk/` |
| Komodo | `https://komodo-01.jameshouse:9120/` |
| Zabbix | `https://zabbix.home.jrwroberts.co.uk/` |
| Home Assistant | `http://192.168.2.60/` |
| PROXMOX | `https://proxmox.home.jrwroberts.co.uk:8006/` |
| Proxmox-2 | `https://proxmox-2.home.jrwroberts.co.uk:8006/` |
| BirdNET-Go | `http://192.168.2.220:8080/` |

These are LAN/VPN administration/service endpoints unless another authoritative document explicitly defines public exposure.

## Open architecture / engineering items

The following are genuine future work and must not be confused with completed migrations:

- wait for the final post-remediation Greenbone scan and reconcile its findings;
- encode the already-proven Proxmox GDS boot mitigation in IaC;
- review/pin the Cloudflare Python dependency used by Certbot DNS validation before a future incompatible major version;
- complete the remaining estate-wide Docker image/update lifecycle review;
- representative QEMU restore proof;
- application-consistent Nextcloud/PostgreSQL restore proof;
- independent second backup copy/failure domain;
- controlled legacy-infrastructure cleanup where still justified;
- Raspberry Pi overclocking feasibility/thermal/power review before any clock changes are approved;
- Cloudflare Tunnel only when a real service requirement exists;
- password-manager product/design selection only if deliberately prioritised.

## Historical evidence

Dated audits, migrations and commissioning records under `docs/` and `production docs/` remain point-in-time evidence. They should preserve the state observed at the time and must not be rewritten to look current when they conflict with this document or `IaC/inventory/estate.json`.
