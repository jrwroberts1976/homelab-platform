# Nextcloud 35 remaining CRITICAL image CVEs — exposure assessment (26 October 2026)

<!-- estate-authority: IaC/inventory/estate.json -->

**Status:** Analysis-only documentation; no additional host or container changes. Based on user-run read-only Ansible commands and Debian security tracker checks dated 2026-10-26. **Do not reduce Trivy finding counts without a new evidence-based scan or patched package.**

## Scope and scan provenance

- Host: `cloud-01`; Nextcloud `35.0.2.2`, image `nextcloud:35.0.2-apache`.
- Most recent verified full Trivy image scan: 2026-10-26 08:53:20 UTC, before EXR policy rollout. Nextcloud image **4 CRITICAL / 231 HIGH** package rows; cloud-01 all-image total **18 CRITICAL / 427 HIGH**.
- Debian 13 Trixie image base; the four CRITICAL package findings are below. Trivy severity describes scanner metadata and does not establish network reachability or exploitability.

| CVE | Trivy package and installed version | Operational disposition | Remaining action |
| --- | --- | --- | --- |
| `CVE-2026-42216` | `libopenexr-3-1-30 3.1.13-2` | **ImageMagick EXR coder route mitigated** via read/write policy-denial tests in app and matching policy in cron; Debian library remains unpatched | Track an approved Debian image/package fix; retain finding |
| `CVE-2026-42217` | `libopenexr-3-1-30 3.1.13-2` | **ImageMagick EXR coder route mitigated**, not a library-wide fix | Same as above |
| `CVE-2026-6653` | `libxml2 2.12.7+dfsg+really2.9.14-2.1+deb13u3` | **Open; vulnerable package loaded; actual exploit route unconfirmed** | Watch Debian 13 security tracker and reassess application reachability |
| `CVE-2026-93221` | `linux-libc-dev 6.12.113-1` | **Open package advisory; no running NFS server detected** on cloud-01 | Monitor host kernel and NFS server state, track supported Debian 13 kernel fix |

## CVE-2026-6653 — libxml2 in PHP/Nextcloud

- `dpkg-query -W libxml2` returned `2.12.7+dfsg+really2.9.14-2.1+deb13u3`. `php --ri libxml` reported compiled **2.9.14**, loaded **20914**. `ldconfig -p` showed `/lib/x86_64-linux-gnu/libxml2.so.2`.
- Installed PHP XML extensions include DOM, libxml, SimpleXML, XML, XMLReader and XMLWriter. Nextcloud 35.0.2.2 has DAV, federation, Office and other bundled apps enabled. These facts show XML capability, **not confirmed exploitation**.
- PHP reports constants `LIBXML_NOENT`, `LIBXML_DTDLOAD`, `LIBXML_DTDVALID` and `LIBXML_NONET` defined; `LIBXML_NO_XXE` was unavailable. Availability of constants is **not evidence of their use**.
- Searches of app, core, lib, bundled `3rdparty` and custom_apps code for explicit `LIBXML_(NOENT|DTDLOAD|DTDVALID)`, `substituteEntities`, `resolveExternals`, and `setParserProperty` returned no matches. **Negative grep results are not proof that crafted XML cannot reach the affected libxml2 function.**
- Bundled XML parser entry points were present in Sabre XML, phpseclib, Symfony DOM Crawler/XLIFF, and Masterminds HTML5. Symfony `addXmlContent()` defaults to `LIBXML_NONET`, but callers can override options; grep showed no direct caller in the Nextcloud app/core/lib directories searched.
- Sabre XML `Service.php` defines public `$options = 0`, passes those options to `XMLReader::XML(...)`, and its `Reader.php` disables the external entity loader only if `LIBXML_VERSION < 20900` (not true for loaded 2.9.14). This behaviour does **not** demonstrate CVE-2026-6653 is exploitable or mitigated.
- Debian's [security tracker](https://security-tracker.debian.org/tracker/CVE-2026-6653) lists Trixie vulnerable, notes `no-dsa` (minor issue), and lists a fix in newer development releases, not the observed Trixie package. Distinguish Debian's advisory prioritisation from Trivy's CRITICAL severity.
- **Decision:** No change to PHP XML extensions or vendored libraries. Keep finding open and re-evaluate when an approved Debian 13 fixed package / Nextcloud image is published or if a relevant untrusted XML entry point is demonstrated.

## CVE-2026-93221 — kernel NFSv4 server, NOT an actively running Nextcloud NFS service

- The [Debian security tracker](https://security-tracker.debian.org/tracker/CVE-2026-93221) identifies an `nfsd` concurrency bug in NFSv4 grace/reclaim handling, affecting Debian's 6.12 security kernel branch as checked. A kernel fix exists upstream / in newer development releases; do **not** assume the Debian 13 6.12 kernel includes that fix.
- Host `uname -r`: `6.12.111+deb13-cloud-amd64`. **This is not the same thing as** Nextcloud image's `linux-libc-dev 6.12.113-1`. Container header packages do not supply the running host kernel.
- Host `systemctl is-active nfs-server.service`: `inactive`; `systemctl is-enabled`: `not-found`. No `nfsd` entry in `/proc/modules`, no readable `/proc/fs/nfsd/threads` status, and no TCP 2049 listener in `ss -ltn`.
- These controls provide good evidence that the NFS server-specific vulnerable code path is **not active on cloud-01 at the time of inspection**. This does not prove the host kernel has received the fix, nor does it describe exposure on other homelab hosts.
- **Decision:** No Nextcloud container change or header removal. Keep `nfsd` disabled unless explicitly needed; track supported Debian 13 kernel fixes and security patch compliance using the host IaC baseline. Reassess immediately if any NFS-server role is proposed.

## Acceptance and next actions

- No actions taken against the running application during this triage. Final `php occ status`: installed true, version 35.0.2.2, maintenance false, needsDbUpgrade false.
- Nextcloud EXR policy was **successfully deployed earlier** with Ansible recap `ok=18 changed=1 failed=0 skipped=1`, and its decoder-level mitigating evidence is separately documented in [EXR mitigation runbook](NEXTCLOUD-EXR-MITIGATION-2026-10-26.md).
- Maintain all four package-based CRITICAL rows in historical Trivy evidence. Two have a verified **partial compensating control**, two have an **exposure assessment only**.
- Track potential vendor fixes with approved image version updates, repeat full Trivy scan after any image change, and update issue #187 without claiming package remediation prematurely.
