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
