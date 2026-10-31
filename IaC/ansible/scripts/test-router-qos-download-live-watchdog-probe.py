#!/usr/bin/env python3
"""Offline tests for read-only sensor watchdog probe."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

p=Path(__file__).with_name("router-qos-download-live-watchdog-probe.py")
spec=importlib.util.spec_from_file_location("qos_live_probe",p)
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

def response(code=0, output=""):
    return SimpleNamespace(returncode=code,stdout=output)

def fake_command(*argv):
    if argv[:1]==("hostname",): return response(output="sensor-01\n")
    if argv[:2]==("stat","-Lc"):
        return response(output="42\n" if "qos-p5" in argv[-1] else "1\n")
    if argv[:2]==("systemctl","is-active"): return response(code=3,output="inactive\n")
    if argv[:2]==("systemctl","show"): return response(output="n/a\n")
    raise AssertionError(argv)

class ProbeTests(unittest.TestCase):
    def test_inactive_watchdog_never_authorizes(self):
        with patch.object(m,"command",side_effect=fake_command),patch.object(m.Path,"is_file",return_value=False):
            r=m.probe()
        self.assertFalse(r["timer_active"])
        self.assertFalse(r["verified_for_mutation"])
        self.assertFalse(r["network_modified"])
        self.assertIsNone(r["deadline_monotonic_us"])

    def test_wrong_host_refused(self):
        with patch.object(m,"command",return_value=response(output="router-01\n")):
            with self.assertRaises(RuntimeError): m.probe()

    def test_missing_namespace_fail_closed(self):
        def commands(*argv):
            if argv[:2]==("stat","-Lc") and "qos-p5" in argv[-1]: return response(1,"")
            return fake_command(*argv)
        with patch.object(m,"command",side_effect=commands),patch.object(m.Path,"is_file",return_value=False):
            r=m.probe()
        self.assertIsNone(r["namespace_inode"])
        self.assertFalse(r["verified_for_mutation"])

    def test_probe_has_no_modifying_commands(self):
        calls=[]
        def observed(*argv):
            calls.append(argv)
            return fake_command(*argv)
        with patch.object(m,"command",side_effect=observed),patch.object(m.Path,"is_file",return_value=False):
            m.probe()
        self.assertTrue(all(argv[0] in ("hostname","stat","systemctl") for argv in calls))
        self.assertTrue(all(argv[0]!="systemctl" or argv[1] in ("show","is-active") for argv in calls))

if __name__=="__main__":
    unittest.main(verbosity=2)
