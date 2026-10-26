# Nextcloud 35 ImageMagick EXR decoder mitigation — 2026-10-26

<!-- estate-authority: IaC/inventory/estate.json -->

**Status: PARTIALLY DEPLOYED 2026-10-26 at ~10:17 local — app EXR reading policy DENIAL verified; cron NOT YET RECREATED. Findings remain OPEN until post-deployment verification.**

Host: `cloud-01` (192.168.2.53), Nextcloud `35.0.2.2` on `nextcloud:35.0.2-apache`. Managed by Ansible. This is a targeted mitigation of the EXR decoding path and not an upgrade to patched OpenEXR packages.

## Evidence collected from the running application

- Trivy completed a full scan on 2026-10-26 at 08:53:20 UTC; Nextcloud image has 4 CRITICAL and 231 HIGH package-finding rows after the upgrade.
- Two CRITICAL findings are `CVE-2026-42216` and `CVE-2026-42217` in Debian package `libopenexr-3-1-30` version `3.1.13-2`, with no fixed version listed in the local Trivy report.
- `Imagick::queryFormats("EXR")` returned `["EXR"]`. Imagick 3.8.1 is enabled and uses ImageMagick 7.1.1-43.
- The EXR coder at `/usr/lib/x86_64-linux-gnu/ImageMagick-7.1.1/modules-Q16/coders/exr.so` was confirmed by `ldd` to link against `libOpenEXR-3_1.so.30`, `libOpenEXRCore-3_1.so.30` and `libImath-3_1.so.29`.
- Existing `/etc/ImageMagick-7/policy.xml` is an *open* policy: it contains seven resource/path restrictions and explicit URL/HTTP/HTTPS denies (plus the undefined deny), but no EXR deny.
- Successful Nextcloud `php occ status`: 35.0.2.2, installed true, maintenance false, needsDbUpgrade false.
- These observations confirm an installed and exposed ImageMagick **coder capability**; exploitation through a specific Nextcloud upload/preview endpoint has **not** been demonstrated.

## Actual partial cutover and diagnostic — 2026-10-26

The user explicitly approved the guarded playbook `nextcloud-exr-hardening.yml`; it stopped at its original Imagick PHP test with `ok=10 changed=4 failed=1`.

- The controller passed identity/version and stock ImageMagick baseline checks, created `/opt/cloud-01/imagemagick/policy.xml`, rendered the Compose mounts and recreated only `cloud-01-app-1`.
- Existing app had the managed policy `<policy domain="coder" rights="none" pattern="EXR"/>` in `/etc/ImageMagick-7/policy.xml`; **EXR reading** actually failed with `attempt to perform an operation not allowed by the security policy 'EXR' @ ... IsCoderAuthorized`.
- The original EXR **writing** test used `getImageBlob()` on a newly created image and returned the ambiguous exception `Failed to get the image contents (empty or invalid image?)`. The original playbook rejected this as an unexpected exception (rc 12), before reaching the EXR read test. This is a **verification design fault, not evidence of permitted EXR writes**. EXR writing remains unverified.
- Subsequent user-run diagnostics confirmed Nextcloud 35.0.2.2: installed true, maintenance false, needsDbUpgrade false. HTTPS status returned the expected healthy JSON and app port stayed `127.0.0.1:8080`; PostgreSQL and Redis healthy with their original containers.
- `cloud-01-cron-1` was still the earlier instance, so **do not yet describe the whole service as mitigated**.
- The playbook was revised to accept either the original eleven-rule policy or the approved twelve-rule hardened policy, skip app recreation when its read-only mount already exists, and separately probe EXR read and **EXR write with `writeImage("EXR:/dev/null")`**, requiring a literal ImageMagick security-policy denial. It still fails closed on unexpected failures.
- **Do not rerun the old checked-out playbook.** Fetch the latest security branch, run static/estate/syntax checks, inspect changes; then seek explicit approval for live continuation. If the revised write probe fails, inspect the exception and adjust the test; do not bypass the security gate or merge as successful.
- GitHub PR #192 remains open; live deployment is separate from merging source changes. Rollback is not indicated solely by the original verification error while application health remains good.

## Step 128 evidence — EXR write denial confirmed in the app

The user ran a standalone, read-only `docker exec cloud-01-app-1 php -r` diagnostic at approximately 10:17 on 2026-10-26. The test created an in-memory 1×1 Imagick image and called `writeImage("EXR:/dev/null")`. It returned an `ImagickException` with the exact message:

```text
attempt to perform an operation not allowed by the security policy `EXR' @ error/constitute.c/IsCoderAuthorized/454
```

This proves the deployed **app** policy denies EXR writing; the prior `readImage("EXR:/dev/null")` check separately proved EXR reading is denied by the same policy. This confirms the old `getImageBlob()` test was unsuitable as a policy-denial assertion. Neither successful diagnostic changes Nextcloud persistent files.

**Next action remains pending:** synchronize the revised IaC branch, validate the corrected playbook and complete its explicit approval-gated cutover. The app read-only policy mount is already installed, so the revised playbook should skip app recreation; cron still requires recreation with the same mount. Validate PNG/JPEG checks, EXR policy read/write denial, HTTPS, loopback binding and healthy app/cron/db/redis before recording end-to-end mitigation. Do not close either CVE yet.

## Proposed IaC implementation

- `IaC/ansible/roles/cloud_stack/templates/imagemagick-policy.xml.j2` captures the **exact effective active policy rules** from the observed Nextcloud 35 image and appends `<policy domain="coder" rights="none" pattern="EXR"/>` as the last rule. The original file's long explanatory comments and DTD are not copied; its active restrictions are retained. Review this policy against each future upstream image before upgrading.
- `IaC/ansible/roles/cloud_stack/defaults/main.yml` specifies `cloud_nextcloud_imagemagick_policy_path` and `cloud_nextcloud_exr_policy_enabled` (true by default).
- `IaC/ansible/roles/cloud_stack/tasks/main.yml` manages `/opt/cloud-01/imagemagick/policy.xml` **after** the existing deployment approval gate, before Compose.
- `IaC/ansible/roles/cloud_stack/templates/docker-compose.yml.j2` bind-mounts that host policy **read-only** onto the **app and cron** containers at `/etc/ImageMagick-7/policy.xml`, conditional on `cloud_nextcloud_exr_policy_enabled`.
- Dedicated `nextcloud-exr-hardening.yml` validates the approved stock **or already-hardened** live policy, approval, host/version, XML, Docker Compose, PNG/JPEG operation, EXR read/write policy denial through PHP Imagick, HTTP loopback isolation and HTTPS. It recreates the app **only if its policy mount is missing**, then cron, with `--no-deps`.
- Dedicated `nextcloud-exr-rollback.yml` (explicit approval) renders Compose with policy mounts disabled, recreates app/cron only and checks health. The policy file remains on disk; the full cloud-stack role would reenable the mount because its canonical default is true, so do not run it until a failed mitigation has been resolved.

ImageMagick processes policy rules in order, with the **last matching rule winning**. Source: [official ImageMagick security policy documentation](https://imagemagick.org/security-policy/).

## Review and syntax checks — no deployment

From `admin-01` after fetching the branch:

```bash
cd ~/projects/homelab-platform
git fetch origin
git switch security/nextcloud-exr-policy-20261026
git pull --ff-only origin security/nextcloud-exr-policy-20261026
git diff origin/main...HEAD -- IaC/ansible
python3 scripts/validate-estate.py --base origin/main --head HEAD

cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/nextcloud-exr-hardening.yml --syntax-check
ansible-playbook -i inventory/hosts.yml playbooks/nextcloud-exr-rollback.yml --syntax-check
```

Review these results and the proposed configuration before any runtime change. A policy bind mount will restart the app and cron containers, briefly interrupting Nextcloud.

## Optional approved cutover — live write

**Only execute after successful validation and explicit change approval:**

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/nextcloud-exr-hardening.yml \
  --ask-become-pass -e nextcloud_exr_hardening_approved=true
```

Verify Ansible completes all tasks. Actual code-level acceptance requires PHP Imagick to throw a **security-policy** error on EXR reading and writing, while 1x1 PNG and JPEG encoding passes. `Imagick::queryFormats("EXR")` may continue listing EXR even when access is denied; that listing alone is not the enforcement test. Confirm `app`, `cron`, PostgreSQL and Redis running; Nextcloud version 35.0.2.2, HTTPS health and port `127.0.0.1:8080`.

## Explicit approved rollback — live write

If the policy breaks normal image processing, application health, or deployment:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/nextcloud-exr-rollback.yml \
  --ask-become-pass -e nextcloud_exr_rollback_approved=true
```

This restores the original image policy by removing the bind mounts. Preserve the failure evidence and review before reattempting. The rollback does not undo Nextcloud 35's database schema migration and does not change the Nextcloud version.

## Security tracking / closure

Track this work against homelab issue #187. **Do not mark the CVEs fixed or fully mitigated before a successful runtime enforcement test on both app and cron.** If deployed and enforcement passes, record them as **decoder access mitigated; vulnerable OpenEXR packages still present**. A fresh Trivy scan may continue reporting both CVEs until the packages are fixed, removed or the scanner database is updated.

Separate outstanding criticals: `CVE-2026-6653` (libxml2) and `CVE-2026-93221` (linux-libc-dev). Host kernel exposure should be assessed independently of installed container development headers.
