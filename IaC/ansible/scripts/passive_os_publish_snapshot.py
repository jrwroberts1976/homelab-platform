#!/usr/bin/env python3
"""Publish only sanitised pending OS evidence into a dedicated read-only SSH file.

Run manually as root after the transport account is created. No EVE reading,
checkpoint advancement, acknowledgement, daemon, timer or router network changes.
The pending spool remains private (0700); SSH can read only the snapshot.
"""
import argparse
import fcntl
import os
import pwd
import stat
import tempfile
from pathlib import Path

from passive_os_ssh_export import export_batch

PENDING = Path("/var/lib/homelab-passive-os/pending.json")
OUT_DIR = Path("/var/lib/homelab-passive-os-outbound")
OUT_FILE = OUT_DIR / "batch.json"
TRANSFER_USER = "homelab-os-transfer"


def publish(pending=PENDING, directory=OUT_DIR, user=TRANSFER_USER):
    """Atomic bounded snapshot; caller must be root. Return its byte count."""
    if os.geteuid() != 0:
        raise PermissionError("Root required to publish private pending evidence")
    identity = pwd.getpwnam(user)
    if directory.is_symlink():
        raise ValueError("Symlinked outbound directory refused")
    if not directory.exists():
        directory.mkdir(mode=0o750)
    directory_info = directory.stat()
    if not stat.S_ISDIR(directory_info.st_mode) or directory_info.st_uid != 0:
        raise ValueError("Outbound directory must be root-owned")
    if stat.S_IMODE(directory_info.st_mode) != 0o750:
        raise ValueError("Outbound directory must be mode 0750")
    if directory_info.st_gid != identity.pw_gid:
        raise ValueError("Outbound directory group must be transfer account group")
    target = directory / "batch.json"
    if target.is_symlink():
        raise ValueError("Outbound symlink refused")
    if target.exists() and (
        not target.is_file() or target.stat().st_uid != 0
    ):
        raise ValueError("Untrusted existing outbound target")
    # The existing exporter strictly projects fields; it cannot export
    # checkpoints, user agent strings, domains or raw EVE events.
    payload = export_batch(pending, "get-batch")
    fd, temporary = tempfile.mkstemp(prefix=".batch-", dir=directory)
    try:
        os.fchmod(fd, 0o640)
        os.fchown(fd, 0, identity.pw_gid)
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        parent = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return len(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", required=True,
                        help="Publish one already-prepared pending batch")
    args = parser.parse_args()
    if args.publish:
        print("SANITISED_SNAPSHOT_BYTES=" + str(publish()))


if __name__ == "__main__":
    main()
