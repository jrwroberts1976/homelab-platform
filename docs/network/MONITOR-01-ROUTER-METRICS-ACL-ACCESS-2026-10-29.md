<!-- estate-authority: IaC/inventory/estate.json -->
# monitor-01 restricted router metrics SSH key: minimal ACL access — 29 October 2026

**CURRENT STATUS: DEPLOYED on monitor-01; operator postflight PASS (29 October 2026).** The source-only status below records pre-deployment history. After separately approved live deployment, the service account can read and parse its original private key; no router SSH authorisation, tunnel, host-key pin, Prometheus change, exporter exposure or SSH reload is claimed.

## Live operator postflight — verified success (29 October 2026)

Following merged [PR #225](https://github.com/jrwroberts1976/homelab-platform/pull/225), the operator fast-forwarded `admin-01` to commit `93cbbcb2`, and both ACL writer and rollback syntax checks **PASSED**. The operator explicitly approved **both** Debian `acl` package installation and granting `router-metrics-tunnel` `--x` on `/etc/homelab`, then ran the source-controlled, guard-railed ACL writer with two approval variables.

**Verified from pasted live Ansible playbook tail:**
```text
TASK [Confirm dedicated non-login user can now read its own key] ok: [monitor-01]
TASK [Confirm dedicated user can parse private key without exposing bytes] ok: [monitor-01]
TASK [Confirm key and directory have not been chmodded or reowned] ok: [monitor-01] (2 items)
TASK [Assert original non-ACL filesystem modes remain protected] ok: [monitor-01]
TASK [Report exact completed scope and next independently gated stages] ok: [monitor-01]
"Traverse-only named user ACL for router-metrics-tunnel: PASS"
"Private SSH key bytes, mode 0600, owner unchanged; other access remains denied"
"No router authorised_keys, SSH trust/pinning, sshd reload, tunnel, firewall, exporter listener or Prometheus configuration changed"
PLAY RECAP monitor-01: ok=24 changed=2 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

**Interpretation:** The approved live writer succeeded, with no failures/rescues. The non-login `router-metrics-tunnel` user can now access and parse the existing valid key; safety assertions passed with directory and key protection unchanged. `changed=2` is consistent with `acl` package install and creating its narrow user ACL, although the pasted tail does not separately show the earlier package/ACL writer tasks. Keep the rollback playbook for separately approved future recovery; it was **not run**. This completed step **does not** constitute live SSH authentication or Prometheus router metrics ingestion.

**Next read-only verification:** test the private/public pair match without logging either key; inspect router's authentic SSH host-key fingerprint via direct Pi SSH command, compare to monitor's pinned entry once established, and only then design independent approvals for Pi authorised-key installation and container-safe tunnel. Do not commit credentials or run obsolete `.3.1` scripts.

## Historical initial source-only plan (completed for ACL access only)


## Evidence and problem

Operator ran multiple independent read-only Ansible checks from `admin-01` against `monitor-01 192.168.2.52` and `router-01 192.168.2.1`:

- `monitor-01` Prometheus container `monitoring-prometheus-1` uses Docker bridge `monitoring_default` (`172.18.0.0/16`, host gateway `172.18.0.1`); no tunnel listener on port `19100`, no matching systemd tunnel unit.
- `router-metrics-tunnel` exists on `monitor-01` as UID `992`, home `/var/lib/router-metrics-tunnel`, `/usr/sbin/nologin`. Existing private key `/etc/homelab/router-metrics-ssh/id_ed25519` is owned by the account, mode `0600`; corresponding public key exists.
- `ssh-keygen -y -P '' -f <private-key>` succeeds **as root** but fails **as service account**; `runuser ... test -r` also FAILS. Private key is a valid OpenSSH key; **do not regenerate it**.
- `namei -l` isolated denial at `/etc/homelab`: **`root:root 0750`**; the child `router-metrics-ssh` directory is `root:root 0755`. The account lacks execute/traverse on the parent, even though it owns the key.
- `getfacl` and `setfacl` binaries are both **missing**; no claim that the underlying filesystem lacks POSIX ACL support has been made. There was no write to test ACL support.
- The Pi's `router-metrics` sshd Match policy has `authenticationmethods publickey`, no passwords/TTY/session, `allowtcpforwarding local`, `permitopen 127.0.0.1:9100`, `permitlisten none`. The currently configured `authorized_keys` and `authorized_keys2` files **do not exist** in the Pi service home, and the monitor's pinned `known_hosts` entry for `192.168.2.1` is **MISSING**. No authenticated tunnel is working. These are **separate future steps**.
- Router Node Exporter is healthy but bound only to Pi `127.0.0.1:9100`, HTTP 200. Prometheus has router ICMP target UP but no verified router-01 node-exporter target. Do not expose TCP/9100 to the LAN or WAN.
- The 29 October live checks found Loki and Zabbix network transports reachable from Pi and controller; no router firewall change is needed for those destinations. Issue [#209](https://github.com/jrwroberts1976/homelab-platform/issues/209) tracks the current evidence.

## Proposed isolated fix

`IaC/ansible/playbooks/monitor-01-router-metrics-acl-traverse.yml` has **two independent, false-by-default approvals**, one to install only Debian's `acl` userspace package (necessary because the utilities are absent), and a second to grant only `u:router-metrics-tunnel:--x` on `/etc/homelab`. The source enforces the exact `admin-01` controller and `monitor-01 192.168.2.52` target, service account UID `992`, root-owned `0750` parent, `0755` child and account-owned `0600` private key. It simulates APT and rejects removals or unexpected installations/upgrades before installing anything. It then inspects the real ACL after `acl` is available, fails closed on unexpected named-user permissions, applies the narrow rule only if not present, and tests readability and private-key parsing **as the dedicated account**. It checks owner/group/other permissions after. Sensitive key derivation is hidden with Ansible `no_log`. On failure after attempting the ACL, the rescue step tries to remove **only its newly added named-user ACL**.

The named ACL allows traversal of the parent, **not** listing it. It neither opens `/etc/homelab` for other users nor changes the key's owner/mode. It does not adjust SSH daemon, Node Exporter or Prometheus. The `acl` package was included in a separately approved limited OS change; there is **no claim of zero operational risk**, and installation is not inferred from merging this PR.

## Source review commands (no remote change)

```bash
cd ~/projects/homelab-platform
git pull --ff-only origin main
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-acl-traverse.yml --limit monitor-01 --syntax-check
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-acl-rollback.yml --limit monitor-01 --syntax-check
```

The writer is **intentionally blocked in `--check` mode** (the operator ran real deployment only after separate approval). APT simulation and safety checks run inside the specifically approved writer before any install/ACL mutation; use read-only shell preflights for further evidence without granting writer approvals.

## Historical operator deployment command — EXECUTED successfully on 29 October 2026

The operator explicitly approved both named gates and executed this guarded writer. This command is retained as historical reference, **not an instruction to rerun without a new approval**:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-acl-traverse.yml \
  --limit monitor-01 --ask-become-pass \
  -e router_metrics_acl_package_install_approved=true \
  -e router_metrics_acl_apply_approved=true
```

Review recap for failure/unreachable/rescue. Then re-run independent read-only `runuser -u router-metrics-tunnel -- test -r /etc/homelab/router-metrics-ssh/id_ed25519` and a quiet `ssh-keygen -y -P ''` parser test as that account, reporting PASS/FAIL only. Preserve root-only parent modes and prohibit key-material output.

## Separately approved rollback — NOT YET EXECUTED

Only after verifying there is **no dependent live metrics tunnel** and intentionally approving rollback:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-metrics-acl-rollback.yml \
  --limit monitor-01 --ask-become-pass \
  -e router_metrics_acl_rollback_approved=true \
  -e router_metrics_acl_no_active_tunnel_verified=true
```

Rollback removes the single named-user ACL only; it **does not uninstall `acl`** (package removal could disrupt other ACL management) and does not touch SSH or key files. Preserve any unrelated ACL entries. It intentionally revokes the monitoring identity's access to this private key.

## Future monitoring stages, NOT approved by this change

1. Reconfirm the existing private/public key pairing and inspect the securely pinned Pi host fingerprint; **never** accept an unknown host key automatically.
2. Prepare a separate reviewed Pi `router-metrics` `authorized_keys` installation, using the matching monitor public key and no secret bytes committed to Git.
3. Design monitor-to-Pi restricted SSH local forwarding with explicit container network routing; Prometheus is in `monitoring_default`, so host `127.0.0.1:19100` does **not** automatically mean container reachability. Keep Pi exporter `127.0.0.1:9100` only; protect any necessary bridge listener from other containers/hosts and never expose it on WAN.
4. Independent scrape validation, Grafana/Zabbix/Alloy integration as separate scoped, change-approved IaC. Do not run obsolete `192.168.3.1` code from closed PR #210.
