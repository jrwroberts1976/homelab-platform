"""Offline tests for first-seen device notifications."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from device_mailer import build_device_message

MAC = "aa:bb:cc:dd:ee:02"
RECIPIENT = "jrwroberts1976@gmail.com"


class DeviceMailerTests(unittest.TestCase):
    def setUp(self):
        self.device = {
            "status": "pending",
            "last_ip": "192.168.2.20",
            "hostname": "NEW-LAPTOP",
            "discovered_at": 1000,
        }
        self.record = {
            "status": "complete",
            "profiled_ip": "192.168.2.20",
            "profile": {
                "tcp": {
                    "os_matches": [
                        {"name": "Windows 11", "accuracy": "93"}
                    ],
                    "ports": [{
                        "port": 445, "state": "open",
                        "service": {"name": "microsoft-ds"},
                    }],
                },
                "udp": {
                    "os_matches": [],
                    "ports": [{
                        "port": 137, "state": "open",
                        "service": {"name": "netbios-ns"},
                    }],
                },
            },
        }

    def build(self):
        return build_device_message(
            MAC, self.device, self.record,
            "device-alert@jameshouse", RECIPIENT
        )

    def test_email_contains_scan_results(self):
        message = self.build()
        body = message.get_body(
            preferencelist=("plain",)
        ).get_content()

        self.assertEqual(message["To"], RECIPIENT)
        for expected in (
            MAC, "NEW-LAPTOP", "192.168.2.20",
            "Windows 11", "445/tcp", "137/udp"
        ):
            self.assertIn(expected, body)

        attachment = next(message.iter_attachments())
        evidence = json.loads(
            attachment.get_payload(decode=True)
        )
        self.assertEqual(evidence["mac"], MAC)
        self.assertEqual(evidence["status"], "complete")

    def test_baselined_device_never_notified(self):
        self.device["status"] = "baseline"
        with self.assertRaises(ValueError):
            self.build()

    def test_unfinished_scan_not_notified(self):
        self.record["status"] = "reserved"
        with self.assertRaises(ValueError):
            self.build()
