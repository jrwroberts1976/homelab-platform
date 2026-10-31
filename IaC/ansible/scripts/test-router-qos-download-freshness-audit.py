#!/usr/bin/env python3
"""Offline tests for freshness and journal locking, with no kernel operations."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

p=Path(__file__).with_name("router-qos-download-freshness-audit.py")
s=importlib.util.spec_from_file_location("qos_freshness_test",p)
m=importlib.util.module_from_spec(s)
sys.modules[s.name]=m
s.loader.exec_module(m)
A={"generation":"A","ifindex":5}

def evidence():
    return {"status":"OBSERVED_NOT_AUTHORIZED","namespace_inode":42,
            "recorded_inode":42,"host_inode":1,"observations":{
              "source":{"rc":0,"stdout":"qd31 up","stderr":""},
              "ifb":{"rc":1,"stdout":"","stderr":'Device "qi31" does not exist.'},
              "filter":{"rc":0,"stdout":"","stderr":""},
              "qdisc":{"rc":0,"stdout":"qdisc noqueue 0: root","stderr":""}}}

class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.j=m.journal_module.Journal(self.temp.name)
        self.j.begin(None,A)

    def check(self,**kw):
        args=dict(event_generation="A",observed_generation="A",
                  observed_monotonic_ns=100_000_000_000,
                  now_monotonic_ns=100_500_000_000)
        args.update(kw)
        return m.inspect(self.temp.name,None,A,evidence(),**args)

    def test_fresh_pending_is_observation_only(self):
        r=self.check()
        self.assertEqual(r["status"],"OBSERVED_FRESH_PENDING_NOT_AUTHORIZED")
        self.assertFalse(r["journal_recovery_authorized"])
        self.assertEqual(self.j.read()["phase"],"pending")

    def test_stale_observation_refused(self):
        self.assertEqual(self.check(now_monotonic_ns=104_000_000_000)["status"],"REFUSE_UNVERIFIED")

    def test_future_observation_refused(self):
        self.assertEqual(self.check(now_monotonic_ns=99_000_000_000)["status"],"REFUSE_UNVERIFIED")

    def test_session_mismatch_refused(self):
        self.assertEqual(self.check(observed_generation="B")["status"],"REFUSE_UNVERIFIED")

    def test_journal_session_mismatch_refused(self):
        r=m.inspect(self.temp.name,A,None,evidence(),event_generation="A",
                    observed_generation="A",observed_monotonic_ns=100,now_monotonic_ns=101)
        self.assertEqual(r["status"],"REFUSE_UNVERIFIED")

    def test_completed_journal_refused(self):
        self.j.finish(A,externally_verified=True)
        self.assertEqual(self.check()["status"],"REFUSE_UNVERIFIED")

    def test_dirty_kernel_evidence_refused(self):
        bad=evidence()
        bad["observations"]["filter"]["stdout"]="pref 49131"
        r=m.inspect(self.temp.name,None,A,bad,event_generation="A",
                    observed_generation="A",observed_monotonic_ns=100,now_monotonic_ns=101)
        self.assertEqual(r["status"],"REFUSE_UNVERIFIED")

if __name__=="__main__":
    unittest.main(verbosity=2)
