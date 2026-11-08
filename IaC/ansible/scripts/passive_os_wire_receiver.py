#!/usr/bin/env python3
"""OFFLINE-ONLY receiver of sanitised passive-OS SSH wire batches.

No network calls, SSH authentication, automatic acknowledgment or deployment.
Only the eventual authenticated SSH client may supply bytes. A local receipt is
NOT proof of the remote sender's identity or that an upstream ack is safe.
"""
import argparse
import fcntl
import ipaddress
import json
import os
import re
import stat
import sys
from pathlib import Path

from passive_os_batch_spool import canonical, digest
from passive_os_batch_receiver import capacity_check
from passive_os_ssh_export import MAX_WIRE_BYTES, FAMILIES, KINDS, LAN
from router_eve_minimizer import safe_write

BATCH_ID = re.compile(r"^[0-9a-f]{64}$")
EVENT_FIELDS = frozenset({"src_ip", "timestamp", "event_type", "os_family_hint"})
WIRE_FIELDS = frozenset({"protocol", "batch_id", "digest", "observations"})
MAX_EVENTS = 2000


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def validate_wire(raw):
    """Return canonical, strictly minimal batch bytes after validation.

    The batch id is checked for *syntax*, not derivable from the wire format:
    the source's next_state is deliberately omitted. Only a future mutually
    authenticated transfer and trusted upstream coordinator can bind it.
    """
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_WIRE_BYTES:
        raise ValueError("Invalid wire byte length")
    try:
        batch = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid wire JSON") from exc
    if not isinstance(batch, dict) or set(batch) != WIRE_FIELDS:
        raise ValueError("Unexpected wire fields")
    if type(batch["protocol"]) is not int or batch["protocol"] != 1:
        raise ValueError("Invalid wire protocol")
    if not isinstance(batch["batch_id"], str) or not BATCH_ID.fullmatch(batch["batch_id"]):
        raise ValueError("Invalid wire batch ID")
    if not isinstance(batch["digest"], str) or not BATCH_ID.fullmatch(batch["digest"]):
        raise ValueError("Invalid wire digest")
    observations = batch["observations"]
    if not isinstance(observations, list) or len(observations) > MAX_EVENTS:
        raise ValueError("Invalid observation count")
    for event in observations:
        if not isinstance(event, dict) or not (
            {"src_ip", "timestamp", "event_type"} <= set(event) <= EVENT_FIELDS
        ):
            raise ValueError("Unexpected event fields")
        if type(event["timestamp"]) is not int or not (
            1577836800 <= event["timestamp"] <= 4102444800
        ):
            raise ValueError("Invalid event time")
        if event["event_type"] not in KINDS:
            raise ValueError("Invalid event kind")
        if "os_family_hint" in event and (
            event["event_type"] != "http" or
            not isinstance(event["os_family_hint"], str) or
            event["os_family_hint"] not in FAMILIES
        ):
            raise ValueError("Invalid OS family hint")
        if not isinstance(event["src_ip"], str) or len(event["src_ip"]) > 45:
            raise ValueError("Invalid client address")
        try:
            addr = ipaddress.ip_address(event["src_ip"])
        except ValueError:
            raise ValueError("Invalid client address") from None
        if addr not in LAN or addr in (
            LAN.network_address, LAN.broadcast_address, LAN.network_address + 1
        ) or event["src_ip"] != str(addr):
            raise ValueError("Client outside approved LAN")
    if batch["digest"] != digest(canonical(observations)):
        raise ValueError("Wire observation digest mismatch")
    result = canonical(batch) + b"\n"
    if len(result) > MAX_WIRE_BYTES:
        raise ValueError("Canonical batch exceeds cap")
    return batch, result


def _durable_write(path, payload):
    """Atomic file replace plus parent directory fsync.

    Production still needs filesystem-specific power-cut validation and a
    reviewed receipt+checkpoint two-phase protocol.
    """
    safe_write(path, payload)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def receive_wire(raw, destination):
    """Testable offline single-writer operation. CLI holds exclusive lock."""
    batch, payload = validate_wire(raw)
    if destination.is_symlink():
        raise ValueError("Unsafe destination symlink")
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not destination.is_dir() or destination.stat().st_mode & 0o077:
        raise ValueError("Unsafe receipt directory")
    batch_id = batch["batch_id"]
    saved = destination / (batch_id + ".json")
    receipt = destination / (batch_id + ".receipt.json")
    record = {
        "protocol": 1, "batch_id": batch_id, "digest": batch["digest"],
        "stored_bytes": len(payload),
    }
    receipt_data = canonical(record) + b"\n"
    # Check all entries, symlinks, quota and name rules before writing either.
    fresh = not saved.exists()
    additional = (len(payload) if fresh else 0) + (
        len(receipt_data) if not receipt.exists() else 0
    )
    capacity_check(destination, additional_bytes=additional, new_batch=fresh)

    if saved.exists():
        if saved.is_symlink() or not stat.S_ISREG(saved.stat().st_mode) or (
            saved.read_bytes() != payload
        ):
            raise ValueError("Existing wire batch differs; no overwrite")
    else:
        _durable_write(saved, payload)
    if receipt.exists():
        if receipt.is_symlink() or not stat.S_ISREG(receipt.stat().st_mode) or (
            receipt.read_bytes() != receipt_data
        ):
            raise ValueError("Existing wire receipt differs; no overwrite")
        status = "duplicate"
    else:
        _durable_write(receipt, receipt_data)
        status = "stored"
    return {"status": status, **record}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.input.is_symlink() or not args.input.is_file():
        raise ValueError("Wire source must be a regular local file")
    if args.input.stat().st_size > MAX_WIRE_BYTES:
        raise ValueError("Wire source exceeds cap")
    raw = args.input.read_bytes()
    args.destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    if args.destination.is_symlink() or args.destination.stat().st_mode & 0o077:
        raise ValueError("Unsafe receipt directory")
    lock_path = args.destination / ".lock"
    if lock_path.is_symlink():
        raise ValueError("Unsafe receiver lock")
    with lock_path.open("a+b") as lock:
        os.fchmod(lock.fileno(), 0o600)
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        result = receive_wire(raw, args.destination)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
