#!/usr/bin/env python3
"""OFFLINE prototype: bounded passive OS clues, never packet capture or Nmap.

Input is *already minimised* JSONL with {timestamp, src_ip, event_type,
http_user_agent?}; independent lease snapshot maps IP -> MAC with valid_from/
valid_until Unix seconds. No DNS queries, domains, URLs, TLS SNI or raw
User-Agent values are written to output. No networking or runtime installation.

Do not connect this directly to router-01 EVE until a separate approved,
rotation-safe transport/retention design is implemented.
"""
import argparse
import ipaddress
import json
import re
from collections import defaultdict
from pathlib import Path

LAN = ipaddress.ip_network("192.168.2.0/24")
MAC = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$")
MAX_EVENTS = 20000
MAX_LINE = 8192
MAX_FILE = MAX_EVENTS * MAX_LINE


def family_from_user_agent(value):
    """Application self-report, never authoritative OS identity."""
    if not isinstance(value, str):
        return None
    s = value[:1024].lower()
    if "cros " in s or "chromebook" in s:
        return "ChromeOS"
    if "android" in s:
        return "Android"
    if "iphone" in s or "ipad" in s or "ipod" in s:
        return "iOS/iPadOS"
    if "windows nt" in s:
        return "Windows"
    if "mac os x" in s or "macintosh" in s:
        return "macOS"
    if "linux" in s or "x11;" in s:
        return "Linux"
    return None


def valid_client(ip):
    try:
        address = ipaddress.ip_address(ip)
    except (TypeError, ValueError):
        return False
    return address in LAN and address not in (
        LAN.network_address, LAN.broadcast_address, LAN.network_address + 1
    )


def lease_mac(leases, ip, stamp):
    """Fail closed if no time-bounded, unambiguous lease matches event time."""
    entries = leases.get(ip, [])
    if not isinstance(entries, list):
        return None
    matching = set()
    for lease in entries:
        if not isinstance(lease, dict):
            continue
        try:
            start = int(lease["valid_from"])
            end = int(lease["valid_until"])
            mac = str(lease["mac"]).lower()
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        if start <= stamp < end and MAC.fullmatch(mac):
            matching.add(mac)
    return next(iter(matching)) if len(matching) == 1 else None


def classify(events, leases, max_events=MAX_EVENTS):
    """Return bounded, privacy-minimised device summaries from event iterable."""
    groups = defaultdict(lambda: {"families": defaultdict(int),
                                  "http_without_os": 0,
                                  "metadata_only": 0,
                                  "last_observed": 0})
    processed = 0
    skipped_unattributed = 0
    for event in events:
        processed += 1
        if processed > max_events:
            raise ValueError("Too many input events")
        if not isinstance(event, dict):
            continue
        ip = event.get("src_ip")
        if not valid_client(ip):
            continue
        try:
            stamp = int(event["timestamp"])
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        mac = lease_mac(leases, ip, stamp)
        if mac is None:
            skipped_unattributed += 1
            continue
        kind = event.get("event_type")
        if kind not in ("http", "dns", "tls", "quic"):
            continue
        entry = groups[(mac, ip)]
        entry["last_observed"] = max(stamp, entry["last_observed"])
        if kind == "http":
            family = family_from_user_agent(event.get("http_user_agent"))
            if family:
                entry["families"][family] += 1
            else:
                entry["http_without_os"] += 1
        else:
            # Domain names and TLS fingerprints are NOT OS proof.
            entry["metadata_only"] += 1
    result = []
    for (mac, ip), item in sorted(groups.items()):
        candidates = sorted(item["families"])
        if len(candidates) == 1:
            os_family, confidence, status = candidates[0], "low", "candidate"
        elif len(candidates) > 1:
            os_family, confidence, status = "unknown", "none", "conflicting"
        else:
            os_family, confidence, status = "unknown", "none", "insufficient"
        result.append({
            "ip": ip, "mac": mac, "os_family": os_family,
            "confidence": confidence, "status": status,
            "source": "http_user_agent" if candidates else "passive_metadata",
            "observations": sum(item["families"].values()),
            "last_observed": item["last_observed"],
        })
    return {"schema_version": 1, "devices": result,
            "skipped_unattributed": skipped_unattributed,
            "processed_events": processed}


def read_bounded_jsonl(path):
    if path.stat().st_size > MAX_FILE:
        raise ValueError("Input file exceeds bounded limit")
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if len(line) > MAX_LINE:
                raise ValueError("Input record exceeds bounded limit")
            yield json.loads(line)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--events", type=Path, required=True,
                    help="Minimised local JSONL; not raw EVE")
    ap.add_argument("--leases", type=Path, required=True,
                    help="Time-bounded IP-to-MAC lease JSON dictionary")
    args = ap.parse_args()
    if args.leases.stat().st_size > 1_000_000:
        raise ValueError("Lease mapping too large")
    leases = json.loads(args.leases.read_text(encoding="utf-8"))
    if not isinstance(leases, dict):
        raise ValueError("Lease mapping must be an IP-keyed dictionary")
    print(json.dumps(classify(read_bounded_jsonl(args.events), leases),
                     sort_keys=True))


if __name__ == "__main__":
    main()
