#!/usr/bin/env python3
"""Offline atomic owner-record tests; no router or network access."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).parent))
from router_qos_download_owner_record import write_new, load

RECORD = {
    "boot_id": "11111111-2222-3333-4444-555555555555",
    "ifb_name": "ifbqosdl0",
    "ifb_ifindex": 17,
    "token": "0123456789abcdef0123456789abcdef",
}

class RecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "owner.json"

    def test_atomic_create_and_read(self):
        write_new(self.path, RECORD)
        self.assertEqual(load(self.path), RECORD)

    def test_private_mode(self):
        write_new(self.path, RECORD)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_no_overwrite(self):
        write_new(self.path, RECORD)
        with self.assertRaises(FileExistsError):
            write_new(self.path, dict(RECORD, ifb_ifindex=18))
        self.assertEqual(load(self.path), RECORD)

    def test_reject_symlink_destination(self):
        target = Path(self.tmp.name) / "foreign"
        target.write_text("do not touch")
        self.path.symlink_to(target)
        with self.assertRaises(FileExistsError):
            write_new(self.path, RECORD)
        self.assertEqual(target.read_text(), "do not touch")

    def test_reject_malformed_record(self):
        with self.assertRaises(ValueError):
            write_new(self.path, dict(RECORD, ifb_ifindex=True))
        self.assertFalse(self.path.exists())

    def test_reject_extra_fields(self):
        with self.assertRaises(ValueError):
            write_new(self.path, dict(RECORD, caller_verified=True))
        self.assertFalse(self.path.exists())

    def test_reject_stale_file_contents(self):
        self.path.write_text('{"boot_id":"unexpected"}')
        with self.assertRaises(ValueError):
            load(self.path)

    def test_reject_symlink_read(self):
        target = Path(self.tmp.name) / "record"
        target.write_text(json.dumps(RECORD))
        self.path.symlink_to(target)
        with self.assertRaises(ValueError):
            load(self.path)

    def test_no_leftover_temp(self):
        write_new(self.path, RECORD)
        self.assertEqual([p.name for p in self.path.parent.iterdir()], ["owner.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
