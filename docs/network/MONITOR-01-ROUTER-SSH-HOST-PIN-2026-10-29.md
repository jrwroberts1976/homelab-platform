<!-- estate-authority: IaC/inventory/estate.json -->
# monitor-01 — fingerprint-gated router-01 SSH host pin (29 October 2026)

## Independent post-deployment check — PASS (29 October 2026)

After the corrected playbook's **successful live host-key installation** (Ansible `ok=27 changed=1 failed=0 rescued=0`), the operator ran a **separate read-only** Python/Ansible postflight. It checked `/etc/homelab/router-metrics-ssh/known_hosts` regular file ownership/mode, then executed `ssh-keygen -F 192.168.2.1` under the dedicated non-login `router-metrics-tunnel` user without printing key bytes. It counted the returned record and independently SHA256-hashed the ED25519 public-key blob:

```text
TRUST_FILE_SECURITY=PASS
LOOKUP_EXIT_CODE=0
HOST_KEY_RECORDS=1
PINNED_FINGERPRINT=SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI
HOST_PIN_POSTFLIGHT=PASS
```

This confirms the dedicated service identity can read **exactly one correctly pinned Pi SSH host key**, matching independently verified physical router identity. The Ansible ad-hoc shell recap `CHANGED rc=0` reflects the shell module's convention, **not a modification**. This satisfies the previously pending optional independent postflight (historical instructions further below). **Host-key trust is complete; Pi-side public-key authorisation is still absent, and no authenticated connection or tunnel is working yet.** Do not start a tunnel or change Prometheus as a result of this postflight.


## CURRENT STATUS — successful live deployment (29 October 2026)

**The host-key pin is LIVE on `monitor-01`**. The source-only preparation, first failed attempt and unpinned statements further below are preserved only as **historical** context and are superseded by this verified successful run. The Pi user authorised-key and monitoring tunnel remain separate **NOT DEPLOYED** work.

After PR #228 merged as `af175185`, operator synced `admin-01` main and independently passed Ansible syntax checks for the corrected writer and rollback. With **fresh, explicit operator approval** for this trust pin only, the corrected writer's live output confirmed:

```text
TASK [Classify current-Pi ED25519 records without revealing raw scan output] ok
TASK [Reject missing, duplicate, or conflicting router SSH host keys] ok
TASK [Require exact independent physical-Pi fingerprint before touching known_hosts] ok
TASK [Fail closed on conflicting or ambiguous existing router pins] ok
TASK [Append only verified router key to existing dedicated trust file] changed
TASK [Require exactly one correct router key usable by the service user] ok
TASK [Require root-owned non-symlink trust file with preserved access mode] ok
"Physical router ED25519 fingerprint matched: SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI"
"Pinned 192.168.2.1 host key usable by router-metrics-tunnel: PASS"
PLAY RECAP monitor-01: ok=27 changed=1 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

The monitoring identity `router-metrics-tunnel` can read exactly the matching, pinned ED25519 host key from its protected `/etc/homelab/router-metrics-ssh/known_hosts`. The writer verified existing `root:root 0644` mode and the originally independently verified physical Pi fingerprint. There was no rollback. The **first** deployment had been stopped by an over-strict total `ssh-keyscan` stdout-line count (`changed=0`); this later corrected run **succeeded**.

No on-router `authorized_keys`, SSH daemon, tunnel, packet filter, exporter listener or Prometheus change was made by this trust stage. Router `router-metrics` public-key authorisation was previously unconfigured. **Do not confuse host trust with a completed SSH connection or scraped metrics.** Further actions require separate reviewed Ansible/IaC and explicit approval.

### Optional independent read-only postflight (not yet supplied by operator)

From `admin-01`, inspect the existing entry *as the dedicated monitoring identity* without printing key material, check it matches the independently verified physical Pi SHA256 fingerprint, and verify the trust file remains protected. Do not accept a new host key or attempt an SSH login. Any postflight output should show only a PASS/FAIL summary and safe metadata.


## Live preflight failure and corrected source — 29 October 2026

The operator synchronised `admin-01` to source `57cfec26`, and both writer and rollback syntax checks PASSED. After explicit live approval **for this host pin only**, the writer attempted to validate a network SSH scan but stopped **before any write**:

```text
TASK [Reject unexpected host keys or ambiguous scan results] FAILED
assertion: host_pin_scan.stdout_lines | length == 1
PLAY RECAP monitor-01 ok=10 changed=0 unreachable=0 failed=1 skipped=0 rescued=0 ignored=0
```

A follow-up **read-only** diagnostic on `monitor-01` captured the exact scan shape **without exposing public key bytes**:

```text
SCAN_RETURN_CODE=0
OUTPUT_LINES=2
VALID_ED25519_LINES=1
UNIQUE_FINGERPRINTS=1
FINGERPRINT=SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI
EXPECTED_FINGERPRINT_PRESENT=True
```

The scanner returned two stdout lines, but exactly one **valid** key line for the current Pi and that one fingerprint **matches the independently verified physical Pi**. The content/type of the second non-key line was not collected; no assumption is made that it is a specific banner or error. The strict total-line count was too broad, and the first-line selection had an unsafe order assumption.

**Source-only correction:** classify key records before the preflight: demand exactly one syntactically valid `192.168.2.1 ssh-ed25519` record, refuse duplicate/missing or other recognisable SSH host-key records, and select **that** validated record rather than `stdout_lines[0]`. Non-key output alone is no longer a reason to abort. The **independently verified physical-Pi SHA256 fingerprint check remains mandatory and unchanged** before the writer ever touches `known_hosts`. CI includes synthetic extra-line, missing, duplicate and conflicting host-key tests.

**HISTORICAL INITIAL FAILURE ONLY:** The original approved writer failed with `changed=0` before any pin; this was subsequently corrected and the fresh approved deployment succeeded (see live status above). Never bypass the host fingerprint, disable host-key verification, add Pi authorised keys or start the tunnel as part of this stage.


**HISTORICAL SOURCE-ONLY STATUS (SUPERSEDED BY LIVE PASS ABOVE):** This runbook initially described an unexecuted host-trust change. The pin was subsequently approved and deployed successfully; no Pi monitoring account authorisation, tunnel, sshd, exporter access or Prometheus changes were included.

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

## Historical live deployment procedure — executed successfully with fresh approval

The operator gave explicit fresh approval and executed this procedure successfully. Retained as historical reference, **not permission for another run**:

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

1. Genuine Pi host key pin — **COMPLETE and live verified on monitor-01**.
2. Separately authorise the verified existing monitor public key for Pi `router-metrics` without copying secrets, weakening its sshd policy, or reloading unrelated services.
3. Design an SSH tunnel using strict pinned host verification, restricted account, and the Prometheus `monitoring_default` Docker bridge (`172.18.0.0/16`, gateway `172.18.0.1`); a forward on monitor host `127.0.0.1` does not automatically reach a container. Firewall scope and tunnel activation require separate approval. Never expose Pi TCP/9100 to WAN or general LAN.
4. Verify live Prometheus node metrics/health and logs independently; reachability is not evidence of ingestion.
