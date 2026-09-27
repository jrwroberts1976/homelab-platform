#!/usr/bin/env python3
"""Fail-closed, read-only protection for the migrated collector post-hook.

Never let an empty/missing registry seed all existing devices as new
baseline. Pin every historical source MAC to its frozen copy even after
new alerts are delivered. Do not print MACs or the SMTP recipient.
"""
import json
import os
import stat
from pathlib import Path

STATE = Path("/var/lib/homelab-network-hosts")
CONFIG = Path("/etc/homelab-network-hosts")
SYNC = STATE / "network-discovery-final-sync.json"
APPROVAL = CONFIG / "network-discovery-cutover-approved"
REGISTRY = STATE / "alerted-macs.json"
ALERT_ENV = CONFIG / "alerts.env"
BACKUP_ROOT = Path("/var/backups/homelab-network-migration")


def protected(path):
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_nlink != 1):
        raise ValueError("A protected first-seen file is unsafe")
    return path.read_bytes()


def main():
    if os.geteuid() != 0:
        raise ValueError("First-seen protection must run as root")
    sync = json.loads(protected(SYNC))
    approval = json.loads(protected(APPROVAL))
    if (sync.get("schema_version") != 1
            or sync.get("event") != "network_discovery_final_sync_complete"
            or sync.get("target_host") != "monitor-01"
            or approval.get("event") != "network_discovery_cutover_approved"
            or approval.get("run_id") != sync.get("run_id")):
        raise ValueError("Missing matching final-sync and approval records")
    hashes = sync.get("sha256")
    if not isinstance(hashes, list) or len(hashes) != 5:
        raise ValueError("Missing verified final-source file hashes")
    expected = int(sync["historical_registry_count"])
    if expected < 1:
        raise ValueError("Missing historical first-seen count")

    backup_dir = Path(sync["target_backup_dir"])
    if backup_dir.parent != BACKUP_ROOT or (
            backup_dir.name != "gate3-target-" + sync["run_id"]):
        raise ValueError("Unrecognised final-sync registry backup path")
    backup = backup_dir / "final-alerted-macs.json"
    import hashlib
    original_bytes = protected(backup)
    if hashlib.sha256(original_bytes).hexdigest() != hashes[3]:
        raise ValueError("Frozen historical registry backup does not match source")
    original = json.loads(original_bytes)
    current = json.loads(protected(REGISTRY))
    if original.get("version") != 1 or current.get("version") != 1:
        raise ValueError("Unknown first-seen schema")
    source_macs = original.get("devices")
    known = current.get("devices")
    if (not isinstance(source_macs, dict) or not isinstance(known, dict)
            or len(source_macs) != expected
            or len(known) < expected
            or not source_macs.keys() <= known.keys()):
        raise ValueError("A historical first-seen entry is missing")

    for mac, original_entry in source_macs.items():
        current_entry = known[mac]
        if not isinstance(original_entry, dict) or not isinstance(current_entry, dict):
            raise ValueError("Malformed historical alert record")
        if original_entry.get("status") == "alerted" and (
                current_entry.get("status") != "alerted"):
            raise ValueError("Previously alerted MAC lost its delivery state")
    if any(not isinstance(entry, dict) or entry.get("status") not in
           ("baseline", "alerted") for entry in known.values()):
        raise ValueError("Invalid first-seen delivery state")

    environment = protected(ALERT_ENV).decode("utf-8")
    recipients = [
        line.split("=", 1)[1].strip().strip("'\"")
        for line in environment.splitlines()
        if line.strip().startswith("NETWORK_DEVICE_ALERT_TO=")
    ]
    if len(recipients) != 1 or not recipients[0]:
        raise ValueError("Protected first-seen recipient is unavailable")
    print(json.dumps({
        "event": "network_firstseen_guard_ready",
        "historical_entries": expected,
        "current_known_entries": len(known),
        "recipient_configured": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
