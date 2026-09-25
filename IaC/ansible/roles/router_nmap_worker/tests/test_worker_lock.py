"""Offline tests for exclusive Nmap worker locking."""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from worker_lock import WorkerBusy, exclusive_worker_lock


class WorkerLockTests(unittest.TestCase):
    def test_second_worker_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.lock"
            with exclusive_worker_lock(path):
                with self.assertRaises(WorkerBusy):
                    with exclusive_worker_lock(path):
                        pass

    def test_lock_released_after_error(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.lock"
            with self.assertRaises(RuntimeError):
                with exclusive_worker_lock(path):
                    raise RuntimeError("Simulated worker failure")
            with exclusive_worker_lock(path):
                pass

    def test_private_permissions(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "worker.lock"
            with exclusive_worker_lock(path):
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
