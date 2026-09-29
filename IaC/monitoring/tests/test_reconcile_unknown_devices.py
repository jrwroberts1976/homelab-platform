"""Offline regression tests for selective identity reconciliation."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "audits/reconcile_unknown_devices.py"
spec = importlib.util.spec_from_file_location("reconcile_unknown_devices", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReconcileTests(unittest.TestCase):
    def test_known_devices_skipped_and_undocumented_remain_unresolved(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder)
            (evidence / "managed-hosts").mkdir()
            (evidence / "managed-hosts/dns-01.json").write_text("{}")
            (evidence / "network-scan.json").write_text(json.dumps({
                "subnet": "192.168.2.0/24",
                "hosts": [
                    {"ip": "192.168.2.51", "mac": "AA:BB:CC:DD:EE:FF", "names": [], "open_ports": []},
                    {"ip": "192.168.2.6", "mac": "58:02:05:FD:E1:8B", "names": [], "open_ports": []},
                    {"ip": "192.168.2.206", "mac": "16:C1:05:AD:4B:8A", "names": [], "open_ports": []},
                ],
            }))
            (evidence / "os-fingerprints.json").write_text(json.dumps([
                {"ip": "192.168.2.6", "result_present": True,
                 "matches": [{"name": "Linux", "accuracy": "85"}]},
                {"ip": "192.168.2.206", "result_present": True, "matches": []},
            ]))
            dns = evidence / "dns-clues.json"
            dns.write_text(json.dumps([{
                "ip": "192.168.2.206", "server": "dns-01",
                "query_count": 12, "top_domains": ["example.test"],
            }]))
            oui = evidence / "oui.csv"
            oui.write_text("Registry,Assignment,Organization Name,Organization Address\n"
                           "MA-L,580205,Example Wireless,Example\n")
            report = module.reconcile(evidence, {
                "assets": [{"name": "dns-01", "state": "active", "address": "192.168.2.51"}]
            }, dns, oui)
            self.assertEqual(report["counts"]["known"], 1)
            self.assertEqual(report["counts"]["unresolved"], 2)
            unknown = {x["ip"]: x for x in report["unresolved_devices"]}
            self.assertTrue(unknown["192.168.2.6"]["os_fingerprint_present"])
            self.assertEqual(unknown["192.168.2.6"]["mac_manufacturer"]["name"],
                             "Example Wireless")
            self.assertEqual(unknown["192.168.2.206"]["mac_manufacturer"]["type"],
                             "locally_administered")
            self.assertEqual(unknown["192.168.2.206"]["dns_clues"][0]["query_count"], 12)
            self.assertIn("192.168.2.206", report["no_direct_or_nmap_os_evidence"])
            self.assertEqual(report["known_devices"][0]["known_identity"], "dns-01")
            self.assertTrue(report["known_devices"][0]["direct_os_evidence"])

    def test_reject_other_subnet(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder)
            (evidence / "network-scan.json").write_text(json.dumps({
                "subnet": "10.0.0.0/8", "hosts": [],
            }))
            with self.assertRaises(ValueError):
                module.reconcile(evidence, {"assets": []})

    def test_atomic_report_is_private(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "private.json"
            module.atomic_json(output, {"test": True})
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(output.read_text()), {"test": True})


if __name__ == "__main__":
    unittest.main()
