<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 DHCP-driven automatic device pages — issue #291

**Status: Router-01 DHCP source and first Grafana page CANARY PASSED LIVE (17 total; 16 retained); new automatic page timer DISABLED. Email path readiness PASSED LIVE; integrated DHCP email code STAGED IN GIT only (not installed/activated).**

## Goal

For a device receiving a DHCPACK from `router-01` dnsmasq, create **one** Grafana dashboard with a stable MAC-derived UID. A DHCP renewal, hostname update or IP change updates the existing page. Join in the existing `monitor-01` Nmap, MAC/OUI and discovery evidence as it becomes available. The OS remains explicitly **inferred** (Nmap match score), or **unknown/pending** if the device does not expose enough evidence.

The old ASUS/HP collectors and their 57 deleted dashboards (issue #287) are **not** restored.

## Data flow

```text
router-01 dnsmasq DHCPACK
         |
         v
Existing router DHCP telemetry -> monitor-01 Loki (router-01/dnsmasq labels)
         |
         v
Read-only bounded, source-labelled DHCPACK query (36h, <=3000 events)
         |
         v
MAC-keyed private state on monitor-01 (no duplicate pages on IP change)
         |
         +--> Existing discovery inventory for MAC/vendor/on-line state
         +--> Existing Nmap deep-profile for OS guess + open TCP services
         |
         v
Ansible-managed generator -> dedicated Grafana file-provider directory
         |
         v
Router DHCP Devices folder; one generated dashboard per MAC
```

Only validated DHCPACK(eth0) records within `192.168.2.0/24` create new pages. A pending OS means the existing targeted, bounded Nmap worker has not yet obtained a current match; it does not start an extra scan. Locally administered MAC addresses are retained as stable observations without inventing a manufacturer. Static-IP-only machines that do not request DHCP are **not** enrolled by this DHCP-driven generator.

**Source qualification:** The code is built to use the existing router-01 DHCP Loki pipeline. Its live event labels, freshness and volume must still pass the operator's read-only preflight. The currently available 38 network discovery records must not be mistaken for 38 confirmed DHCP lease clients. The default router lease file is checked separately but not copied or published; no DNS browsing-history export is involved.

## Preflight and rollout gates

1. **Read-only source check**: `router-01-dhcp-device-pages-preflight.yml`. Verify active dnsmasq, router lease evidence, local Alloy/forwarder states, positive well-formed router DHCPACK events in Loki, existing Nmap/inventory JSON schemas, six discovery timers and two protected Grafana providers. Does **not** make changes. If `router_source_ready_for_canary=false`, stop and investigate; do not fake an event.
2. **Source-only staging (explicit approval)**: `router-01-dhcp-device-pages-stage.yml` with `-e router_dhcp_device_pages_stage_approved=true`. Installs the script and audit helper, an isolated source directory and **disabled** service/timer. It does not start a timer, touch Grafana providers, change router configuration or scan.
3. **One-device canary (different explicit approval)**: `router-01-dhcp-device-pages-canary.yml` requires `-e router_dhcp_device_pages_canary_approved=true -e router_dhcp_device_pages_canary_phrase=CREATE_ONE_ROUTER_DHCP_DEVICE_PAGE`. Requires original 16 dashboard UID fingerprint, a clean new output directory, positive router DHCPACK data, a successful check-only preview, and rendered canonical provider config with the new provider explicitly opted in. It restarts **Grafana only**, creates exactly one source JSON, polls Grafana for 17 dashboards with all original 16 protected UIDs unchanged, leaves the new timer **disabled**.
4. **Automatic activation (separate approval)**: `router-01-dhcp-device-pages-enable.yml` requires `-e router_dhcp_device_pages_enable_approved=true -e router_dhcp_device_pages_enable_phrase=ENABLE_ROUTER_DHCP_DEVICE_PAGES`. Requires canary and router DHCP source proof, then enables only the new five-minute timer. It adds at most **10** new MAC pages per worker run to avoid flooding. Existing pages are refreshed for IP/OS/service changes.
5. **Independent postflight**: `router-01-dhcp-device-pages-postflight.yml` checks device-page file/state count, original Grafana UID fingerprint, six old discovery timers, the new timer, protected first-seen registry, Grafana and Prometheus. No writes, scans, restarts or backups.

The Grafana provider is **default-off** in `grafana-dashboard-provider.yml.j2` to prevent accidental activation from a general monitoring-stack deployment. Its permanent enablement must be reconciled in IaC only **after** a successful live canary and activation. Until then, avoid unguarded full `monitoring.yml` redeploys that could revert the opted-in provider.

## File locations on monitor-01 (after approved staging)

- Generator: `/usr/local/sbin/router-dhcp-device-pages`
- Read-only audit: `/usr/local/sbin/router-dhcp-device-pages-audit`
- Private MAC-keyed state: `/var/lib/homelab-network-hosts/router-dhcp-device-pages.json`
- Grafana sources: `/opt/monitoring/grafana/provisioning/dashboards/router-dhcp-devices/routerdhcp-*.json`
- Timer: `router-dhcp-device-pages.timer`, service: `router-dhcp-device-pages.service`

The generated dashboard JSON files and state are **local operational evidence** and must never be committed with private MAC/IP/hostname values to Git. Source code/tests/docs contain no private DHCP lease records. No one-shot scan, legacy ASUS file, direct SQLite mutation, or automatic dashboard deletion is permitted. If a canary or postflight fails, stop rather than replaying earlier destructive cleanup.

## Operator first action

Synchronise a clean worktree for branch `feature/router01-dhcp-device-pages-20261103`, verify `git diff --check`, run preflight `--syntax-check`, then run the same preflight with `--ask-become-pass`. Capture the sanitized counts for router leases, router DHCPACK Loki events and Nmap profiles. Do not run stages 2–4 until source integrity is verified.

## 3 November 2026 — First live dashboard canary PASS; email gate next

- Operator-approved one-device canary **PASSED LIVE**: `monitor-01 ok=36 changed=3 failed=0`, `router-01 ok=8 changed=0 failed=0`. Grafana returned **17 total dashboards: original 16 preserved and exactly 1 MAC-stable router-DHCP page**, with the generator timer **still disabled**. No additional scan, DNS/SMTP send, router change, backup or legacy-collector reactivation.
- **New-device email is not yet integrated into the router-DHCP page generator.** The independent discovery collector already invokes `homelab-network-device-email-alert` and maintains the existing `alerted-macs.json` first-seen registry, previously containing 56 MAC entries. That old notification path is based on the discovery inventory rather than newly provisioned DHCP pages; don't claim a router-only DHCP client will trigger an email.
- To avoid duplicated alerts, keep **one shared MAC-level notification ledger** and respect its existing alerted/baseline entries; do not introduce a second sender that independently emails from the newly generated page state. No retrospective notification blast for the 26 known lease clients or the canary page. Ideally emails include device/IP/hostname/vendor, OS evidence if actually available, and the MAC-stable Grafana page URL, with unknown OS explicitly labelled pending. Existing recurring DHCPACKs must not create another email.
- Before implementing/switching notification integration, run the new **read-only** `router-01-dhcp-device-email-preflight.yml`: verifies original 16 plus canary 1 Grafana UIDs, the existing notifier's systemd ExecStartPost hookup, the recipient environment **without exposing address**, the protected first-seen registry (>=56 entries), the canary page's MAC correspondence, and SMTP greeting from mail-relay-01. **Does not send an email.** A valid SMTP greeting proves reachability only, not delivery.
- **Do not run automatic `router-01-dhcp-device-pages-enable.yml` yet.** Keep the timer disabled until the notifier integration, sender recipient verification, deduplication policy, tests, and separately approved end-to-end delivery check are completed. Do not rerun the one-device canary.

## 3 November 2026 — Shared first-seen DHCP email integration (Git-only, not activated)

**Read-only live email preflight PASSED:** `monitor-01 ok=9 changed=0 failed=0`. Existing collector `homelab-network-device-email-alert` has a verified `ExecStartPost` hook, configured recipient (not printed), and protected `alerted-macs.json` with **56** prior device identities; canary DHCP device is already in that ledger (must NOT re-alert). `mail-relay-01` returns an SMTP 220 greeting, but **no test email has been sent**, so inbox delivery is not yet proven.

**Architecture:** Reuse the existing network collector as the **sole SMTP sender**, not a second independent DHCP email service. The existing MAC-based first-seen ledger remains the single deduplication source. The new `dhcp_device_email_policy.py` is a **read-only** candidate provider. It contributes a router DHCP device only after the separate approved activation marker at `/etc/homelab-network-hosts/router-dhcp-alerts.enabled.json` exists, the MAC is absent from the existing first-seen ledger, its original DHCPACK `first_seen_ns` is AFTER the marker timestamp, and its matching Grafana JSON page exists. This avoids retrospective blasts for old DHCP leases and the canary device. The existing notifier runs after the independent five-minute discovery collector, and appends DHCP candidates, a stable per-device dashboard URL and Nmap-inferred OS (or "Pending identification") to the email. A normal DHCP renewal or IP change never re-alerts a registered MAC. No extra scanning, raw DNS history or router changes are needed.

**Known timing limitation:** The legacy collector may see a device before the new five-minute DHCP page worker creates its page. In that race, the original first-seen email can arrive without a Grafana page link. Once the page exists, the DHCP source uses that same ledger rather than sending another message. We will NOT claim guaranteed exactly-once email delivery during an SMTP/process crash; each successful send is committed immediately to reduce replay risk. A locally randomised MAC looks like a separate device if it changes.

**Rollout after successful canary, in order (each separate gate):**

1. `router-01-dhcp-device-email-stage.yml` with `-e router_dhcp_email_stage_approved=true`: installs the safe, no-send library and an **inert candidate notifier** beside the existing notifier. It verifies original notifier, recipient and registry checksums remained unchanged. No active mailer replacement, no email, no timer change.
2. `router-01-dhcp-device-email-activate.yml` with `-e router_dhcp_email_activate_approved=true -e router_dhcp_email_activate_phrase=ENABLE_SHARED_MAC_DHCP_EMAIL_ALERTS`: rechecks email preflight and live 17-dashboard canary; refuses activation marker replay and running collector; copies candidate to original mailer, tests **--preview** before and after, creates the restrictive, **future-only activation timestamp** marker LAST, protects recipient and 56+ MAC ledger hashes. Does not send mail or start the new page timer.
3. `router-01-dhcp-device-email-postflight.yml`: independently read-only validates future-only activation, unchanged original Grafana identities, same approved notifier code, shared 56+ MAC registry, owner service and **--preview** without sending.
4. **Optional explicit test email** `router-01-dhcp-device-email-test.yml` requires `router_dhcp_email_test_approved=true` and exact phrase `SEND_ONE_ROUTER_DHCP_ALERT_TEST_EMAIL`. Sends one test through the *already configured* `mail-relay-01` path, makes no fake MAC, then verifies ledger/recipient unchanged. SMTP submission alone does not prove inbox delivery; operator must confirm receipt.
5. Only after these gates and explicit operator approval, run the separate `router-01-dhcp-device-pages-enable.yml`. It now **refuses to enable** automatic page generation without the approved DHCP email activation marker and original network-discovery timer.

All code and no-send tests are in branch `feature/router01-dhcp-device-pages-20261103`; current CI [validation](https://github.com/jrwroberts1976/homelab-platform/actions/runs/41673996841) passed. **Do not run** the canary again or old #287 retirement. Preserve automatic first-seen history and all 16 protected original Grafana dashboards.
