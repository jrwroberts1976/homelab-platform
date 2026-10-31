#!/usr/bin/env python3
"""Offline tests for Phase 5 read-only PPP reconciliation; no host access."""
import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).with_name("router-qos-download-ppp-reconciler-plan.py")
spec = importlib.util.spec_from_file_location("qos_ppp_plan", path)
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)

class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.a = module.Session("ppp0", 5, "session-A")
        self.b = module.Session("ppp0", 7, "session-B")

    def test_up_first_and_duplicate(self):
        self.assertEqual(module.decide("up", self.a), "ARM_WATCHDOG_BEFORE_INSTALL")
        self.assertEqual(module.decide("up", self.a, self.a), "NOOP_ALREADY_CURRENT")

    def test_reconnect_requires_old_teardown(self):
        self.assertEqual(module.decide("up", self.b, self.a), "REQUIRE_VERIFIED_OLD_SESSION_TEARDOWN")

    def test_down_ownership(self):
        self.assertEqual(module.decide("down", self.a), "NOOP_NOT_OWNED")
        self.assertEqual(module.decide("down", self.b, self.a), "REFUSE_STALE_DOWN_EVENT")
        self.assertEqual(module.decide("down", self.a, self.a), "VERIFY_OWNERSHIP_THEN_REMOVE")

    def test_foreign_and_partial_fail_closed(self):
        for event in ("up", "down"):
            self.assertEqual(module.decide(event, self.a, foreign=True), "REFUSE_UNVERIFIED_RESOURCES")
            self.assertEqual(module.decide(event, self.a, partial=True), "REFUSE_UNVERIFIED_RESOURCES")

    def test_session_validation(self):
        for data in (
            {"interface": "eth1", "ifindex": 5, "token": "x"},
            {"interface": "ppp0", "ifindex": 0, "token": "x"},
            {"interface": "ppp0", "ifindex": True, "token": "x"},
            {"interface": "ppp0", "ifindex": 5, "token": ""},
        ):
            with self.assertRaises(ValueError):
                module.Session.from_mapping(data)

if __name__ == "__main__":
    unittest.main(verbosity=2)
