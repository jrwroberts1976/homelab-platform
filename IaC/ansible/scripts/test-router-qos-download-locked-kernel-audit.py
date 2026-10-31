#!/usr/bin/env python3
"""Offline locked-collection tests: temporary journal, injected observations."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

p = Path(__file__).with_name("router-qos-download-locked-kernel-audit.py")
s = importlib.util.spec_from_file_location("qos_locked_audit_test", p)
m = importlib.util.module_from_spec(s)
sys.modules[s.name] = m
s.loader.exec_module(m)
A = {"generation": "A", "ifindex": 5}

def clean():
    return {"status": "OBSERVED_NOT_AUTHORIZED", "namespace_inode": 42,
            "recorded_inode": 42, "host_inode": 1, "observations": {
                "source": {"rc": 0, "stdout": "qd31 up", "stderr": ""},
                "ifb": {"rc": 1, "stdout": "", "stderr": 'Device "qi31" does not exist.'},
                "filter": {"rc": 0, "stdout": "", "stderr": ""},
                "qdisc": {"rc": 0, "stdout": "qdisc noqueue", "stderr": ""}}}

class LockAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.j = m.journal.Journal(self.tmp.name)
        self.j.begin(None, A)

    def audit(self, collect=clean, clock=None, **kwargs):
        ticks = iter((100, 200))
        args = {"collect": collect, "clock": clock or (lambda: next(ticks))}
        args.update(kwargs)
        return m.audit(self.tmp.name, None, A, "A", **args)

    def test_clean_is_not_authorized(self):
        r = self.audit()
        self.assertEqual(r["status"], "OBSERVED_UNDER_JOURNAL_LOCK_NOT_AUTHORIZED")
        self.assertFalse(r["journal_recovery_authorized"])
        self.assertEqual(self.j.read()["phase"], "pending")

    def test_missing_namespace_refused(self):
        self.assertEqual(self.audit(collect=lambda: {"status": "INCONCLUSIVE_NAMESPACE_OR_OWNER_ABSENT"})["status"], "REFUSE_UNVERIFIED")

    def test_dirty_filter_refused(self):
        def dirty():
            data = clean()
            data["observations"]["filter"]["stdout"] = "pref 49131"
            return data
        self.assertEqual(self.audit(collect=dirty)["status"], "REFUSE_UNVERIFIED")

    def test_slow_inspection_refused(self):
        self.assertEqual(self.audit(clock=iter((100, 2_000_000_101)).__next__)["status"], "REFUSE_UNVERIFIED")

    def test_generation_mismatch_refused_without_collection(self):
        calls = []
        result = m.audit(self.tmp.name, None, A, "B", collect=lambda: calls.append(True))
        self.assertEqual(result["status"], "REFUSE_UNVERIFIED")
        self.assertEqual(calls, [])

    def test_completed_intent_refuses_collection(self):
        self.j.finish(A, externally_verified=True)
        calls = []
        result = self.audit(collect=lambda: calls.append(True))
        self.assertEqual(result["status"], "REFUSE_UNVERIFIED")
        self.assertFalse(calls)

    def test_collection_exception_refused_and_lock_released(self):
        def fails():
            raise RuntimeError("unavailable")
        self.assertEqual(self.audit(collect=fails)["status"], "REFUSE_UNVERIFIED")
        with self.j.locked():
            self.assertEqual(self.j.read()["phase"], "pending")

if __name__ == "__main__":
    unittest.main(verbosity=2)
