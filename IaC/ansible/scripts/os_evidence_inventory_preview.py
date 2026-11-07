#!/usr/bin/env python3
"""Read-only OS provenance preview using existing inventory, Zabbix and profiles.

Optional validated passive candidate JSON is supplied by operator only; this
script never fetches router/sensor evidence or publishes/promotes metrics.
"""
import argparse
import ipaddress
import json
from pathlib import Path

from os_evidence_precedence import resolve
from passive_os_unmanaged_inventory_audit import (
    DEFAULT_INVENTORY, DEFAULT_TOKEN, DEFAULT_ZABBIX, OS_KEYS,
    compare, zabbix_api,
)

DEFAULT_PROFILES = "/var/lib/homelab-network-hosts/deep-profiles.json"
MAX_BYTES = 5_000_000
PASSIVE_FAMILIES = {"Linux", "Windows", "macOS", "Android", "iOS/iPadOS", "ChromeOS"}


def bounded_json(path):
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Oversized input")
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("Expected JSON object")
    return value


def validate_passive(raw):
    """Accept only minimised dry-run JSON with explicit provenance fields."""
    if (raw.get("status") != "dry_run_only"
            or not isinstance(raw.get("candidates"), list)
            or len(raw["candidates"]) > 2000):
        raise ValueError("Passive input must be a verified dry-run candidate summary")
    validated = []
    for item in raw["candidates"]:
        if (not isinstance(item, dict)
                or set(item) != {"src_ip", "os_family_hint", "observations",
                                   "confidence", "mac_attribution"}
                or item.get("confidence") != "low"
                or item.get("mac_attribution") != "unverified"
                or item.get("os_family_hint") not in PASSIVE_FAMILIES
                or type(item.get("observations")) is not int
                or not 0 < item["observations"] <= 2000):
            raise ValueError("Untrusted passive candidate")
        try:
            ip = ipaddress.ip_address(item["src_ip"])
        except (ValueError, TypeError):
            raise ValueError("Invalid passive IP") from None
        if ip not in ipaddress.ip_network("192.168.2.0/24"):
            raise ValueError("Outside inventory subnet")
        validated.append(item)
    return validated


def preview(inventory, profiles, groups, hints=()):
    membership = {}
    for group, ips in groups.items():
        for ip in ips:
            if ip in membership:
                raise ValueError("Duplicate Zabbix classification")
            membership[ip] = group
    rows = []
    for ip in sorted(inventory, key=lambda v: ipaddress.ip_address(v)):
        host = inventory[ip]
        if not isinstance(host, dict):
            continue
        mac = str(host.get("mac") or "").lower()
        record = profiles.get(mac) if mac else None
        # IP/MAC match required. A historic MAC scan is never carried across
        # to a new IP without the profiler's exact profiled_ip check.
        if not isinstance(record, dict) or record.get("last_ip") != ip:
            record = None
        rows.append(resolve(ip, mac, membership[ip], record, hints))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=Path(DEFAULT_INVENTORY))
    parser.add_argument("--profiles", type=Path, default=Path(DEFAULT_PROFILES))
    parser.add_argument("--token", type=Path, default=Path(DEFAULT_TOKEN))
    parser.add_argument("--zabbix-url", default=DEFAULT_ZABBIX)
    parser.add_argument("--passive-dry-run", type=Path,
                        help="Optional operator-supplied validated sensor dry-run JSON")
    args = parser.parse_args()
    inventory = bounded_json(args.inventory)
    profile_document = bounded_json(args.profiles)
    profiles = profile_document.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError("Missing profile records")
    token = args.token.read_text().strip()
    if not token:
        raise RuntimeError("Zabbix token missing")
    hosts = zabbix_api(args.zabbix_url, token, "host.get", {
        "output": ["hostid", "host", "status"],
        "selectInterfaces": ["ip", "useip"],
    })
    items = zabbix_api(args.zabbix_url, token, "item.get", {
        "output": ["hostid", "key_", "status", "state", "lastclock", "lastvalue"],
        "filter": {"key_": sorted(OS_KEYS)},
    })
    groups = compare(inventory, hosts, items)
    hints = validate_passive(bounded_json(args.passive_dry_run)) if args.passive_dry_run else []
    rows = preview(inventory, profiles, groups, hints)
    result = {
        "mode": "read_only_preview",
        "passive_input": "provided_dry_run" if args.passive_dry_run else "not_supplied",
        "totals": {
            "inventory": len(rows),
            "zabbix_os": len(groups["zabbix_os_authoritative"]),
            "managed_os_missing": len(groups["zabbix_without_os"]),
            "identity_ambiguous": len(groups["ambiguous"]),
            "unmatched_not_proven_unmanaged": len(groups["unmatched_inventory"]),
            "nmap_candidate": sum(r["os_source"] == "nmap" for r in rows),
            "passive_low_confidence": sum(r["os_source"] == "http_user_agent" for r in rows),
        },
        "non_authoritative_rows": [r for r in rows if r["os_source"] != "zabbix"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
