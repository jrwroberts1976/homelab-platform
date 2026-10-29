"""Offline tests for the Nmap worker's final target check."""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from target_guard import target_is_current

MAC = "aa:bb:cc:dd:ee:02"
IP = "192.168.2.20"


class TargetGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "devices.json"
        self.device = {
            "status": "pending",
            "last_ip": IP,
            "last_inventory_seen": 995,
        }
        self.save()

    def save(self):
        self.path.write_text(json.dumps({
            "schema_version": 1,
            "devices": {MAC: self.device},
        }))

    def check(self, ip=IP):
        return target_is_current(self.path, MAC, ip, now=1000)

    def test_valid_target(self):
        self.assertTrue(self.check())

    def test_changed_ip(self):
        self.device["last_ip"] = "192.168.2.21"
        self.save()
        self.assertFalse(self.check())

    def test_stale_device(self):
        self.device["last_inventory_seen"] = 500
        self.save()
        self.assertFalse(self.check())

    def test_baseline_not_scanned(self):
        self.device["status"] = "baseline"
        self.save()
        self.assertFalse(self.check())

    def test_missing_state(self):
        self.path.unlink()
        self.assertFalse(self.check())

    def test_corrupt_state(self):
        self.path.write_text("{invalid")
        self.assertFalse(self.check())


if __name__ == "__main__":
    unittest.main()


class PostScanTests(TargetGuardTests):
    def test_long_scan_with_correct_identity(self):
        from types import SimpleNamespace
        from target_guard import post_scan_identity_verified

        xml = (
            '<nmaprun><host><status state="up"/>'
            f'<address addr="{IP}" addrtype="ipv4"/>'
            f'<address addr="{MAC}" addrtype="mac"/>'
            '</host><runstats><finished exit="success"/>'
            '</runstats></nmaprun>'
        )
        fake = lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=xml
        )

        self.assertTrue(
            post_scan_identity_verified(self.path, MAC, IP, fake)
        )

        self.assertFalse(
            post_scan_identity_verified(
                self.path, "aa:bb:cc:dd:ee:ff", IP, fake
            )
        )

        self.device["last_ip"] = "192.168.2.21"
        self.save()
        self.assertFalse(
            post_scan_identity_verified(self.path, MAC, IP, fake)
        )
