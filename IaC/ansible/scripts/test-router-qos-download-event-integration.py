#!/usr/bin/env python3
"""Offline adapter tests; no network or systemd operations."""
import importlib.util
from pathlib import Path
import sys
import unittest

path = Path(__file__).with_name("router-qos-download-event-integration.py")
spec = importlib.util.spec_from_file_location("qos_adapter", path)
adapter = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = adapter
spec.loader.exec_module(adapter)


def ev(kind, generation="A", index=5, **extra):
    return {"event": kind, "generation": generation, "ifindex": index, **extra}


class IntegrationTests(unittest.TestCase):
    def test_connection_calls_ordered_operations(self):
        runner = adapter.Integration()
        self.assertEqual(runner.event(ev("up")), "PLAN_INSTALL")
        self.assertEqual(runner.backend.calls,
                         ["arm_rollback", "verify_ppp_identity", "attach_owned_ifb"])

    def test_duplicate_does_not_mutate_again(self):
        runner = adapter.Integration()
        runner.event(ev("up"))
        self.assertEqual(runner.event(ev("up")), "NOOP")
        self.assertEqual(len(runner.backend.calls), 3)

    def test_stale_disconnect_and_foreign_refusal(self):
        runner = adapter.Integration()
        runner.event(ev("up"))
        self.assertEqual(runner.event(ev("down", "B", 7)), "REFUSE_STALE_DOWN")
        self.assertEqual(runner.event(ev("down", foreign=True)), "REFUSE_UNVERIFIED")
        self.assertEqual(len(runner.backend.calls), 3)

    def test_teardown_before_reconnect(self):
        runner = adapter.Integration()
        runner.event(ev("up"))
        self.assertEqual(runner.event(ev("up", "B", 7)), "REFUSE_OLD_SESSION_PRESENT")
        self.assertEqual(runner.event(ev("down")), "PLAN_TEARDOWN")
        self.assertEqual(runner.event(ev("up", "B", 7)), "PLAN_INSTALL")
        self.assertEqual(runner.backend.calls[3:6],
                         ["verify_owned_state", "detach_owned_redirect", "remove_owned_ifb"])

    def test_partial_install_refusal(self):
        runner = adapter.Integration()
        self.assertEqual(runner.event(ev("up", partial=True)), "REFUSE_UNVERIFIED")
        self.assertIsNone(runner.owned)
        self.assertEqual(runner.backend.calls, [])

    def test_injected_failure_does_not_commit_owned_state(self):
        runner = adapter.Integration()
        self.assertEqual(runner.event(ev("up"), fail_at="attach_owned_ifb"),
                         "INJECTED_FAILURE_UNCOMMITTED")
        self.assertIsNone(runner.owned)
        self.assertEqual(runner.backend.calls,
                         ["arm_rollback", "verify_ppp_identity"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
