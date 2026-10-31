#!/usr/bin/env python3
"""Offline regression tests: no network commands, deliberate kills, or writes."""
import importlib.util
from pathlib import Path
import sys
import unittest

p = Path(__file__).with_name("router-qos-download-ownership-journal-model.py")
spec = importlib.util.spec_from_file_location("qos_ownership_journal", p)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

def event(kind, generation="A", ifindex=5):
    return {"event": kind, "generation": generation, "ifindex": ifindex}

class OwnershipModelTests(unittest.TestCase):
    def test_normal_reconnect(self):
        c = m.Controller()
        self.assertEqual(c.handle(event("up"))[0], "PLAN_INSTALL")
        self.assertEqual(c.handle(event("up"))[0], "NOOP")
        self.assertEqual(c.handle(event("down"))[0], "PLAN_TEARDOWN")
        self.assertEqual(c.handle(event("up", "B", 7))[0], "PLAN_INSTALL")

    def test_stale_down_cannot_remove_new_session(self):
        c = m.Controller()
        c.handle(event("up", "B", 7))
        self.assertEqual(c.handle(event("down", "A", 5))[0], "REFUSE_STALE_DOWN")
        self.assertEqual(c.owned.generation, "B")

    def test_partial_install_requires_recovery(self):
        c = m.Controller()
        result, completed = c.handle(event("up"), failure_after_operation="attach_owned_ifb")
        self.assertEqual(result, "RECOVERY_REQUIRED")
        self.assertEqual(len(completed), 3)
        self.assertIsNone(c.owned)
        self.assertIsNotNone(c.pending)
        self.assertEqual(c.handle(event("up", "B", 7))[0], "REFUSE_RECOVERY_REQUIRED")
        self.assertEqual(c.handle(event("down"))[0], "REFUSE_RECOVERY_REQUIRED")

    def test_partial_teardown_requires_recovery(self):
        c = m.Controller()
        c.handle(event("up"))
        self.assertEqual(c.handle(event("down"), failure_after_operation="detach_owned_redirect")[0],
                         "RECOVERY_REQUIRED")
        self.assertEqual(c.handle(event("up", "B", 7))[0], "REFUSE_RECOVERY_REQUIRED")

    def test_no_unverified_recovery(self):
        c = m.Controller()
        c.handle(event("up"), failure_after_operation="arm_rollback")
        self.assertEqual(c.recover(verified_clean=False), "REFUSE_NOT_VERIFIED")
        self.assertTrue(c.recovery_required)

    def test_verified_recovery_reopens_state_machine(self):
        c = m.Controller()
        c.handle(event("up"), failure_after_operation="verify_ppp_identity")
        self.assertEqual(c.recover(verified_clean=True), "RECOVERY_ACKNOWLEDGED")
        self.assertEqual(c.handle(event("up", "B", 7))[0], "PLAN_INSTALL")

    def test_recovery_without_incident_refused(self):
        c = m.Controller()
        self.assertEqual(c.recover(verified_clean=True), "REFUSE_NO_PENDING_RECOVERY")

if __name__ == "__main__":
    unittest.main(verbosity=2)
