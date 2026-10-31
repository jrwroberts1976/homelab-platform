#!/usr/bin/env python3
"""Offline tests for the restricted namespace operation adapter."""
import importlib.util
from pathlib import Path
import sys
import unittest

p = Path(__file__).with_name("router-qos-download-isolated-executor.py")
spec = importlib.util.spec_from_file_location("qos_isolated", p)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

attestation_path = Path(__file__).with_name("router-qos-download-watchdog-attestation.py")
attestation_spec = importlib.util.spec_from_file_location("qos_attestation_real", attestation_path)
attestation = importlib.util.module_from_spec(attestation_spec)
sys.modules[attestation_spec.name] = attestation
attestation_spec.loader.exec_module(attestation)

def evidence(inode=42, active=True):
    return attestation.WatchdogEvidence(
        namespace="qos-p5", namespace_inode=inode, owned_inode=inode,
        unit="qos-p5-rollback.timer", timer_active=active,
        callback_path="/run/qos-p5-rollback.sh", callback_exists=True,
        deadline_monotonic_us=20_000_000, now_monotonic_us=10_000_000)

class FakeRunner:
    def __init__(self, fail_at=0):
        self.calls = []
        self.fail_at = fail_at
    def __call__(self, argv):
        self.calls.append(argv)
        if self.fail_at == len(self.calls):
            raise RuntimeError("injected failure")

class ExecutorTests(unittest.TestCase):
    def make(self, fail_at=0, armed=True, identity=None):
        runner = FakeRunner(fail_at)
        ident = identity or mod.NamespaceIdentity("qos-p5", 42, 1, 42)
        return mod.IsolatedExecutor(runner, ident, watchdog_armed=armed,\n                                    watchdog_evidence=evidence(), watchdog_validator=attestation.validate), runner

    def test_unarmed_refuses_without_calls(self):
        x, r = self.make(armed=False)
        with self.assertRaises(mod.Refused): x.install()
        self.assertEqual(r.calls, [])

    def test_wrong_or_host_namespace_refuses(self):
        for ident in (mod.NamespaceIdentity("ppp0", 42, 1, 42),
                      mod.NamespaceIdentity("qos-p5", 1, 1, 1),
                      mod.NamespaceIdentity("qos-p5", 42, 1, 43)):
            x, r = self.make(identity=ident)
            with self.assertRaises(mod.Refused): x.install()
            self.assertEqual(r.calls, [])

    def test_missing_verified_evidence_refuses(self):
        runner = FakeRunner()
        ident = mod.NamespaceIdentity("qos-p5", 42, 1, 42)
        x = mod.IsolatedExecutor(runner, ident, watchdog_armed=True)
        with self.assertRaises(mod.Refused): x.install()
        self.assertEqual(runner.calls, [])

    def test_expired_timer_refuses(self):
        runner = FakeRunner()
        ident = mod.NamespaceIdentity("qos-p5", 42, 1, 42)
        stale = attestation.WatchdogEvidence(
            namespace="qos-p5", namespace_inode=42, owned_inode=42,
            unit="qos-p5-rollback.timer", timer_active=True,
            callback_path="/run/qos-p5-rollback.sh", callback_exists=True,
            deadline_monotonic_us=1, now_monotonic_us=2)
        x = mod.IsolatedExecutor(runner, ident, watchdog_armed=True,
                                 watchdog_evidence=stale, watchdog_validator=attestation.validate)
        with self.assertRaises(mod.Refused): x.install()
        self.assertEqual(runner.calls, [])

    def test_namespace_timer_mismatch_refuses(self):
        runner = FakeRunner()
        ident = mod.NamespaceIdentity("qos-p5", 42, 1, 42)
        x = mod.IsolatedExecutor(runner, ident, watchdog_armed=True,
                                 watchdog_evidence=evidence(43), watchdog_validator=attestation.validate)
        with self.assertRaises(mod.Refused): x.install()
        self.assertEqual(runner.calls, [])

    def test_install_order_namespace_only(self):
        x, r = self.make()
        x.install()
        self.assertTrue(x.installed)
        self.assertEqual(len(r.calls), 5)
        self.assertTrue(all(call[:4] == ["ip", "netns", "exec", "qos-p5"] for call in r.calls))
        self.assertIn("43mbit", r.calls[2])

    def test_duplicate_install_refused(self):
        x, r = self.make()
        x.install()
        with self.assertRaises(mod.Refused): x.install()
        self.assertEqual(len(r.calls), 5)

    def test_partial_install_preserved_for_watchdog(self):
        for point in range(1, 6):
            x, r = self.make(fail_at=point)
            with self.assertRaises(RuntimeError): x.install()
            self.assertTrue(x.pending)
            with self.assertRaises(mod.Refused): x.teardown()

    def test_owned_teardown_order(self):
        x, r = self.make()
        x.install()
        x.teardown()
        self.assertFalse(x.installed)
        self.assertEqual(len(r.calls), 8)
        self.assertEqual(r.calls[-1][-4:], ["link", "del", "dev", "qp5ifb"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
