"""Offline SMTP delivery tests."""
import smtplib
import sys
import unittest
from pathlib import Path
from email.message import EmailMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "files"))
from notification_delivery import send_device_notification


class FakeSMTP:
    refused = {}

    def __init__(self, host, port, timeout):
        assert (host, port, timeout) == ("mail-relay-01", 25, 15)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def send_message(self, message):
        assert message["To"] == "jrwroberts1976@gmail.com"
        return self.refused


class NotificationDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.message = EmailMessage()
        self.message["From"] = "device-alert@jameshouse"
        self.message["To"] = "jrwroberts1976@gmail.com"
        self.message["Subject"] = "New device"
        self.message.set_content("Test notification")

    def test_relay_accepts_email(self):
        FakeSMTP.refused = {}
        self.assertTrue(send_device_notification(
            self.message, smtp_factory=FakeSMTP
        ))

    def test_rejected_recipient_raises(self):
        FakeSMTP.refused = {
            "jrwroberts1976@gmail.com": (550, "Rejected")
        }
        with self.assertRaises(smtplib.SMTPRecipientsRefused):
            send_device_notification(
                self.message, smtp_factory=FakeSMTP
            )

    def test_connection_failure_propagates(self):
        def offline_relay(*args, **kwargs):
            raise ConnectionRefusedError("Relay unavailable")

        with self.assertRaises(ConnectionRefusedError):
            send_device_notification(
                self.message, smtp_factory=offline_relay
            )


class NotificationWorkflowTests(unittest.TestCase):
    """Test persistent delivery without contacting the real relay."""

    def setUp(self):
        import json
        from tempfile import TemporaryDirectory
        from worker_state import save_state

        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.collector = root / "devices.json"
        self.profiles = root / "profiles.json"
        self.lock = root / "worker.lock"
        self.mac = "aa:bb:cc:dd:ee:02"

        self.device = {
            "status": "pending",
            "last_ip": "192.168.2.20",
            "hostname": "NEW-LAPTOP",
            "discovered_at": 100,
        }
        self.collector.write_text(json.dumps({
            "schema_version": 1,
            "devices": {self.mac: self.device},
        }))
        save_state(self.profiles, {
            "schema_version": 1,
            "profiles": {self.mac: {
                "status": "complete",
                "profiled_ip": "192.168.2.20",
                "profile": {
                    "tcp": {"os_matches": [], "ports": []},
                    "udp": {"os_matches": [], "ports": []},
                },
            }},
        })

    def deliver(self, factory=FakeSMTP):
        from notification_delivery import deliver_next_notification
        return deliver_next_notification(
            self.collector, self.profiles, self.lock,
            "device-alert@jameshouse",
            "jrwroberts1976@gmail.com",
            smtp_factory=factory, now=1000,
        )

    def test_successful_delivery_only_once(self):
        from worker_state import load_state
        FakeSMTP.refused = {}

        self.assertEqual(
            self.deliver()["notification"], "sent"
        )
        self.assertIsNone(self.deliver())

        notice = load_state(
            self.profiles
        )["profiles"][self.mac]["notification"]
        self.assertEqual(notice["state"], "sent")
        self.assertEqual(notice["attempts"], 1)

    def test_uncertain_delivery_does_not_resend(self):
        from worker_state import load_state

        def disconnected(*args, **kwargs):
            raise ConnectionResetError("SMTP connection lost")

        self.assertEqual(
            self.deliver(disconnected)["notification"], "uncertain"
        )
        self.assertIsNone(self.deliver())

        notice = load_state(
            self.profiles
        )["profiles"][self.mac]["notification"]
        self.assertEqual(notice["state"], "uncertain")

    def test_baselined_device_never_emailed(self):
        import json
        self.device["status"] = "baseline"
        self.collector.write_text(json.dumps({
            "schema_version": 1,
            "devices": {self.mac: self.device},
        }))

        def forbidden(*args, **kwargs):
            raise AssertionError("Baseline device triggered SMTP")

        self.assertIsNone(self.deliver(forbidden))
