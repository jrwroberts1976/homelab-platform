#!/usr/bin/env python3
"""Offline-only checks for exact SSH command planning and wire rejection."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(ROOT))

from passive_os_batch_spool import prepare
from passive_os_ssh_export import export_batch
from passive_os_transport_plan import retrieval_argv, validate_retrieved_stdout


class TransportPlanTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        root = Path(t.name)
        eve = root / "eve.json"
        spool = root / "spool"
        eve.write_text(json.dumps({
            "timestamp": "2026-11-06T12:00:00Z",
            "src_ip": "192.168.2.113", "event_type": "http",
            "http": {"http_user_agent": "CrOS 123"},
        }) + "\n")
        prepare(eve, spool)
        self.wire = export_batch(spool / "pending.json", "get-batch")
        self.spool = spool

    def test_request_is_fixed_and_constrained(self):
        args = retrieval_argv()
        self.assertEqual(args[0], "ssh")
        self.assertEqual(args[-2:], ["homelab-os-transfer@192.168.2.1", "get-batch"])
        self.assertIn("StrictHostKeyChecking=yes", args)
        self.assertIn("BatchMode=yes", args)
        self.assertIn("ClearAllForwardings=yes", args)
        self.assertIn("IdentitiesOnly=yes", args)
        self.assertIn("ForwardAgent=no", args)
        self.assertIn("RequestTTY=no", args)
        self.assertIn("-T", args)
        self.assertNotIn("sh", args)
        self.assertNotIn("sudo", args)

    def test_valid_synthetic_output_only(self):
        result = validate_retrieved_stdout(self.wire, 0)
        self.assertEqual(set(result), {"protocol", "batch_id", "digest", "observations"})

    def test_failure_rejects_even_valid_stdout(self):
        with self.assertRaisesRegex(ValueError, "retrieval failed"):
            validate_retrieved_stdout(self.wire, 255)

    def test_noncanonical_response_rejected(self):
        with self.assertRaisesRegex(ValueError, "Noncanonical"):
            validate_retrieved_stdout(self.wire.rstrip(b"\n") + b" ", 0)

    def test_empty_response_rejected(self):
        with self.assertRaisesRegex(ValueError, "response size"):
            validate_retrieved_stdout(b"", 0)

    def test_oversize_response_rejected(self):
        with self.assertRaisesRegex(ValueError, "response size"):
            validate_retrieved_stdout(b"x" * (2 * 1024 * 1024 + 8193), 0)

    def test_truncated_json_rejected(self):
        with self.assertRaises(ValueError):
            validate_retrieved_stdout(self.wire[:20], 0)

    def test_modified_payload_rejected(self):
        changed = self.wire.replace(b"ChromeOS", b"Android")
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_retrieved_stdout(changed, 0)

    def test_stderr_overflow_rejected(self):
        with self.assertRaisesRegex(ValueError, "diagnostic length"):
            validate_retrieved_stdout(self.wire, 0, b"x" * 8193)

    def test_no_source_checkpoint_advance(self):
        validate_retrieved_stdout(self.wire, 0)
        self.assertTrue((self.spool / "pending.json").exists())
        self.assertFalse((self.spool / "checkpoint.json").exists())


if __name__ == "__main__":
    unittest.main()
