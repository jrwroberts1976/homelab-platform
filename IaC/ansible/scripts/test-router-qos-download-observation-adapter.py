#!/usr/bin/env python3
"""Offline integration fixture tests; no tc/ip calls or host modifications."""
import importlib.util
from pathlib import Path
import sys
import unittest
from copy import deepcopy

p = Path(__file__).with_name("router-qos-download-observation-adapter.py")
spec = importlib.util.spec_from_file_location("qos_obs_adapter_test", p)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

def fixture():
    return {
        "status": "OBSERVED_NOT_AUTHORIZED", "namespace_inode": 42,
        "recorded_inode": 42, "host_inode": 1,
        "journal_recovery_authorized": False,
        "observations": {
            "source": {"rc": 0, "stdout": "12: qd31: <BROADCAST>\n", "stderr": ""},
            "ifb": {"rc": 1, "stdout": "", "stderr": 'Device "qi31" does not exist.\n'},
            "filter": {"rc": 0, "stdout": "", "stderr": ""},
            "qdisc": {"rc": 0, "stdout": "qdisc noqueue 0: root\n", "stderr": ""},
        },
    }

class AdapterTests(unittest.TestCase):
    def test_clean_observation_never_authorizes(self):
        r = m.interpret(fixture())
        self.assertEqual(r["status"], "OBSERVED_CLEAN_NOT_AUTHORIZED")
        self.assertFalse(r["journal_recovery_authorized"])

    def test_absent_namespace_inconclusive(self):
        f = fixture()
        f["status"] = "INCONCLUSIVE_NAMESPACE_OR_OWNER_ABSENT"
        self.assertEqual(m.interpret(f)["status"], "INCONCLUSIVE_OR_REFUSED")

    def test_mismatched_inode_refuses(self):
        f = fixture()
        f["recorded_inode"] = 43
        self.assertEqual(m.interpret(f)["status"], "REFUSE_UNVERIFIED")

    def test_existing_ifb_refuses(self):
        f = fixture()
        f["observations"]["ifb"] = {"rc": 0, "stdout": "qi31", "stderr": ""}
        self.assertEqual(m.interpret(f)["status"], "REFUSE_UNVERIFIED")

    def test_filter_or_clsact_refuses(self):
        for key, text in (("filter", "pref 49131"), ("qdisc", "qdisc clsact")):
            f = fixture()
            f["observations"][key]["stdout"] = text
            self.assertEqual(m.interpret(f)["status"], "REFUSE_UNVERIFIED")

    def test_missing_or_failed_command_refuses(self):
        f = fixture()
        del f["observations"]["filter"]
        self.assertEqual(m.interpret(f)["status"], "REFUSE_UNVERIFIED")
        f = fixture()
        f["observations"]["qdisc"]["rc"] = 1
        self.assertEqual(m.interpret(f)["status"], "REFUSE_UNVERIFIED")

    def test_invalid_input_refuses(self):
        self.assertEqual(m.interpret(None)["status"], "REFUSE_INVALID_SNAPSHOT")

if __name__ == "__main__":
    unittest.main(verbosity=2)
