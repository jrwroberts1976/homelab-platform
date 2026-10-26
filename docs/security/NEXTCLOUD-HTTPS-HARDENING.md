# Nextcloud HTTPS hardening

Status: Deployed and independently verified
Verified: 2026-10-26
Host: cloud-01
Ansible branch: security/nextcloud-https

## Architecture

- Host: Debian 13 VM200 on PROXMOX
- Nextcloud: 34.0.3.2
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

Actual proxy-peer attribution remains to be verified.

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

Full cloud-stack deployment requires explicit approval
and may reconcile PostgreSQL, Redis, cron and Nextcloud.

Do not run cloud-stack.yml as a routine HTTPS repair.

## Certificate renewal

- Certbot timer enabled and active
- Deploy hook: 35-nextcloud-nginx
- Hook checks the renewed certificate lineage
- Nginx configuration is tested before reload

End-to-end renewal has not yet been tested.

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

## Outstanding work

- Verify actual Nextcloud proxy-peer IP attribution
- Reduce trusted proxies if evidence supports doing so
- Perform certificate renewal simulation
- Complete Nextcloud container CVE remediation
- Commit and review the IaC security changes
