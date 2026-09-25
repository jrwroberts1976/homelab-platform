"""Select new devices from the passive collector's state."""

import ipaddress
import re

MAC_PATTERN = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\Z")


def select_new_device(collector, profiles, network="192.168.2.0/24"):
    """Return the oldest eligible new device without changing either state."""
    if collector.get("schema_version") != 1:
        raise ValueError("Unsupported collector state")

    devices = collector.get("devices")
    if not isinstance(devices, dict) or not isinstance(profiles, dict):
        raise ValueError("Invalid device or profile state")

    subnet = ipaddress.ip_network(network)
    pending = []

    for mac, device in devices.items():
        if device.get("status") != "pending" or mac in profiles:
            continue

        ip = ipaddress.ip_address(device["last_ip"])
        if not MAC_PATTERN.fullmatch(mac) or ip not in subnet:
            raise ValueError("Invalid pending device identity or IP")

        pending.append((device["discovered_at"], mac, str(ip)))

    if not pending:
        return None

    _, mac, ip = min(pending)
    return {"mac": mac, "ip": ip}


def select_next_device(collector, profiles, now, cooldown=86400):
    """Prioritise new devices, then eligible retries."""
    new = select_new_device(collector, profiles)
    if new is not None:
        return new

    retries = []
    for mac, device in collector["devices"].items():
        if device.get("status") != "pending":
            continue

        record = profiles.get(mac, {})
        if record.get("status") not in ("reserved", "failed", "partial"):
            continue

        last = record.get("last_attempt")
        if type(last) not in (int, float) or last < 0:
            continue
        if now - last < cooldown:
            continue

        ip = device["last_ip"]
        if not MAC_PATTERN.fullmatch(mac):
            raise ValueError("Invalid retry MAC")
        if ipaddress.ip_address(ip) not in ipaddress.ip_network(
            "192.168.2.0/24"
        ):
            raise ValueError("Retry target outside approved LAN")

        retries.append((last, mac, ip))

    if not retries:
        return None

    _, mac, ip = min(retries)
    return {"mac": mac, "ip": ip}
