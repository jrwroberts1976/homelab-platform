#!/usr/bin/env python3
"""Offline tests of DHCP rollback worker. No service operations."""
import sys
import fcntl
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "scripts")
)

import router_dhcp_infinite_rollback_worker as worker
from router_dhcp_infinite_recovery import (
    ORIGINAL_RANGE,
    INFINITE_RANGE,
    sha256,
)


class RollbackWorkerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

        directory = Path(self.tempdir.name)
        self.active = directory / "router.conf"
        self.backup = directory / "router.conf.original"

        self.original = (ORIGINAL_RANGE + "\n").encode()
        self.candidate = (INFINITE_RANGE + "\n").encode()

        self.active.write_bytes(self.candidate)
        self.backup.write_bytes(self.original)

        patches = [
            patch.object(worker, "ACTIVE", self.active),
            patch.object(worker, "LOCK", directory / "dhcp.lock"),
            patch.object(worker, "BACKUP", self.backup),
            patch.object(worker, "ORIGINAL_SHA", sha256(self.original)),
            patch.object(worker, "CANDIDATE_SHA", sha256(self.candidate)),
            patch.object(worker.os, "geteuid", return_value=0),
            patch.object(worker, "require_secure_file"),
            patch.object(worker.subprocess, "run"),
        ]

        for item in patches:
            item.start()
            self.addCleanup(item.stop)

    def test_recovery_refuses_busy_lock(self):
        # Hold the lock independently while recovery attempts to start.
        with worker.LOCK.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            with self.assertRaisesRegex(
                RuntimeError, "DHCP recovery lock busy"
            ):
                worker.restore()

        self.assertEqual(self.active.read_bytes(), self.candidate)
        worker.subprocess.run.assert_not_called()

    def test_restores_approved_candidate(self):
        result = worker.restore()
        self.assertEqual(result, "RESTORED_AND_RESTARTED")
        self.assertEqual(self.active.read_bytes(), self.original)
        self.assertEqual(self.backup.read_bytes(), self.original)
        self.assertEqual(worker.subprocess.run.call_count, 3)

    def test_refuses_unknown_configuration(self):
        unexpected = b"unexpected configuration\n"
        self.active.write_bytes(unexpected)

        with self.assertRaisesRegex(
            RuntimeError, "REFUSE_UNKNOWN_CONFIGURATION"
        ):
            worker.restore()

        self.assertEqual(self.active.read_bytes(), unexpected)
        worker.subprocess.run.assert_not_called()

    def test_refuses_corrupted_backup(self):
        self.backup.write_bytes(b"corrupt backup\n")

        with self.assertRaisesRegex(
            RuntimeError, "REFUSE_BACKUP_MISMATCH"
        ):
            worker.restore()

        self.assertEqual(self.active.read_bytes(), self.candidate)
        worker.subprocess.run.assert_not_called()

    def test_already_original(self):
        self.active.write_bytes(self.original)

        # Simulate an already-running dnsmasq service.
        worker.subprocess.run.return_value.returncode = 0

        self.assertEqual(worker.restore(), "ALREADY_ORIGINAL")
        self.assertEqual(worker.subprocess.run.call_count, 2)

    def test_already_original_recovers_stopped_service(self):
        self.active.write_bytes(self.original)
        worker.subprocess.run.return_value.returncode = 1

        self.assertEqual(
            worker.restore(),
            "ORIGINAL_SERVICE_RECOVERED",
        )
        self.assertEqual(worker.subprocess.run.call_count, 4)


if __name__ == "__main__":
    unittest.main()
