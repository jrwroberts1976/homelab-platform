<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01: Bedroom ASUS fixed DHCP reservation — 29 October 2026

**STATUS: LIVE DEPLOYMENT VERIFIED — 29 October 2026.** Reviewed PR #219 merged as `7ff09647`; operator then executed the approval-gated Ansible writer on physical Pi `router-01`. DHCP pool `.100–.199` unchanged. Bedroom MAC-bound `.180` reservation active. The remainder of this runbook retains the source-stage design and historical operator commands for audit/rollback reference; do not repeat deployment merely because it appears here.

## Live deployment and independent postflight — 29 October 2026

- Local `admin-01` Git fast-forward to `7ff09647`, source and rollback playbook syntax checks **PASS**, protected local Ansible Vault content comparison `BEDROOM_MAC_VAULT=PASS`; MAC and vault password **not** included in any repository file.
- Operator-run approval-gated writer **`router-01 ok=28 changed=9 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0`**. Successful playbook completion includes candidate parser test, root-only off-path backup of original `router.conf`, scoped managed-block insertion, complete config validation, dnsmasq restart and service health. Exact backup filename was not provided; don't invent it. No rescue/rollback triggered.
- Separately executed read-only Ansible postflight: `dnsmasq`, `unbound`, `router-pppoe`, `nftables` each **active**; `dnsmasq --test` reports **syntax check OK**; `DHCP_POOL=PASS` (single identical `192.168.2.100–199` range), `BEDROOM_RESERVATION=PASS` (single MAC-bound `dhcp-host` for `.180`), `BEDROOM_LEASE=PASS` (exact private MAC and hostname `RT-AC86U-CCC8`, unexpired), WAN route `default dev ppp0 scope link`.
- Independent controller-side probes: `192.168.2.1` Pi gateway **PASS**, `192.168.2.2` ASUS Home **PASS**, `192.168.2.180` ASUS Bedroom **PASS**, `192.168.2.195` media-01 **PASS**. Direct `dig @192.168.2.1 example.com A` returned **NOERROR** with valid A records; `curl https://example.com` returned **HTTPS_STATUS=200**. This verifies real client-to-LAN, client DNS via router and client outbound HTTPS, beyond service-only checks. A later lease renewal/reboot-persistence test was **not** conducted; no claim that it was.
- `media-01` returned to service at `192.168.2.195/24`: `NetworkManager` active, `ipv4.method=auto`, default route via `.2.1` marked `proto dhcp`. Its address is **DHCP**, not a documented static exception. Any future reserved `.195` requires a **new** independently verified MAC and separate approved IaC; **do not exclude `.195`**.
- The historical `.181/.195` pool-splitting plan is **not applicable**. The old read-only `router-01-dhcp-exclusion-preflight-readonly.yml` presently asserts there are zero `dhcp-host` lines and will reject the new correct state; update it before reuse. Current estate registry and stale ASUS-as-primary-router records must be reconciled separately. Issue #206 tracks evidence and future work.

**No further configuration edits, forced DHCP renewals, firewall changes, ASUS changes, lease-file edits or system restarts were performed for the final read-only verification.**

## Verified current facts

The live Pi router is `router-01` at `192.168.2.1/24` (eth0), PPPoE on ppp0, running dnsmasq, Unbound and nftables. Its active `/etc/dnsmasq.d/router.conf` has one DHCP range `192.168.2.100–199` (24h), router and DNS options `192.168.2.1`. Previous operator-run read-only Ansible preflight: **20 OK, 0 changed, 0 failed**.

The user's ASUS Home RT-AC86U at `192.168.2.2` is manually **static**, outside the DHCP range. ASUS AiMesh UI identifies **Bedroom RT-AC86U**, Ethernet 1 Gbps, at `192.168.2.180`. The user confirmed Bedroom uses **DHCP**. The current Pi's lease file identifies `RT-AC86U-CCC8` at `192.168.2.180` and the user ran a local lease-to-ASUS-GUI MAC comparison: **RESULT: MAC MATCHES ASUS GUI**. The live lease must still be verified at change time.

The third ASUS router is **not in use**; historical lease records for `RT-AC86U-5228` and `RT-AC86U-6238` at old `192.168.3.x` addresses do not prove current connectivity. Historical `192.168.2.181` failed ARP and is **not** a confirmed current static address. At the historical drafting stage `media-01` was offline; it is now online and independently verified DHCP-managed at `192.168.2.195`, as documented in the live addendum above.

**Decision:** reserve the *existing* Bedroom `.180` address for its *verified* DHCP MAC, **without** changing the broad .100–199 DHCP pool, other leases, names, DNS, gateways or firewall. The earlier candidate split ranges excluding `.181` and `.195` are **superseded as an active recommendation**; do not deploy them. Treat `media-01` independently after its configuration is verified.

## Proposed exact managed change

Append only this block to the **existing** `/etc/dnsmasq.d/router.conf`:

```ini
# BEGIN ANSIBLE MANAGED BEDROOM ASUS DHCP RESERVATION
dhcp-host=<verified-DHCP-client-MAC>,192.168.2.180
# END ANSIBLE MANAGED BEDROOM ASUS DHCP RESERVATION
```

The placeholder above is **not a valid deployed MAC**. The real value is supplied from a protected **local Ansible Vault extra-vars file on admin-01**, never committed in plain text or written into a public GitHub issue. No hostname is specified in `dhcp-host`, so the client retains its own DHCP-provided name. dnsmasq supports MAC-bound fixed DHCP address assignment via `dhcp-host` (https://dnsmasq.org/docs/dnsmasq-man.html).

## Deployed Ansible source (historical design and safeguards)

- `IaC/ansible/playbooks/router-01-bedroom-dhcp-reservation.yml` requires **two explicit approvals**, non-check mode, execution from `admin-01` and the isolated, verified `192.168.2.1` Pi inventory. It verifies Pi physical eth0 MAC, gateway address, PPPoE route, core services, dnsmasq config composition, original range and an **unexpired** current Bedroom lease with exactly the user-approved MAC + IP + hostname.
- It creates a temporary **offline candidate configuration in /run** and checks it with the Pi's installed `dnsmasq --test` before touching the active router config. It writes a private backup of `router.conf` in `/var/backups/homelab-router/dnsmasq/` (mode 0600) **outside** the active dnsmasq include directory so the backup cannot be parsed as another configuration fragment.
- Only then it inserts the one managed block into the existing file, checks the full installed dnsmasq syntax, **restarts dnsmasq only**, verifies service and syntax. Failure triggers an attempt to remove its own block and restart the service in its original state. A short DNS/DHCP interruption is expected during any authorised restart; it does not intentionally touch PPPoE/firewall/LAN interfaces.
- `IaC/ansible/playbooks/router-01-bedroom-dhcp-reservation-rollback.yml` requires its **own** rollback/restart approvals, verifies the exact managed line and Pi identity, backs up the currently installed file outside the include directory, removes only this block, validates syntax and restarts only dnsmasq. On error it attempts to reinsert the block and recover the service. Do not blindly restore an old whole-file backup over later approved changes.
- GitHub CI tests playbook syntax and static guardrails, and invokes installed dnsmasq on a synthetic MAC-bound reservation inside the unchanged pool. CI does **not** prove runtime connectivity, availability, actual lease allocation or final deployment.

**These playbooks intentionally refuse ordinary read-only `--check` execution**. The approved writer ran successfully on 29 October; its accompanying rollback playbook is retained but **has not been run**. For future review use `ansible-playbook --syntax-check`, not a repeat of the live writer.

## Local private MAC vault — prepared and validated on admin-01 (retain privately)

The operator already created the private file on `admin-01` and verified its content (`BEDROOM_MAC_VAULT=PASS`). The following is the original setup command kept for disaster recovery; **do not run `ansible-vault create` again on the existing file**. Keep it outside Git and shell history:

```bash
umask 077
mkdir -p "$HOME/.config/homelab"
ansible-vault create "$HOME/.config/homelab/router-bedroom-vars.yml"
```

Its decrypted YAML content is:

```yaml
router_bedroom_client_mac: "<actual verified Bedroom DHCP client MAC>"
```

**Historical deployment command — successfully executed on 29 October; do NOT rerun without new explicit change approval** (restarts dnsmasq if changed):

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/router-01-postcutover-baseline.yml \
  playbooks/router-01-bedroom-dhcp-reservation.yml --limit router-01 \
  --ask-become-pass --ask-vault-pass \
  -e @"$HOME/.config/homelab/router-bedroom-vars.yml" \
  -e router_bedroom_reservation_apply_approved=true \
  -e router_bedroom_reservation_restart_approved=true
```

**Rollback command — for a separate approved rollback only**:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/router-01-postcutover-baseline.yml \
  playbooks/router-01-bedroom-dhcp-reservation-rollback.yml --limit router-01 \
  --ask-become-pass --ask-vault-pass \
  -e @"$HOME/.config/homelab/router-bedroom-vars.yml" \
  -e router_bedroom_reservation_rollback_approved=true \
  -e router_bedroom_reservation_restart_approved=true
```

## Operational validation and recovery gates

Before any live run: check current lease ownership/IP/expiry and dnsmasq status, inspect CI and exact PR diff, confirm access to the Pi independent of DHCP, agree a short maintenance window and prepare a local console/recovery route. After deployment: recheck dnsmasq active/syntax, Bedroom IP remains .180 on lease renewal, Home AP .2, existing LAN client internet/DNS, PPPoE and firewall unchanged. **Reservation installation does not itself force immediate client renewal.**

If Ansible cannot reconnect or dnsmasq fails despite rescue, use the protected off-path backup and local console to investigate. Do not rely on automated rollback as a guarantee of zero outage.

The live installation and independent connectivity evidence are recorded at the start of this file, in `gpt-handover.md` and issue #206. Remaining tasks are to revise the **split-exclusion preflight** (now incompatible with the correct new `dhcp-host` entry) and reconcile historical ASUS/router records using verified live identity; do not rerun the old exclusion plan.
