# Passive OS DNS evidence — offline prototype

This opt-in offline utility processes **exported** Zeek JSON `dns.log` records (`id.orig_h`, `query`, `ts`) or a separately normalised Pi-hole JSONL export (`src_ip`, `query`, `timestamp`). It does not connect to Loki, Pi-hole, Zeek, or any live host, install a service, or schedule a timer.

Example (use synthetic test data first):

```bash
python3 IaC/ansible/roles/network_host_os_evidence/files/os_dns_evidence.py \
  --inventory /path/to/inventory.json \
  --dns-jsonl /path/to/exported-dns.jsonl \
  --start 1780000000 --end 1780086400 \
  --exclude-ip 192.168.2.50 --exclude-ip 192.168.2.51 \
  --output /tmp/os-dns-evidence.json
```

Always exclude shared resolvers, proxies and NAT egress IPs. Do not pass logs with ambiguous client attribution. A current IP-keyed inventory cannot prove historical IP ownership; events outside a host's recorded first/last seen timestamps are rejected, but a DHCP reassignment *within* that range still requires a historical lease ledger before production attribution. Treat all output as unverified hints.

The script retains only aggregated indicator category, MAC/IP, timestamps, count and sensor name; it does not retain full domain queries or unrelated browsing data. Restrict output permissions and retention according to the homelab's privacy policy. Domain hints must never independently identify or verify an OS. AI integration is **not** enabled.

Tests: `python3 -m unittest discover -s IaC/ansible/roles/network_host_os_evidence/tests`.
