#!/usr/bin/env python3
"""Offline-testable, atomic ownership record persistence.

Only writes a record supplied by an authorised caller. It does not grant
authority to delete a kernel object; recovery still needs independent
kernel-side identity evidence and a verified PPP session transition.
"""
import json
import os
from pathlib import Path
import tempfile

from router_qos_download_ownership import BOOT_RE, TOKEN_RE


def validate_record(record):
    if not isinstance(record, dict) or set(record) != {"boot_id", "ifb_name", "ifb_ifindex", "token"}:
        raise ValueError("invalid ownership schema")
    if not isinstance(record["boot_id"], str) or not BOOT_RE.fullmatch(record["boot_id"]):
        raise ValueError("invalid boot id")
    if record["ifb_name"] != "ifbqosdl0":
        raise ValueError("unexpected interface")
    if type(record["ifb_ifindex"]) is not int or record["ifb_ifindex"] <= 0:
        raise ValueError("invalid ifindex")
    if not isinstance(record["token"], str) or not TOKEN_RE.fullmatch(record["token"]):
        raise ValueError("invalid token")


def write_new(path, record):
    """Create a new record; never overwrite ambiguous existing state.

    Use a temporary file in the same directory, fsync, link without overwrite,
    then fsync the directory. Caller must hold the shared controller lock.
    """
    validate_record(record)
    path = Path(path)
    if path.is_symlink() or path.exists():
        raise FileExistsError("ownership record already exists")
    directory = path.parent
    fd, tmp = tempfile.mkstemp(prefix=".router-qos-owner-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            os.fchmod(f.fileno(), 0o600)
            json.dump(record, f, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.link(tmp, path, follow_symlinks=False)
        dfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        os.unlink(tmp)


def load(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("symlink ownership record")
    record = json.loads(path.read_text(encoding="utf-8"))
    validate_record(record)
    return record


if __name__ == "__main__":
    raise SystemExit("Library only: no unauthorised CLI write entrypoint")
