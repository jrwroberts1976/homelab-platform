#!/usr/bin/env python3
"""Stage 5.7E synthetic local integration. Never contacts router or sensor."""
import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from passive_os_batch_spool import prepare
from passive_os_ssh_export import export_batch
from passive_os_offline_pipeline import receive_local_fixture


class OfflinePipelineTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        eve = self.root / "eve.json"
        self.spool = self.root / "spool"
        self.dest = self.root / "receiver"
        self.dest.mkdir(mode=0o700)
        eve.write_text(json.dumps({
            "timestamp": "2026-11-06T12:00:00Z",
            "src_ip": "192.168.2.113", "event_type": "http",
            "http": {"http_user_agent": "CrOS 123"},
        }) + "\n")
        prepare(eve, self.spool)
        self.wire = export_batch(self.spool / "pending.json", "get-batch")

    def fixture(self, raw=None, exit_code=0, delay=0):
        if raw is None:
            raw = self.wire
        encoded = base64.b64encode(raw).decode("ascii")
        code = ("import base64,sys,time;"
                "time.sleep(" + str(delay) + ");"
                "sys.stdout.buffer.write(base64.b64decode('" + encoded + "'));"
                "sys.exit(" + str(exit_code) + ")")
        return [sys.executable, "-c", code]

    def invoke(self, argv=None, destination=None, **kw):
        return receive_local_fixture(
            argv or self.fixture(), destination or self.dest,
            synthetic_test_only=True, **kw)

    def test_successful_synthetic_delivery(self):
        result = self.invoke()
        self.assertEqual(result["status"], "stored")
        self.assertEqual(set(p.suffix for p in self.dest.iterdir()), {".json"})
        self.assertEqual(len(list(self.dest.glob("*.json"))), 2)

    def test_duplicate_delivery_is_idempotent(self):
        first = self.invoke()
        second = self.invoke()
        self.assertEqual(second["status"], "duplicate")
        self.assertEqual(first["batch_id"], second["batch_id"])
        self.assertEqual(len(list(self.dest.glob("*.json"))), 2)

    def test_corrupt_wire_writes_nothing(self):
        with self.assertRaises(ValueError):
            self.invoke(self.fixture(self.wire[:25]))
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_failed_fixture_even_with_valid_output_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonzero"):
            self.invoke(self.fixture(exit_code=12))
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_stalled_fixture_does_not_store(self):
        with self.assertRaises(TimeoutError):
            self.invoke(self.fixture(delay=2), timeout_seconds=0.15)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_oversized_output_rejected_before_store(self):
        cmd = [sys.executable, "-c", "import sys;sys.stdout.buffer.write(b'x'*3000000)"]
        with self.assertRaisesRegex(ValueError, "output limit"):
            self.invoke(cmd)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_missing_explicit_synthetic_gate_rejected(self):
        with self.assertRaises(PermissionError):
            receive_local_fixture(self.fixture(), self.dest)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_ssh_execution_is_refused(self):
        with self.assertRaises(PermissionError):
            self.invoke(["ssh", "homelab-os-transfer@192.168.2.1", "get-batch"])
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_world_accessible_destination_refused(self):
        self.dest.chmod(0o755)
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_destination_symlink_refused(self):
        link = self.root / "receiver-link"
        link.symlink_to(self.dest, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.invoke(destination=link)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_failed_second_delivery_preserves_first_receipt(self):
        first = self.invoke()
        existing = {p.name: p.read_bytes() for p in self.dest.iterdir()}
        with self.assertRaises(ValueError):
            self.invoke(self.fixture(self.wire[:-1] + b"X"))
        self.assertEqual({p.name: p.read_bytes() for p in self.dest.iterdir()}, existing)
        self.assertEqual(first["status"], "stored")

    def test_no_checkpoint_advance(self):
        self.invoke()
        self.assertTrue((self.spool / "pending.json").exists())
        self.assertFalse((self.spool / "checkpoint.json").exists())


if __name__ == "__main__":
    unittest.main()
