# Nextcloud HTTPS hardening

<!-- estate-authority: IaC/inventory/estate.json -->

Status: Deployed and independently verified
Verified: 2026-10-26
Host: cloud-01
Ansible branch: security/nextcloud-https

## Architecture

- Host: Debian 13 VM200 on PROXMOX
- Nextcloud: 35.0.2.2 (upgraded from 34.0.3.2 on 2026-10-26)
- HTTPS: nextcloud.home.jrwroberts.co.uk
- Nginx listener: 192.168.2.53:443
- Docker HTTP backend: 127.0.0.1:8080
- PostgreSQL and Redis: Docker Compose services

Nginx provides HTTPS and forwards requests to the
loopback-only Nextcloud HTTP backend.

Direct LAN access to 192.168.2.53:8080 is blocked.

## Security controls

- APACHE_DISABLE_REWRITE_IP=1
- Nginx replaces X-Forwarded-For with $remote_addr
- Nginx replaces X-Real-IP with $remote_addr
- X-Forwarded-Proto is set to https
- Trusted proxies: 192.168.2.53 and 172.18.0.1
- Nextcloud trusted domains include the HTTPS hostname

Reverse-proxy peer and forwarding code reviewed on 2026-10-26; application-level resolved client IP was not independently observed.

## Verified acceptance tests

On 2026-10-26:

- HTTPS status endpoint returned HTTP 200
- HTTPS login returned HTTP 200 during cutover
- TLS verification returned 0
- Direct LAN HTTP returned a connection failure
- Docker published only 127.0.0.1:8080
- Nextcloud maintenance mode was disabled
- No database upgrade was required

A transient 502 occurred during Nginx cutover.
The second HTTPS verification attempt succeeded.

## Infrastructure as Code

Managed in homelab-platform.

Relevant components:

- IaC/ansible/playbooks/nextcloud-certificate.yml
- IaC/ansible/playbooks/nextcloud-https-stage.yml
- IaC/ansible/playbooks/nextcloud-https-finalize.yml
- IaC/ansible/playbooks/nextcloud-app-hardening-stage.yml
- IaC/ansible/roles/cloud_stack/
- IaC/ansible/scripts/nextcloud-http-isolation-cutover.sh
- IaC/ansible/playbooks/nextcloud-upgrade-35.yml (one-time, approval-gated version 35 upgrade)

Full cloud-stack deployment requires explicit approval
and may reconcile PostgreSQL, Redis, cron and Nextcloud.

Do not run cloud-stack.yml as a routine HTTPS repair.

## Certificate renewal

- Certbot timer enabled and active
- Deploy hook: 35-nextcloud-nginx
- Hook checks the renewed certificate lineage
- Nginx configuration is tested before reload

Certbot renewal dry-run (Cloudflare DNS-01) and deploy-hook Nginx reload were tested successfully on 2026-10-26. The hook was invoked directly with the expected lineage; actual production certificate renewal remains unobserved. See the separate renewal-evidence PR #190.

## Recovery

Historical cutover checkpoint:

/root/nextcloud-http-isolation-20261021/

WARNING: This checkpoint contains the previous LAN-facing
HTTP configuration. Restoring it would reopen port 8080.

It is retained as historical emergency recovery evidence,
not the desired long-term production configuration.

For routine recovery, preserve the hardened loopback
binding and investigate Nginx and application health first.

The cutover script must not be rerun without reviewing
its assumptions and rollback configuration.

### Hardened recovery checkpoint

Verified: 2026-10-26

Preferred configuration recovery baseline:
`/root/nextcloud-hardened-baseline-20261026/`

Contains:
- `docker-compose.yml`
- `nextcloud-https.conf`

Both files were verified against the running configuration.

The earlier checkpoint dated 2026-10-21 is historical
and would reopen LAN-facing HTTP port 8080 if restored.

Restore operations require explicit approval.
Configuration recovery does not replace application-data backups.

## Change list — 26 October 2026: Nextcloud 34 to 35

| Item | Before | After / evidence |
| --- | --- | --- |
| Nextcloud server | 34.0.3.2 (image `nextcloud:34.0.3-apache`) | 35.0.2.2 (image `nextcloud:35.0.2-apache`) |
| Docker services | `app`, `cron` on 34.0.3 | Both recreated on 35.0.2; `--no-deps` used |
| Dependencies | PostgreSQL 18.6, Redis 8.2.9 | Both still running and healthy; not recreated |
| HTTPS / networking | Nginx HTTPS; backend `127.0.0.1:8080` | HTTPS version/health checks passed; loopback-only binding preserved |
| Application migration | Maintenance disabled before upgrade | `installed=true`, `maintenance=false`, `needsDbUpgrade=false` after upgrade |
| Ansible / Git | Prior cloud-stack pin 34.0.3 | `security/nextcloud-34-to-35`, commit `519cbc31`; approval-gated `IaC/ansible/playbooks/nextcloud-upgrade-35.yml` |
| Trivy image | Historical 33 CRITICAL / 502 HIGH rows | Fresh 26 Oct 08:53 UTC scan: 4 CRITICAL / 231 HIGH (29 fewer critical and 271 fewer high) |

Live deployment: upgrade Ansible recap `ok=12 changed=5 failed=0 unreachable=0`; post-deployment `docker compose ps`, `php occ status`, backend port, and HTTPS verification passed. The application and cron both use immutable local image ID `sha256:1d5a25fae9df8df7ba9b49dbd75628c5e08e9a2fc463c02596641ee950935937` according to the fresh scanner inventory. The user confirmed there was no production user data to preserve and chose a **direct** 34.0.3 to 35.0.2 upgrade, without deploying 34.0.5. A configuration checkpoint is not a post-migration database backup: do **not** assume a Docker tag downgrade can reverse the schema migration.

### Official upstream release notes

- [Nextcloud 35.0.2 (15 October 2026) — full server changelog](https://github.com/nextcloud-releases/server/releases/tag/v35.0.2).
- [Nextcloud maintenance and release schedule](https://github.com/nextcloud/server/wiki/Maintenance-and-Release-Schedule).

Selected 35.0.2 upstream changes: limits on reshared permissions and link-expiration defaults; encryption size/version consistency; remember-me cookie/session handling; rejecting filenames with newline characters; improvements to rename and search behaviour; and setup-check performance. These are **upstream release-note items**, not a claim that the corresponding features were exercised in this homelab or that particular CVEs are remediated.

### Security interpretation and remaining work

The Trivy 35 report contains **4 CRITICAL and 231 HIGH package-finding rows**; historical 34 image counts were 33 CRITICAL and 502 HIGH. These are not counts of unique CVEs or confirmed exploitable issues. Scan completed at 2026-10-26 08:53:20 UTC; `RUNNING_IMAGES=4`, `VALID_IMAGES=4`, `SCAN_COMPLETE=TRUE` on cloud-01. Investigate the 4 remaining critical findings by advisory, package and fixed version; preserve the old scan baseline for comparison. See [container vulnerability status](CONTAINER-VULNERABILITY-STATUS.md).

The Nginx log identified client `192.168.2.48`, Apache saw Docker bridge peer `172.18.0.1`; trusted-proxy configuration and Nextcloud `getRemoteAddress()` source were reviewed. The resolved address **inside a live application request** was not directly observed. Certbot dry-run renewal and an explicitly invoked Nginx reload hook passed on 26 Oct; an actual production renewal has not been observed.

## Nextcloud OpenEXR coder mitigation — verified 26 October 2026

**Deployed:** Ansible-managed ImageMagick policy denies EXR decoding and encoding in the Nextcloud application. The policy retains all eleven active upstream baseline restrictions and is mounted read-only into both `cloud-01-app-1` and `cloud-01-cron-1` via Compose.

The first approved execution installed the policy and recreated app, but its original `getImageBlob()` EXR write test returned an ambiguous exception and halted before cron. Subsequent direct read/write probes confirmed the app returned explicit `security policy 'EXR'` denials. The corrected playbook was committed to PR #192 and validated, then an explicitly approved second cutover completed **successfully** with `ok=18 changed=1 failed=0 skipped=1`. App recreation was skipped because its read-only policy mount was already present; only cron was recreated. PNG and JPEG encoding, EXR read/write denial in app, cron's policy file, HTTPS, Nextcloud 35.0.2 health and loopback binding all passed. PostgreSQL and Redis remained healthy and unchanged.

**Security interpretation:** `CVE-2026-42216` and `CVE-2026-42217` are mitigated for the ImageMagick EXR coder path, **not patched**. Their affected Debian OpenEXR library package remains present; Trivy may still flag both. The other findings `CVE-2026-6653` (libxml2) and `CVE-2026-93221` (linux-libc-dev) require separate assessment. PR #192 is the pending repository integration until merged.

See [full EXR decoder remediation, evidence, and rollback runbook](NEXTCLOUD-EXR-MITIGATION-2026-10-26.md).

## Outstanding work

- Verify application-level resolved client IP on an authenticated/runtime Nextcloud request; do not assert this is complete based on code inspection alone.
- Reassess and reduce trusted proxies only when direct evidence supports it.
- Observe future real certificate renewal and Nginx reload; dry-run and hook invocation have passed.
- Triage four remaining CRITICAL Nextcloud image rows (and 231 HIGH) by specific CVE/package/fix; refresh Grafana/Prometheus.
- Review/merge the upgrade branch and documentation; avoid re-running the one-time upgrade playbook after success.
