"""Coordinate device selection and identity verification."""

import json
from pathlib import Path
from contextlib import contextmanager

from device_queue import select_new_device
from presence import probe_mac_ip
from target_guard import target_is_current


def find_verified_target(state_path, profiles, runner,
                         interface="eth0", now=None):
    """Return one verified target, or None. No profiling scans."""
    state = json.loads(Path(state_path).read_text())
    candidate = select_new_device(state, profiles)

    if candidate is None:
        return None

    mac, ip = candidate["mac"], candidate["ip"]

    # Check the latest collector state, not just our initial snapshot.
    if not target_is_current(state_path, mac, ip, now=now):
        return None

    if not probe_mac_ip(ip, mac, runner, interface=interface):
        return None

    # DHCP may have changed while ARP discovery was running.
    if not target_is_current(state_path, mac, ip, now=now):
        return None

    return candidate

@contextmanager
def prepare_verified_scan(state_path, worker_state_path, lock_path,
                          runner, interface="eth0", now=None,
                          cooldown=86400):
    """Verify and durably reserve exactly one device for profiling."""
    import time

    from device_queue import select_next_device
    from worker_lock import exclusive_worker_lock
    from worker_state import load_state, reserve_scan

    now = time.time() if now is None else now

    with exclusive_worker_lock(lock_path):
        collector = json.loads(Path(state_path).read_text())
        worker_state = load_state(worker_state_path)

        # Skip stale devices before selecting new work or retries.
        if not isinstance(collector.get("devices"), dict):
            raise ValueError("Invalid collector device state")

        eligible = {}
        for mac, device in collector["devices"].items():
            if not isinstance(device, dict):
                continue
            seen = device.get("last_inventory_seen")
            if type(seen) not in (int, float):
                continue
            if 0 <= now - seen <= 360:
                eligible[mac] = device

        collector = {**collector, "devices": eligible}
        candidate = select_next_device(
            collector,
            worker_state["profiles"],
            now=now,
            cooldown=cooldown,
        )

        if candidate is None:
            yield None
            return

        mac = candidate["mac"]
        ip = candidate["ip"]

        if not target_is_current(
            state_path, mac, ip, now=now
        ):
            yield None
            return

        if not probe_mac_ip(
            ip, mac, runner, interface=interface
        ):
            yield None
            return

        if not target_is_current(
            state_path, mac, ip, now=now
        ):
            yield None
            return

        if not reserve_scan(
            worker_state_path,
            mac,
            ip,
            now,
            cooldown=cooldown,
        ):
            yield None
            return

        yield candidate
