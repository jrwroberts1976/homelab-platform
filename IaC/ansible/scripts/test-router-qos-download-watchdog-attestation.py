#!/usr/bin/env python3
"""Read-only unit tests for watchdog evidence admission gate."""
import importlib.util
from pathlib import Path
import sys
import unittest

path = Path(__file__).with_name("router-qos-download-watchdog-attestation.py")
spec = importlib.util.spec_from_file_location("qos_attestation", path)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def evidence(**overrides):
    data = dict(
        namespace="qos-p5",
        namespace_inode=4020000001,
        owned_inode=4020000001,
        unit="qos-p5-rollback.timer",
        timer_active=True,
        callback_path="/run/qos-p5-rollback.sh",
        callback_exists=True,
        deadline_monotonic_us=15_000_000,
        now_monotonic_us=10_000_000,
    )
    data.update(overrides)
    return mod.WatchdogEvidence(**data)


class AdmissionTests(unittest.TestCase):
    def test_valid_evidence_allows_only_planned_operations(self):
        self.assertEqual(len(mod.authorized_operations(evidence())), 4)

    def test_absent_timer_refused(self):
        with self.assertRaises(mod.NotReady):
            mod.validate(evidence(timer_active=False))

    def test_expired_deadline_refused(self):
        with self.assertRaises(mod.NotReady):
            mod.validate(evidence(deadline_monotonic_us=10_000_000))

    def test_missing_callback_refused(self):
        with self.assertRaises(mod.NotReady):
            mod.validate(evidence(callback_exists=False))

    def test_wrong_namespace_refused(self):
        with self.assertRaises(mod.NotReady):
            mod.validate(evidence(namespace="ppp0"))

    def test_namespace_identity_mismatch_refused(self):
        with self.assertRaises(mod.NotReady):
            mod.validate(evidence(owned_inode=42))

    def test_unknown_unit_refused(self):
        with self.assertRaises(mod.NotReady):
            mod.validate(evidence(unit="other.timer"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
