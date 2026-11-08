#!/usr/bin/env python3
"""Router-local DHCP rollback worker. NOT installed or scheduled by this file.

Intended for invocation by an independently armed systemd recovery unit.
Requires deployment-specific full-file SHA-256 values.
"""
import argparse
import fcntl
import os
import subprocess
import tempfile
from pathlib import Path

from router_dhcp_infinite_recovery import recovery_decision

ACTIVE = Path("/etc/dnsmasq.d/router.conf")
BACKUP = Path(
    "/var/backups/homelab-router/dhcp-infinite/router.conf.original"
)

ORIGINAL_SHA = (
    "341d0c4271500127654c94b0bb4e21950f1929dce229bc7b9943bcd500042730"
)
CANDIDATE_SHA = (
    "152e161010d5492173a39bd01140e359471f6a61a06886d079f5e0dfde6e2160"
)


def require_secure_file(path, expected_mode):
    if path.is_symlink():
        raise RuntimeError("Symlink refused")
    info = path.stat()
    if not path.is_file() or info.st_uid != 0 or info.st_gid != 0:
        raise RuntimeError("Unexpected file ownership or type")
    if info.st_mode & 0o777 != expected_mode:
        raise RuntimeError("Unexpected file permissions")


LOCK = Path("/run/homelab-dhcp-infinite/recovery.lock")


def restore():
    if os.geteuid() != 0:
        raise PermissionError("Root required")

    with LOCK.open("a+b") as lock:
        try:
            fcntl.flock(
                lock.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )
        except BlockingIOError:
            raise RuntimeError("DHCP recovery lock busy") from None

        return restore_unlocked()


def restore_unlocked():
    if os.geteuid() != 0:
        raise PermissionError("Root required")

    require_secure_file(ACTIVE, 0o600)
    require_secure_file(BACKUP, 0o600)

    original = BACKUP.read_bytes()
    active = ACTIVE.read_bytes()

    decision = recovery_decision(
        active, original, ORIGINAL_SHA, CANDIDATE_SHA
    )

    if decision == "ALREADY_ORIGINAL":
        # The configuration may already have been restored by another
        # recovery path while dnsmasq remains stopped.
        subprocess.run(
            ["/usr/sbin/dnsmasq", "--test"],
            check=True,
        )

        state = subprocess.run(
            ["/usr/bin/systemctl", "is-active", "--quiet", "dnsmasq"],
            check=False,
        )

        if state.returncode != 0:
            subprocess.run(
                ["/usr/bin/systemctl", "restart", "dnsmasq"],
                check=True,
            )
            subprocess.run(
                ["/usr/bin/systemctl", "is-active", "--quiet", "dnsmasq"],
                check=True,
            )
            return "ORIGINAL_SERVICE_RECOVERED"

        return "ALREADY_ORIGINAL"

    if decision != "RESTORE_APPROVED":
        raise RuntimeError(decision)

    # Stage a protected temporary file in the destination filesystem.
    fd, staged = tempfile.mkstemp(
        prefix=".router-dhcp-rollback-", dir=ACTIVE.parent
    )
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(original)
            handle.flush()
            os.fsync(handle.fileno())

        # Refuse if the active configuration changed during staging.
        from router_dhcp_infinite_recovery import sha256
        if sha256(ACTIVE.read_bytes()) != CANDIDATE_SHA:
            raise RuntimeError("Active configuration changed; refuse rollback")

        os.replace(staged, ACTIVE)
        dirfd = os.open(ACTIVE.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)

    finally:
        if os.path.exists(staged):
            os.unlink(staged)

    # Fail visibly if restored syntax is invalid.
    subprocess.run(["/usr/sbin/dnsmasq", "--test"], check=True)
    subprocess.run(
        ["/usr/bin/systemctl", "restart", "dnsmasq"],
        check=True
    )
    subprocess.run(
        ["/usr/bin/systemctl", "is-active", "--quiet", "dnsmasq"],
        check=True
    )
    return "RESTORED_AND_RESTARTED"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-approved-rollback",
        action="store_true",
        help="Execute the explicitly configured production rollback",
    )
    args = parser.parse_args()

    if not args.execute_approved_rollback:
        parser.error("Rollback is disabled without explicit execution flag")

    print(restore())
