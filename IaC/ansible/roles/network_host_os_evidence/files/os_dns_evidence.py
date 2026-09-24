#!/usr/bin/env python3
"""Offline, opt-in OS update-domain evidence extraction. No network calls."""
import argparse
import collections
import ipaddress
import json
from pathlib import Path

INDICATORS = {
    "ubuntu": ("security.ubuntu.com", "archive.ubuntu.com"),
    "debian": ("deb.debian.org", "security.debian.org"),
    "microsoft_updates": ("windowsupdate.com", "update.microsoft.com"),
    "apple_updates": ("swcdn.apple.com", "mesu.apple.com"),
}
# These domains indicate repository/update traffic, NOT a verified device OS.
def indicator(query):
    name = str(query or "").strip().lower().rstrip(".")
    for family, domains in INDICATORS.items():
        if any(name == domain or name.endswith("." + domain) for domain in domains):
            return family
    return None

def classify(inventory, events, start, end, excluded_ips=()):
    excluded = set(excluded_ips)
    aggregates = collections.defaultdict(lambda: {"count": 0, "first_seen": None, "last_seen": None, "sensors": set()})
    rejected = collections.Counter()
    for event in events:
        if not isinstance(event, dict):
            rejected["invalid_event"] += 1
            continue
        # Zeek JSON dns.log: id.orig_h, query, ts. Normalized Pi-hole
        # adapter: src_ip, query, timestamp, sensor. Never guess source.
        source = event.get("id.orig_h") or event.get("src_ip")
        domain = event.get("query")
        sensor = str(event.get("sensor") or event.get("_sensor") or "unspecified")
        try:
            ts = int(float(event.get("ts", event.get("timestamp"))))
            ip = str(ipaddress.ip_address(source))
        except (ValueError, TypeError):
            rejected["invalid_identity_or_time"] += 1
            continue
        if not start <= ts <= end:
            rejected["outside_window"] += 1
            continue
        if ip in excluded:
            rejected["shared_resolver"] += 1
            continue
        family = indicator(domain)
        if not family:
            continue
        host = inventory.get(ip)
        if not isinstance(host, dict) or not host.get("mac"):
            rejected["unattributed"] += 1
            continue
        # Conservative attribution: historical IP ownership cannot be
        # established from a current inventory snapshot alone.
        first = int(host.get("first_seen") or 0)
        last = int(host.get("last_seen") or 0)
        if not first or not last or ts < first or ts > last:
            rejected["identity_not_valid_at_event_time"] += 1
            continue
        mac = str(host["mac"]).lower()
        item = aggregates[(mac, ip, family)]
        item["count"] += 1
        item["first_seen"] = ts if item["first_seen"] is None else min(item["first_seen"], ts)
        item["last_seen"] = ts if item["last_seen"] is None else max(item["last_seen"], ts)
        item["sensors"].add(sensor)
    records = [
        {"mac": mac, "ip": ip, "indicator": family,
         "count": v["count"], "first_seen": v["first_seen"],
         "last_seen": v["last_seen"], "sensors": sorted(v["sensors"]),
         "classification": "traffic_hint_only"}
        for (mac, ip, family), v in sorted(aggregates.items())
    ]
    return {"schema_version": 1, "window": {"start": start, "end": end},
            "evidence": records, "rejected": dict(sorted(rejected.items())),
            "verified_os_count": 0}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inventory", type=Path, required=True)
    p.add_argument("--dns-jsonl", type=Path, required=True,
                   help="Exported Zeek JSON dns.log or normalized Pi-hole JSONL")
    p.add_argument("--start", type=int, required=True)
    p.add_argument("--end", type=int, required=True)
    p.add_argument("--exclude-ip", action="append", default=[],
                   help="Shared resolver/proxy address; repeat as needed")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.end < args.start or args.end - args.start > 7 * 86400:
        p.error("Window must be nonnegative and no longer than seven days")
    inventory = json.loads(args.inventory.read_text())
    if not isinstance(inventory, dict):
        p.error("Inventory must be an IP-keyed JSON object")
    with args.dns_jsonl.open() as fh:
        events = (json.loads(line) for line in fh if line.strip())
        result = classify(inventory, events, args.start, args.end, args.exclude_ip)
    # Offline output contains only OS-relevant aggregates, never raw queries.
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
