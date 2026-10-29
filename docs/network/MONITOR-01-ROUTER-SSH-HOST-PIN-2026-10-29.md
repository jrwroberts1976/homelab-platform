<!-- estate-authority: IaC/inventory/estate.json -->
# monitor-01 — fingerprint-gated router-01 SSH host pin (29 October 2026)

**STATUS: SOURCE ONLY, NOT DEPLOYED.** This change does not authorise a Pi monitoring account, accept a host key, start a tunnel, modify sshd, enable exporter access, or change Prometheus. It must be separately approved and executed only after local syntax checks.

## Verified operator evidence

- A physically verified Raspberry Pi `router-01`, onboard `eth0` MAC `d8:3a:dd:5a:51:44`, LAN address `192.168.2.1/24`, locally reported its genuine `/etc/ssh/ssh_host_ed25519_key.pub` SHA256 fingerprint as **`SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`**.
- From `monitor-01`, the operator ran **read-only** `ssh-keyscan -T 5 -t ed25519 192.168.2.1`, independently derived its fingerprint with `ssh-keygen -lf - -E sha256` and verified **exact match**: `ROUTER_HOST_KEY_MATCH=PASS`.
- That check found `CURRENT_HOST_PIN=MISSING` for `192.168.2.1` in `/etc/homelab/router-metrics-ssh/known_hosts`. The dedicated file already exists according to that check, but this output did not independently confirm ownership or mode; the live writer fails closed unless it is `root:root 0644` and not a symlink.
- Existing monitor key pair `/etc/homelab/router-metrics-ssh/id_ed25519[.pub]` has passed a dedicated service-user read/parse and exact public/private match after the separately approved ACL repair (Ansible `ok=24 changed=2 failed=0 rescued=0`).
- On the Pi the `router-metrics` SSH policy restricts to local forwarding `permitopen 127.0.0.1:9100`, public-key auth, no ordinary sessions. Its configured per-user authorised-key files are **absent**, so host pinning alone will not authenticate.
- Node Exporter on Pi serves metrics locally at `127.0.0.1:9100`. Prometheus currently has an UP ICMP target for the Pi but no verified node-exporter scrape target. No TCP/9100 exposure is justified.

Evidence: [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209), [current-state](../architecture/CURRENT-STATE.md), [ACL recovery runbook](MONITOR-01-ROUTER-METRICS-ACL-ACCESS-2026-10-29.md).

## Source-only implementation

`IaC/ansible/playbooks/monitor-01-router-ssh-host-pin.yml` has the default-disabled `router_host_pin_apply_approved` flag. It refuses `--check`, wrong controller (`admin-01`), unexpected inventory target (`monitor-01 192.168.2.52`) or wrong runtime monitor identity. It validates dedicated `router-metrics-tunnel` UID, non-login shell, root-owned parent, no symlinks and unchanged protected `known_hosts` owner/mode.

**Before any trust write**, it scans exactly one network-presented ED25519 host key at current router address, verifies the independently acquired exact SHA256 fingerprint, then uses `ssh-keygen -F` to identify existing normal **or hashed** entries. Conflicting or ambiguous previous pins cause an immediate stop. It appends just one audit-marked host-key entry to the existing private service trust file, preserving all unrelated entries, with a backup. It verifies that the dedicated service user sees exactly the matching host key and the original file protections remain. If the newly added pin fails postflight, the playbook attempts to remove only the added audit-marked entry and fails closed. **No key material is embedded in Git**; sensitive variables are `no_log`.

`IaC/ansible/playbooks/monitor-01-router-ssh-host-pin-rollback.yml` requires separate `router_host_pin_rollback_approved` and `router_host_pin_no_active_tunnel_verified` gates. It validates the precise audit marker and **original independently trusted fingerprint** before removing just that one line. It leaves other known_hosts entries intact and does not remove the ACL, private/public keys or packages. This rollback must not be run while any tunnel depends on the pin.

The source includes an offline GitHub Actions safety and syntax validation. CI only validates source; it is **not evidence of runtime execution**.

## Read-only local source validation on admin-01

After the source PR is reviewed and merged:

```bash
cd ~/projects/homelab-platform
git status -sb
git pull --ff-only origin main
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-ssh-host-pin.yml \
  --limit monitor-01 --syntax-check
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-ssh-host-pin-rollback.yml \
  --limit monitor-01 --syntax-check
```

**Neither syntax check modifies hosts. Do not use the runtime command without separate user approval.**

## Proposed live deployment — NOT AUTHORISED YET

Only after explicit user approval of host-key pinning on monitor-01:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-ssh-host-pin.yml \
  --limit monitor-01 --ask-become-pass \
  -e router_host_pin_apply_approved=true
```

Review all reported assertions and recap. Confirm independent postflight by `runuser -u router-metrics-tunnel -- ssh-keygen -F 192.168.2.1 -f /etc/homelab/router-metrics-ssh/known_hosts` while **suppressing raw host-key lines** in captured output and checking the SHA256 fingerprint. No `StrictHostKeyChecking=no`, no `ssh-keyscan` directly piped to known_hosts, and no `ssh` with automatic new-host-key acceptance.

## Proposed rollback — NOT AUTHORISED YET

After independently establishing that no tunnel depends on this host trust, and separately approving rollback:

```bash
cd ~/projects/homelab-platform/IaC/ansible
ansible-playbook -i inventory/hosts.yml \
  playbooks/monitor-01-router-ssh-host-pin-rollback.yml \
  --limit monitor-01 --ask-become-pass \
  -e router_host_pin_rollback_approved=true \
  -e router_host_pin_no_active_tunnel_verified=true
```

## Remaining separately reviewed IaC gates

1. Pin the genuine Pi host key (this source-only step).
2. Separately authorise the verified existing monitor public key for Pi `router-metrics` without copying secrets, weakening its sshd policy, or reloading unrelated services.
3. Design an SSH tunnel using strict pinned host verification, restricted account, and the Prometheus `monitoring_default` Docker bridge (`172.18.0.0/16`, gateway `172.18.0.1`); a forward on monitor host `127.0.0.1` does not automatically reach a container. Firewall scope and tunnel activation require separate approval. Never expose Pi TCP/9100 to WAN or general LAN.
4. Verify live Prometheus node metrics/health and logs independently; reachability is not evidence of ingestion.
