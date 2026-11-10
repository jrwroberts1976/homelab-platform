# cloud-01

> Persistent private host record. This page is intended for reviewed operational
> notes and bounded evidence. Do not store passwords, API tokens, recovery keys,
> full raw DNS logs or packet captures here.

## Identity

| Field | Value |
|---|---|
| Canonical name | `cloud-01` |
| Address | `192.168.2.53` |
| Type | vm |
| Role | Production Nextcloud, PostgreSQL and Redis, VM200 on PROXMOX |
| Managed by Ansible | Yes |
| State | Active |

## Network identity

- MAC address:
- Vendor/OUI:
- Hostname / DHCP name:
- VLAN / network:
- Physical location or hypervisor:
- Stable device identifier:

## Operating system and platform evidence

- Authoritative OS:
- OS evidence source:
- Architecture:
- Kernel / firmware:
- Nmap fingerprint:
- Nmap evidence timestamp:
- Confidence / review status:

## Open ports and services

| Port | Protocol | Service | Product/version | Evidence time | Expected? |
|---:|---|---|---|---|---|
| | | | | | |

## Network flows

<!-- BEGIN AUTO:ZEEK-FLOW -->
### Automated Zeek summary

- Zeek flow evidence is not configured for this estate.

> No absence-of-traffic conclusion is made when the Zeek source is unavailable.
<!-- END AUTO:ZEEK-FLOW -->

Record reviewed, useful flow summaries rather than raw packet captures.

| Direction | Peer / destination | Protocol / port | Purpose | First/last observed | Expected? |
|---|---|---|---|---|---|
| | | | | | |

### Expected flows

- 
- 

### Unexpected or investigated flows

- 

## Internet / DNS activity

Keep this section to **bounded domain/service summaries**. Do not commit a
complete household browsing history.

| Service / domain family | Example domains | Evidence source | Last observed | Interpretation |
|---|---|---|---|---|
| | | | | |

### Known cloud/service dependencies

- 

### Browsing / application observations

- 

<!-- BEGIN AUTO:AI-ASSESSMENT -->
## AI-assisted host assessment

> Advisory interpretation of bounded host evidence. Canonical inventory and direct telemetry remain authoritative.

- Assessed: `2026-11-03T18:04:04+00:00`
- Model: `gpt-5.6-luna`
- MAC identity: `bc:24:11:e9:49:60`
- Identity confidence: **high**
- OS confidence: **low**
- Exact OS: **Not established**
- Manual review required: **No**

### Assessment summary

cloud-01 is a managed Proxmox VM hosting production Nextcloud, PostgreSQL and Redis. Linux kernel/containerd evidence is present, but the exact OS is not established. Greenbone reports one medium-severity kernel-mitigation finding; patch telemetry currently reports no available updates.

### Confirmed facts

- The documented device name is cloud-01.
- The canonical estate record identifies this device as a VM on Proxmox, VM200.
- Its documented role is Production Nextcloud, PostgreSQL and Redis.
- The device is managed by Ansible.
- The inventory and Nmap vendor are Proxmox Server Solutions GmbH.
- The host is online at 192.168.2.53.
- Sampled logs contain Linux kernel/module evidence including 6.12.115+deb13.1-cloud-amd64.
- Sampled logs contain containerd and CRI plugin messages.
- Greenbone reports one actionable medium-severity finding for missing Linux kernel mitigations for Processor MMIO Stale Data, with CVEs CVE-2022-21123, CVE-2022-21125 and CVE-2022-21166.
- Patch telemetry reports zero available updates, zero security updates, and no reboot required.

### Inferences

- The device is a Linux-based server virtual machine.
- The exact Linux distribution and OS version cannot be determined from the supplied evidence.

> Greenbone zero-match results are not proof that a host is vulnerability-free. Nmap service labels and OS fingerprints remain evidence, not authoritative identity, unless corroborated.
<!-- END AUTO:AI-ASSESSMENT -->

<!-- BEGIN AUTO:PATCHING -->
## Automated patching status

> Generated from host patch metrics collected by Prometheus. This bounded section is maintained automatically.

- Policy: **Security updates automatically**
- Automatic reboot: **Disabled**
- Last assessed: `2026-11-10T04:17:41+00:00`
- Pending updates: **0**
- Security updates pending: **0**
- Reboot required: **Yes**
- unattended-upgrades installed: **Yes**
- Last APT transaction activity: `2026-11-09T06:53:45+00:00`
- Patch state: **Attention required**

> Automatic reboot remains disabled by policy; reboot-required state is reported for controlled maintenance.
<!-- END AUTO:PATCHING -->

## Reviewed Nextcloud HTTPS configuration

**Verified: 2026-10-26.** Manual operational evidence; this section does not replace automated assessments.

- HTTPS hostname: `nextcloud.home.jrwroberts.co.uk`.
- Nginx listens on `192.168.2.53:443` with a trusted certificate.
- Docker publishes Nextcloud HTTP only on `127.0.0.1:8080`.
- Independent testing from `admin-01` confirmed that `192.168.2.53:8080` refuses connections.
- HTTPS `/status.php` and `/login` returned HTTP 200 after cutover.
- Nextcloud version: **`35.0.2.2`** (26 October 2026 upgrade from `34.0.3.2`); maintenance mode disabled; no pending DB upgrade.
- `APACHE_DISABLE_REWRITE_IP=1`.
- Nginx replaces incoming `X-Forwarded-For` and `X-Real-IP` with `$remote_addr`.
- Trusted proxies: `192.168.2.53` and `172.18.0.1`. The Nginx access log observed client `192.168.2.48` while Apache observed Docker peer `172.18.0.1`; the installed Nextcloud forwarded-header code was reviewed, but runtime-resolved application IP was not independently observed.
- Certbot timer enabled and active; `35-nextcloud-nginx` deploy hook installed.
- Certbot dry-run renewal via Cloudflare DNS-01 succeeded; a directly triggered deploy-hook Nginx reload also succeeded on 2026-10-26. Real production renewal not yet observed.
- Preferred hardened configuration checkpoint: `/root/nextcloud-hardened-baseline-20261026/`.
- Historical 2026-10-21 rollback checkpoint must not be restored routinely because it reopens LAN HTTP.
- Nextcloud 35 image upgraded and scanned on 2026-10-26: CRITICAL 4 (was 33), HIGH 231 (was 502); report-level triage of remaining CVEs is outstanding.
- Hardened HTTPS configuration is already managed through `homelab-platform`; the Nextcloud 35 upgrade is on branch `security/nextcloud-34-to-35`, commit `519cbc31`, pending review/merge.

The 2026-10-15 automated assessment predates HTTP isolation and may report the former LAN-facing port 8080.

## Nextcloud release and deployment change history

| Date (UTC) | Change and evidence | Git / release references |
| --- | --- | --- |
| 2026-10-26 | Upgraded server 34.0.3.2 to **35.0.2.2**, using `nextcloud:35.0.2-apache` in both `app` and `cron`; PostgreSQL 18.6 and Redis 8.2.9 not recreated. Approval-gated Ansible run: `ok=12 changed=5 failed=0`. HTTPS status verified, HTTP bound only to `127.0.0.1:8080`, maintenance off and no DB upgrade pending. | Branch `security/nextcloud-34-to-35`, commit `519cbc31`; `IaC/ansible/playbooks/nextcloud-upgrade-35.yml` |
| 2026-10-26 08:53 | Fresh `homelab-trivy-cloud.service` scan succeeded; complete 4/4 image coverage. Nextcloud CRITICAL rows **33 to 4**, HIGH **502 to 231** compared with historical image 34 report. Remaining CVEs not yet individually triaged. | [Security evidence](../../security/CONTAINER-VULNERABILITY-STATUS.md) |
| 2026-10-26 | Upstream Nextcloud **35.0.2** maintenance release (published 15 Oct) includes sharing-permission, session-cookie, encryption-metadata, filename-handling and performance fixes. These are upstream release notes, not independent functional/security test results for this host. | [Full official 35.0.2 release notes](https://github.com/nextcloud-releases/server/releases/tag/v35.0.2) |

Operator confirmed there was no production user data requiring preservation and selected direct 34.0.3 to 35.0.2 migration. This does not make a database downgrade automatically safe; application rollback after schema migration requires an appropriate state restore. See [Nextcloud HTTPS and upgrade change list](../../security/NEXTCLOUD-HTTPS-HARDENING.md).

## Monitoring and security

- Grafana host dashboard:
- Zabbix / Node Exporter / other monitoring:
- Alerting:
- Vulnerability findings:
- Firewall/access policy:
- Accepted risks:

## Ownership and administration

- Owner / responsible person:
- Management method:
- Configuration source:
- Patching / maintenance:
- Backup / recovery:
- Planned retirement / replacement:

## Evidence history

| Date | Evidence / change | Source | Reviewed by |
|---|---|---|---|
| 2026-10-26 | Nextcloud 35.0.2.2 application upgrade, full Trivy rescan, hardened HTTPS retained | Ansible playbook, Docker inspection, scanner journal | User-provided live command output |

## Notes

- 
