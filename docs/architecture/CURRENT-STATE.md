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

**19 October accepted-risk review (planning only):** User chose to evaluate the 15 previously accepted findings before launching another scan. These consist of **14 ICMP Timestamp Reply** disclosures (NVT 1.3.6.1.4.1.25623.1.0.103190) across the 14 named hosts and **one BirdNET-Go csrf cookie missing HttpOnly** (NVT 1.3.6.1.4.1.25623.1.0.105925). The accepted-risk allowlist separately includes 15 historical TCP timestamp entries, not present in the last reported 15. Candidate: selectively drop ICMP IPv4 type 13 requests through each host's existing managed firewall, after verifying firewall ownership and rollback (media-01 as possible pilot). BirdNET upstream deliberately makes its csrf token cookie JavaScript-readable; preserve acceptance until exact deployed version and CSRF functionality are tested before forcing HttpOnly. A read-only Ansible audit of the 14 ICMP hosts and the plan in `docs/security/GREENBONE-ACCEPTED-RISKS-2026-10-19.md` are now Git-staged but **not run or deployed**. No accepted-risk status has changed. Fresh Greenbone scan and evidence checks remain pending.


**Latest verified 19 October 2026 — qBittorrent HTTPS-only cutover deployed:** User applied the scoped Git-managed media-01 firewall playbook; `ok=19 changed=2 failed=0`. From admin-01 the trusted HTTPS WebUI returned HTTP 200, direct LAN TCP/8081 was confirmed **BLOCKED**, and the reverse proxy's loopback HTTP/8081 backend remains **AVAILABLE**. The user confirmed working HTTPS login/password. qBittorrent, Kodi, SMB and NFS were not restarted. BirdNET-Go's HTTPS CSRF Secure cookie was separately verified on both tested paths. **Service/network mitigations for the two prior Mediums are complete, but a new authenticated Greenbone scan and published evidence are still needed to close the scan findings.** The 15 accepted findings from the prior report remain pending review after verification; the separately staged Greenbone boot-readiness guard has not been deployed. Next: existing read-only `greenbone-scan-evidence-readonly.yml` plus `greenbone-gmp-preflight.yml`, then consider a single managed scan only if none is active and GMP is ready.


**19 October approved qBittorrent HTTP cutover — Git-staged, not deployed:** HTTPS WebUI works and user completed administrator password recovery/login, authorising direct LAN HTTP port 8081 closure. The intended managed media-01 policy now defaults to LAN HTTPS/443 allowed, direct LAN HTTP/8081 disallowed, with loopback Nginx→qBittorrent backend (127.0.0.1:8081), SSH, Kodi/DLNA, SMB, Proxmox NFS and monitoring allowances preserved. A scoped Ansible cutover plus emergency HTTP rollback and offline validators are committed. The **currently deployed** media firewall still permits both 443 and 8081 until the user runs the new playbook; a source commit is not evidence of closure. A new authenticated Greenbone report remains necessary after successful cutover to confirm remediation.


`greenbone-01` is the active LAN-only Greenbone scanner. The operating model includes managed scans, machine-readable evidence, restricted evidence transfer to `monitor-01`, schema/freshness validation, accepted-risk separation and management-report integration.

The 14 October managed validation had 0 Critical, 0 High, 1 actionable Medium (Zabbix cleartext management HTTP), 0 Low and 30 accepted risks. Trusted Zabbix HTTPS/reverse-proxy remediation was implemented subsequently.

**19 October live remediation progress:** BirdNET-Go `csrf` cookie `Secure` attribute was independently confirmed on `/` and `/login` after the isolated Nginx-cookie Ansible playbook (`docker-01 ok=7 changed=0 failed=0`); Nginx configuration was already compliant and no reload was required. The `media-01` qBittorrent HTTPS prerequisite check (`ok=3 changed=0 failed=0`) found no Nginx, Certbot, certificate or 443 listener and no `qbittorrent.home.jrwroberts.co.uk` DNS answer from either Pi-hole resolver. Git-managed, **not deployed** HTTPS staging now adds that FQDN to both resolvers, a scoped qBittorrent TLS reverse proxy through existing DNS-01 certificate issuance, and a source validator. **19 October controller validation passed:** Jinja HTTPS template render, source/safety contracts, estate (20 active / 0 planned / 5 retired guarded), DNS playbook syntax and TLS-stage syntax. DNS rollout completed successfully on 19 October: dns-01 and dns-02 each returned `192.168.2.195` for `qbittorrent.home.jrwroberts.co.uk` (`ok=4 changed=0 failed=0` on each). Trusted qBittorrent TLS certificate/Nginx stage **was successfully deployed on 19 October**: Ansible `media-01 ok=33 changed=9 failed=0`, Nginx syntax check passed and local trusted HTTPS returned HTTP 200 (`QBITTORRENT_HTTPS_STAGE=PASS`). No qBittorrent/Kodi/SMB/NFS restart. **LAN TCP/443 is now permitted through the managed media firewall** (`qbittorrent-https-lan-stage.yml` passed live on 19 October: `media-01 ok=16 changed=2 failed=0`, nftables config updated/reloaded). Trusted HTTPS and HTTP 8081 fallback were each verified by admin-01 with HTTP 200. LAN HTTP/8081 remains allowed until browser HTTPS login and function testing. The LAN/443-with-8081-rollback stage was validated on admin-01 and **deployed successfully**. User has now confirmed HTTPS opens successfully in a LAN browser, but WebUI password recovery/reset is pending and **authenticated login remains unverified**. A non-secret, read-only Ansible WebUI password preflight is Git-staged, not yet run. Later closure of LAN HTTP/8081 and fresh Greenbone confirmation remain outstanding. Actual browser login and final HTTP cutover are outstanding. The proxy cookie wildcard expression was made explicit (`proxy_cookie_flags ~.* secure;`) in Git; offline revalidation on admin-01 is pending. Legacy HTTP 8081 firewall access remains unchanged until separate end-to-end HTTPS verification/cutover. Fresh Greenbone scan confirmation of both Medium remediations is outstanding.

**19 October targeted read-only verification:** On `media-01`, qBittorrent-nox was confirmed on `*:8081`, with Nginx inactive and no Let's Encrypt certificate directory. On `docker-01`, Nginx 1.26.3 served BirdNET-Go over HTTPS and returned a `csrf` cookie without `Secure` or `HttpOnly` on both `/` and `/login`. Focused Ansible inspection finished `ok=3 changed=0 failed=0` on each host. A Git-managed `proxy_cookie_flags csrf secure;` Nginx update plus a scoped Nginx-only Ansible deployment and validation playbook are now staged, **NOT deployed**. A read-only qBittorrent HTTPS certificate/DNS readiness playbook is also staged; no qBittorrent, DNS, firewall, or certificate changes have occurred. The missing HttpOnly flag is not being changed until application CSRF behavior is verified. Both Mediums remain open.

**Newer emailed result, not yet independently reconciled with machine-readable published evidence:** On **19 October 2026 at 03:07 UTC (04:07 BST)** a Greenbone authenticated managed scan completion email reported ID `6e75928d-f251-426f-809c-991ffcbf6603`, **0 Critical / 0 High / 2 actionable Medium / 0 Low**, 789 informational and 15 accepted risks. The two new Medium findings are `media-01` (`192.168.2.195:8081`) cleartext sensitive information over HTTP, score 4.8, OID `1.3.6.1.4.1.25623.1.0.108440`, and `docker-01` (`192.168.2.220:443`) missing Secure cookie attribute, score 5.0, OID `1.3.6.1.4.1.25623.1.0.902661`. Neither lists a CVE. Only 15 accepted items appear in the new email (14 ICMP timestamp plus one BirdNET cookie missing HttpOnly); the 15 accepted TCP timestamp findings in the 16 October report are not present and their absence is **not proof of remediation**. This email shows the direct-socket scan runner completed at least one subsequent scan, but published `managed.json`, transfer to `monitor-01` and dashboard freshness are **not verified**. The bounded systemd boot guard remains Git-only, not deployed or validated. **Security remediation remains open for both Medium findings and readiness/telemetry verification.**

For historical comparison, the latest **available saved managed evidence**, inspected through Ansible on **18 October 2026**, was collected **16 October 2026 at 14:28 UTC** (report `35dc10c3-aac0-46fa-b6ce-7c1b31440d38`):

```text
Critical / High / Medium / Low actionable: 0
Log / informational:                    828
Accepted risks:                          30
```

The `Proxmox-2` outage temporarily made VM203 unreachable; the 18 October 16:29 BST cluster inspection showed both nodes online, quorum healthy with QDevice and VM203 running. **The 18 October 16:18 BST scheduled/restart-associated scan failed**, because GMP could not connect to `/run/gvmd/gvmd.sock` (`Connection refused`). The 16 October evidence is historical and stale as of the 18 October review; a fresh successful scan is still required before vulnerability-remediation closure. Ansible health checks after recovery show `gvmd` and `pg-gvm` both healthy and the management socket present. The restart-associated scan launched at **16:17:47 BST** before `gvmd` became GMP-ready at **16:19:29 BST**, establishing a startup timing defect. The 190,103-VT rebuild and feed synchronisation subsequently finished around **16:37 BST**; the PostgreSQL logs also warned of frequent checkpoints during this heavy import. A subsequent non-scanning Ansible GMP preflight on 18 October **timed out after 150 seconds (exit 124)** with no output; authentication and managed task lookup remain unverified even though the containers were healthy. The ensuing read-only Ansible investigation confirmed the root-owned, mode-0640 temporary GMP credentials file remains, with no detected scan lock owner or active helper process, while `gvmd` and PostgreSQL remain healthy. The safety-gated Ansible playbook `greenbone-gmp-orphan-cleanup.yml` **successfully removed the orphaned file** on 18 October after verifying no active scan, helper process or lock owner; Ansible reported `ok=12 changed=1 failed=0`, and confirmed the file absent. No credentials were read and no service or scan started. The historical `greenbone-gmp-latency-readonly.yml` passed live on 18 October: the Docker journal shows gvm-tools helper launch activity at 16:45:46 BST and task deletion at 16:45:47 BST, but no definitive timeout root cause; 5.6 GB RAM and 61 GB disk were available, and orphan credentials remained absent. Updated Python runner/preflight IaC now contains non-secret `--check` progress markers, a shorter 75s GMP task-lookup deadline, SIGTERM-aware best-effort cleanup, a pre-existing-credential guard and explicit GMP/cleanup failure assertion. **Controller Ansible validation and deployment succeeded:** runner/preflight syntax checks passed; scoped runner first deployment `ok=3 changed=1 failed=0` and repeat `ok=3 changed=0 failed=0`. The updated non-scanning preflight nonetheless failed with `rc=124` after `GMP_CHECK_STAGE=querying_managed_task`. SIGTERM cleanup succeeded (`Temporary GMP config absent: True`); final Ansible assertion failed as designed. The first read-only `greenbone-gmp-request-path-readonly.yml` run was interrupted at its `docker compose exec -T gvmd` socket inspection; a second run has no complete result in the user output. A revised Git-managed diagnostic replaces Docker exec with Docker inspect plus host-side socket `stat`, without making GMP requests. That revision has not yet been tested on `admin-01`. A Docker exec/attach stall is suspected but not established. Direct Unix socket connection and a GMP `get_version` request **both passed** from Ansible on 18 October (`GMP_STATUS=200`, `GMP_VERSION=22.7`), confirming a responsive protocol service independent of Docker Compose. The read-only direct-socket authenticated lookup now **passed live** on 18 October: `DIRECT_GMP_AUTH_STATUS=200`, `DIRECT_GMP_TASKS_STATUS=200`, one matching managed task, `DIRECT_GMP_CHECK=PASS`, Ansible `ok=6 changed=0 failed=0`. Existing runtime credentials and task are verified independently of Docker helpers. A Git-managed change to the existing scan runner now **stages direct-socket GMP communication** instead of the problematic Compose helper; the preflight is adjusted to 60 seconds. **Controller validations passed on 18 October:** Jinja render, Python syntax, mock GMP authentication/task lookup, both Ansible playbook syntax checks, and estate validation (20 active assets). The new direct-socket runner **was deployed on greenbone-01 through Ansible** on 18 October (`ok=3 changed=1 failed=0`); its generated Python passed host-side compilation. The live, non-scanning production GMP preflight **passed on 18 October 2026** (`ok=10 changed=0 failed=0`), with task lookup in **0.1 seconds**, exit code 0, `CHECK=PASS`, and legacy credentials file absent. The managed scan systemd service still reported `failed` from the previous boot-time scan; no reset, service restart or new scan was performed. Report retrieval and complete scan validation remain pending. Complete scan/report handling and startup readiness remain unverified. A fail-closed, bounded `ExecStartPre` systemd GMP readiness gate has been **committed as IaC but not yet validated on admin-01 or deployed**. It retries only the direct-socket authenticated `managed --check` before the persistent timer's scan can start (30-minute maximum; fail closed), and a dedicated scoped Ansible playbook installs only the helper and service unit without changing the timer. The old failed scan state is unchanged. A fresh completed scan, evidence publication and end-to-end report validation remain outstanding.

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
