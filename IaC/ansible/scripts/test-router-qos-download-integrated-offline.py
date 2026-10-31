#!/usr/bin/env python3
"""One offline install/teardown/failure suite; zero host network mutations."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

p = Path(__file__).with_name("router-qos-download-integrated-offline.py")
spec = importlib.util.spec_from_file_location("qos_end_to_end", p)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
A = {"generation": "test-A", "ifindex": 11}

class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.commands = []
        self.actual = None
        self.fail_at = 0
        self.watchdog_ok = True

        def runner(command):
            self.commands.append(command)
            if self.fail_at and len(self.commands) == self.fail_at:
                return False
            # Synthetic state change only; never executes ip/tc.
            if command == m.actions(True)[-1]:
                self.actual = A
            elif command == m.actions(False)[-1]:
                self.actual = None
            return True

        def observe(target):
            return self.actual == target

        def watchdog():
            return self.watchdog_ok

        self.workflow = m.OfflineLifecycle(
            self.tmp.name, runner=runner, observe=observe, watchdog=watchdog)

    def test_complete_install_and_teardown(self):
        self.assertEqual(self.workflow.transition(None, A), "COMMITTED")
        self.assertEqual(self.workflow.inspect()["owned"], A)
        self.assertEqual(len(self.commands), 5)
        self.assertEqual(self.workflow.transition(A, None), "COMMITTED")
        self.assertIsNone(self.workflow.inspect()["owned"])
        self.assertEqual(len(self.commands), 8)
        self.assertEqual(self.workflow.inspect()["phase"], "clean")

    def test_watchdog_refusal_has_no_mutations(self):
        self.watchdog_ok = False
        with self.assertRaises(m.Refused):
            self.workflow.transition(None, A)
        self.assertEqual(self.commands, [])
        self.assertEqual(self.workflow.inspect()["phase"], "clean")

    def test_partial_failure_stays_pending(self):
        self.fail_at = 3
        with self.assertRaises(m.Refused):
            self.workflow.transition(None, A)
        self.assertEqual(self.workflow.inspect()["phase"], "pending")
        with self.assertRaises(m.Refused):
            self.workflow.transition(None, A)
        self.assertEqual(len(self.commands), 3)

    def test_stale_session_fails_closed(self):
        self.workflow.transition(None, A)
        with self.assertRaises(m.Refused):
            self.workflow.transition(None, {"generation": "other", "ifindex": 12})
        self.assertEqual(self.workflow.inspect()["owned"], A)

    def test_bad_postcondition_stays_pending(self):
        self.workflow.observe = lambda target: target is None
        with self.assertRaises(m.Refused):
            self.workflow.transition(None, A)
        self.assertEqual(self.workflow.inspect()["phase"], "pending")

    def test_reopen_preserves_session(self):
        self.workflow.transition(None, A)
        other = m.OfflineLifecycle(self.tmp.name, runner=lambda _: True,
                                  observe=lambda _: True, watchdog=lambda: True)
        self.assertEqual(other.inspect()["owned"], A)

if __name__ == "__main__":
    unittest.main(verbosity=2)
