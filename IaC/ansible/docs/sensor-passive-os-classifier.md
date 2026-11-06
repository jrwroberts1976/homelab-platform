# Passive OS inference — offline prototype (6 Nov 2026)

**Status: code and offline tests only. Not deployed anywhere.**

Goal: derive **low-confidence candidate OS families** from metadata already observed by router-01's Suricata, then eventually analyse on sensor-01 and report to monitor-01, without Nmap retries, a mirrored NIC, or changes to live NFQUEUE.

## Boundaries

- `router-01`: source of **existing** Suricata event observations, DNS/DHCP metadata; no new active scanning, interface mirroring, capture, NFQUEUE, or IPS configuration changes.
- `sensor-01`: future batch classifier and evidence correlation, **not an active packet sensor** in the new design.
- `monitor-01`: later Prometheus/Grafana consumption.
- Ansible/Zabbix remain authoritative for managed OS facts; passive UA is self-reported and cannot override those facts.
- Existing Nmap deep-profiler attempts are capped at one automatic attempt per MAC and are not affected.

## First offline program

`IaC/ansible/scripts/sensor_passive_os_classifier.py` accepts **locally prepared, minimised, time-bounded** JSONL events and a lease-history JSON map. It does **not** reach any host and should not be pointed at a full EVE file; Suricata timestamps need converting from ISO8601 to Unix seconds during a future reviewed extraction step.

Example conceptual input (synthetic values, no live traffic):

```json
{"timestamp":1793950000,"src_ip":"192.168.2.113","event_type":"http","http_user_agent":"Mozilla/5.0 (X11; CrOS x86_64 1)"}
```

Corresponding **synthetic** lease-history mapping:

```json
{"192.168.2.113":[{"mac":"ec:91:61:9c:a4:45","valid_from":1793946400,"valid_until":1793953600}]}
```

The IP-to-MAC association must be validated **for the time of the observation**. A present-day dnsmasq lease snapshot alone is not reliable historical proof. When a lease is missing, expired, or has conflicting MACs, the event is excluded. IP addresses are not stable device IDs; MAC randomisation means a new MAC may not denote a new physical device.

The classifier:
- allows at most 20,000 events, 8 KiB per line and 160 MiB input and bounded lease-map size;
- supports candidate families Windows, macOS, iOS/iPadOS, Android, ChromeOS and Linux from user agents;
- labels a single-family observation `candidate / low` even when repeated many times (not independent confirmation);
- reports `conflicting` if different families are observed for the same IP/MAC;
- never infers a family from DNS/TLS/QUIC **alone**; these signals may count as observed metadata only;
- emits only device IP, MAC, OS family, status, confidence, source, observation count and last observed timestamp — **no domain, URL, SNI or raw User-Agent**;
- has no service, timer, capture or export action.

## Next design gates before live collection

1. Audit the available encrypted/read-only transfer mechanisms and authentication from router-01 to sensor-01, with minimal router CPU and disk I/O. Never expose a network-accessible raw EVE feed.
2. Design incremental tailing with checkpoints, inode changes, `copytruncate` rotation, truncated/partial JSON lines and bounded catch-up. Avoid reading the ~1.2GB EVE log on every invocation.
3. Build a privacy-minimised extraction format on the router with strict fixed resource and rate caps, and test on synthetic/archived inputs **off the live NFQUEUE path**.
4. Validate client/server direction and lease-time attribution (including router DNS forwarding, privacy MACs, reused IPs, guests, and NAT). For managed hosts, cross-check authoritative agent OS.
5. Unit and integration-test resilience, resource ceilings, atomic output, failure isolation and rollback. Deploy via approval-gated Ansible with no router Suricata restarts.
6. Add provenance/expiry and Prometheus metric export only after acceptance. Don't publish a guessed precise version; surface `unknown` when insufficient.

## Offline validation on admin-01

```bash
cd ~/projects/homelab-network-enrichment/IaC/ansible
python3 -m unittest discover -s tests -p test_sensor_passive_os_classifier.py -v
python3 -m py_compile scripts/sensor_passive_os_classifier.py
```

No production deployment is authorised by these tests.


## Stage 2 offline router EVE minimiser — staged, NOT deployed

`IaC/ansible/scripts/router_eve_minimizer.py` is a **local file prototype** only. It parses a pre-existing file of Suricata EVE JSONL records and emits strictly `timestamp`, LAN `src_ip`, `event_type`, and (HTTP only, when recognisable) `os_family_hint`. Source records' URLs, DNS domains, TLS/QUIC SNI, raw User-Agent strings, remote IP addresses and payloads are never copied to the sanitised output. It does not read DHCP leases or assert an OS identity. `sensor_passive_os_classifier.py` accepts these hints but still requires a historical time-bounded IP→MAC lease map to attribute them, and labels each resulting OS as **low-confidence candidate** at best.

- Resource cap per run: **1 MiB** of input and **2,000 complete lines**; each line ≤8 KiB; checkpoint file ≤4 KiB.
- Resumes from persisted device/inode/offset and a short overlap hash; detects inode changes, file shrink, and changed content around the read position. Incomplete/oversized lines stop that batch without consuming them; a persistent oversized line can block progress pending an operator decision.
- Writes sanitised output and checkpoint using root-/owner-private mode **0600** with atomic rename. No network listener, SSH service, timer, scans, or Suricata modifications.
- **Reliability limitations:** the two output/checkpoint replacements are not transactional; a crash can cause replay or loss of an untransferred batch. Consumer acknowledgement, idempotency/deduplication, queue/spool limits, and recovery from copytruncate while content has already regrown beyond the prior offset remain unsolved. A 64-byte overlap check is *not* a guarantee of lossless rotation. The extractor is therefore **not approved for unattended production scheduling**. A future live design must address rotation gaps and input/output security without affecting NFQUEUE service operation.
- The script currently starts at byte 0 of a supplied file if no checkpoint exists. **Never run it directly against the 1.2 GB live router EVE file** as a quick fix or infer that this handles the historical backlog; a first-live-start-from-current-EOF design is separately required.
- Historical DHCP lease snapshots are not already available; the existing current leases cannot prove historical IP-to-MAC identity and must not be substituted without validation.

Offline tests (on admin-01 after pulling the feature branch):

```bash
cd ~/projects/homelab-network-enrichment/IaC/ansible
python3 -m unittest discover -s tests -p 'test_router_eve_minimizer.py' -v
python3 -m unittest discover -s tests -p 'test_sensor_passive_os_classifier.py' -v
python3 -m py_compile scripts/router_eve_minimizer.py scripts/sensor_passive_os_classifier.py
```

The extractor's 12 regression tests were exercised against a matching offline prototype locally in the authoring environment before committing. Re-run them from the actual Git checkout to validate committed bytes. **No live deployment or permission changes have been performed.**


## Stage 3 — offline delivery and acknowledgement proof of concept

**Not deployed. No router-01 or sensor-01 runtime changes.** The following new files are committed on the feature branch:

- `scripts/passive_os_batch_spool.py`: single pending batch prepared from a bounded EVE read. A private, atomic `pending.json` contains only the sanitised observations and next checkpoint. A second prepare while unacknowledged returns the **same batch ID**; the checkpoint is not advanced. `--ack-id` exists as an **offline test hook only**; it must never be automatically called based solely on an SSH exit code or file copy.
- `scripts/passive_os_batch_receiver.py`: offline local recipient that validates the pending payload's integrity and batch ID, saves an immutable batch, and returns an idempotent receipt; duplicate deliveries do not generate duplicate batch files.
- `tests/test_passive_os_batch_spool.py` and `tests/test_passive_os_batch_receiver.py`: verify blocked progress before ack, wrong ack rejection, retry, crash window, no sensitive fields, private modes, duplicate receipt, and corruption rejection. **These newly committed tests still need to be run on admin-01.**

Manual offline experiment must use synthetic input in a private temporary directory. Do **not** copy any live EVE logs into the repo or GitHub. There is **no sensor-to-router SSH automation** and **no automatic wire-level acknowledgment** in this stage.

Acknowledging a batch advances the extractor checkpoint. An operator or future coordinator must only acknowledge after proof that the sensor has durably stored, validated, and processed the batch as intended; the present offline receiver validates local storage only. The downstream classifier also still needs deduplicated cumulative host-summary behaviour for repeated/reordered event timestamps.

### Remaining blockers before production

1. **Gapless rotation handling is not solved:** copytruncate can lose bytes that arrive between copy and truncate; file overlap checking cannot recover historical bytes already removed. Need an architectural decision such as configuring a safe local nonblocking log output or accepting explicitly documented best-effort sampling. No changes to NFQUEUE/Suricata until separately approved.
2. **Power-loss durability:** atomic replacement plus per-file fsync is implemented, but directory fsync and end-to-end delivery/ack recovery are not; the current program does not claim exact-once guarantees.
3. **Access security:** no service account, restricted forced-command SSH key, peer key verification or source-IP restriction has been provisioned. Existing router EVE is mode 0644; separately review access with rotation, Suricata and minimiser ownership.
4. **Lease timeline:** current dnsmasq lease snapshot does not establish historical IP-to-MAC attribution. Need time-bounded lease history; fail closed for stale/ambiguous clients.
5. **Resource ceilings and retention:** the spool has at most one unacknowledged batch, but the offline recipient directory has no automatic retention/quota. Must specify quota, rate limits, monitoring and cleanup policy before scheduling.
6. **Production safety:** design no live copy of full logs, explicit start-at-current-EOF bootstrap, rotation-aware bounded reads, under-load CPU/IO limits, safe rollback and approval-gated Ansible. Do not run this prototype against active `/var/log/suricata/eve.json`.

Validate stage 3 locally on admin-01 after `git pull --ff-only`:

```bash
cd ~/projects/homelab-network-enrichment/IaC/ansible
python3 -m unittest discover -s tests -p 'test_passive_os_batch_spool.py' -v
python3 -m unittest discover -s tests -p 'test_passive_os_batch_receiver.py' -v
python3 -m py_compile scripts/passive_os_batch_spool.py scripts/passive_os_batch_receiver.py
```


## Stage 4 — rotation continuity gate (staged, not yet operator-tested)

- The offline spool now **fails closed** whenever a previously checkpointed EVE stream reports `rotated`, `truncated` or `content_replaced`: no new batch is published, and the checkpoint is preserved for review. Three new synthetic regression cases were added to `test_passive_os_batch_spool.py`.
- Added **read-only**, non-mutating Ansible playbook `playbooks/router-01-suricata-logrotate-readonly-audit.yml`. It checks expected router inventory target, actual hostname (currently `raspberrypi`), dedicated NFQUEUE service status, logrotate policy, logrotate timer and EVE file metadata. It does not invoke logrotate, read the EVE contents, change SSH/accounts/permissions, or restart services.
- The fail-closed guard protects against **detected** discontinuity; it cannot guarantee that all gaps are detected. In particular a same-inode copytruncate and rapid regrowth may evade a short overlap hash, and logrotate's copy/truncate interval can itself lose data. **Do not claim gapless collection or approve production scheduling.**
- Recommended policy unless a separately approved logging architecture removes the gap: a **best-effort, explicitly marked incomplete** passive OS evidence feed, never an authoritative source. Any continuity alarm must be surfaced as an operational fault rather than silently resuming. Never use the pipeline for security incident reconstruction.
- A policy change from `copytruncate` or changing the HUP interaction with NFQUEUE is **out of scope** until independently proven safe for the live IPS.

Next operator validation:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m unittest discover -s tests -p 'test_passive_os_batch_spool.py' -v
ansible-playbook -i inventory/hosts.yml playbooks/router-01-suricata-logrotate-readonly-audit.yml --syntax-check
```

Only after the syntax check passes, optionally run the read-only playbook with `--ask-become-pass` to verify the *actual* rotation policy. No live collector should be enabled afterward just because the audit succeeds.


## Stage 4 — observed DHCP snapshots, NOT lease history (offline only)

Read-only router audit on 6 Nov 2026: dnsmasq enabled/active, 28 current DHCP leases, none expired or non-expiring, 24h pool `192.168.2.100–199`; lease-file root:root mode 0644. No `dhcp-script` hook was visible in the inspected configuration references. Current lease records have **expiry but no authoritative lease-start timestamp**, so don't backdate device identity.

`scripts/passive_os_lease_snapshot.py` parses an **operator-provided, local** dnsmasq lease-file copy and emits `observed_at`, IP→MAC mapping, lease expiry bounded to a *maximum 5-minute forward observation window*, and an explicit `observed_dhcp_snapshot_not_verified_lease_history` provenance string. It rejects expired leases, outside-LAN entries, malformed MACs and conflicting IP assignments. Hostnames and lease client identifiers are not exported. Its `leases` object matches the offline classifier's expected lease input shape when extracted, but the classifier must not be pointed at the entire wrapper object.

**Limitations:** forward windows are assumptions about continuity, not audited evidence that DHCP ownership could not have changed between observations; they may not capture static addresses or privacy MAC rotations. This cannot recover past IP→MAC history, and there is **no live DHCP capture, no timer, and no dnsmasq configuration change**. For stronger confidence later, evaluate a read-only neighbour/lease observation sampling policy and explicit temporal conflict management, or separately approve a dnsmasq lease-change hook after assessing DHCP/router risk.

New offline validation (awaiting operator run):

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m unittest discover -s tests -p 'test_passive_os_lease_snapshot.py' -v
python3 -m py_compile scripts/passive_os_lease_snapshot.py
```


## Stage 5 — receiver integrity verification (offline only)

Added `scripts/passive_os_receipt_verify.py` and eight regression tests in `tests/test_passive_os_receipt_verify.py`. The verifier compares the exact pending source batch with the locally stored receiver batch and verifies the receipt's ID, digest, protocol and size. It refuses missing, truncated, modified and symlinked artifacts. **It does not change a router checkpoint, call the ack hook, connect over SSH or create accounts.** Tests have been committed but **not yet executed on admin-01**.

### Proposed future transfer/security contract (not configured)

- **Account on router-01:** dedicated minimally privileged account, no password, only a pinned forced command to retrieve a pre-sanitised batch/receipt protocol, source-bound to sensor-01; deny PTY, X11, agent and TCP forwarding and disallow arbitrary shell commands. Do not grant general EVE read permission or sudo without reviewing an audited minimiser that writes only sanitised private batches.
- **sensor-01:** use strict host key verification pinned to a separately validated router SSH host key; private key readable only by dedicated service account, no agent forwarding; retrieve only limited batches with maximum byte/time caps. Never disable host-key checking for convenience.
- **End-to-end logic:** receiver writes batch and receipt durably; sensor independently confirms storage, then provides a receipt via a mutually authenticated channel. Router validates authenticated receipt against its still-pending batch ID/digest before a guarded checkpoint ack. The current local verifier **does not authenticate the receiver's identity** and a copied receipt alone is not sufficient.
- **Resource limits:** one unacknowledged source batch; before deploying receiver enforce bounded retained batch count/bytes, safe cleanup only after verified processing and monitoring for backlog. Existing receiver lacks retention quota; **do not schedule**.
- **Recovery and lease safety:** copytruncate can lose EVE lines; source best-effort only. DHCP snapshots are observational, not authoritative history. Explicitly monitor gaps, stalled batches, storage pressure and classification conflict.
- **Deployment:** once fully reviewed, add approval-gated Ansible to stage code and account separately from any start/timer, with preflight checks on actual hostname `raspberrypi` and inventory host `router-01`, backup/rollback and no IPS, QoS, routing or DNS changes.

Offline test command after pulling branch:

```bash
cd ~/projects/homelab-network-enrichment/IaC/ansible
python3 -m unittest discover -s tests -p 'test_passive_os_receipt_verify.py' -v
python3 -m py_compile scripts/passive_os_receipt_verify.py
```

**There is no production transfer yet.**


## Stage 5.2 — offline receiver capacity guard (not deployed)

The receiver now rejects new batches when the private receiving directory would exceed **256 stored batch files** or **64 MiB** of retained batch-plus-receipt content. It rejects symlinks, unexpected file names and excessive directory entries. Retried delivery of an existing unchanged batch remains idempotent. There is **no automatic deletion**, so quota pressure is a safe operational stop rather than evidence loss.

Six new tests were added to `tests/test_passive_os_batch_receiver.py` for byte and batch ceilings, retries, unexpected/symlinked files, and non-deletion. These tests have **not yet been verified by the operator**; the earlier 6 receiver tests were verified and the previous cumulative total was 62 tests.

Caveat: these are local prototype limits only. A production pipeline still needs an explicitly scoped storage location, filesystem safety and crash durability validation, signed/verified remote receipts, authenticated SSH forced commands, retention governance, and a separate reviewed process that marks evidence as *processed* before cleanup. No timers or automated acknowledgments may be enabled on this basis.

Offline validation:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m unittest discover -s tests -p 'test_passive_os_batch_receiver.py' -v
python3 -m unittest discover -s tests -p 'test_passive_os_receipt_verify.py' -v
python3 -m py_compile scripts/passive_os_batch_receiver.py
```

## Stage 5.3 — restricted SSH transport policy (offline, NOT installed)

New `scripts/passive_os_ssh_policy.py` creates a **candidate** authorized_keys line with Ed25519 key, `restrict`, source IP 192.168.2.55, and fixed command `/usr/local/libexec/homelab-passive-os-export`. The forced-command program has **not** been created. No identity, key or SSH configuration has been installed. `tests/test_passive_os_ssh_policy.py` adds eleven offline synthetic security tests, not yet run on admin-01.

New `playbooks/passive-os-ssh-readonly-preflight.yml` audits SSH daemon global defaults, service state, runtime hostname and ED25519 public host-key file *metadata only*. It does not retrieve private keys, change configuration, or validate effective per-user `Match`/authorized_keys restrictions.

Security gates before live transport: (1) independently verify/pin router host key and use a distinct non-login service identity; (2) source-IP-scoped restricted forced-command key, rejecting shells, PTY, forwarding, arbitrary commands and paths, with no access to raw EVE; (3) bound bytes, time and server CPU plus storage and lease observation schedule; (4) prove authentic end-to-end receiver receipt and durability before any automatic source checkpoint acknowledgment; (5) fail closed on identity, host key, network or rotation interruption; (6) independently reviewed Ansible approval/rollback with no IPS, routing, QoS, DHCP or SSH daemon restart.

Run after `git pull --ff-only` on admin-01:

```bash
cd ~/projects/homelab-network-enrichment/IaC/ansible
python3 -m unittest discover -s tests -p 'test_passive_os_ssh_policy.py' -v
python3 -m py_compile scripts/passive_os_ssh_policy.py
ansible-playbook -i inventory/hosts.yml playbooks/passive-os-ssh-readonly-preflight.yml --syntax-check
```

If syntax/test checks succeed, the optional read-only audit is: `ansible-playbook -i inventory/hosts.yml playbooks/passive-os-ssh-readonly-preflight.yml --ask-become-pass`. The static policy tests are not proof of a functioning or secure SSH deployment; **do not provision users/keys or enable any timer yet**.

## Stage 5.4 — fixed-command sanitised exporter prototype (OFFLINE ONLY)

New `scripts/passive_os_ssh_export.py` is a **candidate** implementation, not installed at the configured `/usr/local/libexec/homelab-passive-os-export` path. It does not open SSH connections or modify any files. `main()` accepts **no CLI arguments**, obtains the exact SSH original command, and only accepts `get-batch`. It reads a fixed path `/var/lib/homelab-passive-os/pending.json`; tests call its pure export function with synthetic private temporary files.

Exporter checks the pending batch is an ordinary private file, verifies existing batch/digest integrity, validates allowlisted per-event fields and LAN source IPs, then emits **only** protocol, batch ID, digest and minimised observations. No `next_state`, offset, file paths, DNS domains, URLs, SNI or raw user agents travel in its output. It cannot prepare a batch, acknowledge delivery or advance the checkpoint. It performs no account creation, chmod, HUP or Suricata actions.

Added ten regression cases in `tests/test_passive_os_ssh_export.py`, including command injection, missing/unsafe input, extra sensitive fields, public IP, tampering, empty batch and no-ack behavior. **Tests require operator verification** after pulling the feature branch.

**Integration caveat:** the existing offline receiver currently expects the internal pending-batch schema (including `next_state`), whereas this exporter deliberately sends a narrower wire schema. This **cannot yet be connected to a receiver**. A separate authenticated wire receiver and receiver-proof protocol must be designed and tested before deploying the exporter. Actual forced-command executable, SSH keys, service account, known_hosts pinning and scheduled work are still absent. No transport endpoint is authorised.

Offline validation:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m unittest discover -s tests -p 'test_passive_os_ssh_export.py' -v
python3 -m py_compile scripts/passive_os_ssh_export.py
```

Keep source-and-sensor live configuration unchanged until a manual, approval-gated and rollback-tested deployment design is complete.

## Stage 5.5 — offline sanitised wire receiver (NOT deployed)

New `scripts/passive_os_wire_receiver.py` accepts the **four-field wire batch** emitted by the Stage 5.4 exporter (`protocol`, `batch_id`, `digest`, `observations`) without receiving any internal router checkpoint state. It rejects extra fields, duplicate JSON keys, invalid event/IP/OS fields, mismatched observation digest, oversized data, symlinks, insecure destination permissions and conflicting existing evidence. `receive_wire()` stores the canonical batch and a local receipt privately, with file fsync and an explicit parent-directory fsync, and reuses the Stage 5.2 fail-closed 256-batch/64MiB capacity rules. Command-line mode operates exclusively on local files under an exclusive destination lock; no SSH sockets or service actions are implemented.

**Security limit:** the wire-format `batch_id` derives from the router's private checkpoint data, so the receiver can validate only its syntax and the observations digest, **not recompute the batch ID**. The future authenticated transport must establish the sender and bind that received ID to a verified router pending batch before upstream acknowledgment. A local receipt is NOT sender authentication, NOT a network acknowledgment, and NOT authority for the old `--ack-id` test hook. Durability is best-effort pending power-loss, filesystem and interrupted-write recovery testing. No automatic cleanup or timer.

Fifteen additional tests in `tests/test_passive_os_wire_receiver.py` exercise local exporter/receiver roundtrip, malicious data rejection, idempotent retry, storage quota handling and no checkpoint advancement. **Tests pending operator verification.** The old internal-schema receiver remains for its prior offline regression suite; it must NOT be connected directly to the new restricted export.

To validate on admin-01 after pulling:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m py_compile scripts/passive_os_wire_receiver.py
python3 -m unittest discover -s tests -p 'test_passive_os_wire_receiver.py' -v
python3 -m unittest discover -s tests -p 'test_passive_os_ssh_export.py' -v
```

Remaining deployment blockers: separately verified pinned router host key, restricted account and installed forced-command program, manually validated authenticated transport/receipt proof, inter-host failure tests, storage quota observability, and an Ansible-approved no-automatic-ack pilot. No router-01 or sensor-01 settings changed.

## Stage 5.6 — offline Ed25519 receipt attestation (NOT deployed)

Added `scripts/passive_os_signed_receipt.py` and eleven tests in `tests/test_passive_os_signed_receipt.py`, pending operator validation. Requires Python package `cryptography` for Ed25519 and **fails to import if unavailable**; do not install it automatically on router-01.

A synthetic receiver signer checks the expected canonical sanitised wire bytes, saved wire bytes and existing local receipt, then signs a domain-separated proof with batch ID, observation digest, stored bytes, SHA-256 of the complete wire batch, receiver identity `sensor-01` and a 32-byte caller challenge (hex). Verification accepts a separately pinned Ed25519 public key; it rejects wrong keys, modified proofs/signatures, stale challenges and mismatched expected wire batches. Test signing keys are generated only in process memory. No SSH keys or signed receipts are deployed.

**Trust limits:** this helper operates on caller-supplied byte strings, not independently authenticated storage or a locked receiver filesystem. It does **not** obtain a live authenticated SSH identity, prove an actual network transfer or physical power-cut durability, obtain a fresh challenge securely, establish key custody/rotation or allow router acknowledgment. A production signer must be bound to private receiver storage and authentic key material; the verifier must receive the router's **currently pending** batch context over a trusted coordinator before any ack is even considered. The wire batch ID cannot be independently recalculated without the router-private checkpoint; signing an attacker-supplied batch alone does not resolve that.

Offline validation after pulling feature branch:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -c 'from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; print("Ed25519 available")'
python3 -m py_compile scripts/passive_os_signed_receipt.py
python3 -m unittest discover -s tests -p 'test_passive_os_signed_receipt.py' -v
python3 -m unittest discover -s tests -p 'test_passive_os_wire_receiver.py' -v
```

Expected new test count: 11; previous confirmed suites total 104. No new SSH host key trust established; no key provisioning, account creation, service installation, timer or checkpoint mutation.

## Stage 5.7A — read-only SSH identity baseline (NOT provisioned)

Staged `playbooks/passive-os-ssh-identity-readonly-preflight.yml`. This playbook checks the two canonical endpoints (router-01 at 192.168.2.1 and sensor-01 at 192.168.2.55), runtime hostname, whether the **candidate** `homelab-os-transfer` account already exists, Ed25519 public host-key metadata and locally computed SHA256 fingerprint, and SSH daemon global defaults. The public key fingerprint is not secret. The playbook does **not** create or modify any account, key, known_hosts entry, authorised_keys, sshd configuration, firewall, or running service. Uses become only for reading `sshd -T` global effective settings.

**Crucial trust boundary:** a fingerprint read from router-01 through the existing admin SSH connection is audit evidence only; it is *not independently authenticated* simply because the command executed over SSH. Record the expected fingerprint using a trusted local/console route or a prior independently verified inventory, compare it out-of-band, and obtain explicit approval before pinning. Never use `ssh-keyscan` alone as proof of authenticity and do not auto-accept host keys.

Service account name is a collision probe only; do not assume an existing account is safe to reuse. `sshd -T` reports broad/global defaults, not per-user `Match` or forced-command policy. No login or end-to-end transfer test is performed.

Run after fast-forward pull from feature branch:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/passive-os-ssh-identity-readonly-preflight.yml --syntax-check
ansible-playbook -i inventory/hosts.yml playbooks/passive-os-ssh-identity-readonly-preflight.yml --ask-become-pass
```

Expected result: `changed=0` for both endpoints. Review the printed fingerprints and candidate-account collision state; **do not add a pinned key or create credentials** until independent verification and the approval-gated identity provisioning playbook have been reviewed. Stage 5.6 has 115/115 uniquely verified offline tests; this read-only host audit does not add a new unit test.

## Stage 5.7B — gated *dormant identity* staging (NOT executed)

Added `playbooks/passive-os-ssh-identity-provision-gated.yml`, targeted **only** at router-01. It is fail-closed by default: requires two explicit operator approval variables and a fingerprint value which the operator must **first** verify independently using a trusted local console or independently trusted record. The value currently observed through Ansible, `SHA256:4+g89AyhxUGCOGMZD5FRlqMSOlwdgVwt/0N/N4a7XxI`, is **not** itself trusted proof. The playbook checks the endpoint, runtime hostname `raspberrypi`, on-host ED25519 public-key fingerprint and absence of the prospective account before any write. It stops if the account already exists, requiring a separate idempotence/reconciliation policy. Never run with approval flags just to bypass the gate.

If and only if approved later, this playbook creates a **dormant password-locked account** (`homelab-os-transfer`) with no home directory and `/usr/sbin/nologin`. It installs **no** authorised SSH key, known_hosts pin, SSH config, executable, timer, service or checkpoint hook. Such a nologin account **cannot run the planned forced-command exporter**; a separate future security-reviewed account activation mechanism is required and deliberately **not included** here.

Offline-only Ansible syntax verification:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
ansible-playbook -i inventory/hosts.yml playbooks/passive-os-ssh-identity-provision-gated.yml --syntax-check
```

Do not run the playbook in apply mode or supply approval variables at this stage. To independently verify the host key, run the public-key fingerprint command **from a physically trusted local console**, not by SSH through the same currently unverified path:

```bash
ssh-keygen -l -E sha256 -f /etc/ssh/ssh_host_ed25519_key.pub
```

Record a verified fingerprint and obtain separate explicit approval before changing accounts. Later deployment needs an approved rollback plan, proper least-privilege execution with per-account restrictions, keyed authentication, evidence transfer, and no automatic acknowledgment.

## Stage 5.7B continuation — rollback and default-deny guardrails (OFFLINE)

Added `playbooks/passive-os-ssh-identity-rollback-gated.yml` and seven lightweight offline source-level checks in `tests/test_passive_os_identity_playbook_gates.py`. The rollback targets router-01 **only**, is disabled by default (`passive_os_rollback_approved: false`), checks the live hostname, requires the exact project-owned dormant account marker, home and shell, refuses an existing account with active processes or unexpected login material, and only then removes the account without deleting a home directory. It never changes sshd or gateway services. **This rollback is NOT suited to later activated identities**: if the account has been modified, the playbook intentionally refuses removal.

Neither the gated identity provisioning nor rollback playbook has been applied to any host. Their current status is prepared but **not authorised for execution**. The published fingerprint match from `james@raspberrypi` confirms consistency with the audit, but independent verification is conditional on a trusted local console path; that provenance has not yet been established by the user's latest messages. Do not set either approval flag as an inference.

Operator offline checks:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m unittest discover -s tests -p 'test_passive_os_identity_playbook_gates.py' -v
ansible-playbook -i inventory/hosts.yml playbooks/passive-os-ssh-identity-provision-gated.yml --syntax-check
ansible-playbook -i inventory/hosts.yml playbooks/passive-os-ssh-identity-rollback-gated.yml --syntax-check
```

These tests are simple source-policy checks, not proof of runtime safety or account ownership. Deployment still needs physical-console confirmation, explicit user approval for the live identity change, and a rollback/change window. **Do not run either playbook in apply mode at this stage.**

## Stage 5.7C — offline authenticated-transport argv and response planner (NOT deployed)

Added `scripts/passive_os_transport_plan.py` and 10 offline checks in `tests/test_passive_os_transport_plan.py`. These generate only a fixed `ssh` argument list (source identity sensor-01, restricted router destination `homelab-os-transfer@192.168.2.1`, exact `get-batch`), strict host-key checking with a *future* trusted known_hosts file and private identity key, no forwarding, and bounded connection attempts. The module neither executes SSH nor checks that files exist. Response validation fails closed on failed SSH exit codes, empty/oversized/noncanonical/corrupt data. The read-only API never alters a router checkpoint.

**Host-key provenance verified as NOT independent:** user explicitly confirmed that the fingerprint command at `james@raspberrypi` was run over an SSH connection. It matched the preflight, but it was obtained over the same class of management channel and therefore does **not** satisfy independent host identity validation. Do not set `passive_os_fingerprint_independently_verified`, do not pin this key as trusted, and do not run either live identity provisioning or rollback playbook. A trusted local console or independently authenticated inventory record is still needed before future activation.

This is a test-only transport planner: no service users, SSH key material, known_hosts pinning, forced-command installation, real key authentication, host key verification or receipt transfer has occurred. The client plan does not implement subprocess timeouts/output streaming or cancellation; these must be designed and exercised before any live transport. The forced command cannot run using the dormant `/usr/sbin/nologin` identity; a separately reviewed activation is required.

Offline operator validation:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m py_compile scripts/passive_os_transport_plan.py
python3 -m unittest discover -s tests -p 'test_passive_os_transport_plan.py' -v
```

Ten new tests require operator validation. Previous confirmed unique test count is 122; if all ten pass, total becomes 132. Continue without production changes.

## Stage 5.7D — bounded local subprocess runner (OFFLINE, NOT connected to SSH)

Committed `scripts/passive_os_bounded_process.py` and 13 synthetic LOCAL subprocess tests in `tests/test_passive_os_bounded_process.py`. The runner uses fixed argv (no shell), detached process group, disabled stdin, no inherited handles, concurrent nonblocking reads of stdout/stderr via selectors, an absolute monotonic deadline (maximum 8 seconds), a 2 MiB+8 KiB stdout ceiling and 8 KiB stderr ceiling. On timeout, stream overflow, nonzero exit or interruption it rejects output and kills/reaps the isolated process group.

**Not transport deployment:** this is an intentionally unconnected, low-level LOCAL test primitive. It does not call `retrieval_argv`, execute SSH, authenticate identities, pin host keys, transfer evidence, touch the router or update a checkpoint. Runtime process/failure guarantees require real integration/fault-injection review. If integrated later, use the fixed approved SSH argv and separately validate source identity, receipt durability, challenge freshness and trusted acknowledgments.

**Host identity blocker remains:** operator explicitly said the router key fingerprint was collected *over SSH*. Matching repeated readings does not satisfy independent host authentication. The live identity provisioning and rollback approval flags remain unset. Do not create any account/key or enable a timer.

Validate on admin-01 only:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m py_compile scripts/passive_os_bounded_process.py
python3 -m unittest discover -s tests -p 'test_passive_os_bounded_process.py' -v
python3 -m unittest discover -s tests -p 'test_passive_os_transport_plan.py' -v
```

Expected new cases: 13. Previously confirmed 132 unique offline tests; when these pass, 145 unique cases. **No production apply step.**


## Stage 5.7E — synthetic local end-to-end validation (NOT deployed)

Added `scripts/passive_os_offline_pipeline.py` and `tests/test_passive_os_offline_pipeline.py` (**12 tests pending operator execution**). The deliberately local-only harness accepts an explicit `synthetic_test_only=True` gate and a Python `-c` fixture command, never SSH. It exercises the existing bounded subprocess runner, strict canonical wire validation and local private durable receiver. It does **not** automatically acknowledge, advance or delete a source-side pending batch.

Tests cover successful store, duplicate retry, corrupted and truncated wire, nonzero child status, stalled subprocess, oversized stdout, explicit local-only gate, refusing ssh argv, unsafe destination mode and symlink, preserving existing receipt on later failure and unchanged source checkpoint. Tests are synthetic, not actual network authentication nor an end-to-end proof of crash consistency.

Run on **admin-01** only:

```bash
cd ~/projects/homelab-network-enrichment
git pull --ff-only origin feature/network-enrichment-independent-proxmox-20261105
cd IaC/ansible
python3 -m py_compile scripts/passive_os_offline_pipeline.py
python3 -m unittest discover -s tests -p 'test_passive_os_offline_pipeline.py' -v
```

Prior confirmed unique offline checks: **145/145**. If all 12 newly staged cases pass, cumulative becomes **157/157**. **Do not invoke any account provisioning/rollback playbook, install keys or enable SSH transport**: independently authenticated router host key is still unavailable (the user confirmed the repeated fingerprint came via SSH) and explicit production approval is absent.

### Open Stage 5.7E questions before any rollout

- Simulate process cancellation and system crash at each write/fsync boundary; validate durability on actual intended filesystem before claiming power-loss guarantees.
- Add cross-host authenticated sender identity and signed receiver attestation, with replay protection and proven write receipt before a separately gated upstream acknowledgment. This offline harness does not combine those guarantees.
- Review path ownership and symlink races, concurrent receiver locking and quotas in integrated operation. The synthetic wrapper itself is not an authorised deployable service.
