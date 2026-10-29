<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01: Bedroom ASUS fixed DHCP reservation — 29 October 2026

**STATUS: DRAFT SOURCE ONLY — NOTHING DEPLOYED.** Review this PR and its CI before merging; merging source does not approve or execute the playbook. dnsmasq currently continues serving the unchanged pool.

## Verified current facts

The live Pi router is `router-01` at `192.168.2.1/24` (eth0), PPPoE on ppp0, running dnsmasq, Unbound and nftables. Its active `/etc/dnsmasq.d/router.conf` has one DHCP range `192.168.2.100–199` (24h), router and DNS options `192.168.2.1`. Previous operator-run read-only Ansible preflight: **20 OK, 0 changed, 0 failed**.

The user's ASUS Home RT-AC86U at `192.168.2.2` is manually **static**, outside the DHCP range. ASUS AiMesh UI identifies **Bedroom RT-AC86U**, Ethernet 1 Gbps, at `192.168.2.180`. The user confirmed Bedroom uses **DHCP**. The current Pi's lease file identifies `RT-AC86U-CCC8` at `192.168.2.180` and the user ran a local lease-to-ASUS-GUI MAC comparison: **RESULT: MAC MATCHES ASUS GUI**. The live lease must still be verified at change time.

The third ASUS router is **not in use**; historical lease records for `RT-AC86U-5228` and `RT-AC86U-6238` at old `192.168.3.x` addresses do not prove current connectivity. Historical `192.168.2.181` failed ARP and is **not** a confirmed current static address. `media-01` historically `192.168.2.195` is offline, with static-vs-DHCP mode not yet known.

**Decision:** reserve the *existing* Bedroom `.180` address for its *verified* DHCP MAC, **without** changing the broad .100–199 DHCP pool, other leases, names, DNS, gateways or firewall. The earlier candidate split ranges excluding `.181` and `.195` are **superseded as an active recommendation**; do not deploy them. Treat `media-01` independently after its configuration is verified.

## Proposed exact managed change

Append only this block to the **existing** `/etc/dnsmasq.d/router.conf`:

```ini
# BEGIN ANSIBLE MANAGED BEDROOM ASUS DHCP RESERVATION
dhcp-host=<verified-DHCP-client-MAC>,192.168.2.180
# END ANSIBLE MANAGED BEDROOM ASUS DHCP RESERVATION
```

The placeholder above is **not a valid deployed MAC**. The real value is supplied from a protected **local Ansible Vault extra-vars file on admin-01**, never committed in plain text or written into a public GitHub issue. No hostname is specified in `dhcp-host`, so the client retains its own DHCP-provided name. dnsmasq supports MAC-bound fixed DHCP address assignment via `dhcp-host` (https://dnsmasq.org/docs/dnsmasq-man.html).

## Prepared Ansible source — not run

- `IaC/ansible/playbooks/router-01-bedroom-dhcp-reservation.yml` requires **two explicit approvals**, non-check mode, execution from `admin-01` and the isolated, verified `192.168.2.1` Pi inventory. It verifies Pi physical eth0 MAC, gateway address, PPPoE route, core services, dnsmasq config composition, original range and an **unexpired** current Bedroom lease with exactly the user-approved MAC + IP + hostname.
- It creates a temporary **offline candidate configuration in /run** and checks it with the Pi's installed `dnsmasq --test` before touching the active router config. It writes a private backup of `router.conf` in `/var/backups/homelab-router/dnsmasq/` (mode 0600) **outside** the active dnsmasq include directory so the backup cannot be parsed as another configuration fragment.
- Only then it inserts the one managed block into the existing file, checks the full installed dnsmasq syntax, **restarts dnsmasq only**, verifies service and syntax. Failure triggers an attempt to remove its own block and restart the service in its original state. A short DNS/DHCP interruption is expected during any authorised restart; it does not intentionally touch PPPoE/firewall/LAN interfaces.
- `IaC/ansible/playbooks/router-01-bedroom-dhcp-reservation-rollback.yml` requires its **own** rollback/restart approvals, verifies the exact managed line and Pi identity, backs up the currently installed file outside the include directory, removes only this block, validates syntax and restarts only dnsmasq. On error it attempts to reinsert the block and recover the service. Do not blindly restore an old whole-file backup over later approved changes.
- GitHub CI tests playbook syntax and static guardrails, and invokes installed dnsmasq on a synthetic MAC-bound reservation inside the unchanged pool. CI does **not** prove runtime connectivity, availability, actual lease allocation or final deployment.

**These playbooks intentionally refuse ordinary read-only `--check` execution**, because the writer is designed only for a separately approved maintenance-window deployment. For review, inspect source, CI checks and use `ansible-playbook --syntax-check`; do not run the writer with approvals until the operator decides.

## Local private MAC vault — prepare later, not in Git

After code review, if the operator authorises deployment, use `ansible-vault create` with a locally held encrypted file on admin-01 (do not add to Git or shell history):

```bash
umask 077
mkdir -p "$HOME/.config/homelab"
ansible-vault create "$HOME/.config/homelab/router-bedroom-vars.yml"
```

Its decrypted YAML content is:

```yaml
router_bedroom_client_mac: "<actual verified Bedroom DHCP client MAC>"
```

**Deployment command — for later explicit approval only** (will restart dnsmasq briefly):

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

After actual installation, revise the earlier **split-exclusion preflight** (which will correctly reject any new reservation as unexpected), reconcile historical ASUS/router records with `IaC/inventory/estate.json` and `CURRENT-STATE.md`, and write the observed live outcome to `gpt-handover.md` and issue #206. No rollout is claimed by this plan.
