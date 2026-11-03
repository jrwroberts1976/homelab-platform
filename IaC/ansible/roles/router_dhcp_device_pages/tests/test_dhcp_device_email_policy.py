"""Offline, no-SMTP tests of the optional shared-MAC DHCP notification path."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

FILES = Path(__file__).parents[1] / "files"
PATH = FILES / "dhcp_device_email_policy.py"
spec = importlib.util.spec_from_file_location("dhcp_device_email_policy", PATH)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

MAC = "02:11:22:33:44:55"
MAC_B = "02:11:22:33:44:66"
TIME = 1_800_000_000_000_000_000  # synthetic nanoseconds


class DHCPEmailPolicyTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.pages = self.root / "pages"
        self.pages.mkdir()
        self.profiles = {MAC: {
            "profiled_ip": "192.168.2.101",
            "profile": {"tcp": {"os_matches": [{
                "name": "Linux 6.x", "accuracy": "95"}]}}
        }}
        self.inventory = {"192.168.2.101": {
            "mac": MAC, "vendor": "Example vendor", "online": True}}
        self.records = {"schema_version": 1, "devices": {
            MAC: {"ip": "192.168.2.101", "hostname": "test-laptop",
                  "first_seen_ns": TIME + 1_000_000_000,
                  "last_seen_ns": TIME + 2_000_000_000},
        }}
        self.marker = {"schema_version": 1, "activated_at_ns": TIME}
        self.now = TIME + 4_000_000_000
        self._write_page(MAC)

    def _write_page(self, mac):
        (self.pages / (policy.uid_for(mac) + ".json")).write_text(
            json.dumps({"uid": policy.uid_for(mac)}))

    def run_policy(self, known=None):
        return policy.candidates(self.records, self.marker, known or {},
                                 self.inventory, self.profiles, self.pages,
                                 now_ns=self.now)

    def test_new_dhcp_device_includes_link_and_inferred_os(self):
        results = self.run_policy()
        self.assertEqual(len(results), 1)
        device = results[0]
        self.assertEqual(device["mac"], MAC)
        self.assertEqual(device["source"], "router-01 DHCPACK")
        self.assertIn("Nmap inferred", device["os_evidence"])
        self.assertIn("95%", device["os_evidence"])
        self.assertEqual(device["dashboard_url"],
                         "https://grafana.home.jrwroberts.co.uk/d/" + policy.uid_for(MAC))

    def test_shared_first_seen_registry_blocks_every_repeat(self):
        self.assertEqual(self.run_policy({MAC: {"status": "baseline"}}), [])
        self.assertEqual(self.run_policy({MAC: {"status": "alerted"}}), [])
        self.assertEqual(self.run_policy({MAC: {"status": "seen"}}), [])

    def test_historical_dhcp_before_activation_not_sent(self):
        self.records["devices"][MAC]["first_seen_ns"] = TIME - 100
        self.assertEqual(self.run_policy(), [])

    def test_renewal_does_not_realert_after_shared_registry_send(self):
        self.records["devices"][MAC]["ip"] = "192.168.2.105"
        self.records["devices"][MAC]["last_seen_ns"] += 1_000_000_000
        self.assertEqual(self.run_policy({MAC: {"status": "alerted"}}), [])

    def test_missing_or_mismatched_nmap_does_not_claim_os(self):
        self.profiles[MAC]["profiled_ip"] = "192.168.2.102"
        self.assertEqual(self.run_policy()[0]["os_evidence"],
                         "Pending identification")

    def test_no_dashboard_file_means_no_email(self):
        (self.pages / (policy.uid_for(MAC) + ".json")).unlink()
        self.assertEqual(self.run_policy(), [])

    def test_mismatched_dashboard_identity_fails_closed(self):
        (self.pages / (policy.uid_for(MAC) + ".json")).write_text(
            json.dumps({"uid": "some-other-identity"}))
        with self.assertRaises(ValueError):
            self.run_policy()

    def test_malformed_activation_or_mac_fails_closed(self):
        self.marker["activated_at_ns"] = -1
        with self.assertRaises(ValueError):
            self.run_policy()
        self.marker["activated_at_ns"] = TIME
        self.records["devices"]["01:11:22:33:44:55"] = {
            "ip": "192.168.2.105", "first_seen_ns": TIME+2,
            "last_seen_ns": TIME+2}
        with self.assertRaises(ValueError):
            self.run_policy()

    def test_candidate_limit_for_approved_backlog(self):
        for n in range(11):
            mac = f"02:00:10:20:30:{n+30:02x}"
            self.records["devices"][mac] = {
                "ip": f"192.168.2.{n+101}", "hostname": "test",
                "first_seen_ns": TIME + n + 1, "last_seen_ns": TIME + n + 2}
            self._write_page(mac)
        self.assertEqual(len(self.run_policy()), policy.MAX_PENDING)

    def test_from_files_does_not_mutate_registry(self):
        paths = {name: self.root / (name + ".json")
                 for name in ("state", "marker", "profiles")}
        paths["state"].write_text(json.dumps(self.records))
        paths["marker"].write_text(json.dumps(self.marker))
        paths["profiles"].write_text(json.dumps({"profiles": self.profiles}))
        reg = {"version": 1, "devices": {}}
        result = policy.from_files(
            paths["state"], paths["marker"], reg, self.inventory,
            paths["profiles"], self.pages, now_ns=self.now)
        self.assertEqual(len(result), 1)
        self.assertEqual(reg, {"version": 1, "devices": {}})
        paths["state"].unlink()
        with self.assertRaises(ValueError):
            policy.from_files(paths["state"], paths["marker"], reg,
                              self.inventory, paths["profiles"], self.pages,
                              now_ns=self.now)


if __name__ == "__main__":
    unittest.main()
