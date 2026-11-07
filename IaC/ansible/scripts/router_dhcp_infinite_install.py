#!/usr/bin/env python3
"""Guarded DHCP configuration installer. Not installed or invoked by Ansible yet."""
import fcntl
import os
import stat
import tempfile
from pathlib import Path

from router_dhcp_infinite_recovery import (
    ORIGINAL_RANGE, INFINITE_RANGE, sha256,
)

ACTIVE = Path("/etc/dnsmasq.d/router.conf")
BACKUP = Path("/var/backups/homelab-router/dhcp-infinite/router.conf.original")
LOCK = Path("/run/homelab-dhcp-infinite/recovery.lock")

ORIGINAL_SHA = "341d0c4271500127654c94b0bb4e21950f1929dce229bc7b9943bcd500042730"
CANDIDATE_SHA = "152e161010d5492173a39bd01140e359471f6a61a06886d079f5e0dfde6e2160"


def secure_file(path):
    if path.is_symlink():
        raise RuntimeError("Symlink refused")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise RuntimeError("Regular file required")
    if (info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)) != (0, 0, 0o600):
        raise RuntimeError("Unexpected configuration ownership or mode")


def install(active=ACTIVE, backup=BACKUP, lock=LOCK,
            original_sha=ORIGINAL_SHA, candidate_sha=CANDIDATE_SHA):
    if os.geteuid() != 0:
        raise PermissionError("Root required")

    with lock.open("a+b") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("DHCP deployment lock busy") from None

        secure_file(active)
        secure_file(backup)

        original = active.read_bytes()
        saved = backup.read_bytes()

        if sha256(original) != original_sha:
            raise RuntimeError("Active baseline checksum mismatch")
        if sha256(saved) != original_sha or saved != original:
            raise RuntimeError("Protected backup mismatch")

        old = ORIGINAL_RANGE.encode()
        new = INFINITE_RANGE.encode()

        if original.count(old) != 1 or new in original:
            raise RuntimeError("Unexpected DHCP range")

        candidate = original.replace(old, new)

        if sha256(candidate) != candidate_sha:
            raise RuntimeError("Candidate checksum mismatch")

        fd, staged = tempfile.mkstemp(
            prefix=".dhcp-infinite-", dir=active.parent
        )
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb") as output:
                output.write(candidate)
                output.flush()
                os.fsync(output.fileno())

            # Detect changes before the atomic replacement.
            secure_file(active)
            if sha256(active.read_bytes()) != original_sha:
                raise RuntimeError("Active configuration changed during staging")

            os.replace(staged, active)

            directory_fd = os.open(
                active.parent, os.O_RDONLY | os.O_DIRECTORY
            )
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(staged):
                os.unlink(staged)

        if sha256(active.read_bytes()) != candidate_sha:
            raise RuntimeError("Installed checksum mismatch")

        return "CANDIDATE_INSTALLED"


if __name__ == "__main__":
    print(install())
