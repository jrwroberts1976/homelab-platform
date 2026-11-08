#!/usr/bin/env python3
"""OFFLINE-ONLY candidate fixed-command exporter for sanitised OS evidence.

No SSH, key provisioning, routing changes, router log access, timer or Nmap.
NOT deployable as-is: the forced-command target is not installed. The future
consumer must validate transport authentication and durable delivery separately.
"""
import ipaddress
import os
import re
import stat
import sys
from pathlib import Path

from passive_os_batch_spool import canonical, validated_pending, MAX_PENDING_BYTES

# These are fixed policy values, NOT configurable by remote arguments.
PENDING = Path("/var/lib/homelab-passive-os/pending.json")
REQUEST = "get-batch"
FAMILIES = frozenset({"ChromeOS", "Android", "iOS/iPadOS", "Windows", "macOS", "Linux"})
KINDS = frozenset({"dns", "http", "tls", "quic"})
BATCH_ID = re.compile(r"^[0-9a-f]{64}$")
MAX_WIRE_BYTES = 2 * 1024 * 1024 + 8192
LAN = ipaddress.ip_network("192.168.2.0/24")


def validate_request(original_command):
    """Exactly one read-only verb; never interpolate remote command into shell."""
    if original_command != REQUEST:
        raise PermissionError("Unsupported export request")


def export_batch(pending_path, original_command):
    """Export only a bounded, explicitly allowlisted wire-format projection.

    This method is testable with local synthetic files. No access to the EVE
    log, checkpoint mutation, acknowledgement or downstream processing.
    """
    validate_request(original_command)
    if pending_path.is_symlink():
        raise ValueError("Symlinked pending batch refused")
    info = pending_path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077:
        raise ValueError("Pending batch must be a private regular file")
    if info.st_size > MAX_PENDING_BYTES:
        raise ValueError("Pending batch exceeds size limit")
    batch = validated_pending(pending_path)
    if batch is None:
        raise ValueError("No pending batch")
    if not BATCH_ID.fullmatch(batch["batch_id"]):
        raise ValueError("Malformed batch ID")
    observations = batch["observations"]
    if len(observations) > 2000:
        raise ValueError("Excessive observation count")
    clean = []
    for e in observations:
        if not isinstance(e, dict) or set(e) - {
            "src_ip", "timestamp", "event_type", "os_family_hint"
        }:
            raise ValueError("Unexpected event fields")
        if not isinstance(e.get("timestamp"), int) or not (
            1577836800 <= e["timestamp"] <= 4102444800
        ):
            raise ValueError("Invalid event timestamp")
        if e.get("event_type") not in KINDS:
            raise ValueError("Invalid event kind")
        if "os_family_hint" in e and (
            e["event_type"] != "http" or e["os_family_hint"] not in FAMILIES
        ):
            raise ValueError("Invalid family hint")
        if not isinstance(e.get("src_ip"), str) or len(e["src_ip"]) > 45:
            raise ValueError("Invalid client address")
        try:
            addr = ipaddress.ip_address(e["src_ip"])
        except ValueError:
            raise ValueError("Invalid client address") from None
        if (addr not in LAN or addr in
                (LAN.network_address, LAN.broadcast_address, LAN.network_address + 1)):
            raise ValueError("Client outside approved LAN")
        # Normalise nothing; wire evidence must match the locally stored batch.
        clean.append(e)
    wire = {
        "protocol": 1,
        "batch_id": batch["batch_id"],
        "digest": batch["digest"],
        "observations": clean,
    }
    encoded = canonical(wire) + b"\n"
    if len(encoded) > MAX_WIRE_BYTES:
        raise ValueError("Wire batch exceeds size cap")
    return encoded


def main():
    # A future SSH forced-command entry would execute without any arguments.
    # This script intentionally has no '--pending' or '--command' override.
    if len(sys.argv) != 1:
        raise PermissionError("No command-line arguments allowed")
    data = export_batch(PENDING, os.environ.get("SSH_ORIGINAL_COMMAND", ""))
    sys.stdout.buffer.write(data)


if __name__ == "__main__":
    main()
