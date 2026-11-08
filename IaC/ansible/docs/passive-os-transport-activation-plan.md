# Passive OS transfer — production activation contract

**Status (7 November 2026): implementation design; NOT approved for production.** Scoped to #297, existing router-01 -> sensor-01 -> monitor-01 evidence path. No new packet capture, Suricata reload, Nmap, DHCP, QoS, firewall, or Proxmox dependencies.

## Verified starting point
- Router `192.168.2.1` runtime `raspberrypi`, SSH valid (OpenSSH 10.0p2), `/etc/ssh/sshd_config` has `Include /etc/ssh/sshd_config.d/*.conf` at line 12 and existing `Match User router-metrics` at line 126. Do not place a new `Match` in an early include: it can change the scope of subsequent directives.
- Existing router-metrics identity is forwarding-only. Its exact `sshd -T -C` effective policy must remain unchanged through deployment and rollback.
- Proposed `homelab-os-transfer` is absent. Existing provision/rollback pair only handles a **dormant** nologin identity; not a live forced-command transport.
- Existing passive OS exporter reads only a private sanitised pending batch, **not** raw EVE. It is marked offline-only; cannot yet be used as a production forced command.
- SSH host key `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI` matches a dedicated monitor-01 pin dated Oct 29. Original independent physical-key provenance is disputed by subsequent SSH-only statements: new sensor trust requires a documented operator decision, not silent approval.
- Current router EVE size >1.4GB, `copytruncate` policy and absent `/var/run/suricata.pid`. Never read full live log or claim gapless evidence.

## Minimal implementation sequence — do not expand scope
1. **Source file contract:** create a root-controlled bounded synthetic sanitised batch output, using private permissions and reviewed group/ACL/readability. Prove exporter cannot access EVE, URLs, raw UA, checkpoint or arbitrary paths. Output maximum 2MiB+8KiB. Limit retained files and writes. Source checkpoint never advances on a mere SSH success.
2. **Client trust and identity:** distinct service user/key on sensor-01, root-protected private key and separate pinned host-key trust file. Never reuse monitor-01 monitoring credentials or trust files. Only approve host-key pinning after documented provenance/risk decision. No AutoAdd, `StrictHostKeyChecking=no`, or TOFU masked as independent verification.
3. **Restricted server:** dedicated `homelab-os-transfer` with a confirmed workable command execution shell and a single fixed exporter command; no interactive shell. Key restriction `from="192.168.2.55",restrict,command="..."`; service `Match User` requires public-key only, PermitTTY no, X11 no, agent/stream/local/TCP forwarding no, PermitTunnel no, PermitUserRC no. No permitopen/listen. A `nologin` shell must not be assumed capable of running the fixed command.
4. **Preflight of SSH scope:** stage a candidate configuration in a disposable path, validate via `sshd -t -f`, then compare `sshd -T -f ... -C user=...` for the administrator, router-metrics and transfer identity before any live write. Preserve router-metrics and admin effective policies. Avoid injecting a new `Match` in the early drop-in.
5. **Ansible change:** create **separate** default-deny approval-gated activate/verify/rollback playbooks. Back up existing files and their SHA256/owners/modes, refuse foreign account or config edits, and never touch SSH until rollback is ready. Any deliberate sshd reload requires explicit independent permission plus a tested session-recovery path. Do not use the dormant-only rollback for an activated account.
6. **Proof:** run a single **synthetic** bounded authenticated transfer, validate exact canonical batch, duplicate retry, challenge/pinned Ed25519 receipt, denied arbitrary command, unchanged source pending and checkpoint. Afterwards separately approve small live bounded incremental extraction, with health/latency and stale/rotation-gap observation. No timer until all gates pass.
7. **Final user-visible result:** feed low-confidence OS family candidate + source/freshness to existing monitor-01/Grafana; managed Ansible/Zabbix OS stays authoritative. Protect Panel 29/30 and source-qualified Panel 31; controlled deployment, proof, merge and issue closeout.

## Explicit stop criteria
Unknown client or server key; change in admin or router-metrics SSH effective policy; noncanonical or oversized wire; exporter ability to access EVE/raw UA; unchecked directory/symlink ownership; fresh-account collision; lack of rollback; collection overhead affecting router PPPoE/DNS/CAKE/NFQUEUE; checkpoint advanced without authenticated proof; gaps shown as complete evidence.

## Current validated evidence
- Offline receipt coordinator 10/10 PASS; full synthetic end-to-end suite 5/5 PASS; identity source gates 7/7 PASS and provision/rollback syntax PASS.
- Identity audits on router-01 and sensor-01 both 9 OK / 0 changed; Suricata rotation audit 7 OK / 0 changed. SSH effective *unrestricted* baseline for absent transfer user: `permittty yes`, `allowtcpforwarding yes`, `forcecommand none`.
- **No production transfer or passive OS service deployed.** This document is the fixed scope for the next implementation PR; refrain from extra exploratory transport prototypes.
