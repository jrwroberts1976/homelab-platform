#!/usr/bin/env python3
"""Offline wire receiver safety tests; no SSH/network and no remote ack."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(ROOT))
from passive_os_batch_spool import canonical, digest, prepare
from passive_os_ssh_export import export_batch
from passive_os_wire_receiver import receive_wire, validate_wire


class WireReceiverTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.eve = self.root / "eve.json"
        self.spool = self.root / "spool"
        self.dest = self.root / "wire-received"
        self.eve.write_text(json.dumps({
            "timestamp": "2026-11-06T12:00:00Z", "src_ip": "192.168.2.113",
            "event_type": "http",
            "http": {"http_user_agent": "Mozilla/5.0 (X11; CrOS x86_64 1)"},
            "http_url": "/sensitive-path",
        }) + "\n")
        prepare(self.eve, self.spool)
        self.wire = export_batch(self.spool / "pending.json", "get-batch")

    def modified(self, change, refresh_digest=True):
        batch = json.loads(self.wire)
        change(batch)
        if refresh_digest:
            batch["digest"] = digest(canonical(batch["observations"]))
        return canonical(batch) + b"\n"

    def test_roundtrip_export_to_wire_receiver(self):
        result = receive_wire(self.wire, self.dest)
        self.assertEqual(result["status"], "stored")
        batch = self.dest / (result["batch_id"] + ".json")
        receipt = self.dest / (result["batch_id"] + ".receipt.json")
        self.assertEqual(batch.stat().st_mode & 0o777, 0o600)
        self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
        self.assertEqual(batch.read_bytes(), self.wire)
        self.assertNotIn(b"next_state", batch.read_bytes())
        self.assertNotIn(b"sensitive-path", batch.read_bytes())
        self.assertFalse((self.spool / "checkpoint.json").exists())

    def test_retry_is_idempotent(self):
        first = receive_wire(self.wire, self.dest)
        files = {p.name: p.read_bytes() for p in self.dest.iterdir()}
        second = receive_wire(self.wire, self.dest)
        self.assertEqual(second["status"], "duplicate")
        self.assertEqual(first["batch_id"], second["batch_id"])
        self.assertEqual(files, {p.name: p.read_bytes() for p in self.dest.iterdir()})

    def test_digest_mismatch_fails(self):
        bad = self.modified(lambda b: b["observations"][0].update(
            {"os_family_hint": "Android"}), refresh_digest=False)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            receive_wire(bad, self.dest)
        self.assertFalse(self.dest.exists())

    def test_extra_raw_browsing_data_refused(self):
        bad = self.modified(lambda b: b["observations"][0].update(
            {"http_url": "/private"}))
        with self.assertRaisesRegex(ValueError, "Unexpected event fields"):
            receive_wire(bad, self.dest)

    def test_checkpoint_data_refused(self):
        bad = self.modified(lambda b: b.update({"next_state": {"offset": 123}}))
        with self.assertRaisesRegex(ValueError, "Unexpected wire fields"):
            receive_wire(bad, self.dest)

    def test_duplicate_json_keys_refused(self):
        bad = self.wire.replace(b'"protocol":1', b'"protocol":1,"protocol":1')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            receive_wire(bad, self.dest)

    def test_invalid_client_ip_refused(self):
        bad = self.modified(lambda b: b["observations"][0].update(
            {"src_ip": "8.8.8.8"}))
        with self.assertRaisesRegex(ValueError, "outside approved LAN"):
            receive_wire(bad, self.dest)

    def test_oversized_payload_refused(self):
        with self.assertRaisesRegex(ValueError, "wire byte length"):
            receive_wire(b"x" * (2 * 1024 * 1024 + 8193), self.dest)

    def test_batch_id_collision_does_not_overwrite(self):
        receive_wire(self.wire, self.dest)
        changed = self.modified(lambda b: b["observations"][0].update(
            {"os_family_hint": "Android"}))
        with self.assertRaisesRegex(ValueError, "Existing wire batch differs"):
            receive_wire(changed, self.dest)

    def test_world_readable_destination_refused(self):
        self.dest.mkdir(mode=0o755)
        with self.assertRaisesRegex(ValueError, "Unsafe receipt directory"):
            receive_wire(self.wire, self.dest)

    def test_symlinked_destination_refused(self):
        self.dest.symlink_to(self.spool, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Unsafe destination symlink"):
            receive_wire(self.wire, self.dest)

    def test_byte_quota_refuses_new_batch(self):
        with patch("passive_os_batch_receiver.MAX_RETAINED_BYTES", 8):
            with self.assertRaisesRegex(ValueError, "byte quota"):
                receive_wire(self.wire, self.dest)
        self.assertEqual(list(self.dest.glob("*.json")), [])

    def test_batch_quota_refuses_new_batch(self):
        with patch("passive_os_batch_receiver.MAX_RETAINED_BATCHES", 0):
            with self.assertRaisesRegex(ValueError, "batch quota"):
                receive_wire(self.wire, self.dest)
        self.assertEqual(list(self.dest.glob("*.json")), [])

    def test_wrong_schema_and_boolean_timestamp_refused(self):
        bad = self.modified(lambda b: b["observations"][0].update(
            {"timestamp": True}))
        with self.assertRaisesRegex(ValueError, "Invalid event time"):
            receive_wire(bad, self.dest)
        bad = self.modified(lambda b: b.update({"protocol": True}))
        with self.assertRaisesRegex(ValueError, "Invalid wire protocol"):
            receive_wire(bad, self.dest)

    def test_local_receipt_never_acks_router(self):
        receive_wire(self.wire, self.dest)
        self.assertTrue((self.spool / "pending.json").exists())
        self.assertFalse((self.spool / "checkpoint.json").exists())


if __name__ == "__main__":
    unittest.main()
