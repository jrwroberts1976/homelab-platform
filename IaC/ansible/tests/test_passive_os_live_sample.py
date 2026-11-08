#!/usr/bin/env python3
"""Small offline tests for the one-shot bounded EVE tail pilot."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from passive_os_live_sample import make_wire, sample_tail, READ_BYTES


class LiveTailSampleTests(unittest.TestCase):
    def event(self, timestamp, src="192.168.2.113"):
        return {
            "timestamp": timestamp,
            "src_ip": src,
            "event_type": "http",
            "http": {"http_user_agent": "Mozilla/5.0 (X11; CrOS x86_64 1)"},
            "http_url": "/private-url",
            "dns": {"rrname": "private.example"},
        }

    def test_sanitises_user_agent_and_url(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "eve.json"
            path.write_text(json.dumps(self.event("2026-11-07T05:00:00Z")) + "\n")
            wire = json.loads(make_wire(sample_tail(path)))
            self.assertEqual(wire["observations"][0]["os_family_hint"], "ChromeOS")
            self.assertNotIn("CrOS x86", json.dumps(wire))
            self.assertNotIn("private-url", json.dumps(wire))
            self.assertNotIn("private.example", json.dumps(wire))
            self.assertNotIn("next_state", wire)

    def test_tail_skips_partial_first_record(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "eve.json"
            a = self.event("2026-11-07T05:00:00Z")
            b = self.event("2026-11-07T05:01:00Z")
            path.write_text(json.dumps(a) + "\n" + json.dumps(b) + "\n")
            records = sample_tail(path, read_bytes=len(json.dumps(b)) + 25)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["timestamp"], 1794027660)

    def test_invalid_ceiling_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "eve.json"
            path.write_text("{}\n")
            with self.assertRaises(ValueError):
                sample_tail(path, read_bytes=READ_BYTES + 1)

    def test_no_checkpoint_or_network(self):
        script = (Path(__file__).resolve().parents[1] / "scripts" /
                  "passive_os_live_sample.py").read_text()
        self.assertNotIn("checkpoint.json", script)
        self.assertNotIn("subprocess", script)
        self.assertNotIn("socket.", script)
        self.assertNotIn("ack(", script)


if __name__ == "__main__":
    unittest.main()
