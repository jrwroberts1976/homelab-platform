"""Persistent one-time notification tracking, keyed by MAC."""

import json
from pathlib import Path

from worker_state import load_state, save_state

FINISHED = {"complete", "partial", "failed"}


def claim_first_notification(collector_path, profiles_path, mac, now):
    """Reserve one notification for a genuinely new, profiled MAC."""
    collector = json.loads(Path(collector_path).read_text())
    if collector.get("schema_version") != 1:
        raise ValueError("Invalid collector state")

    device = collector.get("devices", {}).get(mac)
    if not isinstance(device, dict) or device.get("status") != "pending":
        return False

    state = load_state(profiles_path)
    record = state["profiles"].get(mac)
    if not isinstance(record, dict) or record.get("status") not in FINISHED:
        return False

    notice = record.get("notification") or {}
    if notice.get("state") in ("sending", "sent", "uncertain"):
        return False

    record["notification"] = {
        "state": "sending",
        "claimed_at": now,
        "attempts": notice.get("attempts", 0) + 1,
    }
    save_state(profiles_path, state)
    return True


def finish_notification(profiles_path, mac, now, accepted,
                        definitely_rejected=False, error=""):
    """Record relay acceptance or preserve an uncertain delivery."""
    state = load_state(profiles_path)
    record = state["profiles"].get(mac)
    if not isinstance(record, dict):
        raise ValueError("Unknown device")

    notice = record.get("notification")
    if not isinstance(notice, dict) or notice.get("state") != "sending":
        raise ValueError("No active notification claim")

    if accepted:
        notice.update({"state": "sent", "sent_at": now})
    elif definitely_rejected:
        notice.update({"state": "retry", "last_error": error[:500]})
    else:
        notice.update({"state": "uncertain", "last_error": error[:500]})

    save_state(profiles_path, state)


def next_unsent_device(collector, state, now, retry_delay=86400):
    """Find the oldest eligible first-seen device awaiting an email."""
    from device_queue import MAC_PATTERN

    if (
        collector.get("schema_version") != 1
        or state.get("schema_version") != 1
        or not isinstance(collector.get("devices"), dict)
        or not isinstance(state.get("profiles"), dict)
    ):
        raise ValueError("Invalid notification inventory")

    candidates = []

    for mac, device in collector["devices"].items():
        if not isinstance(device, dict):
            continue
        if device.get("status") != "pending":
            continue
        if not MAC_PATTERN.fullmatch(mac):
            continue

        record = state["profiles"].get(mac)
        if not isinstance(record, dict):
            continue
        if record.get("status") not in FINISHED:
            continue

        notice = record.get("notification")
        if notice is not None:
            if not isinstance(notice, dict):
                continue
            if notice.get("state") != "retry":
                continue
            claimed = notice.get("claimed_at")
            if type(claimed) not in (int, float):
                continue
            if now - claimed < retry_delay:
                continue

        discovered = device.get("discovered_at")
        if type(discovered) not in (int, float):
            continue

        candidates.append((discovered, mac, device, record))

    if not candidates:
        return None

    _, mac, device, record = min(
        candidates, key=lambda item: (item[0], item[1])
    )
    return {"mac": mac, "device": device, "record": record}
