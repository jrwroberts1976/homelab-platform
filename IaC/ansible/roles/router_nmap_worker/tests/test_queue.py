"""Offline regression tests for the Nmap worker queue."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from device_queue import select_new_device


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.devices = {
            "aa:bb:cc:dd:ee:01": {
                "status": "baseline",
                "last_ip": "192.168.2.10",
                "discovered_at": 10,
            },
            "aa:bb:cc:dd:ee:02": {
                "status": "pending",
                "last_ip": "192.168.2.20",
                "discovered_at": 20,
            },
            "aa:bb:cc:dd:ee:03": {
                "status": "pending",
                "last_ip": "192.168.2.30",
                "discovered_at": 30,
            },
        }
        self.collector = {"schema_version": 1, "devices": self.devices}

    def test_oldest_new_device_first(self):
        self.assertEqual(
            select_new_device(self.collector, {}),
            {"mac": "aa:bb:cc:dd:ee:02", "ip": "192.168.2.20"},
        )

    def test_previously_profiled_device_excluded(self):
        profiles = {"aa:bb:cc:dd:ee:02": {"status": "complete"}}
        self.assertEqual(
            select_new_device(self.collector, profiles)["mac"],
            "aa:bb:cc:dd:ee:03",
        )

    def test_no_duplicate_work(self):
        profiles = {mac: {} for mac in self.devices}
        self.assertIsNone(select_new_device(self.collector, profiles))

    def test_reject_address_outside_lan(self):
        self.devices["aa:bb:cc:dd:ee:02"]["last_ip"] = "10.0.0.20"
        with self.assertRaises(ValueError):
            select_new_device(self.collector, {})


if __name__ == "__main__":
    unittest.main()


from device_queue import select_next_device


class RetryQueueTests(unittest.TestCase):
    def setUp(self):
        self.devices = {
            "aa:bb:cc:dd:ee:02": {
                "status": "pending",
                "last_ip": "192.168.2.20",
                "discovered_at": 20,
            },
            "aa:bb:cc:dd:ee:03": {
                "status": "pending",
                "last_ip": "192.168.2.30",
                "discovered_at": 30,
            },
        }
        self.collector = {
            "schema_version": 1,
            "devices": self.devices,
        }
        self.profiles = {
            "aa:bb:cc:dd:ee:02": {
                "status": "reserved",
                "last_attempt": 1000,
            }
        }

    def test_new_device_before_retry(self):
        result = select_next_device(
            self.collector, self.profiles, now=90000
        )
        self.assertEqual(result["mac"], "aa:bb:cc:dd:ee:03")

    def test_retry_after_cooldown(self):
        self.profiles["aa:bb:cc:dd:ee:03"] = {
            "status": "complete"
        }
        result = select_next_device(
            self.collector, self.profiles, now=90000
        )
        self.assertEqual(result["mac"], "aa:bb:cc:dd:ee:02")

    def test_retry_blocked_during_cooldown(self):
        self.profiles["aa:bb:cc:dd:ee:03"] = {
            "status": "complete"
        }
        self.assertIsNone(
            select_next_device(
                self.collector, self.profiles, now=2000
            )
        )

    def test_retry_outside_lan_rejected(self):
        self.profiles["aa:bb:cc:dd:ee:03"] = {
            "status": "complete"
        }
        self.devices["aa:bb:cc:dd:ee:02"]["last_ip"] = "10.0.0.20"
        with self.assertRaises(ValueError):
            select_next_device(
                self.collector, self.profiles, now=90000
            )
