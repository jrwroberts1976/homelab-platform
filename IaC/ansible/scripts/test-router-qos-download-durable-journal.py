#!/usr/bin/env python3
"""Offline tempfile-only durable journal tests."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

path = Path(__file__).with_name("router-qos-download-durable-journal.py")
spec = importlib.util.spec_from_file_location("qos_durable_journal", path)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

A = {"generation": "A", "ifindex": 5}
B = {"generation": "B", "ifindex": 7}

class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.journal = mod.Journal(self.tmp.name)

    def test_new_directory_is_clean(self):
        self.assertEqual(self.journal.read()["phase"], "clean")
        self.assertIsNone(self.journal.read()["owned"])

    def test_begin_persists_pending_across_instances(self):
        self.journal.begin(None, A)
        reopened = mod.Journal(self.tmp.name)
        self.assertEqual(reopened.read()["phase"], "pending")
        self.assertEqual(reopened.read()["target"], A)

    def test_pending_refuses_reconnect_and_duplicate(self):
        self.journal.begin(None, A)
        for target in (A, B):
            with self.assertRaises(mod.JournalError): self.journal.begin(None, target)

    def test_completion_requires_external_verification(self):
        self.journal.begin(None, A)
        with self.assertRaises(mod.JournalError): self.journal.finish(A)
        self.assertEqual(self.journal.read()["phase"], "pending")
        self.journal.finish(A, externally_verified=True)
        self.assertEqual(self.journal.read()["owned"], A)

    def test_stale_owner_refused(self):
        self.journal.begin(None, A)
        self.journal.finish(A, externally_verified=True)
        with self.assertRaises(mod.JournalError): self.journal.begin(None, B)
        self.journal.begin(A, None)
        self.journal.finish(None, externally_verified=True)
        self.journal.begin(None, B)
        self.assertEqual(self.journal.read()["target"], B)

    def test_recovery_refuses_without_verification(self):
        self.journal.begin(None, A)
        with self.assertRaises(mod.JournalError): self.journal.recover_clean()
        self.assertEqual(self.journal.read()["phase"], "pending")
        self.journal.recover_clean(externally_verified=True)
        self.assertEqual(self.journal.read()["phase"], "clean")

    def test_invalid_and_corrupt_state_fail_closed(self):
        self.journal.path.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(mod.JournalError): self.journal.read()

    def test_symlink_state_refused(self):
        target = Path(self.tmp.name) / "elsewhere"
        target.write_text("don't touch", encoding="utf-8")
        self.journal.path.symlink_to(target)
        with self.assertRaises(mod.JournalError): self.journal.write(
            {"version": 1, "phase": "clean", "owned": None, "target": None})
        self.assertEqual(target.read_text(encoding="utf-8"), "don't touch")

    def test_invalid_sessions_refused(self):
        for invalid in ({"generation": "A", "ifindex": True},
                        {"generation": "", "ifindex": 5},
                        {"generation": "A", "ifindex": -1}):
            with self.assertRaises(mod.JournalError): self.journal.begin(None, invalid)

if __name__ == "__main__":
    unittest.main(verbosity=2)
