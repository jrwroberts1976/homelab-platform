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
