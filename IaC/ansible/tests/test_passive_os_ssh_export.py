#!/usr/bin/env python3
"""Offline candidate exporter tests. No network, SSH or service actions."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(ROOT))
from passive_os_batch_spool import prepare, canonical, digest
from passive_os_ssh_export import export_batch, validate_request


def example():
    return {
        "timestamp": "2026-11-06T12:00:00Z",
        "src_ip": "192.168.2.113",
        "event_type": "http",
        "http": {"http_user_agent": "Mozilla/5.0 (X11; CrOS x86_64 1)"},
        "http_url": "/secret-url",
        "dns": {"rrname": "example.internal"},
    }


class SSHExportTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        root = Path(t.name)
        self.eve = root / "eve.json"
        self.spool = root / "spool"
        self.eve.write_text(json.dumps(example()) + "\n")
        self.batch = prepare(self.eve, self.spool)
        self.path = self.spool / "pending.json"

    def test_valid_request_only_exposes_allowlisted_fields(self):
        wire = json.loads(export_batch(self.path, "get-batch"))
        self.assertEqual(
            set(wire), {"protocol", "batch_id", "digest", "observations"}
        )
        self.assertEqual(
            set(wire["observations"][0]),
            {"src_ip", "timestamp", "event_type", "os_family_hint"},
        )
        self.assertEqual(wire["observations"][0]["os_family_hint"], "ChromeOS")
        self.assertNotIn("/secret-url", str(wire))
        self.assertNotIn("example.internal", str(wire))
        self.assertNotIn("next_state", str(wire))

    def test_exact_command_only(self):
        self.assertIsNone(validate_request("get-batch"))
        for command in ("", "get-batch ", "get-batch; id", "sh",
                        "cat /etc/shadow", "get-batch\nwhoami",
                        "get-batch --ack", "get-batch /tmp/file"):
            with self.subTest(command=command):
                with self.assertRaises(PermissionError):
                    export_batch(self.path, command)

    def test_does_not_advance_checkpoint_or_acknowledge(self):
        before = self.path.read_bytes()
        export_batch(self.path, "get-batch")
        self.assertEqual(before, self.path.read_bytes())
        self.assertFalse((self.spool / "checkpoint.json").exists())

    def test_missing_batch_rejected(self):
        with self.assertRaises(ValueError):
            export_batch(self.path.with_name("missing.json"), "get-batch")

    def test_symlink_rejected(self):
        link = self.path.with_name("alias.json")
        link.symlink_to(self.path)
        with self.assertRaisesRegex(ValueError, "Symlinked"):
            export_batch(link, "get-batch")

    def test_world_readable_pending_rejected(self):
        self.path.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "private regular"):
            export_batch(self.path, "get-batch")

    def test_extra_event_data_rejected(self):
        data = json.loads(self.path.read_text())
        data["observations"][0]["http_url"] = "/secret"
        data["digest"] = digest(canonical(data["observations"]))
        data["batch_id"] = digest(canonical({
            "next_state": data["next_state"], "digest": data["digest"],
            "previous_offset": data["previous_offset"]
        }))
        self.path.write_bytes(canonical(data) + b"\n")
        with self.assertRaisesRegex(ValueError, "Unexpected event fields"):
            export_batch(self.path, "get-batch")

    def test_outside_lan_rejected(self):
        data = json.loads(self.path.read_text())
        data["observations"][0]["src_ip"] = "8.8.8.8"
        data["digest"] = digest(canonical(data["observations"]))
        data["batch_id"] = digest(canonical({
            "next_state": data["next_state"], "digest": data["digest"],
            "previous_offset": data["previous_offset"]
        }))
        self.path.write_bytes(canonical(data) + b"\n")
        with self.assertRaisesRegex(ValueError, "outside approved LAN"):
            export_batch(self.path, "get-batch")

    def test_mismatched_digest_rejected(self):
        data = json.loads(self.path.read_text())
        data["digest"] = "0" * 64
        self.path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            export_batch(self.path, "get-batch")

    def test_empty_batch_works_without_creating_ack(self):
        invalid = example()
        invalid["src_ip"] = "8.8.8.8"
        self.eve.write_text(json.dumps(invalid) + "\n")
        other = Path(self.spool.parent) / "other"
        prepare(self.eve, other)
        result = json.loads(export_batch(other / "pending.json", "get-batch"))
        self.assertEqual(result["observations"], [])
        self.assertFalse((other / "checkpoint.json").exists())


if __name__ == "__main__":
    unittest.main()
