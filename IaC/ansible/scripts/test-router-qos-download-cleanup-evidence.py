#!/usr/bin/env python3
"""Offline captured-output evaluator tests; no network commands."""
import importlib.util
from pathlib import Path
import sys
import unittest
from dataclasses import replace

p = Path(__file__).with_name("router-qos-download-cleanup-evidence.py")
spec = importlib.util.spec_from_file_location("cleanup_evidence", p)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

def clean():
    return m.Snapshot(
        namespace="qos-proof31", namespace_inode=42, recorded_inode=42,
        host_inode=1, source_present=True, ifb_lookup_rc=1,
        ifb_lookup_output="Device \"qi31\" does not exist.",
        ingress_rc=0, ingress_output="", qdisc_rc=0,
        qdisc_output="qdisc noqueue 0: root refcnt 2")

class EvidenceTests(unittest.TestCase):
    def test_clean_is_observation_only(self):
        result = m.evaluate_clean(clean())
        self.assertTrue(result["observed_clean"])
        self.assertFalse(result["journal_recovery_authorized"])
        self.assertFalse(result["network_modified"])

    def test_namespace_mismatch_refused(self):
        for changed in (dict(namespace="ppp0"), dict(recorded_inode=43),
                        dict(host_inode=42), dict(namespace_inode=0)):
            with self.assertRaises(m.Unverified):
                m.evaluate_clean(replace(clean(), **changed))

    def test_ifb_still_present_refused(self):
        with self.assertRaises(m.Unverified):
            m.evaluate_clean(replace(clean(), ifb_lookup_rc=0, ifb_lookup_output="qi31"))

    def test_ambiguous_ifb_error_refused(self):
        with self.assertRaises(m.Unverified):
            m.evaluate_clean(replace(clean(), ifb_lookup_rc=1, ifb_lookup_output="permission denied"))

    def test_ingress_filter_refused(self):
        with self.assertRaises(m.Unverified):
            m.evaluate_clean(replace(clean(), ingress_output="filter protocol all pref 49131"))

    def test_ingress_qdisc_refused(self):
        with self.assertRaises(m.Unverified):
            m.evaluate_clean(replace(clean(), qdisc_output="qdisc clsact ffff: parent ffff:fff1"))

    def test_failed_inspection_refused(self):
        for changed in (dict(ingress_rc=1), dict(qdisc_rc=1), dict(source_present=False)):
            with self.assertRaises(m.Unverified):
                m.evaluate_clean(replace(clean(), **changed))

if __name__ == "__main__":
    unittest.main(verbosity=2)
