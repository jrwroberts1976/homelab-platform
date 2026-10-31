#!/usr/bin/env python3
"""Offline-only validation for PPP event replay. No system changes."""
import importlib.util
import pathlib
import sys
import unittest

p = pathlib.Path(__file__).with_name("router-qos-download-ppp-event-replay.py")
spec = importlib.util.spec_from_file_location("qos_replay", p)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

def event(kind, generation, index, **kw):
    return {"event": kind, "generation": generation, "ifindex": index, **kw}

class ReplayTests(unittest.TestCase):
    def test_reconnect_and_duplicate(self):
        r = mod.replay([event("up","A",5),event("up","A",5),event("down","A",5),event("up","B",7)])
        self.assertEqual([v["decision"] for v in r["transitions"]], ["PLAN_INSTALL","NOOP","PLAN_TEARDOWN","PLAN_INSTALL"])
        self.assertEqual(r["owned"], {"generation":"B","ifindex":7})
        self.assertFalse(r["network_modified"])

    def test_stale_down_refused(self):
        r = mod.replay([event("up","A",5),event("down","B",7)])
        self.assertEqual(r["transitions"][-1]["decision"],"REFUSE_STALE_DOWN")

    def test_foreign_resources_refused(self):
        r = mod.replay([event("up","A",5,foreign=True)])
        self.assertEqual(r["owned"],None)
        self.assertEqual(r["transitions"][0]["decision"],"REFUSE_UNVERIFIED")

    def test_partial_resources_refused(self):
        r = mod.replay([event("up","A",5,partial=True)])
        self.assertEqual(r["transitions"][0]["decision"],"REFUSE_UNVERIFIED")

    def test_failure_has_no_commit(self):
        r = mod.replay([event("up","A",5,fail_before_commit=True)])
        self.assertEqual(r["owned"],None)
        self.assertEqual(r["transitions"][0]["decision"],"INJECTED_FAILURE")

    def test_reconnect_with_old_state_refused(self):
        r = mod.replay([event("up","A",5),event("up","B",7)])
        self.assertEqual(r["transitions"][-1]["decision"],"REFUSE_OLD_SESSION_PRESENT")

if __name__ == "__main__":
    unittest.main(verbosity=2)
