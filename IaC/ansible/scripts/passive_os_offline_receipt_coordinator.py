#!/usr/bin/env python3
"""Stage 5.7F: offline-only locked local receipt-and-signature prototype.

No SSH/network, no durable signer key storage, no source acknowledgment,
and no automatic checkpoint advancement. The caller supplies disposable
test-only keys and a synthetic canonical wire batch. Not deployable.
"""
import fcntl
import os
import stat
from pathlib import Path

from passive_os_wire_receiver import receive_wire, validate_wire
from passive_os_signed_receipt import attest_locally, verify_signed_receipt


def receive_and_attest_local(wire, destination, challenge, signer, *,
                             synthetic_test_only=False):
    """Under one local advisory lock, store/verify wire, receipt, then sign.

    Locking only coordinates callers that use this same lock. It does not
    establish cross-host identity, crash consistency or signer trust.
    """
    if synthetic_test_only is not True:
        raise PermissionError("No production receipt coordinator enabled")
    if not isinstance(destination, Path) or not destination.is_dir():
        raise ValueError("Existing private receiver directory required")
    if destination.is_symlink() or any(p.is_symlink() for p in destination.parents):
        raise ValueError("Symlinked destination path refused")
    mode = destination.stat().st_mode
    if not stat.S_ISDIR(mode) or mode & 0o077:
        raise ValueError("Unsafe receiver directory")
    batch, canonical = validate_wire(wire)
    lock_path = destination / ".lock"
    if lock_path.is_symlink():
        raise ValueError("Symlinked lock refused")
    # File descriptor opened without following a symlink, without truncation.
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        meta = os.fstat(fd)
        if not stat.S_ISREG(meta.st_mode) or meta.st_mode & 0o077:
            raise ValueError("Unsafe lock file")
        with os.fdopen(fd, "rb+", closefd=False) as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            stored = receive_wire(canonical, destination)
            batch_id = batch["batch_id"]
            saved_path = destination / (batch_id + ".json")
            receipt_path = destination / (batch_id + ".receipt.json")
            # Refuse replacing known paths with symlinks before reading.
            if saved_path.is_symlink() or receipt_path.is_symlink():
                raise ValueError("Symlinked receipt record")
            saved = saved_path.read_bytes()
            receipt = receipt_path.read_bytes()
            envelope = attest_locally(canonical, saved, receipt, challenge, signer)
            verified = verify_signed_receipt(
                envelope, canonical, challenge, signer.public_key())
            return {"store_status": stored["status"],
                    "verification_status": verified["status"],
                    "batch_id": batch_id, "envelope": envelope}
    finally:
        os.close(fd)
