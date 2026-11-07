#!/usr/bin/env python3
"""Offline preview regression tests; no file I/O, SSH, scans or Zabbix calls."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from os_evidence_inventory_preview import preview, validate_passive

IP1, IP2, IP3 = "192.168.2.51", "192.168.2.186", "192.168.2.125"
M1, M2, M3 = "aa:bb:cc:00:00:01", "24:b2:b9:30:f8:55", "a4:77:33:5f:94:fe"
MEMBERSHIP = {
    "zabbix_os_authoritative": [IP1],
    "zabbix_without_os": [],
    "ambiguous": [],
    "unmatched_inventory": [IP2, IP3],
}
LAPTOP = {"last_ip": IP2, "profiled_ip": IP2, "status": "partial",
          "profile": {"tcp": {"os_matches": [], "ports": []}}}
HINTS = [
    {"src_ip": IP2, "os_family_hint": "Windows", "observations": 1,
     "confidence": "low", "mac_attribution": "unverified"},
    {"src_ip": IP3, "os_family_hint": "Linux", "observations": 6,
     "confidence": "low", "mac_attribution": "unverified"},
]


class InventoryPreviewTests(unittest.TestCase):
    def setUp(self):
        self.inventory = {
            IP1: {"mac": M1}, IP2: {"mac": M2}, IP3: {"mac": M3},
        }
        self.profiles = {M2: LAPTOP}

    def test_managed_authority_and_laptop_candidate(self):
        rows = preview(self.inventory, self.profiles, MEMBERSHIP, HINTS)
        found = {r["ip"]: r for r in rows}
        self.assertEqual(found[IP1]["os_source"], "zabbix")
        self.assertEqual(found[IP2]["os_source"], "http_user_agent")
        self.assertEqual(found[IP2]["attribution"], "historical_ip_unverified")
        self.assertEqual(found[IP3]["os_family"], "Linux")

    def test_without_passive_laptop_stays_partial(self):
        rows = preview(self.inventory, self.profiles, MEMBERSHIP)
        found = {r["ip"]: r for r in rows}
        self.assertEqual(found[IP2]["status"], "nmap_partial_no_os")
        self.assertEqual(found[IP3]["status"], "unknown")

    def test_wrong_profile_ip_not_used(self):
        self.profiles[M2] = dict(LAPTOP, last_ip=IP3)
        rows = preview(self.inventory, self.profiles, MEMBERSHIP)
        self.assertEqual({r["ip"]: r for r in rows}[IP2]["status"], "unknown")

    def test_conflicting_membership_rejected(self):
        groups = dict(MEMBERSHIP, ambiguous=[IP2])
        with self.assertRaises(ValueError):
            preview(self.inventory, self.profiles, groups, HINTS)

    def test_low_confidence_provenance_required(self):
        with self.assertRaises(ValueError):
            validate_passive({"status": "dry_run_only",
                              "candidates": [dict(HINTS[0], confidence="high")]})

    def test_valid_sensor_dry_run_candidates(self):
        self.assertEqual(validate_passive({"status": "dry_run_only",
                                           "candidates": HINTS}), HINTS)

    def test_other_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_passive({"status": "published", "candidates": HINTS})


if __name__ == "__main__":
    unittest.main()
