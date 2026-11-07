#!/usr/bin/env python3
"""Offline tests for the guarded DHCP installer."""
import fcntl
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "scripts")
)

import router_dhcp_infinite_install as installer

from router_dhcp_infinite_recovery import (
    ORIGINAL_RANGE,
    INFINITE_RANGE,
    sha256,
)


class InstallTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        directory = Path(self.tmp.name)

        self.active = directory / "router.conf"
        self.backup = directory / "router.conf.original"
        self.lock = directory / "recovery.lock"

        self.original = (ORIGINAL_RANGE + "\n").encode()
        self.candidate = (INFINITE_RANGE + "\n").encode()

        self.active.write_bytes(self.original)
        self.backup.write_bytes(self.original)

        self.root_patch = patch.object(
            installer.os, "geteuid", return_value=0
        )
        self.secure_patch = patch.object(
            installer, "secure_file"
        )

        self.root_patch.start()
        self.secure_patch.start()

        self.addCleanup(self.root_patch.stop)
        self.addCleanup(self.secure_patch.stop)

    def install(self):
        return installer.install(
            active=self.active,
            backup=self.backup,
            lock=self.lock,
            original_sha=sha256(self.original),
            candidate_sha=sha256(self.candidate),
        )

    def test_successful_installation(self):
        self.assertEqual(
            self.install(),
            "CANDIDATE_INSTALLED",
        )
        self.assertEqual(
            self.active.read_bytes(),
            self.candidate,
        )
        self.assertEqual(
            self.backup.read_bytes(),
            self.original,
        )

    def test_stale_backup_refused(self):
        self.backup.write_bytes(b"stale backup\n")

        with self.assertRaisesRegex(
            RuntimeError, "Protected backup mismatch"
        ):
            self.install()

        self.assertEqual(self.active.read_bytes(), self.original)

    def test_unexpected_active_configuration_refused(self):
        self.active.write_bytes(b"unexpected change\n")

        with self.assertRaisesRegex(
            RuntimeError, "Active baseline checksum mismatch"
        ):
            self.install()

        self.assertEqual(
            self.active.read_bytes(),
            b"unexpected change\n",
        )

    def test_busy_lock_refused(self):
        with self.lock.open("a+b") as handle:
            fcntl.flock(
                handle.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )

            with self.assertRaisesRegex(
                RuntimeError, "DHCP deployment lock busy"
            ):
                self.install()

        self.assertEqual(self.active.read_bytes(), self.original)

    def test_wrong_candidate_checksum_refused(self):
        with self.assertRaisesRegex(
            RuntimeError, "Candidate checksum mismatch"
        ):
            installer.install(
                active=self.active,
                backup=self.backup,
                lock=self.lock,
                original_sha=sha256(self.original),
                candidate_sha="0" * 64,
            )

        self.assertEqual(self.active.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
