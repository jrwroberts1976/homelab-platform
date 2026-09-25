"""Offline tests for first-seen email queue selection."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from notification_state import next_unsent_device

MAC1 = "aa:bb:cc:dd:ee:01"
MAC2 = "aa:bb:cc:dd:ee:02"


class NotificationQueueTests(unittest.TestCase):
    def setUp(self):
        self.collector = {
            "schema_version": 1,
            "devices": {
                MAC1: {"status": "pending", "discovered_at": 100},
                MAC2: {"status": "pending", "discovered_at": 200},
            },
        }
        self.state = {
            "schema_version": 1,
            "profiles": {
                MAC1: {"status": "complete"},
                MAC2: {"status": "complete"},
            },
        }

    def select(self, now=1000):
        return next_unsent_device(
            self.collector, self.state, now
        )

    def test_oldest_unnotified_device_first(self):
        self.assertEqual(self.select()["mac"], MAC1)

    def test_baselined_devices_excluded(self):
        self.collector["devices"][MAC1]["status"] = "baseline"
        self.assertEqual(self.select()["mac"], MAC2)

    def test_claimed_or_sent_devices_excluded(self):
        for status in ("sending", "sent", "uncertain"):
            with self.subTest(status=status):
                self.state["profiles"][MAC1]["notification"] = {
                    "state": status
                }
                self.assertEqual(self.select()["mac"], MAC2)

    def test_rejected_email_observes_retry_delay(self):
        self.state["profiles"][MAC1]["notification"] = {
            "state": "retry", "claimed_at": 1000
        }
        self.assertEqual(self.select(now=1001)["mac"], MAC2)
        self.assertEqual(self.select(now=87400)["mac"], MAC1)

    def test_partial_and_failed_scans_eligible(self):
        for status in ("partial", "failed"):
            with self.subTest(status=status):
                self.state["profiles"][MAC1]["status"] = status
                self.assertEqual(self.select()["mac"], MAC1)
