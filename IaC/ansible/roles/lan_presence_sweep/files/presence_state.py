"""Persistent, MAC-keyed LAN presence observations."""

import copy
import ipaddress
import math
import re

MAC = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\Z")


def empty_state():
    return {
        "schema_version": 1,
        "last_successful_sweep": None,
        "devices": {},
    }


def merge_sweep(previous, observed, timestamp):
    """Apply one successful sweep without losing historical identity."""
    if previous.get("schema_version") != 1:
        raise ValueError("Unsupported presence-state schema")

    if not isinstance(previous.get("devices"), dict):
        raise ValueError("Invalid presence inventory")

    if (
        not isinstance(timestamp, (int, float))
        or isinstance(timestamp, bool)
        or not math.isfinite(timestamp)
        or timestamp <= 0
    ):
        raise ValueError("Invalid sweep timestamp")

    last_sweep = previous.get("last_successful_sweep")
    if last_sweep is not None and timestamp <= last_sweep:
        raise ValueError("Out-of-order sweep")

    if not isinstance(observed, dict) or not observed:
        raise ValueError("Empty or invalid sweep")

    # Validate everything before modifying any state.
    verified = {}
    used_ips = set()

    for raw_mac, raw_ip in observed.items():
        if not isinstance(raw_mac, str):
            raise ValueError("Invalid MAC address")

        mac = raw_mac.lower()
        if not MAC.fullmatch(mac) or mac in verified:
            raise ValueError("Duplicate or invalid MAC")

        ip = str(ipaddress.IPv4Address(raw_ip))
        if ip in used_ips:
            raise ValueError("IP reported for multiple MACs")

        used_ips.add(ip)
        verified[mac] = ip

    result = copy.deepcopy(previous)
    devices = result["devices"]

    for record in devices.values():
        record["observed"] = False

    for mac, ip in verified.items():
        record = devices.setdefault(mac, {
            "first_seen": timestamp,
        })

        record["last_seen"] = timestamp
        record["last_ip"] = ip
        record["observed"] = True

    result["last_successful_sweep"] = timestamp
    return result
