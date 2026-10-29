"""Offline tests for worker identity verification."""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from worker import find_verified_target

MAC = "aa:bb:cc:dd:ee:02"
IP = "192.168.2.20"


def discovery_xml(mac=MAC):
    return (
        '<nmaprun><host><status state="up"/>'
        f'<address addr="{IP}" addrtype="ipv4"/>'
        f'<address addr="{mac}" addrtype="mac"/>'
        '</host><runstats><finished exit="success"/>'
        '</runstats></nmaprun>'
    )


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "devices.json"
        self.device = {
            "status": "pending",
            "last_ip": IP,
            "last_inventory_seen": 995,
            "discovered_at": 900,
        }
        self.save()

    def save(self):
        self.path.write_text(json.dumps({
            "schema_version": 1,
            "devices": {MAC: self.device},
        }))

    def test_valid_device(self):
        def fake_nmap(*args, **kwargs):
            return SimpleNamespace(
                returncode=0, stdout=discovery_xml()
            )

        self.assertEqual(
            find_verified_target(self.path, {}, fake_nmap, now=1000),
            {"mac": MAC, "ip": IP},
        )

    def test_wrong_mac_blocks_scanning(self):
        def fake_nmap(*args, **kwargs):
            return SimpleNamespace(
                returncode=0,
                stdout=discovery_xml("aa:bb:cc:dd:ee:ff"),
            )

        self.assertIsNone(
            find_verified_target(self.path, {}, fake_nmap, now=1000)
        )

    def test_ip_changes_during_discovery(self):
        def fake_nmap(*args, **kwargs):
            self.device["last_ip"] = "192.168.2.21"
            self.save()
            return SimpleNamespace(
                returncode=0, stdout=discovery_xml()
            )

        self.assertIsNone(
            find_verified_target(self.path, {}, fake_nmap, now=1000)
        )


if __name__ == "__main__":
    unittest.main()


class ScanLockIntegrationTests(WorkerTests):
    def test_lock_held_until_profiling_finishes(self):
        from worker import prepare_verified_scan
        from worker_lock import WorkerBusy, exclusive_worker_lock

        lock = Path(self.temp.name) / "worker.lock"
        state = Path(self.temp.name) / "worker.json"
        fake = lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=discovery_xml()
        )

        with prepare_verified_scan(
            self.path, state, lock, fake, now=1000
        ) as target:
            self.assertEqual(target, {"mac": MAC, "ip": IP})
            with self.assertRaises(WorkerBusy):
                with exclusive_worker_lock(lock):
                    pass

        with exclusive_worker_lock(lock):
            pass

    def test_lock_released_after_scan_failure(self):
        from worker import prepare_verified_scan
        from worker_lock import exclusive_worker_lock

        lock = Path(self.temp.name) / "worker.lock"
        state = Path(self.temp.name) / "worker.json"
        fake = lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=discovery_xml()
        )

        with self.assertRaises(RuntimeError):
            with prepare_verified_scan(
                self.path, state, lock, fake, now=1000
            ) as target:
                self.assertIsNotNone(target)
                raise RuntimeError("Simulated scan failure")

        with exclusive_worker_lock(lock):
            pass
