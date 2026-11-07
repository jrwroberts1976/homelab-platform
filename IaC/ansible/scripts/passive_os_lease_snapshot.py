#!/usr/bin/env python3
"""Offline-only dnsmasq lease snapshot -> conservative time-bounded mapping.

This is NOT a live DHCP collector; it reads an operator-supplied local copy.
Time windows are observational estimates, NOT proof of continuous ownership.
Never store device names/hostnames in output.
"""
import argparse
import ipaddress
import json
import re
from pathlib import Path

LAN = ipaddress.ip_network("192.168.2.0/24")
MAC_RE = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$")
MAX_INPUT_BYTES = 1024 * 1024
MAX_LEASES = 1024
DEFAULT_WINDOW = 300
MAX_WINDOW = 300


def parse_leases(lines, observed_at, window=DEFAULT_WINDOW):
    if not isinstance(observed_at, int) or observed_at < 1577836800:
        raise ValueError("Invalid observation timestamp")
    if not isinstance(window, int) or not (1 <= window <= MAX_WINDOW):
        raise ValueError("Unapproved observation window")
    evidence = {}
    conflicts = set()
    count = 0
    for line in lines:
        count += 1
        if count > MAX_LEASES:
            raise ValueError("Lease record limit exceeded")
        fields = line.split()
        if len(fields) < 4:
            continue
        try:
            expires = int(fields[0])
            ip = ipaddress.ip_address(fields[2])
        except (ValueError, TypeError):
            continue
        mac = fields[1].lower()
        if ip not in LAN or ip in (LAN.network_address, LAN.broadcast_address, LAN.network_address + 1):
            continue
        if not MAC_RE.fullmatch(mac) or expires <= observed_at:
            continue
        # Earliest possible attribution is observation time, never lease start.
        end = min(expires, observed_at + window)
        if end <= observed_at:
            continue
        key = str(ip)
        if key in evidence and evidence[key][0]["mac"] != mac:
            conflicts.add(key)
        else:
            evidence[key] = [{"mac": mac, "valid_from": observed_at, "valid_until": end}]
    for ip in conflicts:
        evidence.pop(ip, None)
    return dict(sorted(evidence.items())), sorted(conflicts)


def snapshot(lease_text, observed_at, window=DEFAULT_WINDOW):
    if len(lease_text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise ValueError("Lease source exceeds size limit")
    leases, conflicts = parse_leases(lease_text.splitlines(), observed_at, window)
    return {"schema_version": 1, "observed_at": observed_at,
            "window_seconds": window, "leases": leases,
            "conflicting_ips": conflicts,
            "attribution_basis": "observed_dhcp_snapshot_not_verified_lease_history"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--leases", required=True, type=Path)
    ap.add_argument("--observed-at", required=True, type=int,
                    help="Unix timestamp captured with the supplied snapshot")
    ap.add_argument("--window-seconds", type=int, default=DEFAULT_WINDOW)
    args = ap.parse_args()
    if args.leases.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("Lease source exceeds limit")
    data = snapshot(args.leases.read_text(encoding="utf-8"),
                    args.observed_at, args.window_seconds)
    print(json.dumps(data, sort_keys=True))


if __name__ == "__main__":
    main()
