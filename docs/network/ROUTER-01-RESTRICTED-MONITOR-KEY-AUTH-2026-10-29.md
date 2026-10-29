<!-- estate-authority: IaC/inventory/estate.json -->
# Router-01 restricted monitoring ED25519 public-key authorisation — 29 October 2026

**STATE: SOURCE-ONLY / NOT DEPLOYED.** This document stages a narrowly scoped, *independently approval-gated* router-side public-key authorisation. The existence of this source code or its CI results **does not authorise a live write**. No SSH login, tunnel or Prometheus router node-metrics scrape has been demonstrated.

## Operator-verified baseline

- Physical `router-01`: onboard `eth0` MAC `d8:3a:dd:5a:51:44`, `192.168.2.1/24` LAN, `router-metrics` UID `999`, `/var/lib/router-metrics` owner UID999 mode `0700`, shell `/usr/sbin/nologin`. The `.ssh`, `authorized_keys`, and `authorized_keys2` paths were all **absent** in a direct read-only Pi audit.
- Existing on-disk `sshd -t` PASS; effective `sshd -T -C user=router-metrics,host=monitor-01,addr=192.168.2.52`: `strictmodes yes`, `authenticationmethods publickey`, `passwordauthentication no`, `authorizedkeyscommand none`, `allowtcpforwarding local`, `permitopen 127.0.0.1:9100`, `maxsessions 0`. This is the on-disk effective policy, **not evidence the running sshd has reloaded it**. Do not reload sshd under this change.
- `monitor-01 192.168.2.52`: dedicated `router-metrics-tunnel` UID992 private ED25519 key can be read through a separately approved parent directory traverse-only ACL and its private/public pair matches. Existing **public** key `/etc/homelab/router-metrics-ssh/id_ed25519.pub`, root:root mode0644, and **private** `id_ed25519`, service UID992 mode0600, independently PASS. Its exact **public-key SHA256 fingerprint**, from read-only operator verification, is **`SHA256:JB8L+7kC5lArmXoRLWfZThwuGblCjzeEHqYxct2JpqY`**.
- The monitor service user's single pinned Pi **SSH host key** at `/etc/homelab/router-metrics-ssh/known_hosts` is independently postflight verified against **`SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`**. Do **not** confuse the *monitor client public-key fingerprint* with the *router SSH server host-key fingerprint*.
- Pi Node Exporter works only on router loopback `127.0.0.1:9100`. The monitor's Prometheus is Docker-bridged: a proposed forward at monitor host `127.0.0.1:19100` alone cannot automatically serve its Prometheus container. That is later, separately reviewed work. Pi DHCP, PPPoE, dnsmasq, Unbound, nftables, SSH daemon and LAN connectivity are out of scope.

Evidence and source of truth: [issue #209](https://github.com/jrwroberts1976/homelab-platform/issues/209), [CURRENT-STATE](../architecture/CURRENT-STATE.md), [trusted Pi host-key runbook](MONITOR-01-ROUTER-SSH-HOST-PIN-2026-10-29.md).

## Source-only writer: strict controls

`IaC/ansible/playbooks/router-01-metrics-authorized-key.yml` targets **only** `router_postcutover_baseline` (physical `router-01 192.168.2.1`) and requires both inventories. Default approval flag `router_metrics_authorize_apply_approved=false` refuses execution without a **new explicit approval**. Local controller must be `admin-01`; monitoring source must be `monitor-01 192.168.2.52`. It validates live router Pi MAC/IP, UID999 restricted account/home and on-disk `sshd` policy; the monitor service identity and original source file metadata.

Before writing anything on the Pi, Ansible reads the *existing* monitor public key via a delegated `slurp` (in-memory, `no_log`; no key bytes saved to GitHub or emitted in logs), re-derives the corresponding public key from the original monitor private key as `router-metrics-tunnel`, and demands **exactly** fingerprint `SHA256:JB8L+7kC5lArmXoRLWfZThwuGblCjzeEHqYxct2JpqY`. The already pinned remote **host** key must independently match `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`. It rejects existing unknown authorised-key contents, symlinks, unsafe ownership/modes or `authorized_keys2`. A clean rerun with the **exact same** restricted line is idempotent.

Only if all checks PASS, it creates `/var/lib/router-metrics/.ssh` with dedicated user ownership and mode `0700`, and `authorized_keys` mode `0600` with exactly one line:

```text
from="192.168.2.52",restrict,port-forwarding,permitopen="127.0.0.1:9100" ssh-ed25519 <existing-verified-monitor-public-key> router-metrics-tunnel@monitor-01
```

The angle-bracketed value above is **explanatory placeholder**, *not* an actual key committed to Git. `restrict` disables standard session privileges; `port-forwarding` re-enables forwarding under the user's `sshd Match` policy and `permitopen` restricts the forwarding destination to the Pi's loopback Node Exporter. `from` further restricts source address. The user still has `maxsessions 0` and `nologin`; no general-purpose interactive login is intended. All postflight checks compare exact content/permissions without printing key bytes. If newly added files fail postflight, scoped recovery attempts to remove only that file **if still byte-for-byte the written line**, and only remove an empty directory. No sshd reload or key rotation is included.

## Separate rollback

`IaC/ansible/playbooks/router-01-metrics-authorized-key-rollback.yml` defaults `router_metrics_authorize_rollback_approved=false` and `router_metrics_authorize_no_active_tunnel_verified=false`. It requires independent user approval that the forward has been stopped, checks live monitor listeners for planned TCP/19100, verifies physical Pi MAC/IP and restricted account/file metadata, reads existing `authorized_keys` privately, demands exactly the original marked single-line restrictions **and** the independent monitor ED25519 fingerprint, then removes only that authorised-key file. The `.ssh` directory is removed only with `rmdir` if empty; unrelated content is preserved. If the existing content/key has changed, the rollback refuses deletion. It does not revoke `james` admin SSH or remove the monitor's private key or pinned Pi host trust.

## Local read-only source validation — do this after PR merge

```bash
cd ~/projects/homelab-platform
git status -sb
git pull --ff-only origin main

cd IaC/ansible
ansible-playbook \
  -i inventory/router-01-postcutover-baseline.yml \
  -i inventory/hosts.yml \
  playbooks/router-01-metrics-authorized-key.yml \
  --limit router-01 --syntax-check

ansible-playbook \
  -i inventory/router-01-postcutover-baseline.yml \
  -i inventory/hosts.yml \
  playbooks/router-01-metrics-authorized-key-rollback.yml \
  --limit router-01 --syntax-check
```

The check-only commands above do not modify router or monitor. **Do not run the writer with the approval variable until the operator has reviewed the merged source and granted fresh explicit permission.** There may be sudo passwords on both router and monitor; delegated source reads use privilege escalation on the monitor, so test both paths carefully. Do not work around failed become permissions by copying key material manually.

## Future live activation — NOT AUTHORISED

After separate explicit approval **only**, the already reviewed writer will require `-e router_metrics_authorize_apply_approved=true`. Review detailed Ansible recap and verify no SSH daemon reload, key rotation, firewall or exporter bind changes. Afterward run an independent **read-only** Pi file/fingerprint/permissions postflight before considering any strict-host-checking `ssh -N` authentication probe. Actual tunnel, socket binding accessible to Docker Prometheus, and scraping require **new, separately reviewed IaC and approval**.

Do not use this runbook to infer SSH authentication already works.
