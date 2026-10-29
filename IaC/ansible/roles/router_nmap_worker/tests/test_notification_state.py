"""Offline regression tests for one-time device notifications."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from notification_state import claim_first_notification, finish_notification
from worker_state import load_state, save_state

MAC = "aa:bb:cc:dd:ee:02"


class NotificationStateTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.collector = root / "devices.json"
        self.profiles = root / "profiles.json"
        self.device = {"status": "pending", "last_ip": "192.168.2.20"}
        self.record = {"status": "complete"}
        self.save()

    def save(self):
        self.collector.write_text(json.dumps({
            "schema_version": 1, "devices": {MAC: self.device}
        }))
        save_state(self.profiles, {
            "schema_version": 1, "profiles": {MAC: self.record}
        })

    def claim(self):
        return claim_first_notification(
            self.collector, self.profiles, MAC, 1000
        )

    def test_successful_email_is_sent_only_once(self):
        self.assertTrue(self.claim())
        self.assertFalse(self.claim())
        finish_notification(self.profiles, MAC, 1001, accepted=True)
        self.assertFalse(self.claim())
        notice = load_state(self.profiles)["profiles"][MAC]["notification"]
        self.assertEqual(notice["state"], "sent")
        self.assertEqual(notice["attempts"], 1)

    def test_baselined_device_never_notified(self):
        self.device["status"] = "baseline"
        self.save()
        self.assertFalse(self.claim())

    def test_uncertain_delivery_prevents_duplicates(self):
        self.assertTrue(self.claim())
        finish_notification(
            self.profiles, MAC, 1001, accepted=False,
            error="SMTP connection dropped"
        )
        self.assertFalse(self.claim())
        notice = load_state(self.profiles)["profiles"][MAC]["notification"]
        self.assertEqual(notice["state"], "uncertain")

    def test_unfinished_scan_not_notified(self):
        self.record["status"] = "reserved"
        self.save()
        self.assertFalse(self.claim())
