#!/usr/bin/env python3
"""Offline-only DHCP fingerprint normaliser.

Synthetic operator-supplied JSON fixtures only.
No packet capture, network access, DHCP changes or production integration.
Option 60 plaintext is never included in output.
"""
import hashlib
import ipaddress
import json
import re
from pathlib import Path

LAN = ipaddress.ip_network("192.168.2.0/24")
MAC = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$")
MAX_RECORDS = 2000
MAX_FILE_BYTES = 1024 * 1024


def normalise(record):
    if not isinstance(record, dict):
        raise ValueError("Expected DHCP observation object")

    if set(record) != {"timestamp", "src_ip", "mac", "option55", "option60"}:
        raise ValueError("Unexpected DHCP observation fields")

    ip = ipaddress.ip_address(record["src_ip"])
    if ip not in LAN or ip in (
        LAN.network_address, LAN.broadcast_address, LAN.network_address + 1
    ):
        raise ValueError("Invalid client IP")

    mac = record["mac"]
    if not isinstance(mac, str) or not MAC.fullmatch(mac.lower()):
        raise ValueError("Invalid MAC")

    stamp = record["timestamp"]
    if type(stamp) is not int or not 1577836800 <= stamp <= 4102444800:
        raise ValueError("Invalid timestamp")

    prl = record["option55"]
    if (
        not isinstance(prl, list)
        or not 1 <= len(prl) <= 128
        or any(type(v) is not int or not 1 <= v <= 254 for v in prl)
        or len(set(prl)) != len(prl)
    ):
        raise ValueError("Invalid DHCP Option 55")

    vendor = record["option60"]
    if (
        not isinstance(vendor, str)
        or not 1 <= len(vendor) <= 128
        or any(not 32 <= ord(c) <= 126 for c in vendor)
    ):
        raise ValueError("Invalid DHCP Option 60")

    return {
        "timestamp": stamp,
        "src_ip": str(ip),
        "mac": mac.lower(),
        "option55": prl,
        "option60_sha256": hashlib.sha256(
            vendor.encode("ascii")
        ).hexdigest(),
        "os_family": None,
        "confidence": "none",
        "status": "fingerprint_only",
        "source": "offline_dhcp_fixture",
        "attribution": "fixture_claim_unverified",
    }


def process(data):
    if not isinstance(data, dict) or set(data) != {"observations"}:
        raise ValueError("Invalid input document")

    records = data["observations"]
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError("Invalid observation count")

    return {
        "schema_version": 1,
        "mode": "offline_synthetic_only",
        "observations": [normalise(record) for record in records],
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    args = parser.parse_args()

    if not args.fixture.is_file():
        raise ValueError("Fixture must be a regular file")

    if args.fixture.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Fixture exceeds size limit")

    data = json.loads(args.fixture.read_text(encoding="utf-8"))
    print(json.dumps(process(data), sort_keys=True))


if __name__ == "__main__":
    main()
