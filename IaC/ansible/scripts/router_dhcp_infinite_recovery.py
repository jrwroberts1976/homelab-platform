#!/usr/bin/env python3
"""DHCP infinite lease recovery decision engine.

Offline development only. No service control or file writes.
"""

import hashlib
from pathlib import Path

ORIGINAL_RANGE = (
    "dhcp-range=192.168.2.100,192.168.2.199,"
    "255.255.255.0,24h"
)

INFINITE_RANGE = (
    "dhcp-range=192.168.2.100,192.168.2.199,"
    "255.255.255.0,infinite"
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def recovery_decision(
    active_bytes,
    backup_bytes,
    expected_original_sha,
    expected_candidate_sha,
):
    """Decide whether rollback is permitted. Never write anything."""

    if sha256(backup_bytes) != expected_original_sha:
        return "REFUSE_BACKUP_MISMATCH"

    if backup_bytes.count(ORIGINAL_RANGE.encode()) != 1:
        return "REFUSE_INVALID_BACKUP"

    active_sha = sha256(active_bytes)

    if active_sha == expected_original_sha:
        return "ALREADY_ORIGINAL"

    if active_sha == expected_candidate_sha:
        return "RESTORE_APPROVED"

    return "REFUSE_UNKNOWN_CONFIGURATION"
