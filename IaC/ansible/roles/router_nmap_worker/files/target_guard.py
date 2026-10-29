"""Check that a scan target is still current and recently seen."""

import ipaddress
import json
import time
from pathlib import Path


def target_is_current(state_path, mac, ip, now=None, max_age=360):
    """Fail closed if the collector no longer confirms the target."""
    now = time.time() if now is None else now
    try:
        state = json.loads(Path(state_path).read_text())
    except (OSError, ValueError, TypeError):
        return False

    if state.get("schema_version") != 1:
        return False

    devices = state.get("devices")
    if not isinstance(devices, dict):
        return False

    device = devices.get(mac)
    if not isinstance(device, dict):
        return False

    try:
        target = ipaddress.IPv4Address(ip)
        recorded = ipaddress.IPv4Address(device["last_ip"])
        seen = float(device["last_inventory_seen"])
    except (KeyError, ValueError, TypeError):
        return False

    return (
        device.get("status") == "pending"
        and target == recorded
        and target in ipaddress.ip_network("192.168.2.0/24")
        and 0 <= now - seen
        and (max_age is None or now - seen <= max_age)
    )



def post_scan_identity_verified(state_path, mac, ip, runner,
                                interface="eth0"):
    """Fresh ARP verification followed by a new collector-state check."""
    from presence import probe_mac_ip

    if not probe_mac_ip(ip, mac, runner, interface=interface):
        return False

    return target_is_current(
        state_path, mac, ip, max_age=None
    )
