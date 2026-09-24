"""Run: python3 -m unittest discover -s IaC/ansible/roles/network_host_os_evidence/tests"""
import importlib.util
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "files/os_dns_evidence.py"
spec = importlib.util.spec_from_file_location("os_dns_evidence", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.inventory = {"192.168.2.25": {"mac": "aa:bb:cc:dd:ee:ff", "first_seen": 100, "last_seen": 1000}}
    def test_ubuntu_hint_not_verified(self):
        result = mod.classify(self.inventory, [{"id.orig_h": "192.168.2.25", "query": "security.ubuntu.com", "ts": 500}], 100, 1000)
        self.assertEqual(result["evidence"][0]["indicator"], "ubuntu")
        self.assertEqual(result["verified_os_count"], 0)
    def test_suffix_boundary_and_generic_google(self):
        self.assertIsNone(mod.indicator("evilsecurity.ubuntu.com"))
        self.assertIsNone(mod.indicator("dl.google.com"))
        self.assertEqual(mod.indicator("a.windowsupdate.com."), "microsoft_updates")
    def test_resolver_exclusion(self):
        result = mod.classify(self.inventory, [{"src_ip": "192.168.2.25", "query": "deb.debian.org", "timestamp": 500}], 100, 1000, ["192.168.2.25"])
        self.assertEqual(result["evidence"], [])
    def test_stale_identity(self):
        result = mod.classify(self.inventory, [{"src_ip": "192.168.2.25", "query": "deb.debian.org", "timestamp": 99}], 0, 1000)
        self.assertEqual(result["evidence"], [])
    def test_unattributed(self):
        result = mod.classify({}, [{"src_ip": "192.168.2.25", "query": "deb.debian.org", "timestamp": 500}], 0, 1000)
        self.assertEqual(result["evidence"], [])
    def test_repeated_queries_not_independent_confidence(self):
        events = [{"src_ip": "192.168.2.25", "query": "deb.debian.org", "timestamp": t} for t in [500, 501]]
        result = mod.classify(self.inventory, events, 100, 1000)
        self.assertEqual(result["evidence"][0]["count"], 2)
        self.assertEqual(result["evidence"][0]["classification"], "traffic_hint_only")
if __name__ == "__main__":
    unittest.main()
