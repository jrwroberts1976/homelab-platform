#!/usr/bin/env python3
"""Mocked, offline read-only collector checks."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

p = Path(__file__).with_name("router-qos-download-sensor-readonly-collector.py")
spec = importlib.util.spec_from_file_location("readonly_qos_collector", p)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

def result(rc=0, stdout=""):
    return SimpleNamespace(returncode=rc, stdout=stdout, stderr="")

class CollectorTests(unittest.TestCase):
    def test_wrong_host_refused(self):
        with patch.object(m, "run", return_value=result(stdout="router-01\n")):
            with self.assertRaises(RuntimeError): m.collect()

    def test_missing_namespace_is_inconclusive(self):
        with patch.object(m, "run", return_value=result(stdout="sensor-01\n")), patch.object(m.Path, "exists", return_value=False):
            evidence = m.collect()
        self.assertFalse(evidence["journal_recovery_authorized"])
        self.assertEqual(evidence["status"], "INCONCLUSIVE_NAMESPACE_OR_OWNER_ABSENT")

    def test_no_mutating_commands_when_absent(self):
        calls = []
        def observe(argv):
            calls.append(argv)
            return result(stdout="sensor-01\n")
        with patch.object(m, "run", side_effect=observe), patch.object(m.Path, "exists", return_value=False):
            m.collect()
        self.assertEqual(calls, [["hostname", "-s"]])

if __name__ == "__main__":
    unittest.main(verbosity=2)
