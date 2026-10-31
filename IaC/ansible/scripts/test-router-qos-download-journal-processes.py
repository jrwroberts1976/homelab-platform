#!/usr/bin/env python3
"""Offline multi-process journal tests. No signals, tc, ip, systemd or host state."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SOURCE = Path(__file__).with_name("router-qos-download-durable-journal.py")
spec = importlib.util.spec_from_file_location("durable_qos_journal_process", SOURCE)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
A = {"generation": "A", "ifindex": 5}
B = {"generation": "B", "ifindex": 7}

class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.journal = m.Journal(self.temp.name)

    def child(self, code):
        return subprocess.run(
            [sys.executable, "-B", "-c", code, str(SOURCE), self.temp.name],
            capture_output=True, text=True, timeout=8, check=True)

    def test_clean_process_exit_keeps_pending_intent(self):
        self.child("""
import importlib.util,sys
s=importlib.util.spec_from_file_location('journal_child',sys.argv[1])
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.Journal(sys.argv[2]).begin(None, {'generation':'A','ifindex':5})
""")
        reopened = m.Journal(self.temp.name)
        self.assertEqual(reopened.read()["phase"], "pending")
        self.assertEqual(reopened.read()["target"], A)
        with self.assertRaises(m.JournalError):
            reopened.begin(None, B)
        with self.assertRaises(m.JournalError):
            reopened.recover_clean()
        reopened.recover_clean(externally_verified=True)
        self.assertEqual(reopened.read()["phase"], "clean")
        reopened.begin(None, B)
        self.assertEqual(reopened.read()["target"], B)

    def test_lock_serializes_two_processes(self):
        # Child announces only after it holds the exact journal flock.
        code = """
import importlib.util,sys,time
s=importlib.util.spec_from_file_location('journal_lock_child',sys.argv[1])
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
with m.Journal(sys.argv[2]).locked():
    print('LOCK_HELD',flush=True)
    time.sleep(0.7)
"""
        proc = subprocess.Popen(
            [sys.executable, "-B", "-c", code, str(SOURCE), self.temp.name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(proc.stdout.readline().strip(), "LOCK_HELD")
            start = time.monotonic()
            self.journal.begin(None, A)
            elapsed = time.monotonic() - start
            self.assertGreaterEqual(elapsed, 0.35)
            self.assertEqual(proc.wait(timeout=5), 0)
            self.assertEqual(self.journal.read()["target"], A)
        finally:
            if proc.poll() is None:
                # Do not send signals; let a bounded child finish naturally.
                proc.wait(timeout=5)
            proc.stdout.close()
            proc.stderr.close()

    def test_completed_session_reopened_refuses_stale_owner(self):
        self.journal.begin(None, A)
        self.journal.finish(A, externally_verified=True)
        reopened = m.Journal(self.temp.name)
        with self.assertRaises(m.JournalError):
            reopened.begin(None, B)
        reopened.begin(A, None)
        self.assertEqual(reopened.read()["phase"], "pending")

if __name__ == "__main__":
    unittest.main(verbosity=2)
