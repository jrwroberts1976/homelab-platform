"""Look up network adapter vendors using Nmap's OUI database."""

import re
from pathlib import Path

MAC_PATTERN = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\Z", re.I)
OUI_PATTERN = re.compile(r"[0-9a-f]{6}\Z", re.I)


def load_vendors(path):
    vendors = {}

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        fields = line.split(None, 1)
        if len(fields) != 2 or not OUI_PATTERN.fullmatch(fields[0]):
            continue

        vendors[fields[0].upper()] = fields[1].strip()

    return vendors


def lookup_vendor(mac, vendors):
    if not isinstance(mac, str) or not MAC_PATTERN.fullmatch(mac):
        return None

    octets = bytes.fromhex(mac.replace(":", ""))

    # Multicast and locally administered/randomised MACs have
    # no reliable manufacturer identification through their prefix.
    if octets[0] & 0x03:
        return None

    return vendors.get(octets[:3].hex().upper())
