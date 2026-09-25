"""Persistent, MAC-keyed Nmap worker state."""

import json
import os
import tempfile
from pathlib import Path


def load_state(path):
    """Load existing state; reject corruption rather than lose evidence."""
    path = Path(path)
    if not path.exists():
        return {"schema_version": 1, "profiles": {}}

    state = json.loads(path.read_text())
    if (
        not isinstance(state, dict)
        or state.get("schema_version") != 1
        or not isinstance(state.get("profiles"), dict)
    ):
        raise ValueError("Invalid worker state")

    return state


def save_state(path, state):
    """Atomically save worker state with private permissions."""
    if (
        not isinstance(state, dict)
        or state.get("schema_version") != 1
        or not isinstance(state.get("profiles"), dict)
    ):
        raise ValueError("Refusing to save invalid worker state")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    fd, temporary = tempfile.mkstemp(
        prefix=".worker-state-", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w") as output:
            json.dump(state, output, indent=2, sort_keys=True)
            output.flush()
            os.fsync(output.fileno())

        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def reserve_scan(path, mac, ip, now, cooldown=86400):
    """Persist a scan reservation before executing Nmap."""
    state = load_state(path)
    profiles = state["profiles"]
    record = profiles.get(mac)

    if record is not None:
        if record.get("status") not in ("reserved", "failed", "partial"):
            return False
        last = record.get("last_attempt", 0)
        if now - last < cooldown:
            return False

    record = dict(record or {})
    record.update({
        "status": "reserved",
        "target_ip": ip,
        "last_attempt": now,
        "attempt_count": record.get("attempt_count", 0) + 1,
        "last_error": "",
    })
    profiles[mac] = record
    save_state(path, state)
    return True


def mark_scan_failed(path, mac, ip, error):
    """Record a failed scan without losing its reservation history."""
    if not isinstance(error, str) or not error.strip():
        raise ValueError("A scan failure requires an error message")

    state = load_state(path)
    record = state["profiles"].get(mac)

    if (
        not isinstance(record, dict)
        or record.get("status") != "reserved"
        or record.get("target_ip") != ip
    ):
        raise ValueError("No matching active scan reservation")

    record["status"] = "failed"
    record["last_error"] = error[:500]
    save_state(path, state)


def mark_scan_complete(path, collector_path, mac, ip, tcp, udp, now, runner, interface='eth0'):
    """Save completed scan evidence only for the verified target."""
    from target_guard import post_scan_identity_verified

    for result in (tcp, udp):
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("os_matches"), list)
            or not isinstance(result.get("ports"), list)
        ):
            raise ValueError("Invalid scan evidence")

    state = load_state(path)
    record = state["profiles"].get(mac)

    if (
        not isinstance(record, dict)
        or record.get("status") != "reserved"
        or record.get("target_ip") != ip
    ):
        raise ValueError("No matching scan reservation")

    if not post_scan_identity_verified(collector_path, mac, ip, runner, interface):
        raise RuntimeError("Device identity changed or became stale")

    record.update({
        "status": "complete",
        "profiled_ip": ip,
        "profiled_at": now,
        "last_error": "",
        "profile": {"tcp": tcp, "udp": udp},
    })
    save_state(path, state)


def mark_scan_partial(path, collector_path, mac, ip, tcp,
                      now, runner, error, interface="eth0"):
    """Preserve TCP evidence after UDP failure, if identity is still valid."""
    from target_guard import post_scan_identity_verified

    if (
        not isinstance(tcp, dict)
        or not isinstance(tcp.get("os_matches"), list)
        or not isinstance(tcp.get("ports"), list)
    ):
        raise ValueError("Invalid TCP scan evidence")

    if not isinstance(error, str) or not error.strip():
        raise ValueError("A partial scan requires a failure reason")

    state = load_state(path)
    record = state["profiles"].get(mac)

    if (
        not isinstance(record, dict)
        or record.get("status") != "reserved"
        or record.get("target_ip") != ip
    ):
        raise ValueError("No matching scan reservation")

    if not post_scan_identity_verified(
        collector_path, mac, ip, runner, interface
    ):
        raise RuntimeError("Device identity changed after scanning")

    record.update({
        "status": "partial",
        "profiled_ip": ip,
        "profiled_at": now,
        "profile": {"tcp": tcp, "udp": None},
        "last_error": error[:500],
    })
    save_state(path, state)
